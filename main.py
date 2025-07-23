import os
from typing import List, Dict, Any
from fastapi import FastAPI, Form, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from openai import OpenAI
from dotenv import load_dotenv
from data import (
    load_vectorstore,
    create_and_save_vectorstore,
    get_relevant_context,
)

load_dotenv()

openai = OpenAI(api_key=os.getenv("OPENAI_API_SECRET_KEY"))

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SYSTEM_PROMPT = {
    'role': 'system',
    'content': (
        "You are a virtual assistant of Ajman University. "
        "Answer questions about admission, tuition, procedures, scholarships, and campus life. "
        "Base every answer solely on the provided context. "
        "If the answer is not present, reply: \"I'm sorry, I couldn't find that information.\" "
        "Do not mention sources or context in your answer."
    )
}

try:
    vectorstore = load_vectorstore()
    print("Vector store loaded successfully.")
except Exception:
    print("Vector store not found. Creating a new one...")
    vectorstore = create_and_save_vectorstore()


@app.get("/debug-web-content")
async def debug_web_content():
    """Verify web content was loaded"""
    from data import load_crawled_txt_files
    docs = load_crawled_txt_files()
    return {
        "count": len(docs),
        "sample": {
            "source": docs[0].metadata['source'],
            "content": docs[0].page_content[:200] + "..."
        } if docs else None
    }


def create_contextual_message(user_input: str) -> str:
    context = get_relevant_context(user_input, vectorstore, k=10)
    print("\n🔍 Retrieved Context:\n", context[:500], "...\n")
    return (
        f"{context}\n\n"
        f"User question: {user_input}\n\n"
        "Answer the student's question as fully as possible using only the information above. "
        "If you don't find the answer in the information above, reply: \"I'm sorry, I couldn't find that information.\""
    )

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": []})

@app.websocket("/ws")
async def chat_socket(websocket: WebSocket):
    await websocket.accept()
    chat_log: List[Dict[str, Any]] = [SYSTEM_PROMPT]
    chat_responses: List[str] = []
    try:
        while True:
            user_input = await websocket.receive_text()
            contextual_message = create_contextual_message(user_input)
            chat_log.append({"role": "user", "content": contextual_message})
            chat_responses.append(user_input)
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=chat_log,
                    temperature=0.0,
                    stream=True,
                )
                ai_response = ""
                for chunk in response:
                    delta = chunk.choices[0].delta
                    if delta and getattr(delta, "content", None):
                        ai_response += delta.content
                        await websocket.send_text(delta.content)
                chat_log.append({"role": "assistant", "content": ai_response})
                chat_responses.append(ai_response)
            except Exception as e:
                await websocket.send_text(f"Error: {str(e)}")
                break
    except WebSocketDisconnect:
        print("WebSocket disconnected.")


@app.post("/", response_class=HTMLResponse)
async def handle_post(request: Request, user_input: str = Form(...)):
    chat_log = [SYSTEM_PROMPT]
    chat_responses = []
    contextual_message = create_contextual_message(user_input)
    chat_log.append({"role": "user", "content": contextual_message})
    chat_responses.append(user_input)
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=chat_log,
        temperature=0.0,
    )
    bot_response = response.choices[0].message.content
    chat_log.append({"role": "assistant", "content": bot_response})
    chat_responses.append(bot_response)
    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})

@app.get("/image", response_class=HTMLResponse)
async def image_page(request: Request):
    return templates.TemplateResponse("image.html", {"request": request})

@app.post("/image", response_class=HTMLResponse)
async def generate_image(request: Request, user_input: str = Form(...)):
    response = openai.images.generate(prompt=user_input, n=1, size="512x512")
    image_url = response.data[0].url
    return templates.TemplateResponse("image.html", {"request": request, "image_url": image_url})