import uuid
from utils.data_primatives import NFT_Data, Ownership_Data, Owner_Data, Transaction_Data
from utils.log import log


class Task_Status:  # Used for creating human readable status
    # Constants for task current state
    STATUS_CREATED = 0
    STATUS_READY = 1
    STATUS_QUEUED = 2
    STATUS_RUNNING = 3
    STATUS_COMPLETE = 4
    STATUS_TIMEOUT = 5
    STATUS_ERROR = 6

    task_state_string = {
        STATUS_CREATED: "Task Created",
        STATUS_READY: "Task Ready",
        STATUS_QUEUED: "Task Queued",
        STATUS_RUNNING: "Task Running",
        STATUS_COMPLETE: "Task Complete",
        STATUS_TIMEOUT: "Task Timeout ",
        STATUS_ERROR: "Task Error"
    }

    def parse_task_status(task_status):
        return Task_Status.task_state_string[task_status]


class DB_task_request:

    DB_ACCESS_TIMEOUT = 10000

    # Constants for requesting tasks
    TASK_UPDATE_RECORD = 0
    TASK_READ_RANGE = 1
    TASK_READ_SINGLE_RECORD = 2
    TASK_READ_ALL_RECORDS = 3
    TASK_CREATE_NEW_RECORD = 4

    # Constants for tables
    TABLE_TO_ACCESS_STATUS = 0
    TABLE_TO_ACCESS_NFT_INFO = 1
    TABLE_TO_ACCESS_OWNERSHIP = 2
    TABLE_TO_ACCESS_OWNERSHIP_LEDGER = 3
    TABLE_TO_ACCESS_OWNERS = 4
    TABLE_TO_ACCESS_YIELD_TRANSACTIONS = 5

    TABLE_NAMES = {
        TABLE_TO_ACCESS_STATUS: 'status',
        TABLE_TO_ACCESS_NFT_INFO: 'NFT_Info',
        TABLE_TO_ACCESS_OWNERSHIP: 'NFT_ownership',
        TABLE_TO_ACCESS_OWNERSHIP_LEDGER: 'NFT_ownership_ledger',
        TABLE_TO_ACCESS_OWNERS: 'NFT_owners',
        TABLE_TO_ACCESS_YIELD_TRANSACTIONS: 'NFT_yield_transactions'
    }

    TABLE_COLUMN_LABELS = {
        TABLE_TO_ACCESS_NFT_INFO: ["NFT_Record_id", "NFT_name", "NFT_id_encoded", "NFT_id_puzzlehash", "NFT_is_blacklisted", "NFT_yield_qty"],
        TABLE_TO_ACCESS_STATUS: ["record_id", "timestamp", "status"],
        TABLE_TO_ACCESS_OWNERSHIP: ["NFT_ownership_id", "NFT_Info_id", "NFT_previous_tracked_owners", "NFT_previous_owner_address", "NFT_current_owner_address", "NFT_ownership_list_update", "NFT_last_transfer_height"],
        TABLE_TO_ACCESS_OWNERS: ["NFT_owners_id", "NFT_owner_address", "NFT_owner_current_nfts_qty", "NFT_owner_blacklisted"],
        TABLE_TO_ACCESS_OWNERSHIP_LEDGER: ["NFT_ledger_id", "NFT_ledger_record_date", "NFT_id", "NFT_owner_id"],
        TABLE_TO_ACCESS_YIELD_TRANSACTIONS: ["transaction_id", "nft_id", "owner_id", "transaction_uuid", "transaction_status", "transaction_id_onchain", "transaction_address", "transaction_amount" ,"transaction_fee_amount", "transaction_date_submitted", "transaction_date_complete", "transaction_height_complete", "transaction_coin_id"]  # to be implemented
    }

    def __init__(self, task_action=None):
        self.task_uuid = str(uuid.uuid4())
        self.table_to_access = None
        self.table_access_name = None
        self.table_column_labels = None
        self.table_pk_label = None
        self.table_pk_index = None
        self.record_data_obj = None  # To contain data object can be an empty array
        self.timeout = self.DB_ACCESS_TIMEOUT
        self.task_began_at = 0
        self.task_action = task_action
        self.task_status = Task_Status.STATUS_CREATED

    def check_task_ready(self):  # Check all conditions are met for the task to be passed to the handler

        if self.table_to_access is None:
            return False
        if self.table_access_name is None:
            return False
        if self.table_column_labels is None:
            return False
        if self.table_pk_label is None:
            return False
        if self.task_action is not self.TASK_CREATE_NEW_RECORD:
            if self.table_pk_index is None:
                return False
        if self.record_data_obj is None:
            
            return False
        if self.task_action is None:
            return False
        self.task_status = Task_Status.STATUS_READY
        return True

    def set_pk_index_to_access(self, index_range):
        self.table_pk_index = index_range

    def set_task_action(self, task):
        try:
            self.task_action = task

        except AssertionError as a:
            log.error(a)

    def set_record_data_object(self, record_data_obj):
        try:
            assert isinstance(record_data_obj, (NFT_Data, Ownership_Data, Owner_Data, Transaction_Data, list))
            self.record_data_obj = record_data_obj

        except AssertionError as a:
            log.error(a)

    def get_record_data_object(self):
        return self.record_data_obj

    def set_table_name(self, table_name, foreign_key_to_use=None):
        try:
            # assert table_name >= 0 or table_name <= 5
            self.table_to_access = table_name
            self.table_access_name = DB_task_request.TABLE_NAMES[table_name]
            self.table_column_labels = DB_task_request.TABLE_COLUMN_LABELS[table_name]
            if foreign_key_to_use is None:
                self.table_pk_label = DB_task_request.TABLE_COLUMN_LABELS[table_name][0]
            else:
                self.table_pk_label = foreign_key_to_use

            log.debug('Using {0} entries as search search parameters'.format(self.table_pk_label))

        except AssertionError as e:
            log.error(e)

    def set_fk_for_access(self, foreign_key_to_use):
        self.table_pk_label = foreign_key_to_use

    def get_table_name(self):
        if self.table_to_access == -1:
            log.error('table to access needs to be set')
            return None
        return self.table_access_name

    def get_colomn_labels(self):
        return self.table_column_labels

    def get_colomn_string_for_sql(self, include_pk=False):
        string_return = ''
        if include_pk:
            string_return = "'" + self.table_pk_label + "', "
        for column in self.get_colomn_labels():
            string_return += "'" + column + "', "
        return string_return[:-2]

    def dump_info(self):
        log.info("""
        DB Task Request Dump
        Task UUID: {0}
        Table to access: {2}
        Table to access Name: {1}
        Table Primary Key Label: {8}
        Table PK index or range to access: {9}
        Record Data Obj: {3}
        timeout: {4}
        task begin at: {5}
        Task action: {6}
        Task_status: {7}
        """.format(
            self.task_uuid,
            self.table_access_name,
            self.table_to_access,
            self.record_data_obj,
            self.timeout,
            self.task_began_at,
            self.task_action,
            Task_Status.parse_task_status(self.task_status),
            self.table_pk_label,
            self.table_pk_index
        ))

    def dump_data_obj_info(self):
        try:
            self.record_data_obj.dump_info()
        except Exception as e:
            log.error(e)


