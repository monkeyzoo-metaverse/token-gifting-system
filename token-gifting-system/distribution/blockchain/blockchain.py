import os
import time
import asyncio
import subprocess
import json
from utils.log import log
from utils.port_scan import port_scan


class Blockchain_Config:

    RPC_WALLET_COMMAND = ['chia', 'rpc', 'wallet']

    def __init__(self):
        log.info( 'Initiaising Block Chain config' )
        self.wallet_fingerprint = ""
        self.XCH_wallet_id = ""
        self.token_wallet_id = ""
        self.wallet_ip = "127.0.0.1" # Local wallet IP address
        self.wallet_port = 9256  # Default chia wallet port
        self.wallet_start_command = 'chia start wallet'
        self.wallet_timeout = 100
        self.is_logged_in = False
        self.is_synced = False

    def set_wallet_fingerprint(self, fingerprint):
        self.wallet_fingerprint = str(fingerprint)

    def get_wallet_fingerprint(self):
        return self.wallet_fingerprint

class Wallet_Info:

    def __init__(self):
        self.wallet_type = ""
        self.wallet_id = 0
        self.total_balance = 0
        self.pending_balance = 0
        self.spendable_balance = 0
        self.XCH_source = False
        self.qty_unspent_coins = 0
    
    def get_wallet_id(self):
        return self.wallet_id
    
    def get_spendable_balance(self):
        return self.spendable_balance
    
    def dump_info(self):
        log.info("""
        Wallet Info:
        Wallet Type: {0}
        Wallet ID: {1}
        Total Balance: {2} Mojo
        Pending Balance: {3} Mojo
        Spendable Balance: {4} Mojo
        Is XCH Source: {5} 
        Number of Unspent Coins {6}
        """.format(
            self.wallet_type,
            self.wallet_id,
            self.total_balance,
            self.pending_balance,
            self.spendable_balance,
            self.XCH_source,
            self.qty_unspent_coins ))

