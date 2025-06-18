import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

from clean_dataset import eval_data, summarize_data

from flask import send_from_directory
import os


#get api key for openai
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
# CORS(
#     app,
#     resources={r"/ask": {"origins": "http://localhost:3000"}},
#     supports_credentials=True,
#     methods=["GET", "POST", "OPTIONS"],
# )
CORS(app, supports_credentials=True)



#cleaning/evaluating data
summarize_data()
eval_data()
# get data
df = pd.read_csv("trade_profits_summary.csv")
summary = pd.read_csv("trade_summary.csv")

def create_prompt(question: str) -> str:
    sample_data = df.to_csv(index=False)
    summarycsv = summary.to_csv(index=False)
    prompt = f"""
            You are a helpful trading assistant AI. Here is a sample of trading data:

            {sample_data}
            
            and some precalculated analysis : {summarycsv}

            Using the dataset summary AND analysis (check if the answer is in either file), answer this question clearly but dont provide excess work, just the final answer:

            Question: {question}
            
            Make sure that you use the monetary amounts when asked about net values, percentages etc. and that you dont include the deposit rows when calculating anything related to profit. Then give a suggestion for another question user can ask based on what is available in the dataset summary and analysis in a conversational tone.
            
            If they ask about general trading advice like minimizing risk, maximizing profits, use knowledge about the market.

            Answer:
            """
    return prompt
#debugging stuff
@app.before_request
def log_method():
    print(f"Received {request.method} request at {request.path}")

@app.route('/ask', methods=['OPTIONS'])
def ask_options():
    return '', 200

#route to open ai 
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")
    is_first = data.get("is_first", False)

    # If it's the first message, greet user and suggest questions
    if is_first:
        welcome_prompt = """You are a friendly AI assistant for analyzing their specific trading data. Start by asking the user how you can assist. Greet the user and encourage them to ask questions."""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": welcome_prompt}],
                temperature=0.6,
                max_tokens=100,
            )
            answer = response.choices[0].message.content.strip()
            print("Welcome message:", answer)
            return jsonify({"answer": answer})
        
        except Exception as e:
            print("Error from OpenAI during greeting:", e)
            return jsonify({"error": str(e)}), 500

    # in case input is empty
    if not question:
        print("No question provided")
        return jsonify({"error": "No question provided"}), 400

    # regular question/answer
    prompt = create_prompt(question)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600,
        )
        answer = response.choices[0].message.content.strip()
        return jsonify({"answer": answer})
    except Exception as e:
        print("Error from OpenAI:", e)
        return jsonify({"error": str(e)}), 500

#added for deployment  
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# tells where static build files are
app.static_folder = 'build'

if __name__ == "__main__":
    app.run(debug=True)
