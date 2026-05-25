import os
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(override=True)

class UserRequest(BaseModel):
    message: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chatbot")
async def chatbot(data: UserRequest, authorization: str = Header(None)):

    if authorization != f"Bearer {os.getenv('CHATBOT_BEARER_TOKEN')}":
        raise HTTPException(status_code=401, detail="unauthorized")

    if data.message is None or data.message.strip() == "":
        return {
            "user_message": data.message,
            "chatbot_response": "pesan yang dikirim tidak valid"
        }

    if data.message == "load_new_data":
        return {
            "user_message": data.message,
            "chatbot_response": "data baru telah dimuat, sekarang anda bisa menanyakan pertanyaan berdasarkan data baru"
        }

    return {
        "user_message": data.message,
        "chatbot_response": "chatbot ngesespon"
    }