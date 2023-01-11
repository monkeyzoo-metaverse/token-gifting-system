import uuid
from utils.log import log
# from utils.coin_utils import get_coin_id
import datetime
import json
import time


class YMS_Configs:

    def __init__(self, config_file):
        self.config_data = 0
        self.config_file = config_file

    def load_from_json(self):
        with open(self.config_file, 'r') as raw_file:
            self.config_data = json.loads(raw_file)
            raw_file.close()

    def save_to_json(self):
        with open(self.config_file, 'w') as raw_output_file:
            json.dump(self.config_data, raw_output_file, ensure_ascii=False, indent=4)
            raw_output_file.close()


class Ownership_Data:

    def __init__(self, nft_record=None):  # class should be initialized with attached nft record
        self.ownership_record_index = None
        self.nft_record = nft_record  # NFT record wrapped inside this class
        if nft_record is None:
            self.nft_record_index = None
        else:
            self.nft_record_index = self.nft_record.get_field_data_all()
            self.nft_record_id = self.nft_record.get_nft_id()
        self.number_of_tracked_owners = 0
        self.previous_owner_address = ""
        self.current_owner_address = ""
        self.ownership_update_timestamp = ""
        self.last_transfer_height = 0

    # Recieves database record array and populates data field from it
    def populate_from_database_record(self, database_record):
        try:
            if database_record is None:
                raise TypeError('record is empty!')
            if self.ownership_record_index is None:
                self.ownership_record_index = database_record[0]
            self.nft_record_index = database_record[1]
            self.number_of_tracked_owners = database_record[2]
            self.previous_owner_address = database_record[3]
            self.current_owner_address = database_record[4]
            self.ownership_update_timestamp = database_record[5]
            self.last_transfer_height = database_record[6]
            return True
        except TypeError as e:
            log.error(e)
            return False

    def get_record_data_for_database(self):
        record = [
            self.ownership_record_index,
            self.nft_record_index,
            self.number_of_tracked_owners,
            self.previous_owner_address,
            self.current_owner_address,
            self.ownership_update_timestamp,
            self.last_transfer_height
        ]
        return record

    def get_is_blacklisted(self):  # Simple check to see if the nft is blacklisted
        return self.nft_record.blacklisted

    def set_ownership_record_index_to_NFT_id(self):
        self.ownership_record_index = self.nft_record_index

    def get_record_string_for_db(self):
        record_data_string = ''
        for record_data in self.get_record_data_for_database():

            record_data_string += "'" + str(record_data) + "', "
        return record_data_string[0:-2]

    def set_new_owner(self, new_owner_address, last_transfer_height=None):
        log.info('setting new owner')
        try:
            self.dump_info()
            if(last_transfer_height):
                if self.last_transfer_height == self.last_transfer_height:
                    raise Exception('Previous and new tranfer hieght are identical has a transfer really taken place')
            log.info('setting current address as previous')
            if new_owner_address == self.current_owner_address:
                log.info('no change in ownership updating timestamp only')
                self.ownership_update_timestamp = time.time()
                return True

            self.previous_owner_address = self.current_owner_address
            log.info('setting New owner as current address')
            self.current_owner_address = new_owner_address
            self.number_of_tracked_owners += 1
            self.last_transfer_height = last_transfer_height
            self.ownership_update_timestamp = time.time()
            return True

        except Exception as e:
            log.error(e, extra={'className': self.__class__.__name__})
            return False

    def get_nft_record_index(self):  # Returns the NFT record index number
        return self.nft_record_index

    def get_ownership_record_index(self):
        return self.ownership_record_index

    def set_nft_record(self, nft_record):
        self.nft_record = nft_record
        self.nft_record_index = self.nft_record.get_field_data_all()

    def get_nft_record(self):
        return self.nft_record

    def dump_info(self):
        if self.ownership_record_index is None:
            log.info("No ownership data!!")
        log.info("""
        NFT Ownership Record Dump
        Ownership Record Index: {0}
        NFT Record Index: {1}
        NFT Id: {2}
        Number of traked owners: {3}
        Previous owner address: {4}
        Current owner address: {5}
        Ownership update timestamp: {6}
        Last transfer height: {7}
        """.format(
            self.ownership_record_index,
            self.nft_record_index,
            self.nft_record_id,
            self.number_of_tracked_owners,
            self.previous_owner_address,
            self.current_owner_address,
            self.ownership_update_timestamp,
            self.last_transfer_height
        ))


