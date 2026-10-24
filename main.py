import rag
import sales_order
import os
import mysql.connector
import bcrypt
from typing import Any
from models import MessageRequest
from models import LoginRequest
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from huggingface_hub import login as loginHF
from utils import get_list_no_trx_so_from_query

load_dotenv(override=True)
loginHF(token=os.getenv("HF_TOKEN"))

llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash~",
    temperature=0
)

app = FastAPI()

app.state.so_as_a_list_document = sales_order.get_as_a_list_document()
app.state.vectorstore = rag.vectorstrore_FAISS(
    app.state.so_as_a_list_document
)
app.state.length_of_data_sales_order_berformat_document = len(
    app.state.so_as_a_list_document
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login")
def login(data: LoginRequest, authorization: str = Header(None)):
    if authorization != f"Bearer {os.getenv('LOGIN_BEABER_TOKEN')}":
        raise HTTPException(status_code=401, detail="unauthorized")

    db = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE name = %s
        """,
        (data.username,)
    )

    user: dict[str, Any] | None = cursor.fetchone()
    cursor.close()
    db.close()

    if not user:
        return {
            "success": False,
            "message": "User tidak ditemukan"
        }

    if not bcrypt.checkpw(
        data.password.encode(),
        user["password"].encode()
    ):
        return {
            "success": False,
            "message": "Password salah"
        }

    return {
        "success": True,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "email_verified_at": user["email_verified_at"],
            "remember_token": user["remember_token"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"]
        }
    }

@app.get("/sales-order")
async def get_sales_order_data(authorization: str = Header(None)):
    if authorization != f"Bearer {os.getenv('SALES_ORDER_BEARER_TOKEN')}":
        raise HTTPException(status_code=401, detail="unauthorized")
    return sales_order.get_as_a_json()

@app.post("/chatbot")
async def chatbot(data: MessageRequest, authorization: str = Header(None)):

    if authorization != f"Bearer {os.getenv('CHATBOT_BEARER_TOKEN')}":
        raise HTTPException(status_code=401, detail="unauthorized")

    query = data.message

    if query is None or query.strip() == "":
        return { 
            "user_message": query,
            "chatbot_response": "pesan yang dikirim tidak valid" 
        }

    if query == "load_new_data":
        app.state.so_as_a_list_document = sales_order.get_as_a_list_document()
        app.state.vectorstore = rag.vectorstrore_FAISS(
            app.state.so_as_a_list_document
        )
        app.state.length_of_data_sales_order_berformat_document = len(
            app.state.so_as_a_list_document
        )
        return {
            "user_message": query,
            "chatbot_response": "data baru telah dimuat, sekarang anda bisa menanyakan pertanyaan berdasarkan data baru"
        }
    
    list_no_trx_so = get_list_no_trx_so_from_query(query)
    retrival_result = rag.retrival(
        query,
        app.state.vectorstore,
        app.state.length_of_data_sales_order_berformat_document
    )
    if list_no_trx_so == []:
        llm_respond = llm.invoke(
            f"""
                Gunakan data berikut untuk menjawab pertanyaan.
                Jika jawabannya tidak ada di data, jawab: "data tidak ditemukan" atau jawaban serupa tapi menyesuaikan

                Data:
                {retrival_result}

                Pertanyaan:
                {query}

                Jawaban:
            """
        ).text
        return {
            "user_message": query,
            "chatbot_response": llm_respond
        }
    else:
        founded_data = []

        for rr in retrival_result:
            for nts in list_no_trx_so:
                if nts in rr.page_content:
                    founded_data.append(rr.page_content)

        if  len(founded_data) == len(list_no_trx_so):
            llm_respond = llm.invoke(
                f"""
                    Gunakan data berikut untuk menjawab pertanyaan.
                    Jika jawabannya tidak ada di data, jawab: "data tidak ditemukan" atau jawaban serupa tapi menyesuaikan

                    Data:
                    {founded_data}

                    Pertanyaan:
                    {query}

                    Jawaban:
                """
            ).text
            return {
                "user_message": query,
                "chatbot_response": llm_respond
            }
        else:
            not_founded_data = []

            for trx in list_no_trx_so:
                found = False

                for doc in founded_data:
                    if trx in doc:
                        found = True
                        break

                if not found:
                    not_founded_data.append(trx)
            return {
                "user_message": query,
                "chatbot_response": f"data dengan No. TRX SO {', '.join(not_founded_data)} tidak ditemukan"
            }