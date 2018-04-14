from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from pymongo import MongoClient
from steem import Steem
from datetime import date, timedelta, datetime
from dateutil import parser
from slugify import slugify
import sys, traceback, json, textwrap, requests, pprint, time

app = Flask(__name__, static_folder='static', static_url_path='')
app.config.from_envvar('BLOCKDEALS_SETTINGS')
app.secret_key=app.config['SESSION_SECRET']
admins = app.config['ADMINS'].split(',')

db = MongoClient("mongodb://mongodb:27017").blockdeals

def confirm_user():
    if not 'token' in session or not 'username' in session:
        return False

    r = requests.get('https://v2.steemconnect.com/api/me', headers={ 'Authorization': session['token'] })
    if r.status_code == 200:
        session['authorized'] = False
        if r.json()['_id'] != session['username']:
            return False
        if 'account_auths' in r.json()['account']['posting']:
            for auth_account in r.json()['account']['posting']['account_auths']:
                if auth_account[0] == "blockdeals":
                    session['authorized'] = True
                    app.logger.info('Confirmed token and auth of {} successful'.format(session['username']))
                    return True
    else:
        session['logged_in'] = False
    return False

@app.template_filter('expires_class')
def _jinja2_filter_expires_class(date, fmt=None):
    date = parser.parse(date)
    native = date.replace(tzinfo=None)
    days = (native-date.today()).days
    if days <= 2:
        return "red pulse"
    else:
        return "grey lighten-1"

@app.template_filter('expires_time')
def _jinja2_filter_expires_time(date, fmt=None):
    date = parser.parse(date)
    native = date.replace(tzinfo=None)
    days = (native-date.today()).days
    if days <= 2:
        return "soon"
    else:
        return "in {} day{}".format(days, '' if days == 1 else 's')

@app.template_filter('datetimeformat')
def _jinja2_filter_datetime(date, fmt=None):
    date = parser.parse(date)
    native = date.replace(tzinfo=None)
    format='%b %d, %Y'
    return native.strftime(format)

@app.route("/vote/<author>/<permlink>/<kind>")
def vote(author, permlink, kind):
    if 'logged_in' in session and session['logged_in'] and 'username' in session:
        try:
            weight=100
            if kind == "flag":
                weight=-100
            identifier = "@" + author + "/" + permlink
            if 'POST_TO_STEEM' in app.config and app.config['POST_TO_STEEM'] == "1":
                s = Steem(nodes=['https://rpc.buildteam.io', 'https://api.steemit.com', 'https://steemd.steemitstage.com'],
                        keys=[app.config['POSTING_KEY'], app.config['ACTIVE_KEY']])
                p = s.commit.vote(identifier, weight, account=session['username'])
                app.logger.info(p)
            return jsonify({ 'status': True })
        except Exception as e:
            app.logger.info(e)
            return jsonify({ 'status': False })
    else:
        return jsonify({ 'status': False })

@app.route("/whoami")
def whoami():
    if 'username' in session:
        return jsonify({ 'username': session['username']})
    else:
        return jsonify({ 'username': "" });

@app.route("/update/<permlink>", methods=['GET', 'POST'])
def update(permlink):
    if 'logged_in' in session and session['logged_in'] and 'username' in session and session['username'] in app.config['ADMINS'].split(','):
        if request.method == 'POST':
            deal_update=request.form.to_dict()

            # fix some values
            if deal_update['warning'].strip() != "":
                deal_update['available'] = False
            else:
                deal_update['available'] = True
            if not 'freebie' in deal_update:
                deal_update['freebie'] = ''
            if not 'global' in deal_update:
                deal_update['global'] = ''
            if not 'hide' in deal_update:
                deal_update['hide'] = False;
            else:
                deal_update['hide'] = True;
            try:
                deal_update['deal_start'] = parser.parse(deal_update['deal_start']).isoformat()
            except ValueError:
                deal_update['deal_start'] = date.today().isoformat()
            try:
                deal_update['deal_end'] = parser.parse(deal_update['deal_end']).isoformat()
            except ValueError:
                deal_update['deal_end'] = (date.today() + timedelta(days=45)).isoformat()
            deal_update['deal_expires'] = deal_update['deal_end']
            deal_update['brand_code'] = slugify(deal_update['brand'])

            app.logger.info("updating {}: {}".format(permlink, deal_update))
            try:
                db.deal.update_one({ 'permlink': permlink },
                                   { '$set': deal_update }, upsert=False)
            except Exception as e:
                flash(u'Sorry but there was an error trying to update your deal: ' + textwrap.shorten(str(e), width=80, placeholder="..."), 'error')
            return redirect(url_for('index'))
        else:
            deal = db.deal.find_one({'permlink':  permlink })
            app.logger.info("requested update of: {}".format(deal))
            return render_template('update.html', deal=deal)
    else:
        app.logger.info("non-authorised update attempt ({}, {})".format(permlink, session['username'] if 'username' in session else 'anon'))
        return render_template('login_failed.html'), 401

