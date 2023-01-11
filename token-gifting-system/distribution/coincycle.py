import config

class CoinCycler:

    def __init__(self, taskmanager):
        self.taskmanager = taskmanager
        self.xch_coin_threshold = config.MINIMUM_XCH_COINS
        self.token_coin_threshold = config.MINIMUM_TOKEN_COINS
        self.address = ''

    