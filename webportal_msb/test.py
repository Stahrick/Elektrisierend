from unittest import TestCase 
from unittest.mock import patch, Mock
import web_server
import api_requests
from datetime import datetime

class API_TEST(TestCase):
    @patch('requests.post')
    @patch('datetime.datetime')
    def test_send_registration_mail(self, mock_datetime, mock_post):
        api_requests.send_registration_mail('123')
        mock_response = Mock()
        mock_response.status_code = 200
        mock_now = datetime(2023, 12, 9, 12, 0, 0)  # Set your desired datetime

        # Set the return value of datetime.now() to the mock datetime
        mock_datetime.now.return_value = mock_now
        mock_datetime.timedelta = datetime.timedelta(days=2)
        # Set the return value of requests.post to the mock response
        mock_post.return_value = mock_response
        mock_post.assert_called_with(url='https://localhost:25565/service-worker/receive-mails', json=[['Registration-Code for meter[123] installation', 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJtc2IiLCJhdWQiOiIxMjMiLCJleHAiOjE3MDIzMDU5MzEsInV1aWQiOiIxMjMiLCJjb2RlIjoiQUM4RmdFMnd2VzNubFE9PSIsInVybCI6Imh0dHA6Ly8vbWV0ZXIifQ.AE2Elf70QgQ_Cs48xUVfwwyaWkWN0liImSWxCa_2V7QPTxhjKsRck_vFsbkrIrI6RPgC5NmOCng0htZu7dU1tRfsMu5F_ubrIKcx4pR-YYVuucKIpBCOah6TbhAg6u6y2ECCWsALX8AlSrZjc8i1QEk7lhzZWiCvmMSMEDZTdYNWZKJfgWWySoe2MLQOXiEzFzwtw-hHSCQrp8eLbzsrS2fHJfJN1QnsQZh2-v0L1GdMaFxFY-niylCcJVi5B3oduQVLthq8Ac30QaeGv0sVwA49JWNSkphOPoE7B9Wvc5pO82RHIvkQsVJ2Qfd_oi0XREBvbuINeomsucALttDLf88j_tfn6fe4f2c8r_F-r-7Dpmq6miV9O2ETotQAoPIe3z6kv5HNWX9ccJ-CIhu-XVIKAAXnr23jdrTLpnTaex1lumherE0muYopXGYNKL3809MeGih2NOmFDnWLvyTNEQsAOuzr-13BN7SUwUgpfFZvvKa7vrZZDwbIFy5yjtbhhuParBUUEXYKvzMUY9L0jlj5y_GubdujvWdBFTYi12YEWf3eASdRc3W3XrxLNZ9Avbu3yv0AYmA2br1LlXhhSnE90HRPPrl-2YLO6lqKfav2NtK-74sDuUbexryjL1HI8ItO2HXPewaXm-R26wnr3X1fVNXRsvX0SyCWR5JoCxM']])