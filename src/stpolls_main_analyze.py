"""
PyCases Database Analysis Program
"""

import sys

import stpolls_utilities as utl
import stpolls_db_api as db_api
from stpolls_data_defs import DB_PATH, StateCalcs, AGE_THRESHOLD, PATH_OUT_CSV, PCT_DIFF_SIG_DIGS

TRACING = False


def show_help():
    """
    Show command-line help and exit to the O/S.
    """
    print("\nUsage:  python3  stpolls_main_analyze.py\n")
    sys.exit(86)


def get_score(arg_ev, arg_vect_3):
    '''
    Given a vector of 3 percentages, compute the raw score:
        2:  100% increasing
        1:  Last 1 increased
        0:  Last 2 or 3 equal
        -1: Last 1 decreased
        -2: 100% decreasing
    Then, weight the score by the number of EVs.
    '''
    if arg_vect_3[1] == arg_vect_3[2]:
        return 0
    if arg_vect_3[0] < arg_vect_3[1] < arg_vect_3[2]:
        return 2 * arg_ev
    if arg_vect_3[0] > arg_vect_3[1] > arg_vect_3[2]:
        return -2 * arg_ev
    if arg_vect_3[1] < arg_vect_3[2]:
        return 1 * arg_ev
    # arg_vect_3[1] > arg_vect_3[2]:
    return -1 * arg_ev


def look_at(arg_ev, arg_vec_3):
    '''
    Each vector: end_yday, ev, dem%, gop%)
    Report Lead and EV effect.
    Report both Dem and GOP scores.
    '''
    if TRACING:
        utl.logger('TRACE look_at: ev={}, last 3={}'.format(arg_ev, arg_vec_3))
    sc = StateCalcs
    tbd_vec = [100 - arg_vec_3[0][2] - arg_vec_3[0][3],
           100 - arg_vec_3[1][2] - arg_vec_3[1][3],
           100 - arg_vec_3[2][2] - arg_vec_3[2][3]]
    sc.dem_score = get_score(arg_ev, [arg_vec_3[0][2], arg_vec_3[1][2], arg_vec_3[2][2]])
    sc.gop_score = get_score(arg_ev, [arg_vec_3[0][3], arg_vec_3[1][3], arg_vec_3[2][3]])
    sc.tbd_score = get_score(arg_ev, tbd_vec)
    sc.dem_ave = (arg_vec_3[0][2] + arg_vec_3[1][2] + arg_vec_3[2][2]) / 3
    sc.gop_ave = (arg_vec_3[0][3] + arg_vec_3[1][3] + arg_vec_3[2][3]) / 3
    sc.tbd_ave = (tbd_vec[0] + tbd_vec[1] + tbd_vec[2]) / 3
    if abs(sc.dem_ave - sc.gop_ave) < PCT_DIFF_SIG_DIGS:
        sc.dem_ev = 0
        sc.gop_ev = 0
    elif sc.dem_ave > sc.gop_ave:
        sc.dem_ev = arg_ev
        sc.gop_ev = 0
    else: # arg_vec_3[2][2] < arg_vec_3[2][3]:
        sc.dem_ev = 0
        sc.gop_ev = arg_ev
    sc.dem_pev = sc.dem_ave * arg_ev / 100
    sc.gop_pev = sc.gop_ave * arg_ev / 100
    sc.tbd_pev = arg_ev - sc.dem_pev - sc.gop_pev

    maxie = max(sc.dem_score, sc.gop_score, sc.tbd_score)
    if maxie == sc.dem_score:
        sc.gaining = 'Dem'
    elif maxie == sc.gop_score:
        sc.gaining = 'GOP'
    else:
        sc.gaining = 'TBD'
       
    minnie = min(sc.dem_score, sc.gop_score, sc.tbd_score)
    if minnie == sc.dem_score:
        sc.losing = 'Dem'
    elif minnie == sc.gop_score:
        sc.losing = 'GOP'
    else:
        sc.losing = 'TBD'
    
    return sc


#==========================================================================
# Main program
#==========================================================================
if __name__ != "__main__":
    utl.oops("stpolls_main_analyze: Must be a main program")
if sys.version_info[0] < 3:
    utl.oops("stpolls_main_analyze: Requires Python 3 or later")

