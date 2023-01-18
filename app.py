import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import cross_origin
from celery import Celery
import openai

app = Flask(__name__)

load_dotenv()

# Configure Celery here we use radis
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# GPT-3 endpoint and credentials
gpt3_endpoint = "https://api.openai.com/v1/engines/text-davinci-003/completions"
gpt3_image_endpoint = "https://api.openai.com/v1/images/generations"
gpt3_api_key = os.getenv("OPEN_AI_KEY")
openai.api_key = gpt3_api_key


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


@celery.task
def generate_image(prompt, number, image_size, image_width):
    response = openai.Image.create(
        prompt=prompt,
        n=number,
        size=str(image_size) + "x" + str(image_width)
    )
    image_url = response['data']

    return image_url


@app.route("/")
def index():
    """
    Index / Main page
    :return: html
    """

    return render_template('templates/index.html')


@app.route('/chat', methods=['POST'])
@cross_origin()
def chat():
    # Get prompt from client
    prompt = request.json.get('prompt')

    # Run GPT-3 task asynchronously
    task = generate_text.apply_async(args=(prompt,))

    # Return task id
    return jsonify({'task_id': task.id})


@app.route('/result/<task_id>', methods=['GET'])
@cross_origin()
def result(task_id):
    # Get task result
    response = generate_text.AsyncResult(task_id).get()
    result = response['choices'][0]['text']

    # Return response
    return jsonify({
        "data": result
    })


@app.route('/image_chat', methods=['POST'])
@cross_origin()
def image_chat():
    # Get prompt from client
    prompt = request.json.get('prompt', "cartoon cat")
    number = request.json.get('number', 1)
    image_size = request.json.get('image_size', 1024)
    image_width = request.json.get('image_width', 1024)

    # Run GPT-3 task asynchronously
    task = generate_image.apply_async(args=(prompt, number, image_size, image_width))

    # Return task id
    return jsonify({'task_id': task.id})


@app.route('/image/<task_id>', methods=['GET'])
@cross_origin()
def image_result(task_id):
    # Get task result
    response = generate_image.AsyncResult(task_id).get()

    # Return response
    return jsonify({
        "data": response
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
