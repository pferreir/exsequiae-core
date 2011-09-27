import markdown2, re
import os, datetime
from babel import Locale

from flask import render_template, url_for, redirect, request, session, jsonify, current_app, Blueprint, json


LINK_PATTERNS = [
    (re.compile(r"\[\[([\w]*)\]\]", re.I), lambda m: url_for('defs.term_definition', term=m.group(1)), r'\1')
    ]


auth = Blueprint('auth', __name__)
defs = Blueprint('defs', __name__)


class NoSuchTermException(Exception):
    pass


class TermAlreadyExistsException(Exception):
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

        tpl = render_template('definition.html', site_title=config['SITE_TITLE'],
                              term=dterm, defHtml=defHtml, metadata=metadata,
                              years=map(lambda x: str(x), range(config['STARTING_YEAR'], datetime.datetime.now().year+1)),
                              author_name=config['AUTHOR_NAME'])
        return tpl
    except NoSuchTermException:
        return render_template('not_found.html', site_title=config['SITE_TITLE'], term=dterm), 404


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


@auth.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'GET':
        return render_template('logout.html', site_title=current_app.config['SITE_TITLE'], term="logout")
    elif request.method == 'POST':
        del session['username']
        return redirect(url_for('defs.index'))


@defs.route('/<term>/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def term_definition(term):
    if request.method == 'GET':
        return render(term)

    # Otherwise, user has to be logged in
    if 'username' not in session:
        return json.dumps({'error': 'You are not logged in!'}), 403

    if request.method == 'PUT':
        if term in current_app.storage:
            raise TermAlreadyExistsException()
        else:
            node = current_app.storage.new(term)
            node.metadata = {}
            node.data = ''
            node.save()
            return ''
    elif request.method == 'DELETE':
        if term in current_app.storage:
            del current_app.storage[term]
            return ''
        else:
            raise NoSuchTermException()
    elif request.method == 'POST':
        node = current_app.storage[term]
        node.data = request.form['content']
        node.save()
        return ''


@defs.route('/<term>/res/', methods=['GET', 'POST'])
def resource_list(term):
    if request.method == 'POST':
        # User has to be logged in
        if 'username' not in session:
            return json.dumps({'error': 'You are not logged in!'}), 403
        else:
            node = current_app.storage[term]
            f = request.files['file']
            node.add_attachment(f.filename, f, f.mimetype)
            return ''
    else:
        return render_template('resource_list.html', site_title=current_app.config['SITE_TITLE'],
                               term=term, storage_node=current_app.storage[term])


@defs.route('/<term>/res/<resource>', methods=['GET', 'DELETE'])
def resource(term, resource):
    node = current_app.storage[term]
    res = node.get_attachment(resource)

    if res == None:
        return 'Not found', 404

    if request.method == 'GET':
        return res.data, 200, [], res.mime
    elif request.method == 'DELETE':
        if 'username' not in session:
            return json.dumps({'error': 'You are not logged in!'}), 403
        else:
            del node[resource]
            return ''


@defs.route('/<term>.json/', methods=['GET'])
def term_definition_json(term):
    return read_term(term)[1]


@defs.route('/', methods=['GET'])
def index():
    return redirect(url_for('defs.term_definition', term=current_app.config['DEFAULT_PAGE']))
