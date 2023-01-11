from nfttracking.api_handler import API_Handler
from db.db import DB_handler
from utils.task_requests import DB_task_request, API_task_request
from utils.data_primatives import NFT_Data, Ownership_Data
from db.db_config import DB_Config
from utils.log import log

#Setup DB Configd
db_config = DB_Config()
db_config.db_path_and_filename = "./tests/dummy_data/" + "dummy_db.db"

# Start DB Handler instance
db_handler = DB_handler(db_config)

# Start API Handler
api_handler = API_Handler()

single_nft_index = 1

def get_nft_record(record_obj):
        # First task get NFT record form DB
    get_nft_record_task = DB_task_request()
    get_nft_record_task.set_task_action(DB_task_request.TASK_READ_SINGLE_RECORD)
    get_nft_record_task.set_record_data_object(record_data_obj=record_obj)

    get_nft_record_task.set_table_name(DB_task_request.TABLE_TO_ACCESS_NFT_INFO)
    get_nft_record_task.set_pk_index_to_access(get_nft_record_task.record_data_obj.get_nft_index())

    get_nft_record_task.check_task_ready()
    get_nft_record_task.dump_info()

    # Send task to DB handler
    db_handler.set_new_task(get_nft_record_task)
    db_handler.execute_current_task()
    db_handler.clear_task()

def get_ownership_record_from_db(ownership_record):
    get_ownership_task = DB_task_request()
    get_ownership_task.set_task_action(DB_task_request.TASK_READ_SINGLE_RECORD)
    get_ownership_task.set_record_data_object(record_data_obj=ownership_record)

    get_ownership_task.set_table_name(DB_task_request.TABLE_TO_ACCESS_OWNERSHIP)
    # Setup access but the NFT_id column
    get_ownership_task.set_fk_for_access(get_ownership_task.get_colomn_labels()[1])
    get_ownership_task.set_pk_index_to_access(get_ownership_task.get_record_data_object().nft_record_index)

    get_ownership_task.check_task_ready()
    get_ownership_task.dump_info()

    # Send task to DB handler
    db_handler.set_new_task(get_ownership_task)
    status = db_handler.execute_current_task()
    # Finally clear task from db handler clear 
    db_handler.clear_task()
    return status

def get_ownership_from_api(ownership_record):
    get_ownership_task = API_task_request()
    get_ownership_task.set_task_action(API_task_request.TASK_GET_NFT_OWNER_SINGLE)
    get_ownership_task.set_record_data_obj(ownership_record)
    get_ownership_task.check_task_ready()
    get_ownership_task.dump_info()
    get_ownership_task.get_record_data_object().dump_info()

    api_handler.set_new_task(get_ownership_task)
    api_handler.execute_current_task()

def set_new_ownership_record_in_db(ownership_record):
    get_ownership_task = DB_task_request()
    get_ownership_task.set_task_action(DB_task_request.TASK_CREATE_NEW_RECORD)
    get_ownership_task.set_record_data_object(record_data_obj=ownership_record)

    get_ownership_task.set_table_name(DB_task_request.TABLE_TO_ACCESS_OWNERSHIP)

    # As this is a new record the NFT_id and ownership_recordid can be the same
    get_ownership_task.set_pk_index_to_access(get_ownership_task.get_record_data_object().nft_record_index)
    get_ownership_task.record_data_obj.set_ownership_record_index_to_NFT_id()
    get_ownership_task.check_task_ready()
    get_ownership_task.dump_info()
    get_ownership_task.record_data_obj.dump_info()

    # Send task to DB handler
    db_handler.set_new_task(get_ownership_task)
    status = db_handler.execute_current_task()
    # Finally clear task from db handler clear 
    db_handler.clear_task()
    return status

def update_ownership_record_in_db(ownership_record):
    log.info('update already excisting record')
    set_ownership_task = DB_task_request()
    set_ownership_task.set_task_action(DB_task_request.TASK_UPDATE_RECORD)
    set_ownership_task.set_record_data_object(record_data_obj=ownership_record)

    set_ownership_task.set_table_name(DB_task_request.TABLE_TO_ACCESS_OWNERSHIP)
    set_ownership_task.set_pk_index_to_access(set_ownership_task.get_record_data_object().get_ownership_record_index())
    set_ownership_task.check_task_ready()
    #set_ownership_task.dump_info()
    #set_ownership_task.dump_data_obj_info()
    # Send task to DB handler

    db_handler.set_new_task(set_ownership_task)
    status = db_handler.execute_current_task()




def test_update_single_record():
    
    # Create a single empty NFT record
    single_nft_record = NFT_Data(single_nft_index)

    get_nft_record(single_nft_record)
    single_nft_record.dump_info()

    # Wrap The NFT record with the ownership Info
    single_owner_data = Ownership_Data(single_nft_record)
    single_owner_data.dump_info()
    #check that there is no wonship referancwe in the database
    record_status = get_ownership_record_from_db(single_owner_data)
    single_owner_data.dump_info()
    get_ownership_from_api(single_owner_data)

    single_owner_data.dump_info()
    if record_status:
        update_ownership_record_in_db(single_owner_data)
    else:
        set_new_ownership_record_in_db(single_owner_data)





def test_all_nfttracking():
    test_update_single_record()

