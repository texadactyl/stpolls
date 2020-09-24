"""
stpolls Database Load Program
* Rename existing database.
* Load new database from all CSV file content.
"""

import os.path
import sys

import stpolls_utilities as utl
import stpolls_db_api as db_api
from stpolls_data_defs import DATA_DIR, DB_PATH, DB_PATH_LAST, DEBUGGING


def show_help():
    """
    Show command-line help and exit to the O/S.
    """
    print("\nUsage: python3 stpolls_dbload.py\n")
    sys.exit(0)


#==========================================================================
# Main program
#==========================================================================
if __name__ != "__main__":
    utl.oops("stpolls_main_load: Must be a main program")
if sys.version_info[0] < 3:
    utl.oops("stpolls_main_load: Requires Python 3 or later")

# Process command-line arguments
NARGS = len(sys.argv)
if NARGS != 2: # There is 1 command line parameter.
    show_help()
csv_path = sys.argv[1]

# Make sure that the data directory exists.
if not os.path.exists(DATA_DIR):
    try:
        os.mkdir(DATA_DIR)
    except Exception as err:
        utl.oops("stpolls_main_load: Cannot create directory {}:\n{}".format(DATA_DIR, str(err)))

# if the database file already exists, rename it
if os.path.exists(DB_PATH_LAST):
    os.remove(DB_PATH_LAST)

# if the database file already exists, rename it
if os.path.exists(DB_PATH):
    os.rename(DB_PATH, DB_PATH_LAST)

# Check the Database file for usability.
try:
    open(DB_PATH, 'wb').close()
except Exception as err:
    utl.oops("stpolls_main_load: Cannot create Database file {}\n{}".format(DB_PATH, str(err)))
try:
    open(DB_PATH, "rb").close()
except Exception as err:
    utl.oops("stpolls_main_load: Cannot open Database file {} for reading\n{}".format(DB_PATH, str(err)))

# Create/re-create the database.
utl.logger("stpolls_main_load: Database {} will be initialized".format(DB_PATH))
db_handle = db_api.DbApi(DB_PATH)
db_handle.db_init()

# Initialize CSV file processing
count_files = 0
count_records = 0

# Collect all of the data from the specified CSV file.
wklist = utl.getcsv(csv_path)
count_records += len(wklist)
if DEBUGGING:
    print("DEBUG stpolls_main_load from getcsv count=", len(wklist))

# For each CSV record
for record in wklist: # For each record in the CSV file
    # Insert/update report
    db_handle.db_add_one_record(record)

# Commit database activity and close database.
db_handle.db_close()
utl.logger("stpolls_main_load: End")