@app.route("/")
def index():
    # TODO: only show non-expired deals... paginate?
    deals = []
    deal_cursor = db.deal.find({'deal_expires': { '$gte': date.today().isoformat()}, 'hide': { '$ne': True}}).sort([('_id', -1)])
    for deal in deal_cursor:
        deals.append(deal)
    if 'username' in session:
        if 'logged_in' in session:
            app.logger.info("{} logged_in: {}, authorized: {}".format(session['username'], session['logged_in'], session['authorized']))
        else:
            app.logger.info("{} logged_in: {}".format(session['username'], False))
    else:
        app.logger.info("anonymous user")
    return render_template('index.html', deals=deals, session=session, admins=admins)

@app.route("/countries")
def countries_json():
    countries = db.deal.find({ 'country_code': { '$ne': '' }}).distinct('country_code')
    return jsonify(countries)

@app.route("/country/<country>")
def countries(country):
    deals = []
    deal_cursor=db.deal.find({'deal_expires': { '$gte': date.today().isoformat()}, 'country_code': country}).sort([('_id', -1)])
    for deal in deal_cursor:
        deals.append(deal)
    return render_template('index.html', deals=deals, country=country, session=session, admins=admins)

@app.route("/freebies")
def freebies():
    deals = []
    deal_cursor=db.deal.find({'deal_expires': { '$gte': date.today().isoformat()}, 'freebie': 'on'}).sort([('_id', -1)])
    for deal in deal_cursor:
        deals.append(deal)
    return render_template('index.html', deals=deals, session=session, admins=admins)

@app.route("/brand/<brand>")
def brands(brand):
    deals = []
    deal_cursor=db.deal.find({'deal_expires': { '$gte': date.today().isoformat()}, 'brand_code': brand}).sort([('_id', -1)])
    for deal in deal_cursor:
        deals.append(deal)
    return render_template('index.html', deals=deals, session=session, admins=admins)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    session.pop('token', None)
    session.pop('authorized', None)
    session['logged_in'] = False
    return redirect(url_for('index'))

@app.route('/auth', methods=['GET'])
def authorized():
    if not 'logged_in' in session or not session['logged_in']:
        return render_template('login_failed.html'), 401

    r = requests.get('https://v2.steemconnect.com/api/me', headers={ 'Authorization': session['token'] })
    if r.status_code == 200:
        app.logger.info('Auth of {} successful'.format(session['username']))
        session['authorized'] = False
        if r.json()['_id'] != session['username']:
            session['logged_in'] = False
            return render_template('login_failed.html'), 401
        if 'account_auths' in r.json()['account']['posting']:
            for auth_account in r.json()['account']['posting']['account_auths']:
                if auth_account[0] == "blockdeals":
                    session['authorized'] = True
        return redirect(url_for('index'))
    else:
        session['logged_in'] = False
        return render_template('login_failed.html'), 401

@app.route('/complete/sc/', methods=['GET'])
def complete_sc():
    # TODO: verify token
    token = request.args.get('access_token')
    expire = request.args.get('expires_in')
    username = request.args.get('username')
    r = requests.get('https://v2.steemconnect.com/api/me', headers={ 'Authorization': token })
    if r.status_code == 200:
        app.logger.info('Login of {} successful'.format(username))
        session['authorized'] = False
        session['logged_in'] = username == r.json()['_id']
        if 'account_auths' in r.json()['account']['posting']:
            for auth_account in r.json()['account']['posting']['account_auths']:
                if auth_account[0] == "blockdeals":
                    session['authorized'] = True
        session['username'] = username
        session['token'] = token
        return redirect(url_for('index'))
    else:
        session['logged_in'] = False
        return render_template('login_failed.html'), 401

