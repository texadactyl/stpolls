"""
State Polling utility functions
"""
import sys
import os
from time import strftime, localtime
import datetime
import pandas as pd
import numpy as np

from stpolls_data_defs import StatePollRecord, DEBUGGING

CSV_DELIM = ","
ORDERCOLS = ["Day", "Len", "State", "EV", "Dem", "GOP", "Pollster"]
FMT_LOGGER_TIMESTAMP = "%Y-%m-%d %H:%M:%S "
FMT_DATE = "%Y-%m-%d"
JAN1 = str(datetime.datetime.now().year) + '-01-01'
FMT_ISO_DATE = "%Y-%m-%d"


def logger(arg_string):
    """
    Time-stamp logger
    """
    now = strftime(FMT_LOGGER_TIMESTAMP, localtime())
    print("{} {}".format(now, arg_string), flush=True)


def oops(arg_string):
    """
    Report an error and exit to the O/S.
    """
    logger("*** Oops, " + arg_string)
    sys.exit(86)


def yday2str(arg_yday):
    """
    Convert a yday to a string of the form 2020-mm-dd
    """
    if not hasattr(arg_yday, "__len__"):
       return str(np.datetime64(JAN1) + np.timedelta64(arg_yday - 1, 'D'))
    str_array = []
    for yday in arg_yday:
        str_array.append(str(np.datetime64(JAN1) + np.timedelta64(yday - 1, 'D')))
    return str_array


def now2yday():
    """
    Convert now to a yday
    """
    now = strftime(FMT_DATE, localtime())
    return int((np.datetime64(now) - np.datetime64(JAN1) - 1) / np.timedelta64(1, 'D'))


def invalid_integer(arg_integer):
    """
    Return True if arg_integer is not an integer; else return False.
    """
    return bool(not isinstance(arg_integer, int))


def getcsv(arg_file_path):
    """
    Given a CSV file path,
        Transform CSV input list to a StatePollRecord list.
        Return the list to caller.
    """
    if DEBUGGING:
        print("DEBUG getcsv: arg_file_path =", arg_file_path)
    # Read in the CSV file into a raw Pandas DataFrame.
    # Then, extract the columns we want and re-order them.
    try:
        raw_data_frame = pd.read_csv(arg_file_path, comment="#", sep=",", usecols=range(16))
        wk_data_frame = raw_data_frame[ORDERCOLS]
        if DEBUGGING:
            print("DEBUG getcsv: wk_data_frame size=", len(wk_data_frame))
            print("DEBUG getcsv wk_data_frame:\n{}".format(wk_data_frame))
    except KeyError as err:
        oops("getcsv pandas.read_csv({})\nKeyError, heading and data columns not 1:1?\n{}"
             .format(arg_file_path, str(err)))
    except ValueError as err:
        oops("getcsv pandas.read_csv({})\nValueError, {}"
             .format(arg_file_path, str(err)))
    except Exception as err:
        oops("getcsv pandas.read_csv({}) failed, unanticipated Exception:\n{}"
             .format(arg_file_path, str(err)))
    # For each DataFrame row, process the data.
    try:
        count = 0
        outlist = []
        # Get source date
        for col in wk_data_frame.itertuples():
            record = StatePollRecord()
            # Throw out left-most pandas data frame column which is a rowid (row[0])
            # Get region
            record.start_yday = int(col[1] - 0.5 * col[2])
            record.end_yday = col[2] + record.start_yday - 1
            record.state = col[3]
            record.ev = col[4]
            record.pct_dem = col[5]
            record.pct_gop = col[6]
            record.pollster = col[7]
            outlist.append(record)
            count += 1
            del col
    except ValueError as err:
        oops("getcsv outlist building encountered ValueError, URL={}, count={}:\n{}"
             .format(arg_file_path, count, str(err)))
    except Exception as err:
        oops("getcsv outlist building failed, URL={}, count={}:\n{}"
             .format(arg_file_path, count, str(err)))
    logger("getcsv: File {}: processed {} CSV records"
           .format(os.path.basename(arg_file_path), count))
    return outlist
