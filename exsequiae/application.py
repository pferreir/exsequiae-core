import markdown2, re
import os, datetime
from babel import Locale

from flask import Flask, render_template, url_for, redirect, request, session, jsonify
from flaskext.babel import format_datetime, format_date, Babel

from storage import DirStorage

LINK_PATTERNS = [
        (re.compile(r"\[([\w]*)\]", re.I), r"/\1/")
        ]

app = Flask(__name__)
app.config.from_object('exsequiae.default_config')
babel = Babel(app)

app.jinja_env.filters['dt'] = format_datetime
app.jinja_env.filters['d'] = format_date

storage = DirStorage('/home/pferreir/alexandria/json/')

class NoSuchTermException(Exception):
    pass


def read_term(term):    
    if term in storage:
        node = storage[term]
        return node.metadata, node.data
    else:
        raise NoSuchTermException(term)


def render(dterm):
    config = app.config

    try:
        metadata, wiki = read_term(dterm)
    
        defHtml = markdown2.markdown(wiki,
                                     extras=["link-patterns"],
                                     link_patterns=LINK_PATTERNS)

        tpl = render_template('page.html', site_title=config['SITE_TITLE'],
                              term=dterm, defHtml=defHtml, metadata=metadata,
                              years=map(lambda x: str(x), range(config['STARTING_YEAR'], datetime.datetime.now().year+1)),
                              author_name=config['AUTHOR_NAME'])
        return tpl
    except NoSuchTermException:
        return '', 404


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', site_title=app.config['SITE_TITLE'], term="login", error='Login failed'), 403
    else:
        return render_template('login.html', site_title=app.config['SITE_TITLE'], term="login")


@app.route('/<term>/', methods=['GET'])
def term_definition(term):
    return render(term)


@app.route('/<term>.json/', methods=['GET', 'POST'])
def term_definition_json(term):
    if request.method == 'GET':
        return read_term(term)[1]
    else:
        if 'username' in session:
            node = storage.new(term)
            node.data = request.form['content']
            node.metadata = {}
            node.save()
            return jsonify({'result': 'ok'})
        else:
            return jsonify({'error': 'You are not logged in!'}), 403


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('term_definition', term=app.config['DEFAULT_PAGE']))

