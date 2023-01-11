from distribution.blockchain.blockchain import Blockchain_Config, Blockchain_Transaction_Handler, Wallet_Info
import time
import json
import config as sysconfig
from utils.log import log
config = Blockchain_Config()

wallets =[]
bt_handler = Blockchain_Transaction_Handler(config=config)
def test_wallet_start_and_detect():

    while bt_handler.wallet_status == Blockchain_Transaction_Handler.STATUS_WALLET_UNKNOWN:
        time.sleep(1)

def test_get_token_wallets():
    global wallets
    wallets = bt_handler.get_token_wallets()
    
    for wallet in wallets:
        log.info('ID: {0} Type:{1} Total:{2} Spenable:{3} Pending:{4} Unspent coins:{5}'.format(wallet.wallet_id, wallet.wallet_type, wallet.total_balance, wallet.spendable_balance, wallet.pending_balance, wallet.qty_unspent_coins))


def test_get_sync_status():
    bt_handler.login_wallet(fingerprint=sysconfig.TOKEN_WALLET_FINGERPRINT)
    bt_handler.get_sync_status()


def check_tranaction_info():
    transaction_info = bt_handler.get_transaction_data( wallet=wallets[0], transaction_id='0x9cfbb0ff8bd8f6d422ca34e7ebc5506e9097136cb45743c7e1bd4355a5007cc5')
'''
def test_send_transaction():
    tranaction_info = bt_handler.send_transaction( wallets[0],  'txch179yujvhdhcpg9433geq5j7v3y6nmavdzmvm3mpruddflnckrchnqxlannw', 1, 0)
'''
def test_all_blockchain():
    test_wallet_start_and_detect()
    test_get_sync_status()
    test_get_token_wallets()  # This must be run
    check_tranaction_info()