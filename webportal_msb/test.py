from unittest import TestCase 
from unittest.mock import patch, Mock
import web_server
import api_requests
from datetime import datetime, timedelta, timezone

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
        mock_post.assert_called_with('https://localhost:25565/service-worker/receive-mails', json=[['Registration-Code for meter[123] installation', 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJtc2IiLCJhdWQiOiIxMjMiLCJleHAiOjE3MDIyOTYwMDAsInV1aWQiOiIxMjMiLCJjb2RlIjoiQUFBQUFBQUFBQUFBQUE9PSIsInVybCI6Imh0dHA6Ly9sb2NhbGhvc3Q6NTAwMC9tZXRlciJ9.vWcc6KNy4pI_I1ZilSSOC_JJRtGGAWzlzxifWQmD0K1FR32i2lHulceMxo_0h_pikbBZnyOCtzZJEeqHSPxwp9FzmB8_nCdo7i8XAD4WZ0mxRjbcy28ZYlvwiJg64xdJPa-BGMrk3dJ6VsN94KekXgew2kA2puk--EOenxrsqPzF8tunKRad9oRb8uz9aq12_9VFDbm-K4P9hSgnt-R9X8r_aGm1W7FfoaKYjKtFSN63JNBTFLDXXpQCdb1J2-1eHsZq4etB0VFgH-S-BBjjtnIOhafqk0Wl2xAKuVzDfnadOKLPRSAYbJErZkPoH_DH2PTwCscuoEjVsWyRBOPxvDJ8o75jPpwYXGzJARVmW_VifQzRG9c_oZnoSinIP9o83FAd9NMzxi6HiJMQGE5E6qnUkhTYurHnW3skXSUfl7RI2XbWprVf0ImjrrrkCMMGy9x0SObZz3aiGAhs3R9rrIlB0_IArDK9E299CucFyufC6BUcQWyN6BiuS7XT4JbNWdbAUHA0v-BEoi9H7FmhSIsOM45UZEy6F6vjBmWg8-Ls8JuyyV1mWboOPbKcHVQGJrubezakw99VXn5Gm6xb5wHURr9FB7KWRe-T0TOqU7cQENvghVR-jIY4k7s0I7SpDxz8u-ZaApEdOcFzhiw6IlQtqpZB_KuuKDKz1tF2J50']], cert=('localhost.crt', 'localhost.key'), verify='RootCA.crt')
    
    @patch('requests.post')
    def test_swap_cert(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        assert api_requests.swap_cert(1,2)
    
    @patch('requests.post')
    def test_place_order(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        assert api_requests.place_order()

    @patch('requests.post')
    def test_send_service_worker_mails(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        api_requests.send_service_worker_mails('a')
        mock_post.assert_called_with('https://localhost:25565/service-worker/receive-mails', json='a', cert=('localhost.crt', 'localhost.key'), verify='RootCA.crt')