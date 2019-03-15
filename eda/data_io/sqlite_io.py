import numpy as np
import pandas as pd
import sqlite3 as sql

import base64, hashlib, os

def update_metadata_table_from_metadata_df(metadata_df, conn,
                                           overwrite_flag='warn'):
    """Adds contents of metadata_df to the table 'metadata'
       if the corresponding file_id is not present. If the
       id is present but any key-value pairs conflict, then
       the existing entries will be overwritten only if the
       overwrite flag is set to 'yes' or 'force'. The 'force'
       flag will overwrite data regardless of the number of
       rows.

        Settings for 'overwrite_flag':
        'add-only': add new key-value pairs, but ignore any
                    conflicts in existing pairs
             'yes': add new key-value pairs and overwrite
                    conflicting key-value pairs
           'force': always erase all existing data and rewrite
                    (even keys not present in metadata_df)
            'warn': print a warning if keys exist that don't
                    match value, still add new keys
        'justwarn': print a warning if keys exist that don't
                    match value, don't change table at all

       Returns True if any rows were added or changed.
    """
    file_file_id = metadata_df.file_id.iloc[0]
    if overwrite_flag == 'force':  # flush what's already there
        delete_file_id_from_metadata(file_file_id, conn)
    query = """SELECT *
               FROM metadata
               WHERE file_id = ?
            """
    qparams = (file_file_id,)  # must be tuple for DB-API
    qdf = pd.read_sql_query(query, conn, params=qparams)
    file_metadata_keys = set(metadata_df.key)
    table_metadata_keys = set(qdf.key)
    missing_keys_from_table = file_metadata_keys.difference(table_metadata_keys)
    shared_keys_with_table = file_metadata_keys.intersection(table_metadata_keys)
    overwrote = False
    if len(table_metadata_keys) == 0:  # easiest case, just add file metadata
        clean_metadata_df = metadata_df.drop_duplicates()
        clean_metadata_df.to_sql("metadata", conn, if_exists='append', index=False)
        return True
    if len(shared_keys_with_table) > 0:  # check if values match
        conflict_list = []
        for key in shared_keys_with_table:
            file_val = metadata_df.value[metadata_df.key == key].iloc[0]
            table_val = qdf.value[qdf.key == key].iloc[0]
            if file_val != table_val:
                conflict_list.append(tuple([key, file_val, table_val]))
                if overwrite_flag == "yes":
                    replace_value_in_metadata(file_file_id, key, file_val, conn)
                    overwrote = True
        if conflict_list and overwrite_flag in ['warn', 'justwarn']:
            print("Warning: key-value mismatch for file_id: {}".format(
                   file_file_id))
            for conflict in conflict_list:
                print("{}: {} vs {}".format(*conflict))
            if overwrite_flag == 'justwarn':
                print("No changes made to database.")
                return False
            else:
                print("Existing values kept. Use overwrite_flag='yes' to update.")
    if len(missing_keys_from_table) > 0:  # add new keys
        if overwrite_flag == 'warn':
            print('adding new keys: {}'.format(missing_keys_from_table))
        new_metadata_df = metadata_df[
            metadata_df.key.isin(missing_keys_from_table)]
        new_metadata_df = new_metadata_df.drop_duplicates()
        new_metadata_df.to_sql("metadata", conn,
                               if_exists='append', index=False)
        return True
    if overwrote:
        return True
    return False

def add_file_df_to_raw_data_if_missing(file_df, conn, overwrite_flag='warn'):
    """Adds contents of file_df to the table 'raw_data' if
       the corresponding file_id is not present. If the id
       is present but the number of rows doesn't match, then
       the existing data will be replaced only if the overwrite
       flag is set to 'yes' or 'force'. 'force' flag will
       overwrite data regardless of the number of rows.
       
        Settings for 'overwrite_flag':
           'yes': overwrite existing data if # rows doesn't match
         'force': always overwrite existing data
          'warn': print a warning if # rows doesn't match,
                       but don't actually change anything
       
       Returns True if the file was written.
    """
    file_file_id = file_df.file_id.iloc[0]
    file_num_rows = len(file_df)
    num_rows_found = num_rows_for_file_id_in_raw_data(file_file_id, conn)
    if num_rows_found == 0:  # easiest case, just add file
        file_df.to_sql("raw_data", conn, if_exists='append', index=False)
        return True
    if overwrite_flag == 'force':
        delete_file_id_from_raw_data(file_file_id, conn)
        file_df.to_sql("raw_data", conn, if_exists='append', index=False)
        return True
    if num_rows_found != file_num_rows:
        if overwrite_flag == 'yes':
            delete_file_id_from_raw_data(file_file_id, conn)
            file_df.to_sql("raw_data", conn, if_exists='append', index=False)
            return True
        elif overwrite_flag == 'warn':
            print("Warning: file mismatch for file_id: {}".format(file_file_id))
            print("{} rows in df, {} rows in raw_data".format(
                   file_num_rows, num_rows_found))
            print("File not written to database.")
    return False

