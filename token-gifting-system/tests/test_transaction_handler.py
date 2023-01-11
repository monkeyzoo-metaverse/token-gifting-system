from utils.log import log
from distribution.transaction_handler import Transaction_Handler 
from utils.data_primatives import Transaction_Data
from utils.task_requests import Transaction_task_request

trans_data_not_enough_fee = Transaction_Data(destination_address='txch179yujvhdhcpg9433geq5j7v3y6nmavdzmvm3mpruddflnckrchnqxlannw', amount=9, fee=9999999999916)
trans_data_not_enough_token = Transaction_Data(destination_address='txch179yujvhdhcpg9433geq5j7v3y6nmavdzmvm3mpruddflnckrchnqxlannw', amount=9999999999916, fee=9)
trans_data_good = Transaction_Data(destination_address='txch179yujvhdhcpg9433geq5j7v3y6nmavdzmvm3mpruddflnckrchnqxlannw', amount=6, fee=9)
trans_data_bad_address = Transaction_Data(destination_address='txch179', amount=6, fee=9)
trans_template_good = Transaction_Data()
trans_template_bad = Transaction_Data()
trans_task = Transaction_task_request()
trans_handler = Transaction_Handler()

trans_handler.set_wallets_to_use(xch_wallet_id=trans_handler.blockchain_conf.XCH_wallet_id, token_wallet_id=trans_handler.blockchain_conf.token_wallet_id)

def checking_funds(transaction_data):
    trans_task.set_transaction_data(transaction_data)
    trans_task.set_transaction_task(trans_task.TASK_CHECK_FUNDS_AVAILABLE)
    trans_handler.set_new_task(trans_task)
    trans_handler.exec_task()

def send_transaction(transaction_data):
    checking_funds(transaction_data=transaction_data) #  This will set transaction to ready
    transaction_data.dump_info()
    trans_task.set_transaction_data(transaction_data)
    trans_task.set_transaction_task(trans_task.TASK_SEND_TRANSACTION)
    trans_task.dump_info()
    trans_handler.set_new_task(trans_task)
    trans_handler.exec_task()

def check_transaction_status(transaction_data):
    transaction_data.dump_info()
    trans_task.set_transaction_data(transaction_data)
    trans_task.set_transaction_task(trans_task.TASK_GET_STATUS)
    trans_task.dump_info()
    trans_handler.set_new_task(trans_task)
    return trans_handler.exec_task()

def test_create_transaction():
    global trans_data, trans_task
    # Set token wallet as XCH wallet
    
    #trans_handler.xch_wallet.dump_info()
    #trans_handler.token_wallet.dump_info()
    checking_funds(transaction_data=trans_data_not_enough_token)
    assert trans_data_not_enough_token.get_status() == Transaction_Data.TRANSACTION_INSUFICIENT_FUNDS_TOKEN
    checking_funds(transaction_data=trans_data_not_enough_fee)
    assert trans_data_not_enough_fee.get_status() == Transaction_Data.TRANSACTION_INSUFICIENT_FUNDS_XCH
    checking_funds(transaction_data=trans_data_good)
    assert trans_data_good.get_status() == Transaction_Data.TRANSACTION_READY

def test_send_bad_transaction():
    log.info('SENDING POORLY FORMED ADDRESS')
    send_transaction(transaction_data=trans_data_bad_address)
    log.info('transaction status: {0}'.format(trans_data_bad_address.get_status()))
    # Make sure that trasaction fails on poorly formed address
    assert trans_data_bad_address.get_status() == Transaction_Data.TRANSACTION_FAIL

def test_good_transaction():
    log.info('SENDING GOOD TRANSACTION')
    checking_funds(transaction_data=trans_data_good)
    send_transaction(transaction_data=trans_data_good)
    log.info('transaction status: {0}'.format(trans_data_good.get_status()))
    trans_data_good.dump_info()
    # Make sure that trasaction fails on poorly formed address
    assert trans_data_good.get_status() == Transaction_Data.TRANSACTION_SUBMITTED

def test_transaction_status_update():
    trans_template_good.transactionId = '0x2db5fde04f651b3d12cb0c1bdf28d2ca0c593284bb9688682183a15029197c56'
    assert check_transaction_status(transaction_data=trans_template_good) == True
    trans_template_good.dump_info()
    assert trans_template_good.get_status() == Transaction_Data.TRANSACTION_COMPLETE

    

    trans_template_bad.transactionId = '0x976324962394629736'
    assert check_transaction_status(transaction_data=trans_template_bad) == False 
    assert trans_template_bad.get_status() == Transaction_Data.TRANSACTION_FAIL
    #check_transaction_status(transaction_data=trans_data_good)


def transaction_handler():
    test_create_transaction()
    test_send_bad_transaction()
    test_good_transaction()
    # test_transaction_status_update()
