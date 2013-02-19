# Copyright (C) 2012 Johnny Vestergaard <jkv@unixcluster.dk>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from webob import Request
from datetime import datetime
import requests
from requests import ConnectionError
from Queue import Queue
import threading
import json
import logging

logger = logging.getLogger(__name__)


class Loggly(object):
    "WSGI middleware which submits logs to loggly.com"

    def __init__(self, app, token, queue_size=2048):
        self.app = app
        self.token = token
        self.queue = Queue(maxsize=queue_size)

        #less verbose logging from requests lib
        requests_log = logging.getLogger("requests")
        requests_log.setLevel(logging.WARNING)

        worker_thread = threading.Thread(target=self.worker)
        worker_thread.daemon = True
        worker_thread.start()

    def __call__(self, environ, start_response):
        start = datetime.now()
        req = Request(environ)
        resp = req.get_response(self.app)
        end = datetime.now()

        username = req.remote_user
        #try to overwrite username with username from beaker
        if 'beaker.session' in environ:
            session = environ['beaker.session']
            if 'username' in session:
                username = session['username']

        log = {'remote_addr': req.remote_addr,
               'username': username,
               'user_agent': req.user_agent,
               'request_method': req.method,
               'full_url': req.url,
               'path': req.path,
               'query_string': req.query_string,
               'response_status': resp.status,
               'response_time': (end - start).microseconds,
               'response_length': resp.content_length,
               }

        self.queue.put(log)

        return resp(environ, start_response)

    def worker(self):
        while True:
            log = self.queue.get()
            try:
                r = requests.post('https://logs.loggly.com/inputs/{0}'.format(self.token), json.dumps(log))
                if r.status_code != 200:
                    logger.debug('Error error occurred while transmitting data to loggly. ({0})'.format(r.text))
            except ConnectionError as ex:
                logger.debug('Error creating connection to loggly. ({0})'.format(ex))
            except KeyboardInterrupt:
                break


