from task_manager.task_manager import Taskmanager
from updater.updater import Updater
from distribution.distribution import disrubtior
from utils.log import log
import datetime
import time
import curses
import config
from frontend.curses_display import Curses_Display


class YMS_Status:

    def __init__(self):
        self.current_time = datetime.datetime.now()
        self.updater_auto_mode = False
        self.last_update_cycle_run = None
        self.nft_index_currently_running = None
        self.collection_total = config.COLLECTION_MAX_NFT_INDEX
        self.status = 1
        self.transaction_auto_mode = False
        self.retries = 0
        self.xch_available = 0
        self.tokens_available = 0
        self.current_transaction_info = 0
        self.current_nft_ownership_info = 0
        self.transactions_waiting = 0
        self.transactions_submitted = 0
        self.tranactions_complete = 0




def task_manager_loop():

    #log.info('Schduler program loop')
    # cli.write_in_debug('Schduler Loop Tick !!')
    update.task_manager.tick()

def update_sys_info():
    sys_info.xch_available = dist.transaction_handler.xch_wallet.total_balance
    sys_info.tokens_available = dist.transaction_handler.token_wallet.total_balance
    sys_info.transaction_auto_mode = dist.auto_mode
    sys_info.transactions_waiting = len(dist.transaction_records)
    sys_info.transactions_waiting, sys_info.transactions_submitted = dist.count_tranaction_states()
    


def main_loop():
    while 1:
        log.debug('mainloop tick')
        sys_info.nft_index_currently_running = update.current_task_record_index
        task_manager_loop()
        dist.distribution_tick()
        cli.draw_YMS_info(sys_info)
        update_sys_info()
        log.debug('Pending tasks{0}'.format(update.task_manager.pending_task_list))
        log.debug('Done tasks{0}'.format(update.task_manager.done_task_list))
        log.debug('Error tasks{0}'.format(update.task_manager.task_error_list))

        # Updater cycle auto
        if update.update_state == update.STATE_UPDATE_COMPLETE or update.update_state == update.STATE_UPDATE_SKIPPED:

            log.info('last completed update cycle task was: {0}'.format(update.current_task_record_index))
            if update.current_task_record_index < config.COLLECTION_MAX_NFT_INDEX:
                update.start_updating_record(update.current_task_record_index + 1)
            else:

                update.last_cycle_complete = datetime.datetime.now()
                sys_info.last_update_cycle_run = update.last_cycle_complete
                log.info('Updater complete at: {0}'.format(update.last_cycle_complete))
                
                # Get the current time
                current_time = datetime.datetime.now()
                # reset updater and set ready to start in 1 day at configured time
                update.start_updating_record(1,
                    datetime.datetime(
                    year=current_time.year,
                    month=current_time.month,
                    day=current_time.day + config.UPDATER_DELTA_DAY,
                    hour=config.UPDATER_HOUR,
                    minute=config.UPDATER_MINUTE
                    ))
                # Once the updater has completed the distributor run should start
                
                dist.set_auto_start_task(start_time=datetime.datetime(
                    year=current_time.year,
                    month=current_time.month,
                    day=current_time.day,
                    hour=current_time.hour,
                    minute=current_time.minute,
                    second=current_time.second
                    ))
                
        # Slight delay to prevent overloading server runtime
        time.sleep(0.1)


def main():

    try:
        log.info('Starting CLI')
        log.info('Starting main_loop')
        update.start_updating_record(1)
        main_loop()

    except Exception as e:
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        log.error(e)
        exit()

# Create required instances
tm = Taskmanager()
cli = Curses_Display()
update = Updater(task_manager=tm)
dist = disrubtior(tm)
sys_info = YMS_Status()

main()