# Process command-line arguments
NARGS = len(sys.argv)
if NARGS != 1: # There are no command line parameters.
    show_help()

# Retrieve the list of states.
utl.logger("stpolls_main_analyze: connecting to database {}".format(DB_PATH))
try:
    db_handle = db_api.DbApi(DB_PATH)
except:
    utl.oops('stpolls_main_analyze: Something went wrong during database connection.')
STATE_LIST = db_handle.db_get_state_list_records()
if TRACING:
    utl.logger('DEBUG stpolls_main_analyze: STATE_LIST={}'.format(STATE_LIST))

csvfd = open(PATH_OUT_CSV, 'w')
csvfd.write('state, Last Poll,, Dem EVs, GOP EVs, TBD EVs,, Dem Pop EVs, GOP Pop EVs, '
            + 'TBD Pop EVs,, Dem Ave Pct, GOP Ave Pct, TBD Ave Pct,, Dem Score, '
            + 'GOP Score, TBD Score,, Gaining, Losing\n')

# For each state, analyze.
dem_total_ev = 0
gop_total_ev = 0
now_yday = utl.now2yday()
csv_row_count = 1
insuff_data = []
too_old = []
for state, ev in STATE_LIST:
    ROW_LIST = db_handle.db_get_state_poll_records(state)
    ROW_COUNT = len(ROW_LIST)
    if ROW_COUNT < 1:
        utl.logger("No data available for STATE: {}".format(state))
    if TRACING:
        utl.logger("Fetched {} rows for STATE: {}".format(ROW_COUNT, state))
    if ROW_COUNT < 3:
        insuff_data.append(state)
        if TRACING:
            utl.logger("insuff_dataicient data available for STATE: {}".format(state))
        continue
    last_3 = [ROW_LIST[-3], ROW_LIST[-2], ROW_LIST[-1]]
    # Each row: end_yday, ev, dem%, gop%)
    if TRACING:
        utl.logger('TRACE stpolls_main_analyze: state={}, ev={}, last 3={}, end_yday={}'
                   .format(state, ev, last_3, last_3[0][0]))
    if now_yday - last_3[0][0] > AGE_THRESHOLD:
        too_old.append(state)
        if TRACING:
            utl.logger("Data too old for STATE: {}".format(state))
        continue
    stc = look_at(ev, last_3)
    stc.last = utl.yday2str(last_3[2][0])
    dem_total_ev += stc.dem_ev
    gop_total_ev += stc.gop_ev
    fmt = '{},{},,{:.1f},{:.1f},,,{:.1f},{:.1f},{:.1f},,{:.1f},{:.1f},{:.1f}' \
        + ',,{:.1f},{:.1f},{:.1f},,{},{}\n'
    csvfd.write(fmt
          .format(state, stc.last, stc.dem_ev, stc.gop_ev, stc.dem_pev, stc.gop_pev,
                  stc.tbd_pev, stc.dem_ave, stc.gop_ave, stc.tbd_ave, stc.dem_score, 
                  stc.gop_score, stc.tbd_score, stc.gaining, stc.losing))
    csv_row_count += 1

# Close database.
db_handle.db_close()
csvfd.write('\n')
tbd_total_ev = 538 - dem_total_ev - gop_total_ev
fmt = 'TOTALS,,,=sum(d2:d{row}),=sum(e2:e{row}),{tbd_ev},,=sum(h2:h{row}),=sum(i2:i{row})' \
        + ',=sum(j2:j{row}),,,,,,=sum(p2:p{row}),=sum(q2:q{row}),=sum(r2:r{row})\n'
csvfd.write(fmt.format(row=csv_row_count, tbd_ev=tbd_total_ev))
csvfd.close()
utl.logger('Number of qualifying states: {}'.format(csv_row_count - 1))
utl.logger('States ({}) with out of date polls: {}'.format(len(too_old), too_old))
utl.logger('States ({}) with insufficient poll data: {}'.format(len(insuff_data), insuff_data))
utl.logger('Poll age threshold used: {} days'.format(AGE_THRESHOLD))
utl.logger('Difference threshold between Dem & GOP: {} %'.format(PCT_DIFF_SIG_DIGS))
utl.logger("stpolls_main_analyze: End")
