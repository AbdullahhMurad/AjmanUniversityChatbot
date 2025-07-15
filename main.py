from openai import OpenAI
from fastapi import FastAPI, Form, Request, WebSocket
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv

load_dotenv()

openai = OpenAI (
    api_key = os.getenv("OPENAI_API_SECRET_KEY") 
)


app = FastAPI()
templates = Jinja2Templates(directory="templates")

chat_responses = []



chat_log = [{'role': 'system', 'content': 'You are a virtual assistant of Ajman University, dedicated to help prospective and enrolled students. You will answer student inquiries about admision fees, tuition fees, application procedures, scholarships, and related information. You may only answer academia related questions, specifically questions related to Ajman University.       Any question that is not related to Ajman University is considered out of your scope, and you may not answer.'}]





@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})


@app.websocket("/ws")
async def chat(websocket: WebSocket):

    await websocket.accept()  
    while True:   
        user_input = await websocket.receive_text()
        chat_log.append({'role': 'user', 'content': user_input})
        chat_responses.append(user_input)

        try:
            response = openai.chat.completions.create(
                 model = 'gpt-3.5-turbo',
                 messages = chat_log, 
                 temperature=0.6,
                 stream = True
            )

            ai_response =''

            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    ai_response += chunk.choices[0].delta.content
                    await websocket.send_text(chunk.choices[0].delta.content)
            chat_responses.append(ai_response)
                
        except Exception as e:
            await websocket.send_text(f'Error: {str (e)}')
            break



@app.post("/", response_class=HTMLResponse)
async def chat(request: Request, user_input: Annotated[str, Form()]):    
    
    chat_log.append({'role': 'user', 'content': user_input})
    chat_responses.append(user_input)

    response = openai.chat.completions.create(
        model = 'gpt-3.5-turbo',
        messages=chat_log, # Changed from hard coded / static to dynamic
        temperature=0.6
    )
    bot_response = response.choices[0].message.content
    chat_log.append({'role':'assistant', 'content': bot_response})
    chat_responses.append(bot_response)
    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})


@app.get("/image", response_class=HTMLResponse)
async def image_page(request: Request):
    return templates.TemplateResponse("image.html", {"request": request})


@app.post("/image", response_class=HTMLResponse)
async def create_image(request: Request, user_input: Annotated[str, Form()]):
    
    response = openai.images.generate(
        prompt = user_input,
        n = 1,
        size = "512x512"
    )
    image_url = response.data[0].url
    return templates.TemplateResponse("image.html", {'request': request, "image_url": image_url})