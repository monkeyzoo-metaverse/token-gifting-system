'''
task_helpers.py
Contains task helpers for creating the basic procedures 
'''

from utils.log import log
from task_manager.task_manager import Task_Manager_Task
from utils.data_primatives import NFT_Data, Ownership_Data, Transaction_Data
from utils.task_requests import DB_task_request, API_task_request, Transaction_task_request


def return_ownership_record_from_TMT(Task_manager_task):
    db_task_req = Task_manager_task.subtasks[len(Task_manager_task.subtasks)-1] # get the second subtask
    if db_task_req.get_record_data_object().get_is_blacklisted():
        log.warning('This NFT has been blacklisted no transactions can be performed from this record')
        return False
    return db_task_req.get_record_data_object()

def return_record_from_TMT(Task_manager_task):
    db_task_req = Task_manager_task.subtasks[len(Task_manager_task.subtasks)-1] # get the second subtask
    return db_task_req.get_record_data_object()

def create_task_get_all_transactions_by_nft_id(nft_id):
    new_task = Task_Manager_Task('Get all transactions by NFT_id: {0}'.format(nft_id))
    new_task.set_subsystems = [Task_Manager_Task.SUBSYSTEM_DB]
    get_transaction_records_tr = DB_task_request()
    get_transaction_records_tr.set_task_action(DB_task_request.TASK_READ_ALL_RECORDS)
    get_transaction_records_tr.set_record_data_object(record_data_obj=[]) # set as an empty list to fill with the raw database data to be reprocessed later
    get_transaction_records_tr.set_table_name(DB_task_request.TABLE_TO_ACCESS_YIELD_TRANSACTIONS)
    get_transaction_records_tr.set_fk_for_access("nft_id")
    get_transaction_records_tr.set_pk_index_to_access(nft_id)
    get_transaction_records_tr.check_task_ready()
    get_transaction_records_tr.dump_info()
    new_task.add_subtask(get_transaction_records_tr)
    return new_task

# Task to access database can aquire NFT record given the index number the wrap that with the reilvant ownership record
def create_task_get_ownership_record_from_db(nft_index):
    new_task = Task_Manager_Task('Update ownership NFT: {0}'.format(nft_index))
    new_task.set_subsystems = [Task_Manager_Task.SUBSYSTEM_DB]
    # setup nft record fetch
    log.info(' Creating get_nft_record Subtask')
    nft_data = NFT_Data(nft_index=nft_index)
    get_nft_record_task = DB_task_request()
    get_nft_record_task.set_task_action(DB_task_request.TASK_READ_SINGLE_RECORD)
    get_nft_record_task.set_record_data_object(record_data_obj=nft_data)
    get_nft_record_task.set_table_name(DB_task_request.TABLE_TO_ACCESS_NFT_INFO)
    get_nft_record_task.set_pk_index_to_access(get_nft_record_task.record_data_obj.get_nft_index())
    get_nft_record_task.check_task_ready()
    log.info('Adding subtask to task manager task')
    new_task.add_subtask(get_nft_record_task)
    log.info('Creaing get_ownership_record_subtask')
    # Add ownership wrapper
    ownership_data = Ownership_Data(nft_record=nft_data)
    # Create task request to get ownership data
    get_ownership_record_task = DB_task_request()
    get_ownership_record_task.set_task_action(DB_task_request.TASK_READ_SINGLE_RECORD)
    get_ownership_record_task.set_record_data_object(record_data_obj=ownership_data)
    get_ownership_record_task.set_table_name(DB_task_request.TABLE_TO_ACCESS_OWNERSHIP)
    # Setup access but the NFT_id column
    get_ownership_record_task.set_fk_for_access(get_ownership_record_task.get_colomn_labels()[1])
    get_ownership_record_task.set_pk_index_to_access(get_ownership_record_task.get_record_data_object().nft_record_index)
    get_ownership_record_task.check_task_ready()
    new_task.add_subtask(get_ownership_record_task)
    return new_task

def create_task_update_ownership_from_api(ownership_record):
    api_t_r = API_task_request()
    api_t_r.set_record_data_obj(ownership_record)
    api_t_r.set_task_action(api_t_r.TASK_GET_NFT_OWNER_SINGLE)
    new_task = Task_Manager_Task('Get ownership from api for: {0}'.format(ownership_record.get_nft_record().nft_name))
    new_task.set_subsystems = [Task_Manager_Task.SUBSYSTEM_API]
    new_task.add_subtask(api_t_r)
    return new_task

def create_admin_task(taskname='Default Admin'):
    new_task = Task_Manager_Task(taskname)
    new_task.set_subsystems([Task_Manager_Task.SUBSYSTEM_ADMIN])
    return new_task

def write_ownership_record_to_db(ownership_record):
    db_t_r = DB_task_request()
    db_t_r.set_task_action(DB_task_request.TASK_UPDATE_RECORD)
    db_t_r.set_record_data_object(record_data_obj=ownership_record)
    db_t_r.set_table_name(DB_task_request.TABLE_TO_ACCESS_OWNERSHIP)
    # Setup access but the NFT_id column
    db_t_r.set_fk_for_access(db_t_r.get_colomn_labels()[1])
    db_t_r.set_pk_index_to_access(db_t_r.get_record_data_object().nft_record_index)
    db_t_r.check_task_ready()
    db_t_r.dump_info()
    new_task = Task_Manager_Task('Updateing database record for {0}'.format(ownership_record.get_nft_record().nft_name))
    new_task.set_subsystems = [Task_Manager_Task.SUBSYSTEM_DB]
    # Add db to task manager task as a single task
    new_task.add_subtask(db_t_r)
    return new_task

