from flask import Flask, request, render_template, jsonify
import requests
import os

app = Flask(__name__)

# Watsonx APIエンドポイントと認証情報
WATSONX_API_URL = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation"
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")   # ← プロジェクトIDを環境変数に追加
MODEL_ID = "ibm/granite-13b-chat-v2"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")

    headers = {
        "Authorization": f"Bearer {WATSONX_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model_id": MODEL_ID,
        "project_id": PROJECT_ID,  # ← プロジェクト連携ポイント
        "input": user_input,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7
        }
    }

    response = requests.post(WATSONX_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        output = data.get("results", [{}])[0].get("generated_text", "")
        return jsonify({"reply": output})
    else:
        return jsonify({"error": response.text}), response.status_code
