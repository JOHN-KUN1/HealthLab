from flask import Flask, render_template, request, jsonify
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
from dotenv import load_dotenv
import openai

app = Flask(__name__)
load_dotenv()
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
# model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

# app = Flask(__name__)


@app.route("/", methods = ["GET", "POST"])
def get_Chat_response():
    if request.method == "POST":
        user_input = request.form["user_input"]
        openai.api_key = os.getenv("API_TOKEN")
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=user_input,
            max_tokens=2040,
            temperature=0
        )
        result = response["choices"][0]["text"]
        return (result)
    return render_template('chat.html')

if __name__== '__main__':
    app.run(debug=True)

    # # Let's chat for 5 lines
    # for step in range(5):
    #     # encode the new user input, add the eos_token and return a tensor in Pytorch
    #     new_user_input_ids = tokenizer.encode(
    #         str(text) + tokenizer.eos_token, return_tensors='pt')

    #     # append the new user input tokens to the chat history
    #     bot_input_ids = torch.cat(
    #         [chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

    #     # generated a response while limiting the total chat history to 1000 tokens,
    #     chat_history_ids = model.generate(
    #         bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

    #     # pretty print last ouput tokens from bot
    #     return tokenizer.decode(
    #         chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
