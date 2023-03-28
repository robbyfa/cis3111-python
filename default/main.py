from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

API_URL = 'https://api-dot-random-numbers-assignment.ew.r.appspot.com'

@app.route('/')
def index():
    response = requests.get(API_URL + 'results')
    results = response.json()
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
