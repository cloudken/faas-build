
# from flask import json
# import mock
# from six.moves import http_client
import testtools

from cloudframe.api import flask_app as my_app
# from cloudframe.common import exception


class TestFlaskAPIServers(testtools.TestCase):
    my_app.app.config['Testing'] = True
    app = my_app.app.test_client()

    def setUp(self):
        super(TestFlaskAPIServers, self).setUp()
