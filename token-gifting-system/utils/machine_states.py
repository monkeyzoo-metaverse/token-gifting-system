# A class contain all common uses states for the various statemachine in YMS

class State:

    STATE_UPDATE_SCHEDULED = 5
    STATE_UPDATE_COMPLETE = 4
    STATE_FETCH_DB_ONWERSHIP_RECORD = 1
    STATE_FETCH_API_ONWERSHIP_DATA = 2
    STATE_UPDATE_DB_OWNERSHIP_RECORD = 3

    STATE_DISTRO_SCHEDULED = 0
    STATE_DISTRO_FETCH_TRANSACTION_RECORD = 1