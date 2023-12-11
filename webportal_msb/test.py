from unittest import TestCase 
from unittest.mock import patch, Mock
import web_server
import api_requests
from datetime import datetime, timedelta, timezone
from os import urandom

class API_TEST(TestCase):
    @patch('os.urandom')
    @patch('datetime.datetime')
    @patch('requests.post')
    def test_send_registration_mail(self, mock_post, mock_datetime, mock_urandom):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        mock_now = datetime(2023, 12, 9, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now
        mock_datetime.timedelta = timedelta(days=2)

        mock_urandom.return_value = b'\x00'*10
        api_requests.send_registration_mail('123')
        mock_post.assert_called_with('https://localhost:25565/service-worker/receive-mails', json=[['Registration-Code for meter[123] installation', 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJtc2IiLCJhdWQiOiIxMjMiLCJleHAiOjE3MDIyOTYwMDAsInV1aWQiOiIxMjMiLCJjb2RlIjoiQUFBQUFBQUFBQUFBQUE9PSIsInVybCI6Imh0dHBzOi8vbG9jYWxob3N0OjUwMDAvbWV0ZXIifQ.ufFgjBJQwrntaop1wItVXr59MX9beQBYH6RLStCr-8ygbMkaSrr0dFsEeplUAGTfVyFiJqkVGN2liqG2k7nFi1uDIHWsNDZOf8WT2xcyqQ_EzElMOzIdQc9BGlfeUTQSku6cIKPVSG1zIeUWj3MYfM9wZ49wiESWmzTNB6N1JhfUVogZXyD_px2AwcJzCsPfw2FDtxkAY1fKmLOOMk7wXi5xvJf5rS37fgYnw2okdqFSFPP4Rx7mu5URuSzTzc0QBn0KW_un1QDojcZ51nQ0sfD6TLxuKmI1fV3D0O5-vDs6rjVY2mkLxRoOrFUHYxtudkVvWUn4ZCBippiNwPpNB1U9qsv8XI5TJxBS_VqcxBxL5N4LS1XcjzKi-KGNJ-I3z6KokVybwatGFRGrOkOwaAzqqy4uONfa0SoUjT-X-AA-b40PY4sMwQhg-OzB0qtUHscEND12tyHCOhm-ViBp3Qt4eZmCNY5zGjsPpqKsvWG18k7RKA7UAgRtHOWoXo7TJYNd-QXFKFCwLCmskTgvFKF9mkrYOX07IoSHIao8PHQxW6fGvvUL90YTp3elxmUBDI4e0Vwbl0g1SfyWunpBW_FN-d1V-nxOc3kUwM4I2kEgl82wcXPJndvr4a9rWywpGvTvBQldyAXKQP357MmbIMd2bZ5r6ytR_ldVmh5Tvgg']], cert=('localhost.crt', 'localhost.key'), verify='RootCA.crt')
    
    @patch('requests.post')
    @patch('api_requests.uuid4')
    def test_place_order(self, mock_uuid4, mock_post):
        mock_uuid4.return_value = '875e85c2-fb32-4de3-bd2f-bb7b3b6da423'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.return_value = "875e85c2-fb32-4de3-bd2f-bb7b3b6da423"
        mock_post.return_value = mock_response
        api_requests.place_order()
        mock_post.assert_called_with('https://localhost:25565/meter/order/', json={'uuid': '875e85c2-fb32-4de3-bd2f-bb7b3b6da423'}, cert=('localhost.crt', 'localhost.key'), verify='RootCA.crt')


    @patch('requests.post')
    def test_swap_cert(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        assert api_requests.swap_cert(1,2)

    @patch('requests.post')
    def test_send_service_worker_mails(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        api_requests.send_service_worker_mails('a')
        mock_post.assert_called_with('https://localhost:25565/service-worker/receive-mails', json='a', cert=('localhost.crt', 'localhost.key'), verify='RootCA.crt')
    
    def test_sign_cert(self):
        csr = b'''-----BEGIN CERTIFICATE REQUEST-----
MIIEuzCCAqMCAQAwTzELMAkGA1UEBhMCREUxETAPBgNVBAgMCE1hbm5oZWltMREw
DwYDVQQHDAhNYW5uaGVpbTEMMAoGA1UECgwDTVNCMQwwCgYDVQQDDANhYmMwggIi
MA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQC9D1Yhah13UeO85TRaN3Jp1azQ
gt+kPpullq9e2NbxWROF0myue7mqUGHTOYhi/lQDPe+z3u8115boJ4i27xHZrcw6
Fi3Gb/wKXmclwSckLygF+KTU4cZN0Oiiz0eekjm+HgMY7ASbV6aTPiyciYIZZ0bM
2zD9iGDrjg7tDJducRQ4pLfgEv+adABuQrVLYtrT4lY/tniAineQs1M6St/WxgAk
zoEPwEYVmQw2CJ2wHiDFMVfPNT3FDzl8xcOsueRAP7HbytRGz0KegtYBVqpxRp3j
1YSU0u0S6DdZ0aIoOMAN7j7n9WDmNLVJxbakhBMzH0bkzzcwWBjRhU9F8Hge4iG0
HCJ4cDrWsLS6N7f+iatvzsWwjHaTtzZDMGQ6A4+7RfQe6gQ2+HuJLCkP3RELiC3j
FOvqbEJ4e+DptSYVXzc+kKkakbh1YC/TJioR0pU1J2IY81us5NZx+L1qbV1ZV5Gj
FAu7tkP2j7aej6i4VWtMG7z/LJFl7g66Wm+aEAZJiSVAt3m11N4SLNZHZOBrr1fJ
M+dwsSZGlbFfY+PlEgNP/XQKPDaWCZ6IDZ0syzRZVhhj/Z0wr2Owvy6t9QiQAN7I
RxFrTR+iEWeDPPuS+vssuebQGS6pNUHoRQsexZQfD1iOKp6KOOAn+XVAaNVYLwkt
ylNqHHUnSoV+1orOTwIDAQABoCcwJQYJKoZIhvcNAQkOMRgwFjAUBgNVHREEDTAL
gglsb2NhbGhvc3QwDQYJKoZIhvcNAQELBQADggIBABJXcDB7p6gECfw90ReJ3bJ/
7FNxmx/stbYHVqEoN4lFYvR53ejAEWLBIlsPzcLoOfi5eZTmhW+eRKxlhGO71gR/
6yf9foBdivBr2Mwnozad4FaczNqo1ekmfMBDhigAVDQqdWHBxlrmykLYoILfRxQq
O/Tuswl4xsp0NNiInw/Hj0VA5MwHyjn9RjxUy6YDJq6ZYD3xRwfssi9qJRjOLscU
FcrRGIB1gpuZe4zBWYD5QNooLWIZ+EDykyKqJbOXRw5+m2jnR2BwXCjTKGs6rvG3
qLLXLsU/B5s9Y2AgD/ub/lftpuicPVnKX4Zx9xZmY/SKHvD8IaedkMfrbVoOKBzT
h82q7hYb1G5iAgEi0ipW7PNtw7zIVrsJXJr4ROxye9nUtu1pVz3K5OLbevt6XZxS
iQmlECEuqz3bwTcRLBZJ1qepUNYjeFvb/yr3cGo0ebsVwjsbtyEwF2+Y0eifB0UP
LV924QP63c5R6++Ojz9PK9GCh78Fe024rWCoLKzsaL2UgVpV2QFWWSRJtEv6sI1v
YhcWKl8xbqxv5jHOBScpPnykrEwCYKse6xgbZmihgOLOssMGPY1dWItBJ9KvkisF
hmohv8KR+jCxhdR4SV2ClNR25lTq2KlFWGglxOpYu0Yakz/y6Hy2jjdnS4Gd6HZJ
fFztaTuSszUEFOg8hs13\n-----END CERTIFICATE REQUEST-----
'''
        assert api_requests.sign_cert(csr)

    @patch('web_server.db_acc_handler.get_account_by_id')
    def test_check_session(self, mock_db):
        mock_db.return_value = 1
        assert web_server.check_session(urandom(10))
    
    @patch('web_server.db_acc_handler.get_account_by_username')
    @patch('web_server.argon2.verify')
    def test_check_login(self, mock_argon, mock_db):
        mock_db.return_value = [{'_id':1,'role':1, 'pw_hash': 1}]
        mock_argon.return_value = True
        assert web_server.check_login(urandom(10), urandom(10))

    def test_check_register(self):
        assert web_server.check_register('test') if web_server.check_register('register') else None

    def test__update_account_data(self):
        assert not web_server._update_acc_data(None)

    def test__update_contract_data(self):
        assert web_server._update_contract_data(None)

    @patch('web_server.db_elmo_handler.get_Em_by_id')
    def test_check_em_id(self, mock_handler):
        mock_handler.return_value = True
        assert web_server.check_em_id("875e85c2-fb32-4de3-bd2f-bb7b3b6da423")