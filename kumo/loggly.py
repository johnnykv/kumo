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
        worker_thread.start()

    def __call__(self, environ, start_response):
        start = datetime.now()
        req = Request(environ)
        resp = req.get_response(self.app)
        end = datetime.now()

        d = {'remote_addr': req.remote_addr,
             'request_method': req.method,
             'full_url': req.url,
             'path': req.path,
             'query_string': req.query_string,
             'timed_microseconds': '{0}'.format((end - start).microseconds),
             'username': req.remote_user,
             'user_agent': req.user_agent,
             'response_status': resp.status,
        }

        self.queue.put(d)
        return resp(environ, start_response)

    def worker(self):
        while True:
            d = self.queue.get()
            #TODO: Handle errors...
            requests.post('https://logs.loggly.com/inputs/{0}'.format(self.token), json.dumps(d))