class API_task_request:

    API_ACCESS_TIMEOUT = 10000

    # Constants for requesting tasks
    TASK_GET_CONNECTION_ID = 0
    TASK_GET_NFT_OWNER_SINGLE = 1
    TASK_GET_NFT_OWNER_RANGE = 2
    TASK_GET_COLLECTION_DATA = 4

    def __init__(self, task_action=None):
        self.task_uuid = str(uuid.uuid4())
        self.task_status = Task_Status.STATUS_CREATED
        self.task_began_at = 0
        self.timeout = 10000
        self.task_action = task_action
        self.record_data_obj = None

    def set_record_data_obj(self, record_data_obj):
        self.record_data_obj = record_data_obj

    def get_record_data_object(self):
        return self.record_data_obj

    def set_task_action(self, task_action):
        try:
            log.info('Setting action for task {0}'.format(self.task_uuid))
            self.task_action = task_action

        except AssertionError as a:
            log.error(a)

    def check_task_ready(self):  # Check all conditions are met for the task to be passed to the handler
        log.info('Checking task is ready for API handler')
        if self.record_data_obj is None:
            log.error('Not Task data object set')
            return False
        if self.task_action is None:
            log.error('Not Task action set')
            return False
        log.info('Setting Task ready')
        self.task_status = Task_Status.STATUS_READY
        return True

    # Used in specific cases where the api has a interal id for searching parameters

    def get_collection_id(self):
        pass

    def dump_info(self):
        log.info("""
        API Task Request Dump
        Task UUID: {0}
        Record Data Obj: {1}
        timeout: {2}
        task begin at: {3}
        Task action: {4}
        Task_status: {5}
        """.format(
            self.task_uuid,
            self.record_data_obj,
            self.timeout,
            self.task_began_at,
            self.task_action,
            Task_Status.parse_task_status(self.task_status),
        ))


class Transaction_task_request:

    TASK_GET_STATUS = 0
    TASK_CHECK_FUNDS_AVAILABLE = 1
    TASK_SEND_TRANSACTION = 2


    def __init__(self):
        self.task_uuid = str(uuid.uuid4())
        self.transaction_status = Task_Status.STATUS_CREATED
        self.transaction_data = 0
        self.task = 0
        pass

    def set_transaction_task(self, task):
        self.task = task
    
    def set_transaction_data(self, transaction_data):
        try:
            if not isinstance(transaction_data, Transaction_Data):
                raise Exception('Transaction data not of a valid type')
            self.transaction_data = transaction_data
            self.transaction_status = transaction_data.get_status()
            self.task_uuid = transaction_data.uuid
            return True
        
        except Exception as e:
            log.error(e)
            return False

    def set_transaction_status(self, status):
        self.transaction_status =  status
        self.transaction_data.set_status(status=status) 


    def check_transaction_ready(self):
        try:
            if (self.task == 0):
                raise Exception('Transaction not ready to send')

            if (self.transaction_data == 0):
                raise Exception('No Transaction Data')

            return True

        except Exception as e:
            log.error(e)
            return False

    
    def get_tranaction_data(self):
        return self.transaction_data
        pass
    
    
    def dump_info(self):
        log.info("""
        Transaction Task Dump
        Status: {0}
        Task: {1}
        Trasnaction Data: {2}
        """.format(
            Transaction_Data.statusText[self.transaction_status],
            self.task,
            self.transaction_data
        ))

