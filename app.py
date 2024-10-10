from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = 'AIzaSyD6dBGo5WtH6-wD_i50gFnljhe1cC64RwM'
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'
URL_TO_CRAWL = 'https://www.intelliboticslimited.com/'

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')

    info = fetch_info_from_website(URL_TO_CRAWL)
    if info:
        response = fetch_text_response(message, info)
        return response
    else:
        return jsonify({"error": "Unable to fetch information from the website."}), 500

def fetch_info_from_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title, headings, and body text for more context
        title = soup.title.string if soup.title else ''
        headings = ' '.join([h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])])
        body_text = soup.find('body').get_text(separator=' ', strip=True)

        # Combine title, headings, and body text for context
        content = f"{title} {headings} {body_text}"
        return content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from the website: {e}")
        return None

def fetch_text_response(question, context):
    prompt = f"""
    Please answer the following question based on the context provided from the Intellibotics Limited website and the result should be on passive voice:

    Question: "{question}"

    Context: {context}

    If you cannot answer based on the provided context, respond with "I'm sorry, but I don't have enough information to answer that question."
    
    Answer:
    """

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload)

    if response.status_code == 200:
        gemini_response = response.json()
        generated_text = gemini_response['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"message": generated_text})
    else:
        return jsonify({"error": response.status_code, "message": response.text}), response.status_code

if __name__ == '__main__':
    app.run(port=5000)
