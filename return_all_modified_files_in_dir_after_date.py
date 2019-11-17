'''
Created on November 06, 2019

Function to determine which files have been modified after a given date

Returns a pandas DataFrame object

@author: pauladjata

'''

# import site-packages and modules
import glob
import os.path, time
import pandas as pd
import os
import datetime
import time
import re

def save_as_excel_file(path_, df):
    
    from pandas import ExcelWriter
    from datetime import datetime
    import time
    
    timestr = time.strftime("%Y%m%d-%H%M%S")
    
    # save df to Excel
    options = {}
    options['strings_to_formulas'] = False
    options['strings_to urls'] = False

    file_name_xls = 'df_of_modified_files_' + str(timestr) + '.xlsx'

    file_to_save = path_ + '/' + file_name_xls

    writer = pd.ExcelWriter(file_to_save, engine='xlsxwriter', options=options)

    df.to_excel(writer, sheet_name='Elements', index=False)

    writer.save()
    
    print('DataFrame was saved as ' + file_to_save)
    
def get_sub_folder_of_returned_path(string_of_full_path, path):
    
    index_of_last_occur_in_path = path.rfind('\\')
    last_folder = path[index_of_last_occur_in_path + 1:]

    index_of_last_occur_in_string = string_of_full_path.rfind(last_folder)

    sub_folder_string = string_of_full_path[index_of_last_occur_in_path + index_of_last_occur_in_string + 1:]
    
    return sub_folder_string

def get_filename_from_sub_filepath(string_of_sub_filepath):

    index_of_last_occur_in_sub_filepath = string_of_sub_filepath.rfind('\\')

    filename_ = string_of_sub_filepath[index_of_last_occur_in_sub_filepath + 1:]

    return filename_

def main(date_, path_, save_as_excel_bool):
    """Returns a pandas dataframe of files modified after a given date and in a given directory"""
    
    files = [f for f in glob.glob(path_ + r'\**\*', recursive=True)]

    file_details_dict = {}

    for i in range(0, len(files)):

        key = i

        file_details_dict.setdefault(key, [])

        # gets last modified and created time
        modified_time = time.ctime(os.path.getmtime(files[i]))
        created_time = time.ctime(os.path.getctime(files[i]))

        modified_time_date = datetime.datetime.strptime(modified_time, "%a %b %d %H:%M:%S %Y").date()

        test_date = datetime.datetime.strptime(date_, '%b %d %Y').date()

        NEW_FILE_BOOL = modified_time_date > test_date

        #checks if path is a file
        IS_FILE_BOOL = os.path.isfile(files[i])

        file_details_dict[key] = {
            'filepath': files[i],
            'last_mod_time': modified_time,
            'created_time': created_time,
            'isFile': IS_FILE_BOOL,
            'newFile': NEW_FILE_BOOL}

    df_file_details = pd.DataFrame.from_dict(file_details_dict, orient='index')

    # convert 'mod_date' and 'create_date' columns to datetime and then delete
    df_file_details['mod_date'] =  pd.to_datetime(df_file_details['last_mod_time'])
    df_file_details['create_date'] =  pd.to_datetime(df_file_details['created_time'])

    df_file_details.drop(['last_mod_time', 'created_time'], axis=1, inplace=True)
    
    df = df_file_details[
        (df_file_details['newFile'] == True)
        &
        (df_file_details['isFile'] == True)
    ].sort_values(by='mod_date', ascending = True)

    df.reset_index(drop=True, inplace=True)
    
    # get sub filepath from full path
    df['sub_filepath'] = df['filepath'].apply(get_sub_folder_of_returned_path, path=path_)

    # get filename from sub filepath
    df['filename'] = df['sub_filepath'].apply(get_filename_from_sub_filepath)
    
    # expand columns of sub filepath to show sub directories
    new_column_header_prefix = 'sub_filepath_'

    df = df.join(df['sub_filepath'].str.split('\\', expand=True).add_prefix(new_column_header_prefix))

    # get list of columns which contain only the prefix 'new_column_header_prefix'
    sub_filepath_cols = list(df.columns)

    sub_filepath_cols = [x for x in sub_filepath_cols if new_column_header_prefix in x]
    
    # sort sub filepaths alphabetically
    df.sort_values(by=sub_filepath_cols, inplace=True)
    df.reset_index(drop=True, inplace=True)

    # drop columns showing whether is a File and whether is a new file
    df.drop(['isFile', 'newFile'], axis=1, inplace=True)

    main_cols = list(df.columns)

    # get list of columns which does not include the sub folder columns
    main_cols = [x for x in main_cols if new_column_header_prefix not in x]

    insert_at = len(main_cols) - 1

    main_cols[insert_at:insert_at] = sub_filepath_cols

    # reorder columns
    df = df[main_cols]
    
    print(df)
    
    if save_as_excel_bool == 1:
        
        save_as_excel_file(path_, df)
        print('DataFrame was saved at this location:', str(path_))
        
    else:
        
        print('DataFrame was not saved at this time')
        
if __name__ == '__main__':

    import argparse
    
    ap = argparse.ArgumentParser()

    # Add the arguments to the parser
    
    # Required positional argument
    ap.add_argument('mod_date', type=str,
       help="A required string positional argument. Format 'Oct 31 2019' Must be surrounded by double quotes")
    
    # Required positional argument
    ap.add_argument('path_to_check', type=str,
       help="A required string positional argument. Format C:\\Users\\John\\Subdirectory  Must be surrounded by double quotes")
    
    # Optional positional argument
    ap.add_argument('save_df_as_excel_bool', type=int,
                    nargs='?', help='An optional integer positional argument. 1 to save as Excel file; 0 or nothing to not save')
    
    args = ap.parse_args()
    
    IS_DATE = bool(re.match(r"[A-Z]{1}[A-Za-z]{2}\s[0-9]{1,2}\s[0-9]{4}", args.mod_date))
    
    IS_DIR = os.path.isdir(args.path_to_check)
    
    # check that args.save_df_as_excel is either None, 1 or 0
    if args.save_df_as_excel_bool == 1 or args.save_df_as_excel_bool == 0 or args.save_df_as_excel_bool is None:
        
        IS_SAVE = True
        
    else:
        
        IS_SAVE = False
    
    if (args.mod_date == None and args.path_to_check == None or not IS_DATE or not IS_DIR or not IS_SAVE):
        ap.print_help()
    else:
        main(date_=args.mod_date, path_=args.path_to_check, save_as_excel_bool=args.save_df_as_excel_bool)