def get_last_ownership_ledger_addition():
    db_t_r = DB_task_request()
    db_t_r.set_task_action(DB_task_request.TASK_READ_SINGLE_RECORD)
    db_t_r.set_table_name(DB_task_request.TABLE_TO_ACCESS_OWNERSHIP)

def write_ownerhip_update_to_ledger(ownership_record):
    pass

def create_new_tranaction_task():
    t_t_r = Transaction_task_request()
    tans_data = Transaction_Data()


def create_task_get_transaction_by_uuid(uuid):
    new_task = Task_Manager_Task('Get a transaction by uuid: {0}'.format(uuid))
    new_task.set_subsystems = [Task_Manager_Task.SUBSYSTEM_DB]
    get_transaction_records_tr = DB_task_request()
    get_transaction_records_tr.set_task_action(DB_task_request.TASK_READ_SINGLE_RECORD)
    get_transaction_records_tr.set_record_data_object(record_data_obj=Transaction_Data()) # set as an empty transaction record
    get_transaction_records_tr.set_table_name(DB_task_request.TABLE_TO_ACCESS_YIELD_TRANSACTIONS)
    get_transaction_records_tr.set_fk_for_access("transaction_uuid")
    get_transaction_records_tr.set_pk_index_to_access('"'+ uuid +'"') # " is required to wrap the uuid otherwise sqlite failes the query
    get_transaction_records_tr.check_task_ready()
    get_transaction_records_tr.dump_info()
    new_task.add_subtask(get_transaction_records_tr)
    return new_task

def create_task_get_all_transactions_by_status(status):
    log.info('creating task to get recod by status')
    new_task = Task_Manager_Task('Get all transactions by status:')
    log.info('set tasksubsystem')
    new_task.set_subsystems = [Task_Manager_Task.SUBSYSTEM_DB]
    log.info('create db request instance')
    get_transaction_records_tr = DB_task_request()
    get_transaction_records_tr.set_task_action(DB_task_request.TASK_READ_ALL_RECORDS)
    get_transaction_records_tr.set_record_data_object(record_data_obj=[]) # set as an empty list to fill with the raw database data to be reprocessed later
    get_transaction_records_tr.set_table_name(DB_task_request.TABLE_TO_ACCESS_YIELD_TRANSACTIONS)
    get_transaction_records_tr.set_fk_for_access("transaction_status")
    get_transaction_records_tr.set_pk_index_to_access(status)
    log.info('Checking task is ready to run')
    get_transaction_records_tr.check_task_ready()
    get_transaction_records_tr.dump_info()
    new_task.add_subtask(get_transaction_records_tr)
    log.info('Task object created')
    return new_task

def create_task_get_transaction_by_onchian_id(on_chain_transaction_id):
    new_task = Task_Manager_Task('Get a transaction by uuid: {0}'.format(on_chain_transaction_id))
    new_task.set_subsystems = [Task_Manager_Task.SUBSYSTEM_DB]
    get_transaction_records_tr = DB_task_request()
    get_transaction_records_tr.set_task_action(DB_task_request.TASK_READ_SINGLE_RECORD)
    get_transaction_records_tr.set_record_data_object(record_data_obj=Transaction_Data()) # set as an empty transaction record
    get_transaction_records_tr.set_table_name(DB_task_request.TABLE_TO_ACCESS_YIELD_TRANSACTIONS)
    get_transaction_records_tr.set_fk_for_access("transaction_id_onchain")
    get_transaction_records_tr.set_pk_index_to_access(on_chain_transaction_id)
    get_transaction_records_tr.check_task_ready()
    get_transaction_records_tr.dump_info()
    new_task.add_subtask(get_transaction_records_tr)
    return new_task

def create_task_write_new_transaction_record_to_db(transaction_data):
    new_task = Task_Manager_Task('starting new transaction uuid: {0}'.format(transaction_data.uuid))
    new_task.set_subsystems = [Task_Manager_Task.SUBSYSTEM_DB]
    get_transaction_records_tr = DB_task_request()
    get_transaction_records_tr.set_task_action(DB_task_request.TASK_CREATE_NEW_RECORD)
    get_transaction_records_tr.set_record_data_object(record_data_obj=transaction_data) # set as an empty transaction record
    get_transaction_records_tr.set_table_name(DB_task_request.TABLE_TO_ACCESS_YIELD_TRANSACTIONS)
    get_transaction_records_tr.set_fk_for_access("transaction_id")
    get_transaction_records_tr.set_pk_index_to_access(None)  # Setting this as NULL creates a new tranaction record with the next ID increament 
    get_transaction_records_tr.check_task_ready()
    get_transaction_records_tr.dump_info()
    new_task.add_subtask(get_transaction_records_tr)
    return new_task

def create_task_update_transaction_record_in_db(transaction_data):
    new_task = Task_Manager_Task('starting new transaction uuid: {0}'.format(transaction_data.uuid))
    new_task.set_subsystems = [Task_Manager_Task.SUBSYSTEM_DB]
    update_transaction_records_tr = DB_task_request()
    update_transaction_records_tr.set_task_action(DB_task_request.TASK_UPDATE_RECORD)
    update_transaction_records_tr.set_record_data_object(record_data_obj=transaction_data) # set as an empty transaction record
    update_transaction_records_tr.set_table_name(DB_task_request.TABLE_TO_ACCESS_YIELD_TRANSACTIONS)
    update_transaction_records_tr.set_fk_for_access("transaction_uuid")
    update_transaction_records_tr.set_pk_index_to_access(update_transaction_records_tr.get_record_data_object().uuid)  # Setting this as NULL creates a new tranaction record with the next ID increament 
    update_transaction_records_tr.check_task_ready()
    update_transaction_records_tr.dump_info()
    new_task.add_subtask(update_transaction_records_tr)
    return new_task










