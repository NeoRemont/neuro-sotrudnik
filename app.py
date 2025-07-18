from flask import Flask, request, jsonify
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Настройки
openai.api_key = os.getenv("OPENAI_API_KEY")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# Авторизация в Google Sheets
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("/etc/secrets/credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
    return sheet

@app.route("/ask", methods=["POST"])
def ask():
    prompt = request.json.get("prompt")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    sheet = get_sheet()
    data = sheet.get_all_records()

    # GPT-ответ
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты помощник по таблице выплат."},
            {"role": "user", "content": f"Вот данные: {data}. Вопрос: {prompt}"}
        ]
    )

    answer = completion["choices"][0]["message"]["content"]
    return jsonify({"answer": answer})

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
