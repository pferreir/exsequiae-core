#!/usr/bin/env python

CONFIG_FILE = "config.py"

import exsequiae

class configClass(object):
    pass

execfile(CONFIG_FILE)

configObj = configClass()

for k,v in locals()['config'].iteritems():
    setattr(configObj, k, v)

app = exsequiae.getApp(configObj)
application = app.wsgifunc()

if __name__ == "__main__":
    app.run()
    
