from utils.log import log
from utils.task_requests import Task_Status, DB_task_request, API_task_request
import uuid
from nfttracking.api_handler import API_Handler
from db.db import DB_handler
from db.db_config import DB_Config
from distribution.transaction_handler import Transaction_Handler
import datetime
import config


# This now combines the Scheduler 
class Task_Manager_Task:
        
    SUBSYSTEM_DB = 0
    SUBSYSTEM_API = 2
    SUBSYSTEM_TRANSACTION = 3
    SUBSYSTEM_ADMIN = 4 



    def __init__(self, name : str, ):
        log.info(' Created task manager task')
        self.time_to_start = 0
        self.time_elapsed = 0
        self.name = ''
        self.subtasks = [] # Contains a List of Task requests to be actioned
        self.subtask_index = 0
        self.subsystems = []
        self.status = Task_Status.STATUS_CREATED
        self.task_uuid = uuid.uuid4()
        self.task_complete_callback = False
        self.task_error_callback = False

    def get_task_uuid(self):
        return self.task_uuid

    def set_subsystems(self, subsystems : list):
        self.subsystems = subsystems

    def add_subtask(self, subtask):
        log.info('Adding subtask {0}'.format(subtask))
        self.subtasks.append(subtask)

    def get_task_list(self):
        return self.subtasks

    def set_status(self, status):
        self.status = status

    def get_status(self):
        return self.status

    def get_current_subtask(self):
        try:
            if self.subtasks == []:
                raise Exception('Subtask list empty')
            else:
                return self.subtasks[self.subtask_index]

        except Exception as e:
            log.error(e)
            return False

    # Below is to do with Task scheduling

    def update_time_elapsed(self):
        if self.time_to_start == 0 :
            self.time_to_start = datetime.datetime.now()
        self.time_elapsed = datetime.datetime.now() - self.time_to_start
        self.time_elapsed = self.time_elapsed.total_seconds()
        #log.info('Task timelapsed: {0}'.format(self.time_elapsed))

    def set_start_time(self, start_time):
        try:
            if not isinstance(start_time, datetime.datetime):
                raise Exception('Start time os not a datetime object')
            log.info('setting task starttime to {0}'.format(start_time))
            self.time_to_start = start_time
            self.status = Task_Status.STATUS_READY
            return True

        except Exception as e:
            log.error(e)
            return False

    def dump_info(self):
        log.info("""
        Schedule Task Info
        Task Name: {0}
        Task UUID: {1}
        Status: {2}
        Subtasks List: {3}
        Current Subtask Index: {4}
        Times to start: {5}
        Time elapsed: {6}
        """.format(
            self.name,
            self.task_uuid,
            Task_Status.parse_task_status(self.status),
            self.subtasks,
            self.subtask_index,
            self.time_to_start,
            self.time_elapsed
        ))

