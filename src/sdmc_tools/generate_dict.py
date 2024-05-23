## ---------------------------------------------------------------------------##
# Author: Beatrix Haddock
# Date: 02/27/2024
# Purpose:  Auto generate a data dictionary for ad hoc processed data.
# INPUTS:   - /path/to/processed_output_data.txt
#           - name_of_data_dictionary.xlsx
#
# OUTPUTS:  - name_of_data_dictionary.xlsx
#           - logs.timestamp
## ---------------------------------------------------------------------------##
import pandas as pd
import time
import math
import sys
import os

# read in settings, build vars -----------------------------------------------##
processed_data_path = sys.argv[1]
data_dict_fname = sys.argv[2]

output_dir = processed_data_path.rpartition("/")[0] + "/"
template_dict_path = os.path.dirname(__file__) + "/data_dictionary_TEMPLATE.xlsx"
# build data dict ------------------------------------------------------------##
template_dict = pd.read_excel(template_dict_path)
template_vars = list(template_dict.variable_name)

processed_data = pd.read_csv(processed_data_path, sep="\t")
processed_data_vars = list(processed_data.columns)

def gen_data_dict():
    if os.path.exists(output_dir + data_dict_fname):
        edit_existing_dict()
    else:
        build_brand_new_dict()

def save_dict(dict_to_save):
    writer = pd.ExcelWriter(
        output_dir + data_dict_fname,
        engine='xlsxwriter'
    )
    dict_to_save.to_excel(writer, sheet_name="Sheet1", index=False)
    workbook = writer.book
    text_format = workbook.add_format({'text_wrap': True})
    worksheet = writer.sheets["Sheet1"]

    # save each column width / + text wrapping
    for idx, col in enumerate(dict_to_save):
        if col in ["notes"]:
            worksheet.set_column(idx, idx, 30, text_format)
        else:
            worksheet.set_column(idx, idx, 25, text_format)

    # force all the values in the "example" column to be strings
    col_idx = dict_to_save.columns.get_loc("example")
    for i, data in enumerate(dict_to_save["example"]):
        if isinstance(data, float):
            if math.isnan(data):
                data = ""
        worksheet.write_string(i + 1, col_idx, str(data))

    writer.close()

def build_brand_new_dict():
    not_in_template = set(processed_data_vars).difference(template_vars)
    not_in_output = set(template_vars).difference(processed_data_vars)

    our_dict = pd.DataFrame({"variable_name": processed_data_vars})
    our_dict = our_dict.merge(template_dict, on="variable_name", how="left")
    our_dict.loc[our_dict.variable_name.isin(not_in_template), "source"] = "Submitted by lab"
    # output logs
    log = ""
    if len(not_in_template)>0:
        log += "The following vars have been added the the data dictionary; their values need to be added manually:\n"
        for var in not_in_template:
            log += f"- {var}\n"

    if len(not_in_output)>0:
        log += "\nNote that the following standard vars are not in the dataset; consider adding:\n"
        for var in not_in_output:
            log += f"- {var}\n"

    name = data_dict_fname.partition(".")[0]
    timestamp = int(time.time())
    f = open(output_dir + f"LOGS_{timestamp}_{name}.txt", "w")
    f.write(log)
    f.close()

    #save
    save_dict(our_dict)

def edit_existing_dict():
    human_edits = pd.read_excel(output_dir + data_dict_fname)

    nonstandard_cols_in_human_edits = set(human_edits.columns).difference(template_dict.columns)
    standard_cols_removed_from_human_edits = set(template_dict.columns).difference(human_edits.columns)
    new_vars_for_dict = set(processed_data.columns).difference(human_edits.variable_name)
    vars_removed_from_dict = set(human_edits.variable_name).difference(processed_data.columns)

    # create a new dict with variable_name sorted as in new processed data
    new_dict = pd.DataFrame({'variable_name': processed_data_vars})

    # add on everything from the original data
    new_dict = new_dict.merge(human_edits, on="variable_name", how='left')

    # for any new variable, add in values from the template (as available)
    for var in new_vars_for_dict:
        for col in new_dict.columns[1:]:
            if col in template_dict.columns:
                if var in list(template_dict.variable_name):
                    val = template_dict.loc[template_dict.variable_name==var, col]
                    if val.notna().values[0]:
                        new_dict.loc[new_dict.variable_name==var, col] = val
    # output logs
    log = ""
    if len(nonstandard_cols_in_human_edits)>0:
        log += "Keeping the following nonstd columns in dictionary:\n"
        for var in nonstandard_cols_in_human_edits:
            log += f"- {var}\n"

    if len(standard_cols_removed_from_human_edits)>0:
        log += "The following standard cols were removed from previous edit; keeping them out:\n"
        for var in standard_cols_removed_from_human_edits:
            log += f"- {var}\n"

    if len(new_vars_for_dict)>0:
        log += "The following variables are being added to the dict since the previous iteration:\n"
        for var in new_vars_for_dict:
            log += f"- {var}\n"

    if len(vars_removed_from_dict)>0:
        log += "The following variables were in the previous iteration of the dict, but weren't in thew newest processed data, so they've been removed:\n"
        for var in vars_removed_from_dict:
            log += f"- {var}\n"

    name = data_dict_fname.partition(".")[0]
    timestamp = int(time.time())
    f = open(output_dir + f"LOGS_{timestamp}_{name}.txt", "w")
    f.write(log)
    f.close()

    # save
    save_dict(new_dict)

def gen_dictionary():
    if os.path.exists(output_dir + data_dict_fname):
        edit_existing_dict()
    else:
        build_brand_new_dict()
