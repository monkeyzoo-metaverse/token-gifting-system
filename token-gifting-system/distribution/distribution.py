from utils.log import log
from utils.task_requests import Task_Status
from utils.data_primatives import Transaction_Data
from distribution.transaction_handler import Transaction_Handler 
from utils.task_requests import Transaction_task_request
from utils.machine_states import State
from task_manager.task_helpers import create_admin_task, create_task_get_ownership_record_from_db, return_ownership_record_from_TMT, create_task_get_all_transactions_by_nft_id, return_record_from_TMT, create_task_get_transaction_by_uuid, create_task_get_all_transactions_by_status, create_task_write_new_transaction_record_to_db, create_task_update_transaction_record_in_db
import datetime
import config

class disrubtior:

    def __init__(self, task_manager):
        self.status = Task_Status.STATUS_CREATED
        self.current_day = datetime.datetime.now()
        self.auto_mode = False
        self.task_manager = task_manager
        self.last_cycle_complete = 0
        self.ownership_record = 0
        self.transaction_records = []
        self.current_transaction_record = 0 
        self.current_task_uuid = 0
        self.current_task_record_index = None
        self.update_state = State.STATE_FETCH_DB_ONWERSHIP_RECORD
        self.transaction_handler = Transaction_Handler()
        self.transaction_handler.set_wallets_to_use(xch_wallet_id=self.transaction_handler.blockchain_conf.XCH_wallet_id, token_wallet_id=self.transaction_handler.blockchain_conf.token_wallet_id)
    
    def get_ownership_record_from_db(self, nft_index, start_time=None):
        task = create_task_get_ownership_record_from_db(nft_index=nft_index)
        task.task_complete_callback = self.done_ownership_record_get
        if start_time == None:
            self.task_manager.execute_task(task)

            if self.done_ownership_record_get(task.get_task_uuid(), task_obj=task) is False:
                return False
        else:
            task.set_start_time(start_time) # start in 10 seconds
            self.task_manager.append_task_list(task)

    def get_transaction_from_db_by_uuid(self, uuid, start_time=None):
        task = create_task_get_transaction_by_uuid(uuid)
        self.task_manager.execute_task(task)
        return return_record_from_TMT(task)
        pass

    def get_transaction_from_db_by_onchain_transaction_id(self, transaction_id, start_time=None):
        pass

    def get_all_transactions_by_nft_id(self, nft_id, start_time=None):
        task = create_task_get_all_transactions_by_nft_id(nft_id=nft_id)
        task.task_complete_callback = self.done_get_transactions_by_nft_id
        if start_time == None:
            self.task_manager.execute_task(task)
            self.done_get_transactions_by_nft_id(task.get_task_uuid(), task_obj=task)
        else:
            task.set_start_time(start_time) # start in 10 seconds
            self.task_manager.append_task_list(task)

    def get_transactions_by_status(self, status, start_time=None):
        log.info('getting records by status')
        task = create_task_get_all_transactions_by_status(status=status)
        log.info('task created')
        task.task_complete_callback = self.done_get_transactions_by_status
        if start_time == None:
            log.info('execute task manager task')
            self.task_manager.execute_task(task)
            self.done_get_transactions_by_status(task.get_task_uuid(), task_obj=task)
        else:
            task.set_start_time(start_time) # start in 10 seconds
            self.task_manager.append_task_list(task)

    def done_ownership_record_get(self, task_uuid, task_obj=None):
        log.info('Callback from Task Manager for task {0}'.format(task_uuid))
        # This is the if the task has been completed emidatly 
        if task_obj:
            if task_obj.status == Task_Status.STATUS_COMPLETE:
                log.info('Processing completed task')
                self.ownership_record = return_ownership_record_from_TMT(task_obj)
                if self.ownership_record is False:
                    log.warning('NFT record black listed')
                    return False
                log.info('set dist owner record as {0}'.format(self.ownership_record))

    def done_get_transactions_by_nft_id(self, task_uuid, task_obj=None):
        log.info('Callback from Task Manager for task {0}'.format(task_uuid))
        transactions = []
        if task_obj:
            if task_obj.status == Task_Status.STATUS_COMPLETE:
                log.info('Processing completed task')
                for record in return_record_from_TMT(task_obj):
                    trans_r = Transaction_Data()
                    trans_r.populate_from_database_record(record)
                    trans_r.dump_info()
                    self.transaction_records.append(trans_r)

                log.info('set uncomplete transaction record as {0}'.format(self.transaction_records))
    
    def done_get_transactions_by_status(self, task_uuid, task_obj=None):
        log.info('Callback from Task Manager for task {0}'.format(task_uuid))
        transactions = []
        if task_obj:
            if task_obj.status == Task_Status.STATUS_COMPLETE:
                log.info('Processing completed task')
                for record in return_record_from_TMT(task_obj):
                    trans_r = Transaction_Data()
                    trans_r.populate_from_database_record(record)
                    trans_r.dump_info()
                    self.transaction_records.append(trans_r)

                log.info('set uncomplete transaction record as {0}'.format(self.transaction_records))

    def check_for_incomplete_tranactions(self, submitted=True):
        incomplete_tranactions = []
        for transaction_record in self.transaction_records:
            if transaction_record.get_status() is not Transaction_Data.TRANSACTION_COMPLETE:
                incomplete_tranactions.append(transaction_record)
        
        return incomplete_tranactions

    def create_new_gift_transaction(self, ownership_record=None):
        if ownership_record:
            new_transaction = Transaction_Data(destination_address=ownership_record.current_owner_address, amount=(ownership_record.get_nft_record().nft_yield_value * config.MOJO_TO_TOKEN_MULTIPLIER), fee=config.DEFAULT_MOJO_FEE)
            new_transaction.nft_record_id = ownership_record.get_nft_record_index()
        else:
            log.info('creating empty tranaction')
            new_transaction = Transaction_Data()
        log.info('Transaction created UUID: {0}'.format(new_transaction.uuid))
        log.info('Writing new transaction record to database')
        write_transaction_task = create_task_write_new_transaction_record_to_db(transaction_data=new_transaction)

        if self.task_manager.execute_task(write_transaction_task):
            return new_transaction

        else:
            log.error('Tansaction not written to database do not excute!!!!')
            return False

    def update_transaction_db_record(self, transaction_record):
        update_tranaction_data_task = create_task_update_transaction_record_in_db(transaction_data=transaction_record)
        if self.task_manager.execute_task(update_tranaction_data_task):
            return True 

        else:
            log.error('Tansaction not written to database do not excute!!!!')
            return False

    def check_funds(self, trans_task):
        trans_task.set_transaction_task(trans_task.TASK_CHECK_FUNDS_AVAILABLE)
        self.transaction_handler.set_new_task(trans_task)
        return self.transaction_handler.exec_task()

    def submit_transaction(self, transaction_record=None):
        trans_tr = Transaction_task_request()
        if transaction_record:
            trans_tr.set_transaction_data(transaction_record)
        else:
            trans_tr.set_transaction_data(self.current_transaction_record)
        if not self.check_funds(trans_tr):
            if self.update_transaction_db_record(trans_tr.get_tranaction_data()): 
                log.info('Transaction Record updated on db')
            else:
                log.error('good tranaction didnt write to database')
                return False
            
            log.warning('Funds curretnly unavailable')
            return False

        trans_tr.set_transaction_task(trans_tr.TASK_SEND_TRANSACTION)
        self.transaction_handler.set_new_task(trans_tr)
        if self.transaction_handler.exec_task():  #  If transaction succesfully submitted
            self.current_transaction_record = trans_tr.transaction_data 
            if self.update_transaction_db_record(self.current_transaction_record): 
                log.info('Transaction Record updated on db')
            else:
                log.error('good tranaction didnt write to database')

            if transaction_record:
                return trans_tr.transaction_data
            else:
                return True

        else:
            return False  # If the transaction fails for any reason

    def get_number_of_coins(self):
        self.transaction_handler.update_wallets() # checks wallets on blockchain
        unspent_token_coins = self.transaction_handler.token_wallet.qty_unspent_coins
        unspent_xch_coins = self.transaction_handler.xch_wallet.qty_unspent_coins
        return unspent_xch_coins, unspent_token_coins

    def get_transaction_status_from_blockchain(self, transaction_data):
        # Not if transaction is canceled its transaction ID is removed completely
        if transaction_data.status == Transaction_Data.TRANSACTION_CREATED or transaction_data.status == Transaction_Data.TRANSACTION_READY:
            return True # Returns a true because there is no sumittion information at this point so would cause a trans fail due to non submittion

        trans_task_req = Transaction_task_request()
        trans_task_req.set_transaction_task(trans_task_req.TASK_GET_STATUS)
        trans_task_req.set_transaction_data(transaction_data=transaction_data)
        self.transaction_handler.set_new_task(trans_task_req)
        return self.transaction_handler.exec_task()

    def update_taransaction_list_status(self, transaction_list):
        for transaction_record in transaction_list:
            self.get_transaction_status_from_blockchain(transaction_data=transaction_record)
            self.update_transaction_db_record(transaction_record=transaction_record)

    def ready_new_transactions_in_db(self, number_of_transactions=0,nft_index_list=[]):
        try: 
            if len(nft_index_list) != number_of_transactions:
                raise ValueError("miss match between list of  nft ids and number of transactions")
            for nft_index in nft_index_list:
                if self.get_ownership_record_from_db(nft_index=nft_index) is False:
                    log.warning('NFT can not be actioned further')
                else:
                    self.create_new_gift_transaction(self.ownership_record)


        except TypeError as e:
            log.error(e)
            return False

    def set_auto_mode(self, task_uuid=None, task_obj=None):
        log.info('starting auto mode called from uuid: {0}'.format(task_uuid))
        self.ready_new_transactions_in_db(number_of_transactions=config.COLLECTION_MAX_NFT_INDEX, nft_index_list=config.COLLECTION_NFT_INDEXES)
        self.auto_mode = True

    def set_auto_start_task(self, start_time):
        admin_task = create_admin_task(taskname='Auto start dist')
        admin_task.set_start_time(start_time=start_time)
        admin_task.task_complete_callback = self.set_auto_mode
        self.task_manager.append_task_list(admin_task)



    def distribution_tick(self, status_only=False):
        try:
            log.debug('distributer tick')
            if not self.auto_mode:
                #log.info('Distributer auto mode not selected')
                return True

            self.transaction_handler.update_wallets()
            log.info('Wallet balances {0} {1}'.format(self.transaction_handler.xch_wallet.total_balance, self.transaction_handler.token_wallet.total_balance))
            if self.transaction_handler.token_wallet.total_balance <= config.MIN_ALLOWED_TOKEN_BALANCE or self.transaction_handler.xch_wallet.total_balance <= config.MIN_ALLOWED_XCH_BALANCE:
                raise Exception('Funds running low please issue more funds to distribution wallets') 
                # The above Prevents further transactions from runnin until the wallets have bee replenished

            #check for funds
            if self.transaction_handler.token_wallet.spendable_balance <= config.MIN_COIN_SIZE or self.transaction_handler.xch_wallet.spendable_balance <= config.MIN_COIN_SIZE:
                log.warning('Waiting for spendable balance to return')
                return True
            # Look to see if there are any transactions in the list to run
            if self.transaction_records == []:
                log.info('Getting new unsubmittted transactions from database')
                self.get_transactions_by_status(Transaction_Data.TRANSACTION_PENDING)
                self.get_transactions_by_status(Transaction_Data.TRANSACTION_CREATED)
                if self.transaction_records == []:
                    log.info('nothing to process exiting automode')
                    self.auto_mode = False
                    return  False  # Requires early exit of the next live causes a crash

            self.current_transaction_record = self.transaction_records.pop(0) # grab the first transaction record in the list
            if self.current_transaction_record.status == Transaction_Data.TRANSACTION_CREATED:
                log.info('submitting current transaction')
                self.submit_transaction()
                self.transaction_records.append(self.current_transaction_record)
            elif self.current_transaction_record.status == Transaction_Data.TRANSACTION_PENDING:
                log.info('checking status of current transaction record')
                self.get_transaction_status_from_blockchain(self.current_transaction_record)
                if self.current_transaction_record.status == Transaction_Data.TRANSACTION_COMPLETE:
                    self.update_transaction_db_record(self.current_transaction_record)
                else: 
                    self.transaction_records.append(self.current_transaction_record)

        except Exception as e:
            log.error(e)
            return False


    def count_tranaction_states(self):
        waiting = 0 
        submitted = 0
        for transactions in self.transaction_records:
            if transactions.get_status() == Transaction_Data.TRANSACTION_CREATED:
                waiting += 1
            if transactions.get_status() == Transaction_Data.TRANSACTION_PENDING:
                submitted += 1
        return waiting, submitted





'''
what needs to happen
finding transaction records to see if they have complete

'''

