import markdown2, re
import os, datetime
from babel import Locale

from flask import Flask, render_template, url_for, redirect

LINK_PATTERNS = [
        (re.compile(r"\[([\w]*)\]", re.I), r"/\1/")
        ]

app = Flask(__name__)
app.config.from_object('exsequiae.default_config')

def _buildMetadata(defs):

    metadata = {}

    for d in defs:
        name = d.group(1)
        values = map(lambda x:x.strip(), d.group(2).split(','))
        if len(values) == 1:
            values = values[0]

        if name == 'date':
            metadata[name] = datetime.datetime.strptime(values, '%Y-%m-%d')
        elif name == 'language':
            metadata[name] = Locale.parse(values).display_name
        else:
            metadata[name] = values

    return metadata


def _readMetadata(text):
    regexp = re.compile(r'^-\*- (\w+): ((?:[ \w\-]+)(?:,(?:[ \w\-]+))*)\s*$', re.MULTILINE)

    defs = list(regexp.finditer(text))

    if len(defs) > 0:
        # cut text till the end of last match
        text = text[defs[-1].end():]

    metadata = _buildMetadata(defs)

    return metadata, text


def render(dterm):
    config = app.config
    fileName = os.path.join(config['DICTIONARY_DIR'], "%s.text" % dterm)

    if os.path.exists(fileName):
        with open(fileName, 'r') as f:
            metadata, wiki = _readMetadata(f.read())

        defHtml = markdown2.markdown(wiki,
                                     extras=["link-patterns"],
                                     link_patterns=LINK_PATTERNS)

        tpl = render_template('page.html', site_title=config['SITE_TITLE'],
                              base_url=url_for('term_definition', term=''),
                              term=dterm, defHtml=defHtml, metadata=metadata,
                              years=map(lambda x: str(x), range(config['STARTING_YEAR'], datetime.datetime.now().year+1)),
                              author_name=config['AUTHOR_NAME'])
        return tpl
    else:
        return '', 404

@app.route('/<term>/', methods=['GET'])
def term_definition(term):
    return render(term)

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('term_definition', term=app.config['DEFAULT_PAGE']))
