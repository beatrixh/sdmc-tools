## ---------------------------------------------------------------------------##
# Author: Beatrix Haddock
# Date: 04/12/2024
# Purpose:  Auto generate a README for ad hoc processed data.
# INPUTS:   - /path/to/processed_output_dir/
#           - /path/to/input_data.xlsx
#           - Author
#
# OUTPUTS:  - README.html
#           - README.md
## ---------------------------------------------------------------------------##
import markdown
import datetime
import pandas as pd
import numpy as np
import os
import sys
import sdmc_tools.constants as constants

# read in settings, build vars -----------------------------------------------##
OUTPUT_DIR = sys.argv[1]
INPUT_DATA_PATH = sys.argv[2]
AUTHOR = sys.argv[3]

# intro logging --------------------------------------------------------------##
def gen_README():
    print("Note that the following assumptions are automatically made:")
    print("  - column names are converted 'Sample ID' -> 'sample_id'")
    print("  - columns are reordered")
    print("  - outputs written to a tab-delimited text file")
    print("IF ANY OTHER MODIFICATIONS SHOULD BE DOCUMENTED, THEY MUST BE DONE SO MANUALLY")

    print("The following were found in the output dir:")
    for file in os.listdir(OUTPUT_DIR):
        print(f"   - {file}")

    # build dict of filepaths in output dir --------------------------------------##
    USEPATHS = {}
    files = np.sort(os.listdir(OUTPUT_DIR))
    for file in os.listdir(OUTPUT_DIR):
        if "process" in file and ".txt" in file:
            USEPATHS["output_data"] = file
        if "dict" in file and ".xlsx" in file:
            USEPATHS["dict"] = file
        if ".py" in file and "process" in file:
            USEPATHS["code"] = file
        if "summary" in file:
            USEPATHS["pivot_summary"] = file
    try:
        USEPATHS["input_data"] = INPUT_DATA_PATH
    except:
        print("NO INPUT DATA PROVIDED")

    print("The following files are being used:")
    for key in USEPATHS:
        print(f"   - {key}:{USEPATHS[key]}")

    # Build dict to write over placeholders in template --------------------------##
    VAR_DICT = {}
    VAR_DICT["@AUTHOR"] = AUTHOR #todo: automate off user running script?
    VAR_DICT["@DATE"] = datetime.date.today().isoformat()
    if "input_data" in USEPATHS:
        VAR_DICT["@INPUT-DATA-PATH"] = USEPATHS["input_data"]

    if "output_data" in USEPATHS:
        #grab name to use for all files
        name = USEPATHS["output_data"].split("/")[-1].split("DRAFT_")[-1].split("_process")[0]
        VAR_DICT["@TITLE"] = name.replace("_", " ") + " Data Processing"

        VAR_DICT["@OUTPUT-SAVEPATH"] = OUTPUT_DIR + USEPATHS["output_data"]
        if "hvtn" in USEPATHS["output_data"].lower() and "covpn" not in USEPATHS["output_data"].lower():
            NETWORK = "HVTN"
            VAR_DICT["@LDMS-PATH"] = constants.LDMS_PATH_HVTN
        elif "covpn" in USEPATHS["output_data"].lower() and "hvtn" not in USEPATHS["output_data"].lower():
            NETWORK = "CoVPN"
            VAR_DICT["@LDMS-PATH"] = constants.LDMS_PATH_COVPN
    if "pivot_summary" in USEPATHS:
        VAR_DICT["@PIVOT-SAVEPATH"] = f'\nA pivot summary is saved to:\n\n* {USEPATHS["pivot_summary"]}'
        VAR_DICT["@PIVOT-WRITING"] = "\n* Generate a pivot summary."
    else:
        VAR_DICT["@PIVOT-SAVEPATH"] = ""
        VAR_DICT["@PIVOT-WRITING"] = ""

    if "dict" in USEPATHS:
        VAR_DICT["@DICT-SAVEPATH"] = OUTPUT_DIR + USEPATHS["dict"]
        datadict = pd.read_excel(OUTPUT_DIR + USEPATHS["dict"])

        inver = {value:key for (key,value) in constants.LDMS_RELABEL_DICT.items()}
        inver["drawdt"] = "drawdy, drawdm, drawdd"
        inver["spectype"] = "primstr, dervstr"

        ldms_cols = datadict.loc[datadict.source.isin([
            "Merged from LDMS by SDMC", "Derived from LDMS by SDMC"
        ])].variable_name.tolist()
        if len(ldms_cols) > 0:
            VAR_DICT["@LDMS-COLS"] = ""
            for col in ldms_cols:
                try:
                    VAR_DICT["@LDMS-COLS"] += f"\n    + {inver[col]}: {col}"
                except:
                    print(f"{col} not in expected LDMS dictionary")
                    VAR_DICT["@LDMS-COLS"] += f"\n    + {col}"
            if "drawdt" in ldms_cols and "spectype" in ldms_cols:
                VAR_DICT["@LDMS-COMBO-COLS"] = '\n* Add "drawdt" and "spectype" columns.'
            elif "drawdt" in ldms_cols:
                VAR_DICT["@LDMS-COMBO-COLS"] = '\n* Add "spectype" column.'
            elif "spectype" in ldms_cols:
                 VAR_DICT["@LDMS-COMBO-COLS"] = '\n* Add "drawdt" column.'

        hand_merged_cols = datadict.loc[datadict.source=="SDMC Background Materials"].variable_name.tolist()
        if len(hand_merged_cols) > 0:
            VAR_DICT["@HAND-MERGED-COLS"] = ""
            for col in hand_merged_cols:
                VAR_DICT["@HAND-MERGED-COLS"] += f"\n    + {col}"
        processing_cols = ['sdmc_processing_datetime', 'sdmc_data_receipt_datetime', 'input_file_name']
        processing_cols = set(processing_cols).intersection(datadict.variable_name)
        if len(processing_cols) > 0:
            VAR_DICT["@SDMC-PROCESSING-COLS"] = "\nMerge on columns summarizing SDMC processing information."
            for col in processing_cols:
                VAR_DICT["@SDMC-PROCESSING-COLS"] += f"\n    + {col}"


    if "output_data" in USEPATHS:
        if "DRAFT" in USEPATHS["output_data"]:
            VAR_DICT['@DRAFT-DESIGNATION-NOTE'] = '\nNote the "DRAFT_" designation will be removed after review from stats.\n'
        else:
            VAR_DICT['@DRAFT-DESIGNATION-NOTE'] = ""

    if "code" in USEPATHS:
        VAR_DICT["@CODE-SAVEPATH"] = OUTPUT_DIR + USEPATHS["code"]

    # read in template, replace vals ---------------------------------------------##
    template_path = os.path.dirname(__file__) + "/readme_template.md"
    with open(template_path, 'r') as f:
        template_text = f.read()

    print("Making the following assignments:")
    for key in VAR_DICT.keys():
        print(f"{key}: {VAR_DICT[key]}")
        template_text = template_text.replace(key, VAR_DICT[key])

    with open(OUTPUT_DIR + name + "_README.md", 'w') as f:
        f.write(template_text)

    OUTPUT_DIR + name + "_README.html"
    html = markdown.markdown(template_text)
    html = "<style>\n*{font-family: sans-serif;}\n</style>\n" + html

    with open(OUTPUT_DIR + name + "_README.html", 'w') as f:
        f.write(html)
