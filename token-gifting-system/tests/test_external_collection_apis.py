# Import all the api submodules
from nfttracking.api_handler import API_Handler
from utils.task_requests import API_task_request
from utils.data_primatives import Ownership_Data, NFT_Data
import configs_for_tests

test_nft_ids = configs_for_tests.TEST_NFT_IDS

test_nfts = []

for index in range(3):
    temp = NFT_Data(nft_index=index)
    temp.nft_id = test_nft_ids[index]
    test_nfts.append(temp)
    test_nfts[index].dump_info()



test_connections = False
api_handler = API_Handler() # creat local instants
api_task = API_task_request()

def test_api_handler_init():

    api_handler = API_Handler() # creat local instants
    api_task = API_task_request()
    
    api_task.dump_info()
    if api_handler.check_connections(): # check no errors 
        test_connections = True #testing of the connections is available 
    

def test_adding_ownership_data():
    owners =[]
    for index in range(len(test_nfts)):
        api_task = API_task_request()
        ownership_data = Ownership_Data(nft_record=test_nfts[index]) 
        api_task.set_record_data_obj(ownership_data)
        api_task.set_task_action(API_task_request.TASK_GET_NFT_OWNER_SINGLE)
        api_handler.set_new_task(api_task)
        api_handler.execute_current_task()
        owners.append(api_task.get_record_data_object())
        api_handler.clear_task()
    
    for owner_info in owners:
        owner_info.dump_info()




def test_all_ext_api():
    test_api_handler_init()
    test_adding_ownership_data()