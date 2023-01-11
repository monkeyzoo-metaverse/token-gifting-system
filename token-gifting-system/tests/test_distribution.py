from utils.log import log
from utils.data_primatives import Transaction_Data
from distribution.distribution import disrubtior
from task_manager.task_manager import Taskmanager
import tests.configs_for_tests
import time
tm = Taskmanager()

dist = disrubtior(task_manager=tm)

temp_destination_address = "TXCH10DAVE"
temp_amount = 0.0
new_transaction = Transaction_Data(destination_address=temp_destination_address, amount=temp_amount)

test_nft_index = 1

def test_get_ownership_record():
    log.info('starting get owner test')
    dist.get_ownership_record_from_db(test_nft_index)
    pass

def test_get_tranaction_records():
    dist.get_all_transactions_by_nft_id(test_nft_index)

def test_check_for_incomplete_tranactions():
    dist.get_all_transactions_by_nft_id(test_nft_index)
    incomplete_list = dist.check_for_incomplete_tranactions()
    log.info(incomplete_list)
    dist.update_taransaction_list_status(incomplete_list)
    incomplete_list = dist.check_for_incomplete_tranactions()
    for trans in incomplete_list:
        log.info(trans.dump_info())

def submit_transaction_to_blockchain(transaction_data):
    return dist.submit_transaction(transaction_data)

def test_get_transaction_by_uuid():
    transdata = dist.get_transaction_from_db_by_uuid(uuid=configs_for_tests.TRANSACTION_RECORD_1_UUID)
    transdata.dump_info()


def update_transaction_status():
    trans_data = dist.get_transaction_from_db_by_uuid(uuid=configs_for_tests.TRANSACTION_RECORD_2_UUID)
    dist.get_transaction_status_from_blockchain(transaction_data=trans_data)
    trans_data.dump_info()
    assert trans_data.status == Transaction_Data.TRANSACTION_COMPLETE
    #update as a new uuid
    dist.update_transaction_db_record(transaction_record=trans_data)


def test_start_next_transaction():
    test_get_transaction_by_uuid()
    xch_coins, token_coins = dist.get_number_of_coins()

    if int(xch_coins) <= 0 :
        log.info('out of xch')
        return
    if int(token_coins) <= 0 :
        log.info('out of tokens')
        return
    
    log.info('number of coins xch:{0} tokens:{1}'.format(xch_coins, token_coins))
    gift_transaction_record = dist.create_new_gift_transaction(dist.ownership_record)
    log.info('token available: {0} XCH Avaiable: {1}'.format(dist.transaction_handler.token_wallet.get_spendable_balance(), dist.transaction_handler.xch_wallet.get_spendable_balance()))
    this_trans = submit_transaction_to_blockchain(gift_transaction_record)
    gift_transaction_record.dump_info()
    assert this_trans != False
    update_transaction_status()

def test_begin_new_transaction_cycle():
    nft_index_list=[]
    for index in range(1,11): # For the 10 testnfts listed on the database
        nft_index_list.append(index)
    
    dist.ready_new_transactions_in_db(number_of_transactions=10, nft_index_list=nft_index_list)
    dist.auto_mode = True
    while dist.auto_mode == True: 
        dist.distribution_tick()
        time.sleep(1)
    