class Taskmanager:

    def __init__(self):
        # Start each of the handlers
        db_configs = DB_Config()
        db_configs.db_path_and_filename = config.DB_CONFIG_PATH + config.DB_CONFIG_FILENAME
        self.db_h = DB_handler(db_configuration=db_configs)
        self.api_h = API_Handler()
        self.trans_h = Transaction_Handler()

        # Task manager task object goes here
        self.task_manager_task_obj = 0

        # All data ojbects for sceduling tasks
        self.current_time_date = datetime.datetime.now()
        log.info('Task Manager started at {0}'.format(self.current_time_date))
        self.pending_task_list = []
        self.done_task_list = []
        self.running_task_list = []
        self.task_to_ececute = 0 
        self.task_error_list = []  # Any tasks that have been in error state are put here for later actioning. 
        self.scheduler_running = False


    def execute_subtask(self, subtask):
        try:
            if isinstance(subtask, DB_task_request):
                log.info('Running DB Task UUID: {0}'.format(subtask.task_uuid))
                self.db_h.set_new_task(subtask)

                if self.db_h.execute_current_task():
                    self.db_h.clear_task()
                    return True
                else:
                    self.db_h.clear_task()
                    raise Exception(' Error in DB task completeion')

            if isinstance(subtask, API_task_request):
                log.info('Running API Task UUID: {0}'.format(subtask.task_uuid))
                self.api_h.set_new_task(subtask)
                if self.api_h.execute_current_task():
                    self.api_h.clear_task()
                    return True
                else:
                    self.api_h.clear_task()
                    raise Exception(' Error in API task completeion')
            '''
            if isinstance(subtask, Updater):
                log.info('Running Update Task UUID: [0}'.format(subtask.task_uuid))
            '''
        except Exception as e:
            log.error(e)
            return False


    def set_task(self, tm_task_obj):
        self.task_manager_task_obj = tm_task_obj

    def execute_task(self, task):
        try:
            self.set_task(task)
            self.task_manager_task_obj.set_status(Task_Status.STATUS_RUNNING)
            if self.task_manager_task_obj.subsystems == Task_Manager_Task.SUBSYSTEM_ADMIN:
                log.info('Perform Admin task')
                # Sets a task as complete to run the task complete callback
                self.task_manager_task_obj.status = Task_Status.STATUS_COMPLETE
                self.task_manager_task_obj.tasks_complete = True
            else:
                self.run_all_subtasks()
            return True

        except Exception as e:
            log.error(e)
            return False 

    def run_all_subtasks(self):
        log.info('subtasks are {0}'.format(self.task_manager_task_obj.get_task_list()))
        for subtask in self.task_manager_task_obj.get_task_list():
            ret = self.execute_subtask(subtask)
            if not ret:
                self.task_manager_task_obj.status = Task_Status.STATUS_ERROR
                self.task_manager_task_obj.tasks_complete = True
                return False
        self.task_manager_task_obj.status = Task_Status.STATUS_COMPLETE
        self.task_manager_task_obj.tasks_complete = True


    def append_task_list(self, t_m_task):
        try:
            if not isinstance(t_m_task, Task_Manager_Task):
                raise Exception('Task is not sceduler task type')
            if t_m_task.status == Task_Status.STATUS_READY:
                t_m_task.status = Task_Status.STATUS_QUEUED
                self.pending_task_list.append(t_m_task)
                log.info('added task to pending list uuid:{0}'.format(t_m_task.get_task_uuid()))
            else:
                raise Exception('Schduler rtask not ready')

        except Exception as e:
            log.error(e)
            return False


    def get_task_by_uuid(self, uuid): 
        try:
            for task in self.pending_task_list:
                if task.get_task_uuid() == uuid:
                    return task

            for task in self.done_task_list:
                if task.get_task_uuid() == uuid:
                    return task
                
            for task in self.task_error_list:
                if task.get_task_uuid() == uuid:
                    return task
            raise Exception('Task with uuid: {0} not found in scheduler'.format(uuid))

        except Exception as e:
            log.error(e)
            return False
        
    def clear_pending_list(self):
        self.pending_task_list = []
        pass

    def clear_done_list(self):
        pass

    def get_error_list(self):
        return self.task_error_list


    # Scheduling related 
    def tick(self):  # This tells the schduler to periodicaly check if there are any tasks due and execute them
        #log.info('Doing Task manager Tick')
        self.current_time_date = datetime.datetime.now()
        #log.info('Checking for tasks in tasklist')
        if self.pending_task_list:
            self.scheduler_running = True
        else:
            log.warning('Scheduler pending task list is empty')

        # Removing completed or errored tasks from pending list
        for task in self.pending_task_list:
            if task.status == Task_Status.STATUS_COMPLETE:
                log.info('Adding task to Completed list UUID: {0}'.format(task.get_task_uuid()))
                self.done_task_list.append(task)
                self.remove_task_by_uuid(task_uuid=task.get_task_uuid(), from_pending=True)
                # can be used to set off a call back routine
                if task.task_complete_callback:
                    task.task_complete_callback(task.get_task_uuid())

            elif task.status == Task_Status.STATUS_ERROR:
                log.info('Adding task to Error list UUID: {0}'.format(task.get_task_uuid()))
                self.task_error_list.append(task)
                self.remove_task_by_uuid(task_uuid=task.get_task_uuid(), from_pending=True)
                # can be used to set off a call back routine
                if task.task_error_callback:
                    task.task_error_callback(task.get_task_uuid())
        # Checking to see if a pending task is ready to execute
        #log.info(self.pending_task_list)
        for task in self.pending_task_list:
            if task.status == Task_Status.STATUS_QUEUED:
                task.update_time_elapsed()
                #log.info('task with UUID: {0} time tampsed: {1}'.format(task.get_task_uuid(), task.time_elapsed))
                if task.time_elapsed > 0:
                    log.info('Executing task {0} as time elapsed is {1}'.format(task.get_task_uuid(), task.time_elapsed))
                    self.execute_task(task=task)

    def remove_task_by_uuid(self, task_uuid, from_pending=False):
        try:
            log.info('removing task from list uuid:{0}'.format(task_uuid))
            if from_pending:
                for task_index in range(len(self.pending_task_list)):
                    if self.pending_task_list[task_index].get_task_uuid() == task_uuid:
                        self.pending_task_list.pop(task_index)
                        log.info('removed task from pending list uuid:{0}'.format(task_uuid))
                        return True
            else:
                for task_index in range(len(self.done_task_list)):
                    if self.done_task_list[task_index].get_task_uuid() == task_uuid:
                        self.done_task_list.pop(task_index)
                        log.info('removed task from done list uuid:{0}'.format(task_uuid))
                        return True
        except Exception as e:
            log.error(e)
            return False


    def get_errored_task_by_uuid(self, task_uuid):
        try:
            log.info('looking for errored task with uuid:{0}'.format(task_uuid))
            for task_index in range(len(self.done_task_list)):
                if self.done_task_list[task_index].get_task_uuid() == task_uuid:
                    self.done_task_list.pop(task_index)
                    log.info('removed task from done list uuid:{0}'.format(task_uuid))
                    return True
            raise Exception('Task not found in error task list')

        except Exception as e:
            log.error(e)
            return False