class Owner_Data:
    def __init__(self):
        self.owner_index = None
        self.owner_address = None
        self.is_blacklisted = False


class NFT_Data:

    def __init__(self, nft_index=None):
        self.nft_index = nft_index  # Location on the NFT_info table
        self.nft_id = ""
        self.nft_name = ""
        self.nft_creator = ""
        self.nft_yield_value = ""
        self.nft_puzzlehash = None
        self.blacklisted = True
        self.ownership_record = Ownership_Data()

    # Recieves database record array and populates data field from it
    def populate_from_database_record(self, database_record):
        self.nft_id = database_record[2]
        self.nft_name = database_record[1]
        self.nft_yield_value = database_record[5]
        self.blacklisted = bool(database_record[4])

    def set_blacklisted(self, blacklisted):  # May requires some level of secturity in the future
        self.blacklisted = blacklisted

    def get_field_data_all(self):
        return (self.nft_index)

    def get_nft_index(self):
        return self.nft_index

    def get_nft_id(self):
        return self.nft_id

    def dump_info(self):

        log.info("""
        NFT Record Dump
        Record Index: {0}
        NFT Name: {1}
        NFT ID Encoded: {6}
        NFT Creator: {2}
        NFT Puzzlehash: {3}
        NFT Yield Value: {4}
        NFT Blacklisted: {5}
        """.format(
            self.nft_index,
            self.nft_name,
            self.nft_creator,
            self.nft_puzzlehash,
            self.nft_yield_value,
            self.blacklisted,
            self.nft_id
        ))


class NFT_Collection_Data:

    def __init__(self):

        self.name = ''
        self.inital_addresses = ['']
        self.collection_qty = 0
        self.collection_uuid = ''
        self.blacklist_nfts = []
        self.max_block_height = 0  # Maximum block hieght seen in the collection
        self.nft_requiring_update = []


