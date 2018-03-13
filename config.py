from flask import Flask, flash, redirect, render_template, request, session, abort

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')



@app.route("/getting_started")
def get_started():
    return render_template('getting_started.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)

