from utils import bech32m
from utils.byte_types import hexstr_to_bytes
from utils.data_primatives import YMS_Configs

def test_bech32m_encoding():
    assert bech32m.encode_puzzle_hash(hexstr_to_bytes('f149c932edbe0282d631464149799126a7beb1a2db371d847c6b53f9e2c3c5e6'), 'txch10') == 'txch10179yujvhdhcpg9433geq5j7v3y6nmavdzmvm3mpruddflnckrchnq85nd05'
    assert bech32m.encode_puzzle_hash(hexstr_to_bytes('f149c932edbe0282d631464149799126a7beb1a2db371d847c6b53f9e2c3c5e6'), 'txch10') != ''

def test_bech32m_decoding():     
    assert str(bech32m.decode_puzzle_hash('txch10179yujvhdhcpg9433geq5j7v3y6nmavdzmvm3mpruddflnckrchnq85nd05')) == 'f149c932edbe0282d631464149799126a7beb1a2db371d847c6b53f9e2c3c5e6'

dummy_data = {'cheese' : '23'}

def test_configs_save():
    test_configs = YMS_Configs('./tests/dummy_data/dummy_configs.json')
    test_configs.config_data = dummy_data
    test_configs.save_to_json()
