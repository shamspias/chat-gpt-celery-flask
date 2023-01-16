import os
import requests
from flask import Flask, request, jsonify
from celery import Celery

app = Flask(__name__)

# Configure Celery here we use radis
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# GPT-3 endpoint and credentials
gpt3_endpoint = "https://api.openai.com/v1/engines/davinci-codex/completions"
gpt3_api_key = os.getenv("OPEN_AI_KEY")


@celery.task
def generate_text(prompt):
    # Send request to GPT-3
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {gpt3_api_key}"
    }
    data = {
        "prompt": prompt,
        "temperature": 0.5,
        "max_tokens": 128
    }
    response = requests.post(gpt3_endpoint, headers=headers, json=data)

    # Return response
    return response.json()


@app.route('/chat', methods=['POST'])
def chat():
    # Get prompt from client
    prompt = request.json.get('prompt')

    # Run GPT-3 task asynchronously
    task = generate_text.apply_async(args=(prompt,))

    # Return task id
    return jsonify({'task_id': task.id})


@app.route('/result/<task_id>', methods=['GET'])
def result(task_id):
    # Get task result
    result = generate_text.AsyncResult(task_id).get()

    # Return response
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
