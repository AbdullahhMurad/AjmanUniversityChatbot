import os
import fitz  # PyMuPDF
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

PDF_FILES = [
    "C:/Users/kinga/Downloads/PymufTest/PDFs/NewStudentFAQs.pdf",
    "C:/Users/kinga/Downloads/PymufTest/PDFs/User Guide - Faculty Members and Staff.pdf"
]
VECTOR_STORE_PATH = "vectorstore"
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

def custom_loader_concat_blocks_and_text(pdf_path):
    """
    Extracts all text from each page using both 'blocks' and 'text' to maximize content coverage.
    Removes duplicate paragraphs.
    """
    doc = fitz.open(pdf_path)
    docs = []
    for page_num, page in enumerate(doc):
        # Get block text
        block_text = "\n".join(
            block[4].strip()
            for block in sorted(page.get_text("blocks"), key=lambda b: (b[1], b[0]))
            if block[4].strip()
        )
        # Get 'text' text
        text_text = page.get_text("text").strip()
        # Merge, deduplicate
        all_paras = set(block_text.splitlines()) | set(text_text.splitlines())
        combined_text = "\n".join([para for para in all_paras if para.strip()])
        if combined_text.strip():
            docs.append(Document(
                page_content=combined_text.strip(),
                metadata={"source": pdf_path, "page": page_num+1}
            ))
    doc.close()
    return docs

def load_pdfs(pdf_files):
    documents = []
    for pdf_file in pdf_files:
        try:
            print(f"🔍 Loading: {pdf_file}")
            docs = custom_loader_concat_blocks_and_text(pdf_file)
            documents.extend(docs)
        except Exception as e:
            print(f"⚠️ Failed to load '{pdf_file}': {e}")
    print(f"✅ Loaded {len(documents)} total documents.")
    # Print each page's extracted text for verification (first 1000 chars)
    for i, doc in enumerate(documents):
        print(f"\n--- PAGE {i+1} ---\n{doc.page_content[:1000]}...\n")
    return documents

def split_text_chunks(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=400,
        separators=["\n\n", "\n", ".", "!", "?", " "]
    )
    chunks = splitter.split_documents(documents)
    for idx, chunk in enumerate(chunks[:5]):
        print(f"\n--- Chunk {idx+1} ---\n{chunk.page_content[:500]}...\n", "Chunk preview for verification")
    print(f"🧩 Created {len(chunks)} text chunks.")
    # Diagnostic: search for frequently-missed keywords
    keywords = ["code of conduct", "tuition", "fees", "scholarship"]
    for keyword in keywords:
        for idx, chunk in enumerate(chunks):
            if keyword in chunk.page_content.lower():
                print(f"\n>>> DIAGNOSTIC: Found '{keyword}' in chunk {idx+1}\n{chunk.page_content}\n")
    return chunks

def create_vectorstore_from_chunks(chunks):
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    store = FAISS.from_documents(chunks, embedding=embeddings)
    print("✅ Vector store created successfully.")
    return store

def save_vectorstore(store, path=VECTOR_STORE_PATH):
    store.save_local(path)
    print(f"💾 Vector store saved to '{path}'")

def load_vectorstore(path=VECTOR_STORE_PATH):
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    store = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
    print(f"📦 Vector store loaded from '{path}'")
    return store

def get_relevant_context(user_input, vectorstore, k=10):
    results = vectorstore.similarity_search(user_input, k=k)
    if not results:
        print("⚠️ No relevant context found.")
        return ""
    print(f"🔎 Retrieved {len(results)} relevant context chunks for: '{user_input}'")
    for i, doc in enumerate(results):
        print(f"\n--- Chunk {i+1} ---\n{doc.page_content[:300]}...\n")
    return "\n".join(doc.page_content for doc in results)

def create_and_save_vectorstore():
    print("📄 Starting vector store creation...")
    documents = load_pdfs(PDF_FILES)
    if not documents:
        print("⚠️ No valid documents were loaded.")
        return None
    for i, doc in enumerate(documents[:3]):
        content = doc.page_content.strip()
        if not content:
            print(f"⚠️ Document {i+1} is empty.")
        else:
            print(f"\n--- Preview of Document {i+1} ---\n{content[:500]}...\n")
    chunks = split_text_chunks(documents)
    store = create_vectorstore_from_chunks(chunks)
    save_vectorstore(store)
    return store

