from flask import Flask, render_template, jsonify
from main import main
from dotenv import load_dotenv
import os

TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/run-script")
def run_script():
    try:
        result = main(TWITTER_USERNAME, TWITTER_PASSWORD)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
