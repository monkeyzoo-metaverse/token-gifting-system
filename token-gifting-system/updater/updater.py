import datetime
from utils.log import log
from task_manager.task_helpers import create_task_get_ownership_record_from_db, return_ownership_record_from_TMT,create_task_update_ownership_from_api, write_ownership_record_to_db, write_ownerhip_update_to_ledger
import config

class Updater:
    STATE_UPDATE_SCHEDULED = 5
    STATE_FETCH_DB_ONWERSHIP_RECORD = 1
    STATE_FETCH_API_ONWERSHIP_DATA = 2
    STATE_UPDATE_DB_OWNERSHIP_RECORD = 3
    STATE_UPDATE_COMPLETE = 4
    STATE_UPDATE_SKIPPED = 5

    def __init__(self, task_manager):
        self.current_day = datetime.datetime.now()
        self.auto_mode = False
        self.task_manager = task_manager
        self.last_cycle_complete = 0
        self.ownership_record = 0
        self.current_task_uuid = 0
        self.current_task_record_index = None
        self.update_state = self.STATE_FETCH_DB_ONWERSHIP_RECORD

    def set_record_range(self, start_index , index_range):
        self.start_index = start_index
        self.record_range = index_range

    def check_last_record_update(self, record_index):
        self.current_task_record_index = record_index
        get_record_task = create_task_get_ownership_record_from_db(record_index)
        get_record_task.set_start_time(datetime.datetime.now())
        get_record_task.task_complete_callback = self.get_last_updated

    def get_last_updated(self, task_uuid):
        tm_task = self.task_manager.get_task_by_uuid(task_uuid)
        ownership_record = return_ownership_record_from_TMT(tm_task)
        log.warning(ownership_record.dump_info())
        log.warning(ownership_record.ownership_update_timestamp)


    def start_updating_record(self, record_index, start_time=None):
        self.update_state = self.STATE_FETCH_DB_ONWERSHIP_RECORD
        self.current_task_record_index = record_index
        get_record_task = create_task_get_ownership_record_from_db(record_index)
        if start_time == None:
            start_time = datetime.datetime.now()
        get_record_task.set_start_time(start_time) # start in 10 seconds
        get_record_task.task_complete_callback = self.do_fetch_from_api
        self.task_manager.append_task_list(get_record_task)

    def get_api_data_task(self, record_index):
        get_api_data_task = create_task_update_ownership_from_api(self.ownership_record)
        get_api_data_task.set_start_time(datetime.datetime.now() + datetime.timedelta(seconds=config.UPDATER_DELAY_BETWEEN_API_TASKS)) # start in 10 seconds
        get_api_data_task.task_complete_callback = self.do_update_database
        get_api_data_task.task_error_callback = self.retry_or_skip
        self.task_manager.append_task_list(get_api_data_task) 

    def update_db_ownership_record(self, record_index):
        update_ownership_db_record_task = write_ownership_record_to_db(self.ownership_record) 
        update_ownership_db_record_task.set_start_time(datetime.datetime.now() + datetime.timedelta(seconds=config.UPDATER_DELAY_BETWEEN_TASKS)) # start in 10 seconds
        update_ownership_db_record_task.task_complete_callback = self.do_mark_done_and_cleanup
        self.task_manager.append_task_list(update_ownership_db_record_task)
    
    def update_ownership_ledger(self, record_index):
        pass


# Callbacks for completed tasks
    def do_fetch_from_api(self, task_uuid):
        log.info(' Next task called from uuid: {0}'.format(task_uuid))
        if self.task_manager.get_task_by_uuid(task_uuid):
            finished_task = self.task_manager.get_task_by_uuid(task_uuid)
            log.info('found task in complete tasks list')
            log.info('task update states {0}'.format(self.update_state) )
            if self.update_state == self.STATE_FETCH_DB_ONWERSHIP_RECORD:
                log.info('Found completed task DB record fetch')
                self.ownership_record = return_ownership_record_from_TMT(finished_task)
                if self.ownership_record is False:
                    log.warning('NFT most likely balcklisted')
                    self.task_manager.remove_task_by_uuid(task_uuid, False) # Finally remove the task from the completed task list
                    # Set next task
                    self.update_state = self.STATE_UPDATE_SKIPPED

                    return False
                log.info(self.ownership_record.get_nft_record().dump_info())

                # todo add somthing that checks the ownership record timestamp and skips if it is below a certain threshold

                self.task_manager.remove_task_by_uuid(task_uuid, False) # Finally remove the task from the completed task list
                # Set next task
                self.update_state = self.STATE_FETCH_API_ONWERSHIP_DATA
                self.get_api_data_task(self.current_task_record_index)
    
    def do_update_database(self, task_uuid):
            if self.update_state == self.STATE_FETCH_API_ONWERSHIP_DATA:
                log.info('Found completed task API data fetch')
                log.info(self.ownership_record.dump_info())
                self.task_manager.remove_task_by_uuid(task_uuid, False) # Finally remove the task from the completed task list
                # Set next task
                self.update_state = self.STATE_UPDATE_DB_OWNERSHIP_RECORD
                self.update_db_ownership_record(self.current_task_record_index)

    def do_mark_done_and_cleanup(self, task_uuid):
            if self.update_state == self.STATE_UPDATE_DB_OWNERSHIP_RECORD:
                log.info('Found completed DB Update task for UUID:{0}'.format(task_uuid))
                log.info('Setting Updater state to Complete')
                self.task_manager.remove_task_by_uuid(task_uuid, False) # Finally remove the task from the completed task list
                self.update_state = self.STATE_UPDATE_COMPLETE

    def retry_or_skip(self, task_uuid):
        pass
