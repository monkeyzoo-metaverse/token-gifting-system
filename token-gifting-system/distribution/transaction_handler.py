import config
from utils.log import log
from utils.task_requests import Transaction_task_request
from utils.data_primatives import Transaction_Data
from distribution.blockchain.blockchain import Blockchain_Config, Blockchain_Transaction_Handler


class Transaction_Handler:

    def __init__(self):
        self.transaction_task = 0
        self.transaction_uuid =''
        self.blockchain_conf = Blockchain_Config()
        self.blockchain_conf.wallet_fingerprint = config.TOKEN_WALLET_FINGERPRINT
        self.blockchain_conf.token_wallet_id= config.TOKEN_WALLET_ID
        self.blockchain_conf.XCH_wallet_id = config.XCH_WALLET_ID
        self.blockchain_h = Blockchain_Transaction_Handler(self.blockchain_conf)
        self.wallets_list = []
        self.xch_wallet = 0
        self.token_wallet = 0
        log.info('Starting or Status check of Chia walet RPC client')
        try:
            if self.blockchain_h.wallet_status != self.blockchain_h.STATUS_WALLET_AVAIABLE:
                raise Exception('Chia wallet client not found check installation and paths')
            
            

            self.blockchain_h.login_wallet(self.blockchain_conf.get_wallet_fingerprint())
        
        except Exception as e:
            log.error(e)
            return False
        
    def get_wallets(self):
        log.info('All token wallet details')
        self.wallets_list = self.blockchain_h.get_token_wallets()
    
    def get_token_wallet_by_id(self, id):
        try:
            log.info('Getting details for wallet id: {0}'.format(id))
            if self.wallets_list == []:
                self.get_wallets()
            for wallet in self.wallets_list:
                if wallet.wallet_id == id:
                    return wallet
            raise Exception('Wallet id:{0} not found in list of token wallets'.format(id))


        except Exception as e:
            log.error(e)
            return False
    
    def update_wallets(self):
        self.get_wallets()
        self.token_wallet = self.get_token_wallet_by_id(self.token_wallet.wallet_id)
        self.xch_wallet = self.get_token_wallet_by_id(self.xch_wallet.wallet_id)



    def set_wallets_to_use(self, xch_wallet_id, token_wallet_id):
        self.xch_wallet = self.get_token_wallet_by_id(xch_wallet_id)
        self.token_wallet = self.get_token_wallet_by_id(token_wallet_id)

    def set_new_task(self, task):
        try:
            if not isinstance(task, Transaction_task_request):  # Check to see if valid task type has been set
                raise Exception('task argument is not a vaid transaction task')
            if task.task == Transaction_task_request.TASK_GET_STATUS:
                if task.get_tranaction_data().transactionId != 0:
                    self.transaction_task = task
                    self.transaction_uuid = task.get_tranaction_data().uuid
                    return True

                else:
                    raise Exception('Transaction does not contain transaction ID')

            if not task.check_transaction_ready():
                raise Exception('Task is not ready for transaction handler')
            self.transaction_task = task
            self.transaction_uuid = task.get_tranaction_data().uuid
        
        except Exception as e:
            log.error(e)
            return False


    def exec_task(self):
        try:
            if self.transaction_task.task== Transaction_task_request.TASK_CHECK_FUNDS_AVAILABLE:
                log.info('Commencing Check available funds task')
                if self.transaction_task.transaction_data.amount > self.token_wallet.spendable_balance:
                    self.transaction_task.set_transaction_status(Transaction_Data.TRANSACTION_INSUFICIENT_FUNDS_TOKEN)
                    raise ValueError('Only {0} avaliable of {1} required in token wallet'.format(self.token_wallet.spendable_balance, self.transaction_task.transaction_data.amount ))
                if self.transaction_task.transaction_data.fee > self.xch_wallet.spendable_balance:
                    self.transaction_task.set_transaction_status(Transaction_Data.TRANSACTION_INSUFICIENT_FUNDS_XCH)
                    raise ValueError('Only {0} avaliable of {1} required in XCH wallet for fee'.format(self.token_wallet.spendable_balance, self.transaction_task.transaction_data.fee ))

                self.transaction_task.set_transaction_status(Transaction_Data.TRANSACTION_READY)
                return True

            elif self.transaction_task.task == Transaction_task_request.TASK_GET_STATUS:
                log.info("Commencing Get Transaction Status task")
                
                transaction_json = self.blockchain_h.get_transaction_data(
                    self.token_wallet,
                    self.transaction_task.transaction_data.transactionId
                    )

                if False in transaction_json:
                        raise Exception('Transaction UUID: {0} Failed get status'.format(self.transaction_task.transaction_data.uuid))
                
                if transaction_json['success']:
                        log.info('transaction info gain successfully from blockchain')
                        self.transaction_task.transaction_data.process_transaction_json(transaction_json=transaction_json)
                        return True

            elif self.transaction_task.task == Transaction_task_request.TASK_SEND_TRANSACTION:
                log.info('Commencing send transaction task')
                if self.transaction_task.transaction_data.get_status() == Transaction_Data.TRANSACTION_READY:

                    transaction_json = self.blockchain_h.send_transaction(
                        self.token_wallet,
                        self.transaction_task.transaction_data.destination_address,
                        self.transaction_task.transaction_data.amount,
                        self.transaction_task.transaction_data.fee
                        )
                    if False in transaction_json:
                        raise Exception('Transaction UUID: {0} Failed to send'.format(self.transaction_task.transaction_data.uuid))
                    
                    if transaction_json['success']:
                        self.transaction_task.set_transaction_status(Transaction_Data.TRANSACTION_SUBMITTED)
                        self.transaction_task.transaction_data.process_transaction_json(transaction_json=transaction_json)
                        return True
                    else:
                        raise Exception('Unknown Transaction Failure check returned json for more info')

                else:
                    raise ValueError('Transaction not at READY Status')
            else:
                raise Exception('Invalid Task call!!')

        except ValueError as e:
            log.warning(e)
            return False

        except Exception as e:
            log.error(e)
            self.transaction_task.set_transaction_status(Transaction_Data.TRANSACTION_FAIL)
            return False