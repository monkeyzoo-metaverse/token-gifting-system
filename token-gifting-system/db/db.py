
'''
Name: yms_db_test.py
Function:
YMS database management tools
'''
from db.db_config import DB_status_record
from utils.task_requests import DB_task_request, Task_Status
from utils.log import log
import sqlite3
import time


class DB_handler:

    def __init__(self, db_configuration):
        log.info('Initializing Database handler')
        self.db_configuration = db_configuration
        self.connected = False
        self.db_status_record = db_configuration.db_status_record
        self.database = 0
        self.db_cursor = 0
        self.db_locked = True  # To be used for thread control

        # Specific to ccurrent task running on the database
        self.task = 0
        self.task_uuid = ""
        self.task_started = False
        self.task_complete = False
        self.task_status = -1  # To be inheitied from DB_task_request

    def connect(self, file_path=None):
        try:
            self.db_locked = True
            log.info('Connecting to dtatbase at {0}'.format(self.db_configuration.db_path_and_filename))
            self.database = sqlite3.connect(self.db_configuration.db_path_and_filename)  # Connect to database file
            self.db_cursor = self.database.cursor()
            self.connected = True
            self.db_locked = False

        except Exception as e:
            log.exception(e)

    def disconnect(self):  # Close database cleanly
        try:
            self.database.close()
            self.connected = False
            self.database = 0
            self.db_cursor = 0

        except Exception as e:
            log.error(e)

    def set_task_complete(self):
        self.task_complete = True
        self.task.task_status = Task_Status.STATUS_COMPLETE
        self.disconnect()
        return True  # Little flag to let system know all is well

    def clear_task(self):
        self.task = 0

    """
    This section is purly for handling the tasks
    """

    def set_new_task(self, task):
        assert isinstance(task, DB_task_request)  # Type check to make sure the correct arg type is passed in
        try:
            if (self.task != 0):
                raise Exception('Previous task has not been cleared from handler')

            if (self.task_started and not self.task_complete):
                raise Exception('Current Task still running')
            if (task.check_task_ready()):  # Final checkthat the task is read other wise thow exception
                self.task = task
                self.task.task_began_at = time.time()
                self.task_uuid = self.task.task_uuid  # Set the hander uuid to tasks_uuid
            else:
                raise Exception('Task is not read to be actioned by DB handler plase check task data members are all correct')

            return True

        except Exception as e:
            log.error(e)
            return False

    def execute_current_task(self, task_complete_callback=None):

        try:
            self.connect()
            log.info('Database connected ...')
            self.task.task_status = Task_Status.STATUS_RUNNING
            if (self.db_locked):
                raise Exception('New task cannot be added with database is locked')
            if (self.task == 0):
                raise ValueError('No current task set')
            log.info('Set Task started')
            self.task_started = True
            if (self.task.task_action == DB_task_request.TASK_CREATE_NEW_RECORD):
                log.info('Selected create method')
                status = self.create_record()
            if (self.task.task_action == DB_task_request.TASK_UPDATE_RECORD):
                log.info('Selected update method')
                status = self.update_record()
            if (self.task.task_action == DB_task_request.TASK_READ_SINGLE_RECORD):
                log.info('set get record method')
                status = self.get_single_record()
            if (self.task.task_action == DB_task_request.TASK_READ_ALL_RECORDS):
                log.info('set get all records method')
                status = self.get_all_records()
            # The following callback can be used to notifiy that the current task is ready for collection
            if task_complete_callback:
                task_complete_callback()
            return status

        except Exception as e:
            log.error(e, extra={'className': self.__class__.__name__})
            return False

    def get_task(self):
        return self.task

    def get_last_record_id(self):
        log.debug(' Getting last record id number in table {0}'.format(self.task.table_access_name))
        if (not self.connected):
            self.connect()
        last_record_id = 0
        self.db_cursor.execute('select * from {0}'.format(self.task.table_access_name))
        last_record_id = self.db_cursor.fetchall()[-1]
        log.debug('last record id = {0}'.format(last_record_id[0]))
        return last_record_id

    def check_record_id_exists(self):
        try:

            log.debug('Check record id number {0} exists in table {1}'.format(self.task.table_pk_index, self.task.table_access_name))
            if (self.get_last_record_id() < self.task.table_pk_index):
                raise Exception('Record pk higher than db records during read place check pk number is correct')
            return True

        except Exception as e:
            log.error(e, extra={'className': self.__class__.__name__})
            return False

    def update_record(self):
        log.info('Upadting database from record obj')
        self.db_locked = True
        sql_command = "UPDATE {0} SET ".format(self.task.table_access_name)
        sql_args = ''
        for column_index in range(len(self.task.get_colomn_labels())):
            if column_index != 0:
                sql_args += '' + self.task.get_colomn_labels()[column_index] + ' = "' + str(self.task.record_data_obj.get_record_data_for_database()[column_index]) + '" , '
        record_location = ' WHERE ' + self.task.table_pk_label + ' = "' + str(self.task.table_pk_index) + '"'
        log.info('Issued SQL command {0}'.format(sql_command))
        log.info('{0}{1}{2}'.format(sql_command, sql_args[:-2], record_location))
        self.db_cursor.execute('{0}{1}{2}'.format(sql_command, sql_args[:-2], record_location))
        self.database.commit()
        self.db_locked = False
        return True
        pass

    def create_record(self):
        try:
            self.db_locked = True
            if (not self.connected):
                self.connect()
            sql_command = "INSERT INTO {0}".format(self.task.table_access_name)

            entry_columns = self.task.get_colomn_string_for_sql()
            entry_values = self.task.record_data_obj.get_black_record_template()

            sql_params = "( {0} ) VALUES ( {1} )".format(entry_columns, entry_values)
            log.info('Issued SQL command {0}'.format(sql_command))
            log.info('{0}{1}'.format(sql_command, sql_params))
            self.db_cursor.execute('{0}{1}'.format(sql_command, sql_params), self.task.record_data_obj.get_record_data_for_database())
            self.database.commit()

            self.db_locked = False
            return True

        except Exception as e:
            log.error(e, extra={'className': self.__class__.__name__})
            return False

    def get_range_of_records(self, task_request):
        self.db_locked = True

        self.db_locked = False
        pass

    def get_all_records(self):
        try:
            log.info('Accessing all records by index')
            self.db_locked = True

            if (not self.connected):
                log.info('C0nnecting to Database')
                self.connect()
            sql_command = "SELECT * FROM {0} WHERE {1}={2}".format(self.task.table_access_name, self.task.table_pk_label, self.task.table_pk_index)
            log.info(sql_command)
            self.db_cursor.execute(sql_command)
            record = self.db_cursor.fetchall()
            log.info('DB record: {0}'.format(record))
            if record is None:
                raise Exception('Database record is empty')
            
            self.task.record_data_obj = record # set the object as a list of all the raw DB records
            self.task.task_status = Task_Status.STATUS_ERROR
            self.set_task_complete()
            self.db_locked = False
            return True
        except Exception as e:
            log.error(e, extra={'className': self.__class__.__name__})
            return False

    def get_single_record(self):
        try:
            log.info('Accessing single record')
            self.db_locked = True

            if (not self.connected):
                log.info('C0nnecting to Database')
                self.connect()
            sql_command = "SELECT * FROM {0} WHERE {1}={2}".format(self.task.table_access_name, self.task.table_pk_label, self.task.table_pk_index)
            log.info(sql_command)
            self.db_cursor.execute(sql_command)
            record = self.db_cursor.fetchone()
            log.info('DB record: {0}'.format(record))
            if record is None:
                raise Exception('Database record is empty')
            
            self.task.record_data_obj.populate_from_database_record(record)
            self.task.task_status = Task_Status.STATUS_ERROR
            self.set_task_complete()
            self.db_locked = False
            return True

        except Exception as e:
            log.error(e, extra={'className': self.__class__.__name__})
            return False

    def dump_info(self):
        pass


