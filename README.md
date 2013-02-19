kumo
====

WSGI for cloud logging.

Basic usage for enabling logging to loggly.net:

``` python
from bottle import route, run, template, install
from bottle_loggly import LogglyPlugin
from kumo.loggly import Loggly
import bottle

app = bottle.app()
myapp = Loggly(app, '37ae0051-c548-497e-9035-31ff2ef41857')

@route('/hello/:name')
def index(name='World'):
    return template('<b>Hello {{name}}</b>!', name=name)

@route('/')
def index():
    return "DAVS"
run(app=myapp,host='localhost', port=8080)

```