class Blockchain_Transaction_Handler:

    STATUS_WALLET_READY = 5
    STATUS_WALLET_SYNC = 4
    STATUS_WALLET_ERROR = 3
    STATUS_WALLET_UNKNOWN = 2
    STATUS_WALLET_AVAIABLE = 1

    RPC_CALL = ""

    def __init__(self, config):
        log.info('Initisising Block chain Handler')
        self.chia_config = config
        self.wallet_status = self.STATUS_WALLET_UNKNOWN
        asyncio.run(self.search_for_wallet(self.chia_config.wallet_timeout))


    async def search_for_wallet(self, timeout=10):
        try:
            start_time = time.time()
            log.info('searching for chia wallet')
            port_status = port_scan(self.chia_config.wallet_ip, self.chia_config.wallet_port)  # Check for inital socket available
            if (port_status == False):
                log.info('Wallet not found issing wallet start command')
                os.system(self.chia_config.wallet_start_command)  
                time.sleep(3)
                while( not port_status):
                    port_status = (port_scan(self.chia_config.wallet_ip, self.chia_config.wallet_port))
                    log.info('waiting for wallet!!')
                    if (time.time() - start_time >= timeout):  # Check for timeout
                        raise Exception("NO WALLET FOUND::Wallet Port not found at IP: {0} Port: {1} after {2}s". format(self.chia_config.wallet_ip, self.chia_config.wallet_port, timeout))
                    time.sleep(3)
            log.info('Found Wallet updateing status')
            self.wallet_status = self.STATUS_WALLET_AVAIABLE
            return True

        except Exception as e:
            log.error(e)
            return False


    def _commandline(self, wallet_info, end_point, json_args=None):
        try:
            log.info('Generating wallet RPC command line call')
            end_point = [end_point]
            command_struct = Blockchain_Config.RPC_WALLET_COMMAND

            if json_args is not None:
                log.info("command call:{0}".format(command_struct + end_point + [json.dumps(json_args)]))
                result = subprocess.run(command_struct + end_point + [json.dumps(json_args)], stdout=subprocess.PIPE)

            else:
                log.info("command call No Args:{0}".format(command_struct + end_point))
                result = subprocess.run(command_struct + end_point , stdout=subprocess.PIPE)

            if result.stderr is not None :
                raise Exception('error from command line call {0}'.format(result.stderr))
            '''
            if (result.stdout[0:15] == 'Request failed: '):
                log.error(result.stout[16:])
                result.stderr = result.stdout[16:]
                raise Exception('Wallet reports transaction fail')
            '''
            try:
                unprocessed_json = result.stdout
                error_result = result.stderr
                log.info(unprocessed_json)
                #log.warning(error_result)
                ret = json.loads(unprocessed_json)
            
            except ValueError:
                return False, 'Unable to proccess json {0}'.format(unprocessed_json)
            log.info('Command responce{0}'.format(ret))
            return ret


        except Exception as e:
            log.error(e)
            return False, result.stderr

    def login_wallet(self, fingerprint):
        try:    
            logged_in_fingerprint = self._commandline(0, 'get_logged_in_fingerprint')
            if logged_in_fingerprint['fingerprint' ] == fingerprint:
                log.info('Wallet already logged in')
                self.chia_config.is_logged_in = True
                return True
            ret = self._commandline(0, 'log_in', {'fingerprint': fingerprint})
            if ret['success'] == True:
                log.info('Logged into wallet with Fingerprint:{0}'.format(fingerprint))
                self.wallet_status = self.STATUS_WALLET_AVAIABLE
                self.chia_config.is_logged_in = True
            else:
                raise Exception('Problem logginf into wallet with fingerprint:{0}'.format(fingerprint))
        
        except Exception as e:
            log.error(e)
            self.wallet_status = self.STATUS_WALLET_ERROR
            return False
        
    # retruns a list of Wallet_Info for each token of wallet type    
    def get_token_wallets(self):
        try:
            wallets = []
            wallets_info = self._commandline(0 , 'get_wallets')
            log.info('Token Wallets List:{0}'.format(wallets_info))
            if not wallets_info['success']:
                raise Exception('problem with getting info on available wallets')
        
            for wallet in wallets_info['wallets']:
                this_wallet = Wallet_Info()
                this_wallet.wallet_id = wallet['id']
                this_wallet.wallet_type = wallet['name']
                json_args = {"wallet_id": this_wallet.wallet_id}
                balance_info =  self._commandline(0 , 'get_wallet_balance', json_args=json_args)
                this_wallet.total_balance = balance_info['wallet_balance']['confirmed_wallet_balance']
                this_wallet.spendable_balance = balance_info['wallet_balance']['spendable_balance']
                this_wallet.pending_balance = balance_info['wallet_balance']['unconfirmed_wallet_balance']
                this_wallet.qty_unspent_coins = balance_info['wallet_balance']['unspent_coin_count']
                if balance_info['wallet_balance']['wallet_type'] == 0:
                    this_wallet.XCH_source = True
                else:
                    this_wallet.XCH_source = False

                wallets.append(this_wallet)
            return wallets
        
        except Exception as e:
            log.error(e)
            self.wallet_status = self.STATUS_WALLET_ERROR
            return False

    def get_sync_status(self):
        logged_fingerprint = self._commandline(0, 'get_logged_in_fingerprint')
        if logged_fingerprint['fingerprint']== self.chia_config.wallet_fingerprint:
            self.chia_config.is_logged_in = True
        if self.chia_config.is_logged_in is False:
            log.info('Wallet not logged in')
            return False
        ret = self._commandline(0, 'get_sync_status')
        log.info('Wallet_ sync status {0}'.format(ret))
        return ret

    def send_transaction(self, wallet, address, amount, fee):
        transaction_dict = {'wallet_id': wallet.wallet_id, 'amount': amount, 'inner_address': address, 'fee': fee}
        ret = self._commandline(0, 'cat_spend', transaction_dict)
        log.info(ret)
        return ret

    def get_transaction_data(self, wallet, transaction_id):
        transaction_id_dict = {'wallet_id': wallet.wallet_id, 'transaction_id': transaction_id}
        ret = self._commandline(0, 'get_transaction', transaction_id_dict)
        return ret

        








