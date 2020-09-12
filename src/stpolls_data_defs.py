"""
State polling data definitions
"""

DEBUGGING = False

TABLE_POLL_RECORDS = "tbl_poll_records"
COL_START_YDAY = "start_yday"
COL_END_YDAY = "end_yday"
COL_STATE = "state"
COL_EV = "ev"
COL_DEM_PCT = "dem_pct"
COL_GOP_PCT = "gop_pct"
COL_POLLSTER = "pollster"
IX_STATE_END_YDAY = 'ix_state_yday'

TABLE_LIST_STATES = "tbl_state_list"
COL_LIST_STATE = "list_state"
COL_LIST_EV = "list_ev"

DATA_DIR = "data"
DB_FILE = "stpolls.db"
DB_PATH = DATA_DIR + "/" + DB_FILE

AGE_THRESHOLD = 124 # days, the oldest poll permitted for significance
PATH_OUT_CSV = DATA_DIR + "/" + 'analysis.csv'
PCT_DIFF_SIG_DIGS = 3 # % difference below which makes a Dem-GOP comparison insignificant


class StatePollRecord:
    """
    Object definition from each CSV line
    """


    def __init__(self):
        self.start_yday = 0   # Start yday [integer]
        self.end_yday = 0     # End yday [integer]
        self.state = "???"    # State [string]
        self.ev = 0           # Electoral votes [integer]
        self.dem_pct = 0.     # % Democrat [float]
        self.gop_pct = 0.     # % GOP [float]
        self.pollster = "???" # Polling organization


    def to_string(self):
        return 'start: ' + str(self.start_yday) + ', end: ' + str(self.end_yday) \
            + ', st: ' + self.state + ', ev: ' + str(self.ev) + ', dem%: ' \
            + str(self.dem_pct) + ', gop%: ' + str(self.gop_pct) + ', pollster: ' + self.pollster

class StateCalcs:
    
    def __init__(self):
        self.last = 'rubbish'    # Last poll date
        self.dem_ave = 0.0      # Average of the last N polls (Dem)
        self.dem_ev = 0.0       # EVs awarded (Dem)
        self.dem_pev = 0.0      # EVs awarded based on popular vote (Dem)
        self.dem_score = 0.0    # Trend score, weighted by EV (Dem)
        self.gop_ave = 0.0      # Average of the last N polls (GOP)
        self.gop_ev = 0.0       # EVs awarded (GOP)
        self.gop_pev = 0.0      # EVs awarded based on popular vote (GOP)
        self.gop_score = 0.0    # Trend score, weighted by EV (GOP)
        self.tbd_ave = 0.0      # Average of the last N polls (TBD)
        self.tbd_score = 0.0    # Trend score, weighted by EV (TBD)
        self.gaining = 'rubbish'
        self.losing = 'rubbish'
