from tests.test_utils import test_bech32m_encoding, test_bech32m_decoding, test_configs_save
from tests.test_external_collection_apis import test_api_handler_init, test_all_ext_api
# from tests.test_db import test_all_database_fuctions
from tests.test_nfttracking_full import test_all_nfttracking
from tests.test_blockchain_handler import test_all_blockchain
# from tests.test_transaction_handler import transaction_handler
from tests.test_distribution import test_get_ownership_record, test_get_tranaction_records, test_check_for_incomplete_tranactions, test_start_next_transaction, test_begin_new_transaction_cycle
import sys
from tests.test_api_spacescan import test_api_space_scan_all


'''
There is a single nft on testnet so far that can be used for tesing
Collectionid: col1j2l2aq4dcrjlmqd48g3wtfmzf0y3fx4v6mszuw9hpaeqtg8gdkxshn4qs7
Name: MonkeyZoo TestNFT #0
NFT_ID: nft1wxra08kr867zkhkv5x4qcwdnytjf8vjqxjrvseyhf260v706st8qan0qtr
txch wallet amount  9.999999999985

'''


def test_all():
    # transaction_handler()
    test_all_blockchain()
    test_all_nfttracking()
    # test_all_database_fuctions()
    test_all_ext_api()
    test_configs_save()
    test_bech32m_encoding()
    test_bech32m_decoding()
    test_api_handler_init()
    test_api_space_scan_all()


def test_single():
    pass
    # transaction_handler()


if 'dist' in sys.argv:
    #test_get_ownership_record()
    #test_get_tranaction_records()
    #test_check_for_incomplete_tranactions()
    #test_start_next_transaction()
    test_begin_new_transaction_cycle()

#test_single()
