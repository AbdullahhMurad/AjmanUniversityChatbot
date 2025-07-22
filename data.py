from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

PDF_FILES = [
    "C:/Users/kinga/Downloads/PymufTest/PDFs/NewStudentFAQs.pdf",
    "C:/Users/kinga/Downloads/PymufTest/PDFs/User Guide - Faculty Members and Staff.pdf"
]

def load_pdfs(pdf_files):
    """Load text content from PDF files"""
    documents = []
    for pdf_file in pdf_files:
        loader = PyMuPDFLoader(pdf_file)
        documents.extend(loader.load())
    return documents

def get_text_chunks(documents):
    """Split documents into chunks"""
    text_splitter = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separator="\n",
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Total chunks created: {len(chunks)}")
    return chunks

def get_vectorstore(text_chunks):
    """Create vector store from text chunks"""
    embeddings = HuggingFaceEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore = FAISS.from_documents(documents=text_chunks, embedding=embeddings)
    print(f"Vector store created with {len(text_chunks)} chunks.")
    return vectorstore

def main():
    # Load PDFs
    print("Loading PDF files...")
    documents = load_pdfs(PDF_FILES)
    print(f"Loaded {len(documents)} documents")
    
    # Split into chunks
    chunks = get_text_chunks(documents)
    
    # Create vector store
    vectorstore = get_vectorstore(chunks)
    print("Vector store created successfully!")
    
    # You can now use vectorstore for similarity searches
    # Example:
    # query = "What are the FAQs for new students?"
    # docs = vectorstore.similarity_search(query)
    # print(docs[0].page_content)

if __name__ == "__main__":
    main()

# # pdf_context_manager.py

# from langchain_community.document_loaders import PyMuPDFLoader
# from langchain.text_splitter import CharacterTextSplitter
# from langchain_community.embeddings import HuggingFaceEmbeddings
# # from langchain.embeddings import HuggingFaceInstructEmbeddings

# from langchain_community.vectorstores import FAISS
# import os

# from langchain_text_splitters import CharacterTextSplitter

# # Change this to your actual PDF files
# PDF_FILES = [
#     "C:/Users/kinga/Downloads/PymufTest/PDFs/NewStudentFAQs.pdf",
#     "C:/Users/kinga/Downloads/PymufTest/PDFs/User Guide - Faculty Members and Staff.pdf"
# ]

# ###

# # Get the text from the PDF files as arguments
# # Split the text into chunks 
# def get_text_chunks(pdf_files=PDF_FILES):
#     text_splitter = CharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200,
#         separators="\n",
#         length_function = len
#     )
#     chunks = text_splitter.split_texts(pdf_files)
#     print(f"Total chunks created: {len(chunks)}")  # For debugging
#     return chunks


# # Store the text chunks in a vector store
# # Using HuggingFaceEmbeddings for embedding the text chunks
# # And FAISS for the vector store
# # And return the vector store
# def get_vectorstore(text_chunks):
#     embeddings = HuggingFaceEmbeddings(model_name="hkunlp/instructor-xl")
#     vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
#     print(f"Vector store created with {len(text_chunks)} chunks.") # For debugging
#     return vectorstore


# if __name__ == "__main__":
#     build_faiss_index()


###

# INDEX_DIR = "student_faiss_index"
# EMBEDDING_MODEL = "BAAI/bge-small-en"

# def build_faiss_index(pdf_files=PDF_FILES, index_dir=INDEX_DIR):
#     """Build and save FAISS index from PDF files"""
#     all_docs = []
#     for path in pdf_files:
#         loader = PyMuPDFLoader(path)
#         docs = loader.load()
#         all_docs.extend(docs)

#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200,
#         separators=["\n\n", "\n", " ", ""]
#     )
#     chunks = splitter.split_documents(all_docs)

#     embeddings = HuggingFaceEmbeddings(
#         model_name=EMBEDDING_MODEL,
#         model_kwargs={"device": "cpu"}
#     )

#     vector_store = FAISS.from_documents(chunks, embeddings)
#     vector_store.save_local(index_dir)
#     print(f"✅ FAISS index stored at '{index_dir}' with {len(chunks)} chunks.")

# def load_faiss_index(index_dir=INDEX_DIR):
#     """Load FAISS index"""
#     embeddings = HuggingFaceEmbeddings(
#         model_name=EMBEDDING_MODEL,
#         model_kwargs={"device": "cpu"}
#     )
#     return FAISS.load_local(index_dir, embeddings)

# def get_context_for_query(query, k=3):
#     """Search FAISS and return top-k chunks as context string"""
#     vector_store = load_faiss_index()
#     results = vector_store.similarity_search(query, k=k)
#     return "\n\n".join([doc.page_content for doc in results])

# # Run this once to build the index
# if __name__ == "__main__":
#     build_faiss_index()



# from langchain_community.document_loaders import PyMuPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.embeddings import HuggingFaceInstructEmbeddings
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS
# import os

# pdf_files = [
#     "C:/Users/kinga/Downloads/PymufTest/PDFs/NewStudentFAQs.pdf",
#     "C:/Users/kinga/Downloads/PymufTest/PDFs/User Guide - Faculty Members and Staff.pdf"
# ]

# def load_documents(file_paths):
#     all_docs = []
#     for path in file_paths:
#         print(f"\n📄 Loading: {os.path.basename(path)}\n" + "-"*50)
#         loader = PyMuPDFLoader(path)
#         docs = loader.load()
#         for i, doc in enumerate(docs):
#             print(f"\n--- Page {i + 1} ---")
#             print(doc.page_content[:1000])  # Print first 1000 characters per page (adjust as needed)
#         all_docs.extend(docs)
#     return all_docs

# def process_pdfs_to_faiss(pdf_paths, index_dir="faiss_index", model_name="BAAI/bge-small-en"):
#     documents = load_documents(pdf_paths)
    
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200,
#         separators=["\n\n", "\n", " ", ""]
#     )
#     chunks = text_splitter.split_documents(documents)

#     embeddings = HuggingFaceEmbeddings(
#         model_name=model_name,
#         model_kwargs={"device": "cpu"}
#     )

#     vector_store = FAISS.from_documents(chunks, embeddings)
#     vector_store.save_local(index_dir)
#     print(f"Stored {len(chunks)} chunks in '{index_dir}'")

# process_pdfs_to_faiss(pdf_files, index_dir="student_faiss_index")

