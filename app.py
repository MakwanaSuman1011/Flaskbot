from flask import Flask,request,render_template,jsonify
import json
import requests
import os
import re

app=Flask(__name__)

def normalize_text(text):
    return re.sub(r'[^\w\s]','', text).lower().strip()

def load_knowledge_base():
    if os.path.exists("knowledge_store.json"):
        with open("knowledge_store.json","r") as file:
            raw_kb=json.load(file)
            return{normalize_text(k):v for k,v in raw_kb.items()}
    return{}

knowledge_base=load_knowledge_base()

def search_duckduckgo(query):
    url="https://api.duckduckgo.com/"
    params={
        "q":query,
        "format":"json",
        "no_redirect":1,
        "no_html":1
    }

    try:
        response=requests.get(url,params=params)
        data=response.json()

        if data.get("Abstract"):
            return data["Abstract"]

        for topic in data.get("RelatedTopics",[]):
            if isinstance(topic,dict) and topic.get("Text"):
                return topic["Text"]

        return"I'm sorry, I couldn't find an answer online."

    except Exception:
        return"⚠️ An error occurred while searching online."

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/ask',methods=['POST'])
def ask():
    user_question=request.json.get("message","")
    normalized_question=normalize_text(user_question)

    answer=knowledge_base.get(normalized_question)

    if not answer:
        answer=search_duckduckgo(user_question)

    return jsonify({"reply":answer})

if __name__=="__main__":
    app.run(debug=True)




