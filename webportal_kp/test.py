from unittest import TestCase 
from unittest.mock import patch, Mock
import web_server
from datetime import datetime, timedelta, timezone
from os import urandom
import time


class API_TEST(TestCase):
   
    @patch('requests.post')
    def test_create_hist_data(self, mock_handler):
        res = Mock()
        res.return_value = True
        res.status_code = 200
        mock_handler.return_value = res
        #test_data = {"id": "875e85c2-fb32-4de3-bd2f-bb7b3b6da423","date": "736e85c2-fb32-ff1f-bd2f-db7b4b6dc4ff", "iban": 123,
        #                                                        "state": 'state', "city": 'stadt',
        #                                                        "zip_code": '55555',
        #                                                        "address": 'Straße 3', "em_id": "aaae85c2-fb32-3de3-4444-236416da423"}
        assert web_server.create_msb_contract('test','test','test','test','test','test','test','test')
    @patch('requests.post')
    def test_create_msb_ems(self, mock_post):
        class em:
            em_consumption = '0778cde5-eb5b-42f2-9919-26f918b100fa'
            hist_id = 'a97d333e-b425-415e-b427-2fe75aadcb14'
            _id = 'cf9e4daa-6c62-4e48-affd-3da3bb758118'
        tmp = em()
        web_server.create_msb_ems(tmp)
        mock_post.assert_called_with('https://localhost:5000/new-em/', json={'consumption': '0778cde5-eb5b-42f2-9919-26f918b100fa', 'hist_id': 'a97d333e-b425-415e-b427-2fe75aadcb14', 'em_id': 'cf9e4daa-6c62-4e48-affd-3da3bb758118'}, cert=('localhost.crt', 'localhost.key'), verify='RootCA.crt')



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

    def test__update_account_data(self):
        assert not web_server._update_acc_data(None)

    def test__update_contract_data(self):
        assert web_server._update_contract_data(None)

    @patch('web_server.db_elmo_handler.get_Em_by_id')
    @patch('web_server.db_hist_handler.get_HistData_by_id')
    def test_get_hist_gram(self, mock_a, mock_b):
        mock_b.return_value = {"hist_id": "aaae85c2-fb32-3de3-4444-236416da423"}
        mock_a.return_value = "736e85c2-fb32-ff1f-bd2f-db7b4b6dc4ff"
        assert web_server.get_hist_data("fbdd-c02f-ac5e-hd3") if web_server.get_hist_data('c21dcc1a-a768-4c06-bd18-7d477c45a3e7') else '875e85c2-fb32-4de3-bd2f-bb7b3b6da423'

    @patch('web_server.db_acc_handler.get_account_by_id')
    def test_session(self, mock_a):
        mock_a.return_value = 1
        x : urandom(10) + time.sleep(1) = "736e85c2-fb32-ff1f-bd2f-db7b4b6dc4ff"
        assert  web_server.check_session(urandom(5)) == web_server.check_session(urandom(len(x[2:4:-1])))