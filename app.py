from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

token = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

app = Flask(__name__)
CORS(app)  

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["POST"])
def chat():
    try:
        data = request.json
        msg = data.get("msg")
        
        if not msg:
            return jsonify({"error": "No message provided"}), 400
        
        response = get_Chat_response(msg)
        return jsonify({"response": response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_Chat_response(text):
    # Encode input and prepare chat history (empty for the first time)
    new_user_input_ids = token.encode(str(text) + token.eos_token, return_tensors='pt')
    chat_history_ids = model.generate(new_user_input_ids, max_length=1000, pad_token_id=token.eos_token_id)
    
    # Decode the generated response
    text = token.decode(chat_history_ids[:, new_user_input_ids.shape[-1]:][0], skip_special_tokens=True)
    
    return text

if __name__ == '__main__':
    app.run()
