from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import uuid

app = Flask(__name__, static_folder='static', static_url_path='')

db = MongoClient("mongodb://mongodb:27017").blockdeals

@app.route("/")
def index():
    # TODO: only show non-expired deals... paginate?
    deals = []
    deal_cursor=db.deal.find({})
    for deal in deal_cursor:
        deals.append(deal)
    print(deals)
    return render_template('index.html', deals=deals)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/deal', methods=['GET', 'POST'])
def deal():
    deal_form=request.form.to_dict()
    print(db['deal'].insert(deal_form))
    # TODO: make a pretty template
    return 'deal posted'
