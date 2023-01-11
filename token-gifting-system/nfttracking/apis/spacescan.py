from .apis_common import api
from utils.bech32m import encode_puzzle_hash
from utils.byte_types import hexstr_to_bytes
import requests
import logging



blockchain = 'xch'

api_plugin = api('SpaceScan NFT')
api_plugin.set_rooturl('https://api2.spacescan.io/v0.1/{0}/nft/'.format(blockchain))


def check_connection(timeout=10000):  # Returns a bool depenant on theif there is a 200 status code from the api
    logging.info('testing connection to {}'.format(api_plugin.name))
    reponse = requests.get(api_plugin.rootUrl)
    if reponse.status_code == 200:
        return True
    else:
        return False


def set_nft_id(encoded_id):
    logging.info('Setting NFT to search to {0}'.format(api_plugin.name + api_plugin.parameter))
    api_plugin.parameter = encoded_id


def get_raw():
    logging.info('get raw data from {0}'.format(api_plugin.name + api_plugin.parameter))
    response = requests.get(api_plugin.rootUrl + api_plugin.parameter)
    if response.status_code == 200:
        response_json = response.json()
        return True, response_json
    else:
        return False, None


def get_owner():  # Must return bool status , string owner address
    try:
        status, raw_json = get_raw()
        if status is True:
            owner_data = raw_json['data']
            return status, encode_puzzle_hash(hexstr_to_bytes('0x'+ owner_data[0]['owner_hash']), 'xch')

        else:
            logging.error('Unexpected responce from {0}'.format(api_plugin.name))
            return False, None

    except KeyError:
        logging.exception('Data entries not found in responce from {0}'.format(api_plugin.name))
        return False, None