# helper function for preprocessing data for sql
def get_updated_metadata_dict(file_metadata_dict, experiment_alias="None"):
    """Takes a metadata dictionary like those from
       eda.csv_to_dataframe, and modifies it to include
       information from the filepath
    """
    relative_filepath = file_metadata_dict['Filepath']
    absolute_filepath = os.path.abspath(relative_filepath)
    this_script_dirpath = os.path.abspath(".")
    filename = relative_filepath.split('\\')[-2]
    file_hash_key = filename + file_metadata_dict['Scan Start']
    exp_hash_key = this_script_dirpath  # + experiment_alias
    file_id = base64.b64encode(hashlib.md5(file_hash_key.encode('utf-8')).digest())
    exp_id = base64.b64encode(hashlib.md5(exp_hash_key.encode('utf-8')).digest())
    new_dict = dict()
    new_dict['file_id'] = file_id
    new_dict['experiment_id'] = exp_id
    new_dict['experiment_alias'] = experiment_alias
    new_dict['run_id'] = file_metadata_dict['Run ID']
    if 'SecondScanIndex' in file_metadata_dict:
        new_dict['index_2d'] = file_metadata_dict['SecondScanIndex']
    else:
        new_dict['index_2d'] = -1
    new_dict['filepath'] = absolute_filepath
    if relative_filepath != absolute_filepath:
        new_dict['relative_filepath'] = relative_filepath
    new_dict['last_modified'] = file_metadata_dict['File Last Modified']
    for key, value in file_metadata_dict.items():
        if key in ['Filepath', 'File Last Modified',
                   'Run ID', 'SecondScanIndex']:
            continue
        new_dict[key] = value
    return new_dict

def create_missing_tables(conn):
    """Ensures database contains the following tables
       and creates them if they do not yet exist:
       raw_data, metadata
    """
    table1command = """CREATE TABLE IF NOT EXISTS raw_data
                       (file_id TEXT, file_row INTEGER, scancoord REAL,
                        lockin2x REAL, lockin1x REAL, lockin2r REAL,
                        lockin1r REAL, laserpower REAL, cwetalon REAL,
                        lockin3x REAL, lockin3r REAL, lockin4x REAL,
                        lockin4r REAL, lockin5x REAL, lockin5r REAL,
                        lasercomponent1 REAL, lasercomponent2 REAL,
                        temperature REAL, labtime REAL)
                    """
    table2command = """CREATE TABLE IF NOT EXISTS metadata
                       (file_id TEXT, key TEXT, value TEXT)
                    """
    cur = conn.cursor()
    cur.execute(table1command)
    cur.execute(table2command)
    conn.commit()

def num_rows_for_file_id_in_raw_data(file_id, conn):
    """Checks if the 'raw_data' table contains the provided
       file_id with the same number of rows. Does not check
       content.
       
       Returns the number of rows in raw_data with the specified
       file_id. If the file_id is not found, the result is zero.
       
       Warning:
       Does not check if table is missing. Check before use.
    """
    query = """SELECT COUNT(*) AS num_rows
               FROM raw_data
               GROUP BY file_id
               HAVING file_id = ?
            """
    qparams = (file_id,)  # must be tuple for DB-API
    qdf = pd.read_sql_query(query, conn, params=qparams)
    num_rows_found = 0
    if len(qdf) > 0:
        num_rows_found = qdf.num_rows.iloc[0]
    return num_rows_found

def metadata_df_from_file_id_in_metadata(file_id, conn):
    """Checks if the 'metadata' table contains the provided
       file_id, and returns the associated metadata dataframe.
       
       If the file_id is not found, the returned DataFrame
       will be empty.
       
       Warning:
       Does not check if table is missing. Check before use.
    """
    query = """SELECT *
               FROM metadata
               GROUP BY file_id
               HAVING file_id = ?
            """
    qparams = (file_id,)  # must be tuple for DB-API
    qdf = pd.read_sql_query(query, conn, params=qparams)
    return qdf

def delete_file_id_from_raw_data(file_id, conn):
    """Removes all rows with given file_id from 'raw_data'."""
    cur = conn.cursor()
    cur.execute("""DELETE FROM raw_data
                   WHERE file_id=?""", (file_id,))
    conn.commit()

def delete_file_id_from_metadata(file_id, conn):
    """Removes all rows with given file_id from 'metadata'."""
    cur = conn.cursor()
    cur.execute("""DELETE FROM metadata
                   WHERE file_id=?""", (file_id,))
    conn.commit()

def replace_value_in_metadata(file_id, key, value, conn):
    """Removes all rows with given file_id from 'metadata'."""
    cur = conn.cursor()
    cur.execute("""UPDATE metadata
                   SET value = ?
                   WHERE key = ? AND
                         file_id = ?""", (value, key, file_id))
    conn.commit()

# helper function for preprocessing metadata for sql
def dict_to_two_column_df(input_dict):
    """Convert a dictionary into a pandas dataframe
       with columns 'key' and 'value'."""
    file_metadata_df = pd.DataFrame.from_dict(input_dict, orient='index',
                                              dtype='str', columns=['value'])
    file_metadata_df.reset_index(inplace=True)
    file_metadata_df.rename(index=str, columns={'index': 'key'}, inplace=True)
    return file_metadata_df