'''
Most of these functions below will be replaced with a new database handler that is
Above
'''


class DB_initalsation:

    def __init__(self, db_configuration):  # Takes db_configuration object
        self.db_configuration = db_configuration
        self.database = None
        self.db_cursor = None
        self.intitalsed = False
        self.connected = False
        self.db_status_record = db_configuration.db_status_record
        self.db_current_status = self.db_status_record.status
        self.file_path = db_configuration.get_filename_and_path()
        log.info("Created instanace of database initasation engine")

    def connect(self, file_path=None):
        try:
            self.database = sqlite3.connect(self.db_configuration.db_path_and_filename)  # Connect to database file
            self.db_cursor = self.database.cursor()

        except Exception as e:

            log.exception(e)

    def set_task(self, task):  # This is where a new database task is passed in

        pass

    # Return a list of all of the DB status records
    def read_all_db_status_records_from_database(self):
        try:
            status_records = []
            self.db_cursor.execute('SELECT * FROM status')
            status = self.db_cursor.fetchall()
            for entry in status:
                status_records.append(DB_status_record(entry[1], entry[2], entry[0]))

            return status_records

        except Exception as e:
            log.error(e)
            return False

    def read_latest_db_status_record_from_database(self):
        try:
            self.db_cursor.execute('SELECT MAX(timestamp) FROM status')
            status = self.db_cursor.fetchall()
            status_record = DB_status_record(status[1], status[2], status[0])
            return [status_record]  # Should always return as a list

        except Exception as e:
            log.error(e)
            return False

    def update_db_status(self, status_record):
        if self.connected:
            if (status_record.status_record_id is None):
                previous_status_record = self.read_latest_db_status_record_from_database()
                values = (previous_status_record.status_record_id + 1, status_record.timestamp, status_record.status)
                self.db_cursor.execute('INSERT INTO NFT_info SET NFT_id_puzzlehash = ? , NFT_is_blacklisted = ? , NFT_yield_qty = ? WHERE NFT_Record_id = ?', values)
            if (status_record.status_record_id == 1):
                values = (1, status_record.timestamp, status_record.status)
                self.db_cursor.execute('INSERT INTO status(status_record_id , timestamp , status ) VALUES (?, ? , ?)', values)
            self.database.commit()
            return True

    def create_db_table(self, table_name, pri_key_name, pri_key_type, column_names=None, column_types=None):
        try:
            column_list = '( ' + pri_key_name + ' ' + pri_key_type + ' ' + 'PRIMARY KEY, '
            for column_index in range(len(column_names)):
                if (column_index < len(column_names) - 1):
                    column_list += '{0} {1}, '.format(column_names[column_index], column_types[column_index])
                else:
                    column_list += '{0} {1})'.format(column_names[column_index], column_types[column_index])  # Do this for last entry
            print('CREATE TABLE {0}{1}'.format(table_name, column_list))
            self.db_cursor.execute("CREATE TABLE {0}{1}".format(table_name, column_list))
            self.database.commit()
            return True

        except sqlite3.OperationalError as e:
            log.error(e)
            return False

        except Exception as e:
            log.error(e)
            return False

    def create_new_db(self, file_path=None):
        try:
            if (self.db_current_status != DB_status_record.DB_NOT_PRESENT):
                log.error("database file already present")
                raise Exception("Unable to create database with database file present")
            else:
                self.database = sqlite3.connect(self.db_configuration.db_path_and_filename)  # Connect to database file
                self.connected = True
                self.create_db_table('status', 'status_record_id', 'integer', ['timestamp', 'status'], ['text', 'integer'])
                self.update_db_status(DB_status_record(time.time(), DB_status_record.DB_STATUS_EMPTY, status_record_id=1))  # Create the first status record pn the table
                self.intitalsed = True
                return True

        except Exception as e:
            log.error(e)
            return False
