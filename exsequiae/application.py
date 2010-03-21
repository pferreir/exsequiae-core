import markdown2, re, pycountry
import web, os, datetime


def definition_meta(config):
    linkPatterns = [
        (re.compile(r"\[([\w]*)\]", re.I), config.baseURL + r"/\1/")
        ]


    class definition:

        def _buildMetadata(self, defs):

            metadata = {}

            for d in defs:
                name = d.group(1)
                values = map(lambda x:x.strip(), d.group(2).split(','))
                if len(values) == 1:
                    values = values[0]

                if name == 'date':
                    metadata[name] = datetime.datetime.strptime(values, '%Y-%m-%d')
                elif name == 'language':
                    metadata[name] = pycountry.languages.get(alpha2=values)
                else:
                    metadata[name] = values

            return metadata

        def _readMetadata(self, text):
            regexp = re.compile(r'^-\*- (\w+): ((?:[ \w\-]+)(?:,(?:[ \w\-]+))*)\s*$', re.MULTILINE)

            defs = list(regexp.finditer(text))

            if len(defs) > 0:
                # cut text till the end of last match
                text = text[defs[-1].end():]

            metadata = self._buildMetadata(defs)

            return metadata, text

        def render(self, term):
            fileName = os.path.join(config.dictDir, "%s.text" % term)

            if os.path.exists(fileName):
                f = open(fileName, 'r')
                metadata, wiki = self._readMetadata(f.read())
            
                defHtml = markdown2.markdown(wiki,
                                             extras=["link-patterns"],
                                             link_patterns=linkPatterns)

                tpl = web.template.render(os.path.dirname(__file__))

                return tpl.page(config.siteTitle, config.baseURL, term, defHtml, metadata, map(lambda x: str(x), range(config.startingYear, datetime.datetime.now().year+1)), config.authorName)
            else:
                return web.webapi.NotFound()
    
        def GET(self, term):
            if not term: 
                term = config.defaultPage
            
            return self.render(term)
        
    return definition


def getApp(config):
    urls = (
    '(?:/(\w*))?/?', definition_meta(config)
    )

    app = web.application(urls, globals())
    return app


