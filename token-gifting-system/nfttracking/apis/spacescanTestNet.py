from .apis_common import api
import requests
from .. import config
import logging


if config.testnet is True:
    blockchain = 'txch10'
else:
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
            return status, owner_data[0]['minter_hash']

        else:
            logging.error('Unexpected responce from {0}'.format(api_plugin.name))
            return False, None

    except KeyError:
        logging.exception('Data entries not found in responce from {0}'.format(api_plugin.name))
        return False, None
