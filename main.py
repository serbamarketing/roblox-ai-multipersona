import os
import google.generativeai as genai

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

chat_memory = {}

PERSONAS = {
    "guard": {
        "name":"Penjaga Kota",
        "personality":"Tegas, suka menjaga keamanan kota, jawab singkat."
    },
    "merchant": {
        "name":"Pedagang",
        "personality":"Ramah, suka menawarkan barang."
    },
    "wizard": {
        "name":"Penyihir",
        "personality":"Bijak, misterius, suka bicara sihir."
    },
    "robot": {
        "name":"Robot AI",
        "personality":"Logis, futuristik, sedikit kaku."
    }
}

class RobloxMessage(BaseModel):
    user:str
    message:str
    persona:str="guard"

@app.get("/")
async def home():
    return {"status":"online","personas":list(PERSONAS.keys())}

@app.post("/webhook/roblox-ai")
async def webhook(data:RobloxMessage):

    persona = PERSONAS.get(data.persona.lower(), PERSONAS["guard"])

    memory_key = f"{data.user}_{data.persona}"

    if memory_key not in chat_memory:
        chat_memory[memory_key] = []

    history = chat_memory[memory_key]

    prompt = f"""
Kamu NPC Roblox.

Nama NPC:
{persona["name"]}

Kepribadian:
{persona["personality"]}

Player:
{data.user}

Riwayat:
{history}

Pesan:
{data.message}

Aturan:
- Maksimal 2 kalimat
- Jangan terlalu panjang
- Tetap sesuai karakter
"""

    try:
        response = model.generate_content(prompt)
        reply = response.text.strip()

    except Exception as e:
        print(e)
        reply = "Server AI sedang sibuk."

    history.append({
        "player":data.message,
        "npc":reply
    })

    chat_memory[memory_key] = history[-10:]

    return {
        "reply":reply,
        "persona":persona["name"]
    }
