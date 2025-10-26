from langchain_community.document_loaders import PyPDFLoader
import langchain
from typing import List
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
load_dotenv()
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_pdf(file_path):
    """
    Load a single PDF and return a list of LangChain Document objects (one per page by default).
    """
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    # docs are LangChain Document objects with page_content and metadata
    return docs

def chunk_documents(documents, chunk_size=400, chunk_overlap=80):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)

def create_vector_store(chunks, index_path="/home/kartikey_singh/Desktop/UL/selenium/insurance_policy_chatbot/vector_store/faiss_index"):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001",api_key=os.getenv("GOOGLE_API_KEY"))
    # embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(index_path)
    print(vectorstore)
    return vectorstore


def get_relevant_chunks(query, index_path="/home/kartikey_singh/Desktop/UL/selenium/insurance_policy_chatbot/vector_store/faiss_index"):
    # embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001",api_key=os.getenv("GOOGLE_API_KEY"))
    vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    docs = vectorstore.similarity_search(query, k=4)
    return docs

def get_result_from_llm(final_prompt):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    response = llm.invoke(final_prompt)
    return response

def main():
    pdf = load_pdf("/home/kartikey_singh/Desktop/UL/selenium/insurance_policy_chatbot/uploaded_pdfs/Kartikey Singh - Python Developer.pdf")
    chunks = chunk_documents(pdf)
    create_vector_store(chunks)
    question = "what technologies are known by kartikey singh?"
    res = get_relevant_chunks(question)
    
    prompt = PromptTemplate(
        template='Answer the question based only on this context:\n{context}\n\nQuestion: {question}',
        input_variables=['question','context']
    )
    content_text = " ".join(doc.page_content for doc in res)
    import pdb; pdb.set_trace()
    final_prompt = prompt.invoke({'context':content_text,'\n\nquestion':question})
    answer = get_result_from_llm(final_prompt)
    # llm.invoke(final_prompt)
    


    print(answer.content)

main()