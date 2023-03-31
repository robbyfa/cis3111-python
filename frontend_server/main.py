try:
    import requests
except ImportError:
    import sys
    print("Error: The 'requests' package is required but not installed. Please add 'requests' to your requirements.txt file.", file=sys.stderr)
    sys.exit(1)

from flask import Flask, jsonify

app = Flask(__name__)

API_URL = "https://api-dot-numbers-generator-assignment.ew.r.appspot.com"

@app.route("/")
def index():
    # Generate random numbers
    generate_numbers_url = f"{API_URL}/generate_numbers"
    requests.get(generate_numbers_url)

    # Get results
    get_results_url = f"{API_URL}/get_results"
    response = requests.get(get_results_url)
    results
