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
        "scopes": "filterRespo",
        "detail": "true",
        "join": "true",
        "paginate": 250
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
                f"Business Unit: {so.get('comp.name')}, "
                f"Sub Business Unit: {so.get('sub_comp.name')}, "
                f"Cabang: {so.get('branch.name')}, "
                f"No. TRX SO: {so.get('no')}, "
                f"SO Date: {so.get('date')}, "
                f"SO Type: {so.get('type')}, "
                f"Item Type: {so.get('item_type.value1')}, "
                f"Customer Type: {so.get('cust_type.value1')}, "
                f"Pemasaran: {so.get('pemasaran.value1')}, "
                f"Pembayaran: {so.get('pembayaran.value1')}, "
                f"Customer: {so.get('cust_name')}, "
                f"Alamat Customer: {so.get('cust_addr')}, "
                f"No. NPWP: {so.get('cust_npwp')}, "
                f"Nama NPWP: {so.get('cust_npwpname')}, "
                f"Contact Person: {so.get('cust_cp')}, "
                f"No. PO Customer: {so.get('cust_no_po')}, "
                f"Bill To: {so.get('ship.name')}, "
                f"Bill To Address: {so.get('ship.addr')}, "
                f"Order Type 1: {so.get('order_type1.value1')}, "
                f"Order Type 2: {so.get('order_type2.value1')}, "
                f"PPN Type: {so.get('ppn_type')}, "
                f"SO Prospek: {so.get('is_prospek')}, "
                f"Nama Penerima: {so.get('ship.name')}, "
                f"Alamat: {so.get('ship.addr')}, "
                f"Due Date: {so.get('ship_duedate')}, "
                f"Payment Term: {so.get('pay_term.value1')}, "
                f"Project: {so.get('project')}, "
                f"Down Payment Percentage: {so.get('dp_pct')}, "
                f"Down Payment Amount: {so.get('dp_amt')}, "
                f"Currency: {so.get('currency.name')}, "
                f"Exchange Rate: {so.get('currency_rate')}, "
                f"Catatan: {so.get('note')}, "
                f"Status: {so.get('status.value1')}, "
                f"Est. Ekspedisi Percentage: {so.get('exp_pct')}, "
                f"Est. Ekspedisi Amount: {so.get('exp_amt')}, "
                f"Est. Operasional Percentage: {so.get('ops_pct')}, "
                f"Est. Operasional Amount: {so.get('ops_amt')}, "
                f"Total Amount: {so.get('amt')}, "
                f"Total Discount Amount: {so.get('disc_amt')}, "
                f"DPP: {so.get('dpp')}, "
                f"PPN Percent: {so.get('ppn_pct')}, "
                f"PPN Amount: {so.get('ppn_amt')}, "
                f"Grand Total: {so.get('netto')}"
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