if __name__ == "__main__":
    create_and_save_vectorstore()

# import os
# import fitz  # PyMuPDF
# from langchain.docstore.document import Document
# from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain.text_splitter import CharacterTextSplitter

# # === Configuration ===
# PDF_FILES = [
#     "C:/Users/kinga/Downloads/PymufTest/PDFs/NewStudentFAQs.pdf",
#     "C:/Users/kinga/Downloads/PymufTest/PDFs/User Guide - Faculty Members and Staff.pdf"
# ]
# VECTOR_STORE_PATH = "vectorstore"
# EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# def custom_loader_concat_blocks(pdf_path):
#     """
#     Load PDF and concatenate all text blocks per page in top-to-bottom, left-to-right order.
#     This reduces missing/skipped text due to PDF's internal block ordering.
#     """
#     doc = fitz.open(pdf_path)
#     docs = []
#     for page_num, page in enumerate(doc):
#         blocks = page.get_text("blocks")
#         # Sort blocks top-to-bottom, then left-to-right
#         blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
#         text = "\n".join(block[4].strip() for block in blocks if block[4].strip())
#         if text:
#             docs.append(Document(
#                 page_content=text,
#                 metadata={"source": pdf_path, "page": page_num+1}
#             ))
#     doc.close()
#     return docs

# def load_pdfs(pdf_files):
#     """Load text content from a list of PDF files using custom block concatenation."""
#     documents = []
#     for pdf_file in pdf_files:
#         try:
#             print(f"🔍 Loading: {pdf_file}")
#             docs = custom_loader_concat_blocks(pdf_file)
#             documents.extend(docs)
#         except Exception as e:
#             print(f"⚠️ Failed to load '{pdf_file}': {e}")
#     print(f"✅ Loaded {len(documents)} total documents.")
#     return documents

# def split_text_chunks(documents):
#     """Split documents into overlapping text chunks."""
#     splitter = CharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=300,
#         separator="\n",
#         length_function=len
#     )
#     chunks = splitter.split_documents(documents)
#     for idx, chunk in enumerate(chunks[:10]):  # Adjust [:10] to see more
#          print(f"\n--- Chunk {idx+1} ---\n{chunk.page_content[:300]}...\n", "Chunk preview for verification")
#     print(f"🧩 Created {len(chunks)} text chunks.")
#     return chunks

# def create_vectorstore_from_chunks(chunks):
#     """Create a FAISS vector store from text chunks."""
#     embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
#     store = FAISS.from_documents(chunks, embedding=embeddings)
#     print("✅ Vector store created successfully.")
#     return store

# def save_vectorstore(store, path=VECTOR_STORE_PATH):
#     """Save a FAISS vector store to disk."""
#     store.save_local(path)
#     print(f"💾 Vector store saved to '{path}'")

# def load_vectorstore(path=VECTOR_STORE_PATH):
#     """Load an existing vector store from disk."""
#     embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
#     store = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
#     print(f"📦 Vector store loaded from '{path}'")
#     return store

# def get_relevant_context(user_input, vectorstore, k=10):
#     """Retrieve top-k most relevant chunks for the user's query."""
#     results = vectorstore.similarity_search(user_input, k=k)

#     if not results:
#         print("⚠️ No relevant context found.")
#         return ""

#     print(f"🔎 Retrieved {len(results)} relevant context chunks for: '{user_input}'")
#     for i, doc in enumerate(results):
#         print(f"\n--- Chunk {i+1} ---\n{doc.page_content[:300]}...\n")

#     return "\n".join(doc.page_content for doc in results)

# def create_and_save_vectorstore():
#     """Load, process, embed documents and save FAISS index to disk."""
#     print("📄 Starting vector store creation...")

#     documents = load_pdfs(PDF_FILES)
#     if not documents:
#         print("⚠️ No valid documents were loaded.")
#         return None

#     for i, doc in enumerate(documents[:3]):
#         content = doc.page_content.strip()
#         if not content:
#             print(f"⚠️ Document {i+1} is empty.")
#         else:
#             print(f"\n--- Preview of Document {i+1} ---\n{content[:500]}...\n")

#     chunks = split_text_chunks(documents)
#     store = create_vectorstore_from_chunks(chunks)
#     save_vectorstore(store)
#     return store

# if __name__ == "__main__":
#     create_and_save_vectorstore()
