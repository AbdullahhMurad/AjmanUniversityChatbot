import fitz

def extract_blocks(pdf_path, page_num):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num)
    blocks = page.get_text("blocks")
    for i, block in enumerate(blocks):
        print(f"\n--- Block {i+1} ---\n{block[4]}")
    doc.close()

extract_blocks("C:/Users/kinga/Downloads/PymufTest/PDFs/NewStudentFAQs.pdf", page_num=1)
 

# import fitz  # PyMuPDF

# def extract_text_from_pdf(pdf_path):
#     doc = fitz.open(pdf_path)
#     all_text = ""
#     for page in doc:
#         text = page.get_text("text")  # "text" mode gets all text on the page
#         all_text += text + "\n"
#     doc.close()
#     return all_text

# print(extract_text_from_pdf("C:/Users/kinga/Downloads/PymufTest/PDFs/NewStudentFAQs.pdf"))




# import pdfplumber

# with pdfplumber.open("C:/Users/kinga/Downloads/PymufTest/PDFs/NewStudentFAQs.pdf") as pdf:
#     text = ""
#     for page in pdf.pages:
#         page_text = page.extract_text()
#         if page_text:
#             text += page_text + "\n"
# print(text)



# from pdf2image import convert_from_path
# import pytesseract

# pages = convert_from_path('C:/Users/kinga/Downloads/PymufTest/PDFs/NewStudentFAQs.pdf')
# all_text = ""
# for page in pages:
#     all_text += pytesseract.image_to_string(page)
# print(all_text)



# import pdfplumber

# with pdfplumber.open("") as pdf:
#     text = ""
#     for page in pdf.pages:
#         text += page.extract_text() + "\n"
# print(text)



# from langchain_huggingface import HuggingFaceEmbeddings

# embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# result = embedding.embed_query("This is a test.")
# print(result[:5])



# from langchain.docstore.document import Document
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS

# documents = [Document(page_content="Hello world"), Document(page_content="This is another doc")]
# embeddings = HuggingFaceEmbeddings(model_name="hkunlp/instructor-xl")
# store = FAISS.from_documents(documents, embedding=embeddings)
# print("✅ FAISS store created")





# FAILED

# from langchain_huggingface import HuggingFaceEmbeddings

# embedding = HuggingFaceEmbeddings(model_name="hkunlp/instructor-xl")
# result = embedding.embed_query("This is a test.")
# print(result[:5])

# from langchain_community.document_loaders import PyMuPDFLoader

# loader = PyMuPDFLoader("C:/Users/kinga/Downloads/PymufTest/PDFs/NewStudentFAQs.pdf")
# docs = loader.load()
# print(len(docs))