Description
====

WSGI middleware for shipping logs to cloud services. Currenly [Loggly](http://loggly.net) is supported, [loggr](http://loggr.com) will be supported in the near future.

Installation
============
```
pip install kumo
```

Usage for shipping request logs to Loggly
=============================================

``` python
from bottle import route, run, template, install
from kumo.loggly import Loggly
import bottle

app = bottle.app()
loggly_token = '37ae0051-c548-497e-9035-31ff2ef41857'
myapp = Loggly(app, loggly_token)

@route('/hello/:name')
def index(name='World'):
    return template('<b>Hello {{name}}</b>!', name=name)

@route('/')
def index():
    return "Ya douchbag!"
run(app=myapp,host='localhost', port=8080)

```

## Logged informaiton
The following information will be sent to loggly:
* Username (Remote_user or beaker session if available)
* Remote addr
* Request_method
* Full_url
* Response status
* Response length
* Response time
* User agent
* Query string
* Path
