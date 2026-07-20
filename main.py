import rag
import sales_order
import os
import mysql.connector
import bcrypt
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from huggingface_hub import login

load_dotenv(override=True)
login(token=os.getenv("HF_TOKEN"))

class MessageRequest(BaseModel):
    message: str

class LoginRequest(BaseModel):
    username: str
    password: str

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password= os.getenv("DB_PASS"),
    database="website_dashboard_sales_order_pt_temprina"
)

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
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
def login(data: LoginRequest):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASS"),
        database="website_dashboard_sales_order_pt_temprina"
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

    user = cursor.fetchone()

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

    data = sales_order.req_data()

    return {
        "data": [
            {
                "business_unit": so.get("comp.name"),
                "sub_business_unit": so.get("sub_comp.name"),
                "cabang": so.get("branch.name"),
                "trx_so": so.get("no"),
                "so_date": so.get("date"),
                "so_type": so.get("type"),
                "item_type": so.get("item_type.value1"),
                "customer_type": so.get("cust_type.value1"),
                "pemasaran": so.get("pemasaran.value1"),
                "pembayaran": so.get("pembayaran.value1"),
                "customer": so.get("cust_name"),
                "alamat_customer": so.get("cust_addr"),
                "npwp": so.get("cust_npwp"),
                "nama_npwp": so.get("cust_npwpname"),
                "contact_person": so.get("cust_cp"),
                "customer_po": so.get("cust_no_po"),
                "bill_to": so.get("ship.name"),
                "bill_to_address": so.get("ship.addr"),
                "order_type_1": so.get("order_type1.value1"),
                "order_type_2": so.get("order_type2.value1"),
                "ppn_type": so.get("ppn_type"),
                "so_prospek": so.get("is_prospek"),
                "nama_penerima": so.get("ship.name"),
                "alamat": so.get("ship.addr"),
                "due_date": so.get("ship_duedate"),
                "payment_term": so.get("pay_term.value1"),
                "project": so.get("project"),
                "down_payment_percentage": so.get("dp_pct"),
                "down_payment_amount": so.get("dp_amt"),
                "currency": so.get("currency.name"),
                "exchange_rate": so.get("currency_rate"),
                "catatan": so.get("note"),
                "status": so.get("status.value1"),
                "est_ekspedisi_percentage": so.get("exp_pct"),
                "est_ekspedisi_amount": so.get("exp_amt"),
                "est_operasional_percentage": so.get("ops_pct"),
                "est_operasional_amount": so.get("ops_amt"),
                "total_amount": so.get("amt"),
                "total_discount_amount": so.get("disc_amt"),
                "dpp": so.get("dpp"),
                "ppn_percent": so.get("ppn_pct"),
                "ppn_amount": so.get("ppn_amt"),
                "grand_total": so.get("netto")
            }
            for so in data
        ]
    }

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
    
    list_no_trx_so = sales_order.get_list_no_trx_so_from_query(query)
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