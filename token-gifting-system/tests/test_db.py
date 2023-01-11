from db.db import DB_initalsation, DB_handler
from db.db_config import DB_Config, DB_status_record
from utils.data_primatives import NFT_Data, Ownership_Data
from utils.task_requests import DB_task_request
from utils.log import log 



db_test_config = DB_Config()
db_test_config.db_path_and_filename = "./tests/dummy_data/" + "dummy_db.db"
initer = DB_initalsation(db_test_config)

# testing the request handleing system 

def test_get_database_nft_record():
    db_test_config = DB_Config()
    db_test_config.db_path_and_filename = "./tests/dummy_data/" + "dummy_db.db"
    db_handler = DB_handler(db_test_config)
    nft_info_list = []
    db_task = DB_task_request()
    for nft_index in range(3):
        nft_info_list.append(NFT_Data(nft_index+1))
        db_task.set_record_data_object(nft_info_list[nft_index])
        db_task.set_task_action(DB_task_request.TASK_READ_SINGLE_RECORD)
        db_task.set_table_name(DB_task_request.TABLE_TO_ACCESS_NFT_INFO)
        db_task.set_pk_index_to_access(db_task.get_record_data_object().nft_index)

        db_handler.set_new_task(db_task)
        db_handler.get_last_record_id()
        db_handler.execute_current_task()
        db_handler.dump_info()
        nft_info_list[nft_index] = db_handler.get_task().record_data_obj
        db_handler.clear_task()

    for nft_info in nft_info_list:
        nft_info.dump_info()

    assert db_handler.execute_current_task() == False # check that a task cannot be excuted without reilave data

def test_get_ownership_data():
    db_test_config = DB_Config()
    db_test_config.db_path_and_filename = "./tests/dummy_data/" + "dummy_db.db"
    db_handler = DB_handler(db_test_config)
    nft_record = NFT_Data(1)
    ownership_data = Ownership_Data(nft_record) #  wraps the ownership data around the nft record
    db_task = DB_task_request() # create Task request
    ownership_data.dump_info()
    db_task = DB_task_request(DB_task_request.TASK_READ_SINGLE_RECORD)
    db_task.set_record_data_object(ownership_data)
    db_task.dump_info()
    db_task.dump_data_obj_info()
    assert db_task.check_task_ready() == False  # Make sure request id not ready to run while PK files are missing

    db_task.set_table_name(DB_task_request.TABLE_TO_ACCESS_OWNERSHIP)
    db_task.set_fk_for_access(db_task.get_colomn_labels()[1])
    db_task.set_pk_index_to_access(db_task.get_record_data_object().nft_record_index)
    db_task.dump_info()
    assert db_handler.set_new_task(db_task) == True
    assert db_handler.execute_current_task() == True
    db_handler.task.record_data_obj.dump_info()
