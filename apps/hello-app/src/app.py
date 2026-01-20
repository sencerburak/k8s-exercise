from flask import Flask, jsonify
import os

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify(message=os.getenv("MESSAGE", "Hello"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
