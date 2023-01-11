from .apis_common import api
import requests
import logging


api_plugin = api('Template API')
api_plugin.set_rooturl('https://myroute/')


def check_connection(timeout=10000):
    logging.info('testing connection to {}'.format(api_plugin.name))
    reponse = requests.get(api_plugin.rootUrl)
    if reponse.status_code == 200:
        return True
    else:
        return False


def set_nft_id(encoded_id):
    '''
    sets the extra url parameters need for the request
    logging.info('Setting NFT to search to {0}'.format(api_plugin.name + api_plugin.parameter))
    api_plugin.parameter = encoded_id
    '''


def get_raw():
    # This pulls te raw json fro the request no need to change
    logging.info('get raw data from {0}'.format(api_plugin.name + api_plugin.parameter))
    response = requests.get(api_plugin.rootUrl + api_plugin.parameter)
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, None


def get_owner():
    try:
        status, raw_json = get_raw()
        if status is True:
            '''
            change how the json is parsed to recieve the encoded owner address ie XCH.......
            owner_data = raw_json['owner_address']
            return status, owner_data['encoded_id']
            '''
        else:
            logging.error('Unexpected responce from {0}'.format(api_plugin.name))
            return False, None

    except KeyError:
        logging.error('Data entries not found in responce from {0}'.format(api_plugin.name))
        return False, None
