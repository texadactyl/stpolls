"""
PyCases  Database Procedures
"""
from sqlite3 import connect, Error, IntegrityError
import stpolls_utilities as utl
import stpolls_data_defs as data_defs
from stpolls_data_defs import DEBUGGING


FMT_RETRIEVE_POLLING = "SELECT {end_yday}, {ev}, {dem}, {gop} FROM {tn}" \
    + " WHERE {key} = '{state}' ORDER BY {end_yday} ASC"

FMT_RETRIEVE_LIST = "SELECT ALL {state}, {ev} FROM {tn}"


class DbApi:
    
    DBCONN = None
    DBCURSOR = None
    
    
    def __init__(self, arg_db_path: str):
        self.db_connect(arg_db_path)
        

    def __del__(self):
        self.db_close()


    def db_get_state_list_records(self):
        """
        Retrieve all of the state poll records.
        """
        try:
            # Insert signature singleton record.
            str_retrieve = FMT_RETRIEVE_LIST \
                            .format(tn=data_defs.TABLE_LIST_STATES,
                                    state=data_defs.COL_LIST_STATE,
                                    ev=data_defs.COL_LIST_EV)
            if DEBUGGING:
                print("DEBUG db_state_list_records:", str_retrieve)
            self.DBCURSOR.execute(str_retrieve)
            return self.DBCURSOR.fetchall()
        except Error as err:
            utl.oops("db_get_state_list_records failed, sqlite3.Error:\n{}"
                     .format(str(err)))
        except Exception as err:
            utl.oops("db_get_state_list_records - unanticipated Exception:\n{}"
                     .format(str(err)))


    def db_get_state_poll_records(self, arg_state):
        """
        Retrieve state poll records for the given state.
        """
        try:
            # Insert signature singleton record.
            str_retrieve = FMT_RETRIEVE_POLLING \
                            .format(tn=data_defs.TABLE_POLL_RECORDS,
                                    key=data_defs.COL_STATE,
                                    state=arg_state,
                                    end_yday=data_defs.COL_END_YDAY,
                                    ev=data_defs.COL_EV,
                                    dem=data_defs.COL_DEM_PCT,
                                    gop=data_defs.COL_GOP_PCT)
            if DEBUGGING:
                print("DEBUG db_state_poll_records:", str_retrieve)
            self.DBCURSOR.execute(str_retrieve)
            return self.DBCURSOR.fetchall()
        except Error as err:
            utl.oops("db_get_state_poll_records failed, sqlite3.Error:\n{}"
                     .format(str(err)))
        except Exception as err:
            utl.oops("db_get_state_poll_records - unanticipated Exception:\n{}"
                     .format(str(err)))


    def db_add_one_record(self, arg_record: data_defs.StatePollRecord):
        """
        Add a poll record.
        Add a state list record if not already done previously.
        """
        try:
            # Insert one poll record.
            str_insert = "INSERT INTO {tn} VALUES "\
                "('{cv1}', '{cv2}', '{cv3}', '{cv4}', '{cv5}', '{cv6}', '{cv7}')"\
                .format(tn=data_defs.TABLE_POLL_RECORDS, 
                            cv1=arg_record.start_yday, cv2=arg_record.end_yday, 
                            cv3=arg_record.state, cv4=arg_record.ev, cv5=arg_record.pct_dem,
                            cv6=arg_record.pct_gop, cv7=arg_record.pollster)
            if DEBUGGING:
                print("DEBUG db_add_one_record:", str_insert)
            self.DBCURSOR.execute(str_insert)
            self.DBCONN.commit()
        except IntegrityError: # duplicate !!
            utl.oops("db_add_one_record Attempted DB duplicate insert:\n{}"
                     .format(str(arg_record.to_string())))
        except Error as err:
            utl.oops("db_add_one_record failed, unexpected sqlite3.Error:\n{}".format(str(err)))
        except Exception as err:
            utl.oops("db_add_one_record failed, unexpected Exception:\n{}".format(str(err)))
    
        try:
            # Insert one state record in the list of states.
            str_insert = "INSERT INTO {tn} VALUES ('{cv1}', '{cv2}')"\
                .format(tn=data_defs.TABLE_LIST_STATES, 
                            cv1=arg_record.state, cv2=arg_record.ev)
            if DEBUGGING:
                print("DEBUG db_add_one_record:", str_insert)
            self.DBCURSOR.execute(str_insert)
            self.DBCONN.commit()
        except IntegrityError: # duplicate - ignore
            if DEBUGGING:
                print("DEBUG db_add_one_record: Saw this state already (ignored)")
        except Error as err:
            utl.oops("db_add_one_record failed, unexpected sqlite3.Error:\n{}".format(str(err)))
        except Exception as err:
            utl.oops("db_add_one_record failed, unexpected Exception:\n{}".format(str(err)))

    
    def db_connect(self, arg_db_path: str):
        """
        Connect to database
        """
    
        try:
            self.DBCONN = connect(arg_db_path)
            self.DBCURSOR = self.DBCONN.cursor()
        except Error as err:
            utl.oops("db_connect failed, SQL Error:\n{}".format(str(err)))
    
    
    def db_init(self):
        """
        Initialize the database table.
        """
    
        # Drop old tables.
        try:
            # Delete old database tables.
            self.DBCURSOR.execute("DROP TABLE IF EXISTS {}".format(data_defs.TABLE_POLL_RECORDS))
        except Error as err:
            utl.oops("db_init: one of the DROP TABLE requests failed, SQL Error:\n{}"
                     .format(str(err)))
        if DEBUGGING:
            utl.logger("DEBUG db_init: Old table dropped")
    
        try:
            str_create_table = "CREATE TABLE {tn} "\
                    "({c1n} INTEGER, {c2n} INTEGER, {c3n} TEXT, {c4n} INTEGER, "\
                    "{c5n} REAL, {c6n} REAL, {c7n} TEXT, "\
                    "PRIMARY KEY({c7n}, {c3n}, {c1n}))"\
                    .format(tn=data_defs.TABLE_POLL_RECORDS,
                            c1n=data_defs.COL_START_YDAY,
                            c2n=data_defs.COL_END_YDAY,
                            c3n=data_defs.COL_STATE,
                            c4n=data_defs.COL_EV,
                            c5n=data_defs.COL_DEM_PCT,
                            c6n=data_defs.COL_GOP_PCT,
                            c7n=data_defs.COL_POLLSTER)
            if DEBUGGING:
                utl.logger("DEBUG db_init: {}".format(str_create_table))
            self.DBCURSOR.execute(str_create_table)

            str_create_table = "CREATE TABLE {tn} "\
                    "({c1n} TEXT, {c2n} INTEGER, "\
                    "PRIMARY KEY({c1n}))"\
                    .format(tn=data_defs.TABLE_LIST_STATES,
                            c1n=data_defs.COL_LIST_STATE,
                            c2n=data_defs.COL_LIST_EV)
            if DEBUGGING:
                utl.logger("DEBUG db_init: {}".format(str_create_table))
            self.DBCURSOR.execute(str_create_table)
    
        except Error as err:
            utl.oops("db_init: SQL Error in setting up one of the tables:\n{}"
                     .format(str(err)))
        if DEBUGGING:
            utl.logger("DEBUG db_init: new table initialized")
    
        str_create_index = "CREATE INDEX {} ON {} ({} ASC)"\
                         .format(data_defs.IX_STATE_END_YDAY, data_defs.TABLE_POLL_RECORDS,
                                 data_defs.COL_STATE)
        self.DBCURSOR.execute(str_create_index)

        # Commit changes
        try:
            self.DBCONN.commit()
        except Error as err:
            utl.oops("db_init: commit() >>> SQL Error\n{}".format(str(err)))
    
        utl.logger("db_init: Done")
    
    
    def db_close(self):
        """
        Commit all database activity and close it.
        Report any exceptions but return to caller.
        """
        if self.DBCONN is None:
            return
        try:
            self.DBCONN.commit()
            self.DBCONN.close()
            self.DBCONN = None
        except Error as err:
            utl.logger("*** db_close: Database failed to commit or close (SQL Error):\n{}"
                       .format(str(err)))
            return
        except Exception as err:
            utl.logger("*** db_close: Database failed to commit or close (Exception):\n{}"
                       .format(str(err)))
        utl.logger("db_close: Database closed")
