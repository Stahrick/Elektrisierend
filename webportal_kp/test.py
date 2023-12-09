from unittest import TestCase
from unittest.mock import patch
import web_server

class API_TEST(TestCase):

    def test_check_session_id(self):
        assert not web_server.check_session('u123218312z3zu12zu3')
    