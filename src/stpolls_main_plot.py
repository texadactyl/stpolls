"""
State Polling Database Plot Program
"""

import sys

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import stpolls_utilities as utl
import stpolls_db_api as db_api
from stpolls_data_defs import DB_PATH, DEBUGGING

PLOT_BASE = "poll_plots/{}.png"
DATE_ROTATION = 45 # degrees
DATE_SPACER = 3 # number of days
MARKER = '*'

def show_help():
    """
    Show command-line help and exit to the O/S.
    """
    print("\nUsage:  python3  stpolls_main_plot.py\n")
    sys.exit(86)

def plotter(arg_state, arg_ev, arg_yday, arg_dem, arg_gop, arg_tbd):
    """
    Create a plot for confirmed/deceased as a function of ordinal dates
    since 2019-12-31.

    Arguments:
        arg_state: name of STATE
        arg_yday: array of integer ydays
        arg_dem: array of Democrat pct
        arg_gop: array of GOP pct

    A plot is generated and saved.
    """
    dt = utl.yday2str(arg_yday)
    plt.figure(dpi=300)
    plt.format_xdata = mdates.DateFormatter(utl.FMT_ISO_DATE)
    plt.plot(dt, arg_dem, label='Dems', color='blue', marker=MARKER)
    plt.plot(dt, arg_gop, label='GOP', color='red', marker=MARKER)
    plt.plot(dt, arg_tbd, label='*TBD*', color='green', marker=MARKER)
    plt.grid(which='major', linestyle='-', linewidth='0.5', color='green')
    plt.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
    plt.xlabel("Poll Date")
    plt.ylabel("Polling Pct")
    plt.title("State: {} ({})".format(arg_state, arg_ev))
    legend = plt.legend(loc='upper left', shadow=False)
    legend.get_frame().set_facecolor("beige")
    plt.gca().xaxis.set_major_locator(plt.MultipleLocator(DATE_SPACER))
    plt.gcf().autofmt_xdate(rotation=DATE_ROTATION, ha="right")
    plot_path = PLOT_BASE.format(arg_state)
    plt.savefig(plot_path, format="png", dpi=300)
    utl.logger("Generated {}".format(plot_path))
    plt.close(fig="all")

#==========================================================================
# Main program
#==========================================================================
if __name__ != "__main__":
    utl.oops("stpolls_main_plot: Must be a main program")
if sys.version_info[0] < 3:
    utl.oops("stpolls_main_plot: Requires Python 3 or later")

# Process command-line arguments
NARGS = len(sys.argv)
if NARGS != 1: # There are no command line parameters.
    show_help()

# Retrieve the list of states.
utl.logger("stpolls_main_plot: connecting to database {}".format(DB_PATH))
try:
    db_handle = db_api.DbApi(DB_PATH)
except:
    utl.oops('stpolls_main_plot: Something went wrong during database connection.')
STATE_LIST = db_handle.db_get_state_list_records()
if DEBUGGING:
    utl.logger('DEBUG stpolls_main_plot: STATE_LIST={}'.format(STATE_LIST))

# For each state, plot it.
count_states = 0
for state, ev in STATE_LIST:
    count_states += 1
    state_records = db_handle.db_get_state_poll_records(state)
    end_yday = []
    dem_pct = []
    gop_pct = []
    tbd_pct = []
    ii = 0
    for row in state_records:
        if DEBUGGING:
            ii += 1
            print('DEBUG stpolls_main_plot: {} {} row={}'.format(state, ii, row))
        end_yday.append(row[0])
        dem_pct.append(row[2])
        gop_pct.append(row[3])
        tbd_pct.append(100 - dem_pct[-1] - gop_pct[-1])
    plotter(state, ev, end_yday, dem_pct, gop_pct, tbd_pct)

# Close database.
db_handle.db_close()
utl.logger("stpolls_main_plot: End, created {} state plots".format(count_states))
