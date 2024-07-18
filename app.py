# app.py
from flask import Flask, request, jsonify
import requests
from PIL import Image
import io
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64

load_dotenv()
app = Flask(__name__)
api_key = os.getenv('api_key')


@app.route('/upload', methods=['POST'])
def upload_image():
    if not api_key:
        jsonify({'error': 'None'}), 400

    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    image_file = request.files['image']
    image = Image.open(image_file.stream)

    # Convert image to base64
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Process the image and question with your AI model
    answer = process_image_with_model(img_str)
    if answer is None:
        return jsonify({'error': 'No answer found'}), 500
 

    return jsonify({'answer': answer})

def process_image_with_model(img_str):

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
        }

    payload = {
    "model": "gpt-4o",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Is this a hot dog? Please respond Yes or No."
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{img_str}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    result = response.json()
    print(result)
    answer = result['choices'][0]['message']['content']
    return answer

if __name__ == '__main__':
    app.run(debug=True)