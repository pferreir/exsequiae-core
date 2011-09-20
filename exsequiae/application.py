import markdown2, re
import os, datetime
from babel import Locale

from flask import render_template, url_for, redirect, request, session, jsonify, current_app, Blueprint

LINK_PATTERNS = [
        (re.compile(r"\[([\w]*)\]", re.I), r"/\1/")
        ]

auth = Blueprint('auth', __name__)
defs = Blueprint('defs', __name__)

class NoSuchTermException(Exception):
    pass

def read_term(term):
    if term in current_app.storage:
        node = current_app.storage[term]
        return node.metadata, node.data
    else:
        raise NoSuchTermException(term)


def render(dterm):
    config = current_app.config

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


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        if username == current_app.config['ADMIN_USERNAME'] and password == current_app.config['ADMIN_PASSWORD']:
            session['username'] = request.form['username']
            return redirect(url_for('defs.index'))
        else:
            return render_template('login.html', site_title=current_app.config['SITE_TITLE'], term="login", error='Login failed'), 403
    else:
        return render_template('login.html', site_title=current_app.config['SITE_TITLE'], term="login")


@defs.route('/<term>/', methods=['GET'])
def term_definition(term):
    return render(term)


@defs.route('/<term>.json/', methods=['GET', 'POST'])
def term_definition_json(term):
    if request.method == 'GET':
        return read_term(term)[1]
    else:
        if 'username' in session:
            node = current_app.storage[term]
            node.data = request.form['content']
            node.save()
            return jsonify({'result': 'ok'})
        else:
            return jsonify({'error': 'You are not logged in!'}), 403


@defs.route('/', methods=['GET'])
def index():
    return redirect(url_for('defs.term_definition', term=current_app.config['DEFAULT_PAGE']))
