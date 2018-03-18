from flask import Flask, render_template

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route("/")
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404