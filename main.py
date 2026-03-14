import os
import requests
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel
from fastapi import FastAPI, Header, HTTPException

load_dotenv(override=True)

class UserRequest(BaseModel):
    message: str

def req_so_data_as_a_list_document() -> list[Document]:
    params = {
        "simplest": "true",
        "searchfield": "this.no,comp.name,sub_comp.name,branch.name,this.date,this.ref_type,cust.name,ship_name,this.amt,status.value1",
        "scopes": "filterRespo",
        "natural": "true",
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('T_SO_BEARER_TOKEN')}",
        "Accept": "application/json",
    }
    response = requests.get(
        os.getenv("T_SO_ENDPOINT"),
        headers=headers,
        params=params,
        timeout=30
    )
    response.raise_for_status()
    data = response.json().get("data", [])
    return [
        Document(
            page_content=(
                f"Nomor Transaksi: {so.get('no')}, "
                f"Business Unit: {so.get('comp.name')}, "
                f"Sub Business Unit: {so.get('sub_comp.name')}, "
                f"Cabang: {so.get('branch.name')}, "
                f"Tanggal: {so.get('date')}, "
                f"Ref Type: {so.get('ref_type')}, "
                f"Customer: {so.get('cust.name')}, "
                f"Shipping To: {so.get('ship_name')}, "
                f"Amount: {so.get('amt')}, "
                f"Status: {so.get('status.value1')}"
            )
        )
        for so in data
    ]

def rag_chain(documents):
    # memilih model embedding
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # tahap embedding data perusahaan, dan penyimpanan ke vectorstore
    vectorstore = FAISS.from_documents(documents, embeddings)

    # mengatur bahwa nanti sistem akan mengambil K data yang paling cocok saat ada pertanyaan
    retriever = vectorstore.as_retriever(search_kwargs={"k": len(documents)})

    # membuat format perintah agar AI hanya menjawab berdasarkan data yang diberikan
    rag_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
            Gunakan data berikut untuk menjawab pertanyaan.
            Jika jawabannya tidak ada di data, jawab: "data tidak ditemukan" atau jawaban serupa tapi menyesuaikan

            Data:
            {context}

            Pertanyaan:
            {question}

            Jawaban:
        """
    )

    # memilih model LLM untuk menjawab pertanyaan
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0
    )

    # menggabungkan proses pencarian data dan pembuatan jawaban menjadi satu alur
    rag_chain = (
        {
            "context": retriever,          # mengambil data yang sesuai
            "question": RunnablePassthrough()  # meneruskan pertanyaan pengguna
        }
        | rag_prompt                       # memasukkan data dan pertanyaan ke format perintah
        | llm                              # AI membuat jawaban
        | StrOutputParser()                # mengubah hasil jawaban menjadi teks biasa
    )

    return rag_chain

app = FastAPI()
chatbot_buffer = rag_chain(req_so_data_as_a_list_document())

@app.post("/chatbot")
async def chatbot(data: UserRequest, authorization: str = Header(None)):
    global chatbot_buffer

    if authorization != f"Bearer {os.getenv('CHABOT_BEARER_TOKEN')}":
        raise HTTPException(status_code=401, detail="unauthorized")


    if chatbot_buffer is None:
        return { 
            "user_message": data.message,
            "chatbot_response": "chatbot masih loading data" 
        }

    if data.message is None or data.message.strip() == "":
        return { 
            "user_message": data.message,
            "chatbot_response": "pesan yang dikirim tidak valid" 
        }
    
    if data.message =="load_new_data":
        chatbot_buffer = rag_chain(req_so_data_as_a_list_document())
        return {
            "user_message": data.message,
            "chatbot_response": "data baru telah dimuat, sekarang anda bisa menanyakan pertanyaan berdasarkan data baru"
        }

    return {
        "user_message": data.message,
        "chatbot_response": chatbot_buffer.invoke(data.message)
    }