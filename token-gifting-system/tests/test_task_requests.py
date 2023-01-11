import logging
from utils.task_requests import DB_task_request, API_task_request
from utils.data_primatives import NFT_Data, Ownership_Data
#
api_t_r = 0
db_t_r = 0 

nft_info = NFT_Data()
ownership_info = Ownership_Data

def test_task_instances():
    # Setup test instances
    api_t_r = API_task_request()
    db_t_r = DB_task_request()
    api_t_r.set_record_data_obj(nft_info)
    api_t_r.record_data_obj.dump_info()
    api_t_r.set_task_action(API_task_request.TASK_GET_CONNECTION_ID)
    api_t_r.dump_info()

def test_all_task_requests():
    pass
