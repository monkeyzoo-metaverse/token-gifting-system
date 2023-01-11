import curses



class Curses_Display:
    def __init__(self):
        self.queued_tasks = 0
        self.curses_inst = curses.initscr()
        self.height = 0
        self.width = 0
        self.mode_display = 'MANUAL'
        self.input_buffer = ''
        self.height, self.width = self.curses_inst.getmaxyx()
        self.dist_col = int(self.width / 2) 
        self.debug_window = curses.newwin(self.height - 1, int((self.width - 1) /2), 0, int(self.width / 2))
        curses.echo()
        
    def draw_YMS_info(self, yms_info):
        self.curses_inst.clear()
        self.curses_inst.addstr(6, 0, 'Updater in Auto mode: {0}'.format(yms_info.updater_auto_mode))
        self.curses_inst.addstr(7, 0, 'Current Updater Index: {0} of a total: {1} NFTs'.format(yms_info.nft_index_currently_running, yms_info.collection_total))
        self.curses_inst.addstr(8, 0, 'Updater last run: {0}'.format(yms_info.last_update_cycle_run))
        self.curses_inst.addstr(6, self.dist_col, 'Distributor:'.format(yms_info.last_update_cycle_run))
        self.curses_inst.addstr(7, self.dist_col, 'XCH:{0}'.format(yms_info.xch_available))
        self.curses_inst.addstr(8, self.dist_col, 'Tokens:{0}'.format(yms_info.tokens_available))
        self.curses_inst.addstr(9, self.dist_col, 'Auto mode:{0} '.format(yms_info.transaction_auto_mode))
        self.curses_inst.addstr(10, self.dist_col, 'Trans waiting:{0} '.format(yms_info.transactions_waiting))
        self.curses_inst.addstr(11, self.dist_col, 'Trans submitted:{0} '.format(yms_info.transactions_submitted))
        self.draw_background()
        self.curses_inst.refresh()
        self.debug_window.refresh()

    def draw_background(self):
        self.curses_inst.addstr(0, 0, "YMS Cli",curses.A_REVERSE)
        self.curses_inst.addstr(1, 0, "a = AutomaticMode")
        self.curses_inst.addstr(2, 0, "u = Manual updater run") 
        self.curses_inst.addstr(3, 0, "Mode: {0}".format(self.mode_display),curses.A_REVERSE)
        self.curses_inst.addstr(4, 0, "Input Buffer: {0}".format(self.input_buffer),curses.A_REVERSE)
        #self.curses_inst.addstr(self.height - 1, 0, 'Screen X: {0} Y: {1}'.format(self.width, self.height))
        self.curses_inst.refresh()
        '''
        if self.curses_inst.getkey() == ord('a'):
            if self.mode_display == 'MANUAL':
                self.mode_display = 'AUTO'
                self.input_buffer = 'a'
            else:
                self.mode_display = 'MANUAL'
                self.input_buffer = 'm'
        
        '''
    def update(self):
        self.draw_background

            

        #self.curses_inst.refresh()
        #self.debug_window.refresh()

    def exit():
        curses.endwin()