class Transaction_Data:

    TRANSACTION_FAIL = -1
    TRANSACTION_CREATED = 1
    TRANSACTION_READY = 2
    TRANSACTION_INSUFICIENT_FUNDS_TOKEN = 5
    TRANSACTION_INSUFICIENT_FUNDS_XCH = 6
    TRANSACTION_SUBMITTED = 3
    TRANSACTION_PENDING = 4
    TRANSACTION_COMPLETE = 100

    
    statusText = {
        TRANSACTION_FAIL: 'Transaction Failed',
        TRANSACTION_CREATED: 'Transaction Created',
        TRANSACTION_SUBMITTED: 'Transaction successfully PUSHED to Blockchain',
        TRANSACTION_PENDING: 'Transaction pending',
        TRANSACTION_COMPLETE: 'Transaction complete',
        TRANSACTION_INSUFICIENT_FUNDS_XCH: 'Transaction Unsufficient Funds XCH',
        TRANSACTION_INSUFICIENT_FUNDS_TOKEN: 'Transaction Unsufficient Funds Token',
        TRANSACTION_READY: 'Transaction Ready'
        }

    def __init__(self, destination_address : str='', amount : int=0, fee : int =0):
        self.uuid = str(uuid.uuid4())
        self.transaction_record_index = None  # Recieved from the database
        self.destination_address = destination_address
        self.nft_record_id = None
        self.nft_owner_id = None
        self.amount = amount
        self.fee = fee
        self.dateCreated = time.time()
        self.dateSubmittedToBlockchain = 0
        self.transactionId = 0
        self.dateCompleted = 0
        self.heightCompleted = 0  # Block heigth of when the appears on the blockchain
        self.coinId = 0  # Id of the coin created in this transaction
        self.status = self.TRANSACTION_CREATED  # It be populated by transaction task
        log.debug('New transaction initalised UUID:{0}'.format(self.uuid))
        pass

    def set_status(self, status):
        log.debug('Status Updated to {1} for transaction UUID:{0}'.format(self.uuid, self.statusText[status]))
        self.status = status

    def get_status(self):
        log.debug('Status Requested for transaction UUID:{0}'.format(self.uuid))
        return self.status

    def get_status_text(self):
        log.info('Status Text Requested for transaction UUID:{0}'.format(self.uuid))
        return self.statusText[self.status]
    
    def set_date_submitted(self, datetime_obj):
        self.dateSubmittedToBlockchain = datetime_obj

    def set_date_completed(self):
        self.dateCompleted = time.time()

    def process_transaction_json(self, transaction_json):
        log.info('Updateing Transaction data')
        # Cheack to see if this is empty transaction data for tracking
        if self.destination_address == '':
            log.info('Updateing Empty Transaction data')
            self.destination_address = transaction_json['transaction']['to_address']
            self.fee = transaction_json['transaction']['fee_amount']
            self.amount = transaction_json['transaction']['additions'][0]['amount']
            self.set_status(Transaction_Data.TRANSACTION_SUBMITTED)

        elif self.status == Transaction_Data.TRANSACTION_SUBMITTED:
            log.info('Update post submitting Record')
            self.transactionId = transaction_json['transaction_id']
            self.set_date_submitted(transaction_json['transaction']['created_at_time']) 
            self.set_status(Transaction_Data.TRANSACTION_PENDING)

        elif self.status == Transaction_Data.TRANSACTION_PENDING:
            log.info('Update pending Record')
            if transaction_json['transaction']['confirmed']:
                self.set_status(Transaction_Data.TRANSACTION_COMPLETE)
                self.heightCompleted = transaction_json['transaction']['confirmed_at_height']
                self.set_date_completed() # dont have blockheight to timestamp converter yet so just using the current status update time
        log.info('transaction json processed')
        return True

            # Recieves database record array and populates da
            # ta field from it
    def populate_from_database_record(self, database_record):
        try:
            if database_record is None:
                raise TypeError('record is empty!')
            if self.transaction_record_index is None:
                self.transaction_record_index = database_record[0]
            self.nft_record_id = database_record[1]
            self.nft_owner_id = database_record[2]
            self.uuid = database_record[3]
            self.status = database_record[4]
            self.transactionId = database_record[5]
            self.destination_address = database_record[6]
            self.amount = database_record[7]
            self.fee = database_record[8]
            self.dateSubmittedToBlockchain = database_record[9]
            self.dateCompleted = database_record[10]
            self.heightCompleted = database_record[11]
            self.coinId = database_record[12]
            self.dateCreated = time.time()  # When this record was created
            return True
        except TypeError as e:
            log.error(e)
            return False
    def get_record_string_for_db(self):
        record = [
            self.transaction_record_index,
            self.nft_record_id,
            self.nft_owner_id,
            self.uuid,
            self.status,
            self.transactionId,
            self.destination_address,
            self.amount,
            self.fee,
            self.dateSubmittedToBlockchain,
            self.dateCompleted,
            self.heightCompleted,
            self.coinId
        ]
        for entry_index in range(len(record)):
            
            if record[entry_index] is None:
                record[entry_index] = 'NULL'
            else:
                record[entry_index] = str(record[entry_index])
        print(record)
        return ", ".join(record)

    def get_black_record_template(self):
        return '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?'


    def get_record_data_for_database(self):
        record = (
            self.transaction_record_index,
            self.nft_record_id,
            self.nft_owner_id,
            self.uuid,
            self.status,
            self.transactionId,
            self.destination_address,
            self.amount,
            self.fee,
            self.dateSubmittedToBlockchain,
            self.dateCompleted,
            self.heightCompleted,
            self.coinId
        )

        return record


        '''
        for coins in transaction_json['transaction']['additions']:
            log.info(' Creating Coin : {0}'.format(coins))
            if coins['amount'] == self.amount:
                self.coinId = 0x00
                # self.coinId = get_coin_id(bytes(coins['parent_coin_info']), bytes(coins['puzzle_hash']), bytes(coins['amount']))
        '''

        



    def dump_info(self):
        log.info("""
        Transaction Dump
        related NFTid: {11}
        Status: {9}
        UUID: {0}
        Destination address: {1}
        Amount: {2}
        Fee applied: {3}
        Date Created: {4}
        Date Submitted: {5}
        Transaction ID: {10}
        Date Completed: {6}
        Height Completed: {7}
        ID of coin created: {8}
        """.format(
            self.uuid,
            self.destination_address,
            self.amount,
            self.fee,
            self.dateCreated,
            self.dateSubmittedToBlockchain,
            self.dateCompleted,
            self.heightCompleted,
            self.coinId,
            self.get_status_text(),
            self.transactionId,
            self.nft_record_id
        ))
