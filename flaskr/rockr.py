from flask import Flask

app = Flask(__name__)

@app.route("/")
def rockr():
    return "Rock n roll ain't noise pollution!"