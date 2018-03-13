from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound


user_blueprint = Blueprint('user_blueprint', __name__, template_folder='templates')


@user_blueprint.route('/submit')
def submit_page():
    return render_template("submit_deals.html")


