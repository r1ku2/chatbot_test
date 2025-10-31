from flask import Flask, request, render_template, jsonify
import requests
import os

app = Flask(__name__)

# Watsonx の API 情報
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
MODEL_ID = "ibm/granite-8b-japanese-v1"
GENERATION_URL = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"

def get_iam_token():
    """IBM Cloud IAM トークンを取得"""
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": WATSONX_API_KEY
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(IAM_TOKEN_URL, data=data, headers=headers)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"IAM token error: {response.text}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")

    # 認証トークン取得
    access_token = get_iam_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model_id": MODEL_ID,
        "project_id": PROJECT_ID,
        "input": user_input,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7
        }
    }

    response = requests.post(GENERATION_URL, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        output = data.get("results", [{}])[0].get("generated_text", "")
        return jsonify({"reply": output})
    else:
        return jsonify({"error": response.text}), response.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
