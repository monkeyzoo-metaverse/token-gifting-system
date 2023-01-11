# from nfttracking.apis import mintgardenTestNet as primary  # For testing
import config
if config.ISTESTNET:
    from nfttracking.apis import mintgardenTestNet as primary
    from nfttracking.apis import spacescanTestNet as secondary
else:
    from nfttracking.apis import mintgarden as primary
    from nfttracking.apis import spacescan as secondary
from utils.task_requests import API_task_request, Task_Status
from utils.log import log
import time


class API_Handler:

    def __init__(self, primary=primary, secondary=secondary, default_timeout=10000):
        self.timeout = default_timeout
        self.primary_connection_status = False
        self.secondary_connection_status = False
        self.apis_available = False
        self.prefer_secondary = False
        self.primary = primary
        self.secondary = secondary
        self.task = 0
        self.task_started = False
        self.task_complete = False

    def check_connections(self):
        log.info('Checking connection to available APIs')

        if self.primary.check_connection() is True:
            self.primary_connection_status = True
            self.apis_available = True
            log.info('Primary API available')
        else:
            self.primary_connection_status = False
            self.apis_available = False

        if self.secondary.check_connection() is True:
            self.secondary_connection_status = True
            self.apis_available = True
            log.info('Secondary API available')

            if self.primary_connection_status is False:
                log.info('Setting Secondary as Prefered API')
                self.prefer_secondary = True
            else:
                self.prefer_secondary = False

        else:
            self.secondary_connection_status = False

    def set_task_complete(self):
        self.task_complete = True
        self.task.task_status = Task_Status.STATUS_COMPLETE
        return True  # Little flag to let system know all is well

    def clear_task(self):
        self.task = 0

    """
    This section is purly for handling the tasks
    """

    def set_new_task(self, task):
        log.info('{1}.{2}| Adding new task uuid: {0}'.format(task.task_uuid, type(self), self.set_new_task.__name__))
        assert isinstance(task, API_task_request)  # Type check to make sure the correct arg type is passed in
        try:
            if (self.task != 0):
                raise Exception('Previous task has not been cleared from handler')

            if (self.task_started and not self.task_complete):
                raise Exception('Current Task still running')
            if (task.check_task_ready()):  # Final checkthat the task is read other wise thow exception
                self.task = task
                self.task.task_began_at = time.time()
                self.task_uuid = self.task.task_uuid  # Set the hander uuid to tasks_uuid
                log.info('task {0} has been added to api handler'.format(self.task_uuid))
            else:
                raise Exception('Task is not ready to be actioned by  handler plase check task data members are all correct')

            return True

        except Exception as e:
            log.error(e, extra={'className': self.__class__.__name__})
            return False

    def get_current_owner_single(self):
        try:
            log.info('Checking connection to Primary api: {0}'.format(primary.api_plugin.name))
            self.check_connections()
            if (self.primary_connection_status):
                log.info('setting ')
                self.primary.set_nft_id(self.task.get_record_data_object().get_nft_record().nft_id)
                log.info('Set NFT id to {0}'.format(self.primary.api_plugin.parameter))
                log.info("Raw json from request: {0}".format(self.primary.get_raw()))
                self.task.record_data_obj.set_new_owner(self.primary.get_owner())
                return True
            elif (self.secondary_connection_status):
                log.info('setting ')
                self.secondary.set_nft_id(self.task.get_record_data_object().get_nft_record().nft_id)
                log.info('Set NFT id to {0}'.format(self.secondary.api_plugin.parameter))
                log.info("Raw json from request: {0}".format(self.secondary.get_raw()))
                self.task.record_data_obj.set_new_owner(self.secondary.get_owner())
                return True

            else:
                raise Exception('Task not completed')
                return False

        except Exception as e:
            log.error(e, extra={'className': self.__class__.__name__})
            return False

    def execute_current_task(self, task_complete_callback=None):

        try:
            log.info('Executing Api task uuid: {0}'.format(self.task_uuid))
            if (self.task == 0):
                raise ValueError('No current task set')
            self.task.task_status = Task_Status.STATUS_RUNNING
            self.task_started = True
            if (self.task.task_action == API_task_request.TASK_GET_CONNECTION_ID):
                pass
            if (self.task.task_action == API_task_request.TASK_GET_NFT_OWNER_SINGLE):
                log.info('Getting current ownerdata for NFT')
                if (self.get_current_owner_single()):
                    self.set_task_complete()
                else:
                    raise Exception('Task incomplete: {0}'.format(self.task_uuid))

            if (self.task.task_action == API_task_request.TASK_GET_COLLECTION_DATA):
                pass
            # The following callback can be used to notifiy that the current task is ready for collection
            if task_complete_callback:
                task_complete_callback()

            return True

        except Exception as e:
            log.error(e, extra={'className': self.__class__.__name__})
            return False

    def get_task(self):
        return self.task
