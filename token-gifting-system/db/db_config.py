'''
Here you will find configs secific to the YMS database
'''


'''
Notes generation commands
sudo apt install sqlite3

'''


class DB_status_record:

    DB_NOT_PRESENT = 0
    DB_STATUS_EMPTY = 1
    DB_STATUS_READY = 2
    DB_STATUS_UNKNOWN = 3

    def __init__(self, status, timestamp=None, status_record_id=None):
        self.status_record_id = status_record_id
        self.timestamp = timestamp
        self.status = status

    def set_status_record_id(self, status_record_id):
        self.status_record_id = status_record_id

    def get_status_record_id(self):
        return int(self.status_record_id)

    def get_status(self):
        return int(self.status)


class DB_Config:

    def __init__(self):
        self.db_local = True
        self.db_path = "./db/"
        self.db_filename = "yms_test.db"
        self.db_path_and_filename = self.db_path + self.db_filename
        self.db_name = "YSM_DATABASE_TEST"
        self.db_status = DB_status_record.DB_NOT_PRESENT
        self.db_status_record = DB_status_record(self.db_status)

    def set_filename_and_path(self, filename, path):
        self.db_filename = filename
        self.db_path = path
        self.db_path_and_filename = self.db_path + self.db_filename

    def get_filename_and_path(self):
        return self.db_path_and_filename
