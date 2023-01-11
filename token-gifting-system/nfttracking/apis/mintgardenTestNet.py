from .apis_common import api
import requests
from utils.log import log


api_plugin = api('Mint Garden NFT (testnet)')
api_plugin.set_rooturl('https://api.testnet.mintgarden.io/nfts/')


def check_connection(timeout=10000):
    log.info('testing connection to {}'.format(api_plugin.name))
    reponse = requests.get(api_plugin.rootUrl)
    if reponse.status_code == 200:
        return True
    else:
        return False


def set_nft_id(encoded_id):
    log.info('Setting NFT to search to {0}'.format(api_plugin.name + api_plugin.parameter))
    api_plugin.parameter = encoded_id


def get_raw():
    log.info('get raw data from {0}'.format(api_plugin.name + api_plugin.parameter))
    response = requests.get(api_plugin.rootUrl + api_plugin.parameter)
    if response.status_code == 200:
        return True, response.json()
    else:
        return None


def get_owner_height():
    try:
        status, raw_json = get_raw()
        if status is True:
            owner_data = raw_json['owner_address']
            return owner_data['encoded_id']

        else:
            log.error('Unexpected responce from {0}'.format(api_plugin.name))
            return None

    except Exception:
        log.error('Data entries not found in responce from {0}'.format(api_plugin.name))
        return None


def get_owner():
    try:
        status, raw_json = get_raw()
        if status is True:
            owner_data = raw_json['owner_address']
            log.info('OWner address: {0}'.format(owner_data['encoded_id']))
            return owner_data['encoded_id']

        else:
            log.error('Unexpected responce from {0}'.format(api_plugin.name))
            return None

    except KeyError:
        log.error('Data entries not found in responce from {0}'.format(api_plugin.name))
        return False, None