@app.route('/deal', methods=['POST'])
def deal():
    if not confirm_user():
        return render_template('login_failed.html'), 401

    deal_form=request.form.to_dict()

    comment_options = {
        'max_accepted_payout': '1000000.000 SBD',
        'percent_steem_dollars': 10000,
        'allow_votes': True,
        'allow_curation_rewards': True,
        'extensions': [[0, {
            'beneficiaries': [
                {'account': 'blockdeals', 'weight': 1000}
            ]}
        ]]
    }

    json_metadata = {
        'community': 'blockdeals',
        'app': 'blockdeals/1.0.0',
        'format': 'markdown',
        'tags': [ 'blockdeals' ]
    }

    if 'country_code' in deal_form:
        json_metadata['tags'].append('blockdeals-'+deal_form['country_code'])

    permlink = ""

    try:
        # Work out our freebie emoji
        freebie = "&#128077;" if deal_form['freebie'] else "&#10060;"
    except KeyError:
        freebie = "&#10060;"

    try:
        if deal_form['image_url'] == "":
            deal_form['image_url'] = 'https://blockdeals.org/assets/images/logo_round.png'

        if 'global' in deal_form and deal_form['global'] == 'on':
            country_text = "multiple ([check details]({}))".format(deal_form['url'])
        else:
            country_text = "{0} ![{0}](https://steemitimages.com/22x22/https://github.com/hjnilsson/country-flags/raw/master/png100px/{1}.png)".format(deal_form['country'], deal_form['country_code'])

        if not 'coupon_code' in deal_form or deal_form['coupon_code'].strip() == "":
            coupon_code = "&#10060;"
        else:
            coupon_code = deal_form['coupon_code'].strip()

        app.logger.info("Sanitised: country_text={}, coupon_code={}".format(country_text, coupon_code))

        if 'POST_TO_STEEM' in app.config and app.config['POST_TO_STEEM'] == "1":
            s = Steem(nodes=['https://rpc.buildteam.io', 'https://api.steemit.com', 'https://steemd.steemitstage.com'],
                      keys=[app.config['POSTING_KEY'], app.config['ACTIVE_KEY']])
            p = s.commit.post(title=deal_form['title'],
                              body="""
# {0}

![{0}]({2})

| Details | |
| - | - |
| &#127991; **Coupon Code** | {3} |
| &#127758; **Country** | {9} |
| &#128198; **Starts** | {4} |
| &#128198; **Ends** | {5} |
| &#128176; **Freebie?** | {6} |
| &#128176; **Deal Link** | [{8}]({7}) |

## Description

{1}

---
### Find more deals or earn Steem for posting deals on [BlockDeals](https://blockdeals.org) today!
[![](https://blockdeals.org/assets/images/blockdeals_logo.png)](https://blockdeals.org)
""".
                              format(deal_form['title'],
                                     deal_form['description'],
                                     deal_form['image_url'],
                                     coupon_code,
                                     deal_form['deal_start'],
                                     deal_form['deal_end'],
                                     freebie,
                                     deal_form['url'],
                                     textwrap.shorten(deal_form['title'], width=40, placeholder="..."),
                                     country_text),
                              author=session['username'],
                              json_metadata=json_metadata,
                              comment_options=comment_options,
                              self_vote=True)

            permlink = p['operations'][0][1]['permlink']
            app.logger.info("Posted to STEEM with id={}".format(permlink))
        else:
            permlink = "testing-{}".format(int(time.time()))

        deal_form['permlink'] = permlink
        deal_form['steem_user'] = session['username']
        try:
            deal_form['deal_start'] = parser.parse(deal_form['deal_start']).isoformat()
        except ValueError:
            deal_form['deal_start'] = date.today().isoformat()
        try:
            deal_form['deal_end'] = parser.parse(deal_form['deal_end']).isoformat()
        except ValueError:
            deal_form['deal_end'] = (date.today() + timedelta(days=45)).isoformat()
        deal_form['deal_expires'] = deal_form['deal_end']
        deal_form['brand_code'] = slugify(deal_form['brand'])
        mongo_id = db['deal'].insert(deal_form)
        app.logger.info("saved to mongodb: {}\n{}".format(mongo_id, deal_form))
    except Exception as e:
        app.logger.info(e)
        traceback.print_exc(file=sys.stdout)
        flash(u'Sorry but there was an error trying to post your deal: ' + textwrap.shorten(str(e), width=80, placeholder="..."), 'error')
        return redirect(url_for("submit_page"))

    # TODO: make a pretty template but for now go to the post
    if 'POST_TO_STEEM' in app.config and app.config['POST_TO_STEEM'] == "1":
        return redirect("https://steemit.com/@{}/{}".format(session['username'], permlink), code=302)
    else:
        return redirect(url_for("index"))

@app.route('/submit')
def submit_page():
    if 'logged_in' in session and session['logged_in'] and 'authorized' in session and session['authorized']:
        return render_template("submit_deals.html")
    return redirect(url_for('index'))
