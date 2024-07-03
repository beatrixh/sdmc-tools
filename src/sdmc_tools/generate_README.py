## ---------------------------------------------------------------------------##
# Author: Beatrix Haddock
# Date: 06/05/2024
# Purpose:  Auto generate a README for ad hoc processed data.
# INPUTS:   - /path/to/yaml
#
# OUTPUTS:  - README.html
#           - README.md
## ---------------------------------------------------------------------------##
import markdown
import datetime
import pandas as pd
import numpy as np
import yaml
import os
import sys
import sdmc_tools.constants as constants
## ---------------------------------------------------------------------------##

#TODO: CONSIDER WRAPPING EACH CALL IN A FUNCTION
#TODO: TEST THIS OUT, MAKE SURE IT WORKS FOR SIMPLEST CASE
#TODO: TEST THIS OUT FOR CASES WITH MULTIPLE INPUTS
#TODO: TEST THIS OUT FOR CASES WITH MULTIPLE OUTPUTS
#TODO: WRAP IN COMMAND LINE FN AND REBUILD

YAML_PATH = sys.argv[1]
AUTHOR = sys.argv[2]

with open(YAML_PATH, 'r') as file:
    yamldict = yaml.safe_load(file)


def gen_README():
    VAR_DICT = {}

    ## TITLE ---------------------------------------------------------------- ##
    if isinstance(yamldict["output_prefix"], list):
        title = yamldict["output_prefix"][0].split("DRAFT_")[-1].split("_process")[0]
    else:
        title = yamldict["output_prefix"].split("DRAFT_")[-1].split("_process")[0]
    title = title.replace("_", " ").replace("-"," ") + " Data Processing"
    VAR_DICT["@TITLE"] = title

    ## AUTHOR --------------------------------------------------------------- ##
    VAR_DICT["@AUTHOR"] = AUTHOR

    ## DATE ----------------------------------------------------------------- ##
    VAR_DICT["@DATE"] = datetime.date.today().isoformat()

    ## INPUT DATA PATH ------------------------------------------------------ ##
    input_data_path = yamldict["input_data_path"]
    if isinstance(input_data_path, list):
        if len(input_data_path)==1:
            input_data_path_string = input_data_path[0]
        elif len(input_data_path)>1:
            input_data_path_string = ", ".join(input_data_path)
        elif len(input_data_path)==0:
            input_data_path_string = "@INPUT-DATA-PATH"
    else:
        input_data_path_string = input_data_path

    VAR_DICT["@INPUT-DATA-PATH"] = input_data_path_string

    ## OUTPUT-SAVEPATH ------------------------------------------------------ ##
    OUTPUT_DIR = yamldict["savedir"]
    if OUTPUT_DIR[-1]!="/":
        OUTPUT_DIR += "/"
    OUTPUT_DIR_FILES = os.listdir(OUTPUT_DIR)
    #filter out weird things saved by excel
    OUTPUT_DIR_FILES = list(np.unique([
        f[2:] if f[:2]=="~$" else f for f in OUTPUT_DIR_FILES
    ]))
    output_savepath = [o for o in OUTPUT_DIR_FILES if "process" in o and ".txt" in o]
    if len(output_savepath)>0:
        if len(output_savepath)>1:
            tmp = output_savepath[0]
            for o in output_savepath[1:]:
                tmp += f"\n* {OUTPUT_DIR + o}"
            output_savepath = tmp
        elif len(output_savepath)==1:
            output_savepath = OUTPUT_DIR + output_savepath[0]

        VAR_DICT["@OUTPUT-SAVEPATH"] = output_savepath
    elif len(output_savepath)==0:
        print(f"/studies folder missing outputs: {OUTPUT_DIR}, {prefix}")

    ## LDMS-PATH ------------------------------------------------------------ ##
    if isinstance(output_savepath, list):
        output_savepath = output_savepath[0]

    if "hvtn" in output_savepath.lower() and "covpn" not in output_savepath.lower():
        NETWORK = "HVTN"
        VAR_DICT["@LDMS-PATH"] = constants.LDMS_PATH_HVTN
    elif "covpn" in output_savepath.lower() and "hvtn" not in output_savepath.lower():
        NETWORK = "CoVPN"
        VAR_DICT["@LDMS-PATH"] = constants.LDMS_PATH_COVPN

    ## QDATA-SAVEPATH ------------------------------------------------------- ##
    if isinstance(input_data_path, list):
        qdata_dir = input_data_path[0].rpartition("/")[0]
    else:
        qdata_dir = input_data_path.rpartition("/")[0]

    if 'processed_by_sdmc' in [i.lower() for i in os.listdir(qdata_dir)]:
        idx = [i.lower() for i in os.listdir(qdata_dir)].index('processed_by_sdmc')
        subd = qdata_dir + "/" + os.listdir(qdata_dir)[idx] + "/"

        prefix = yamldict["output_prefix"]
        if isinstance(prefix, list):
            qdata_output = ""
            for pref in prefix:
                potentials = os.listdir(subd)
                qdata_output_i = [subd + p for p in potentials if pref.lower() in p.lower()]
                qdata_output_i = np.sort(qdata_output_i)[-1]
                qdata_output += f"* {qdata_output_i}"
            qdata_output = qdata_output[2:]
        else:
            potentials = os.listdir(subd)
            qdata_output = [subd + p for p in potentials if prefix.lower() in p.lower()]
            qdata_output = np.sort(qdata_output)[-1]

        VAR_DICT["@QDATA-SAVEPATH"] = f"A finalized copy is saved to:\n\n* {qdata_output}"
    else:
        VAR_DICT["@QDATA-SAVEPATH"] = f"Once data has been approved by stats, it will be moved to {qdata_dir + 'processed_by_sdmc/'}"

    ## PIVOT-SAVEPATH, PIVOT-WRITING ---------------------------------------- ##
    pivots = [p for p in OUTPUT_DIR_FILES if "summary" in p]
    if len(pivots)>0:
        VAR_DICT["@PIVOT-WRITING"] = "* Generate a pivot summary."
        if len(pivots)==1:
            VAR_DICT["@PIVOT-SAVEPATH"] = f'\nA pivot summary is saved to:\n\n* {OUTPUT_DIR + pivots[0]}'
        elif len(pivots)>1:
            VAR_DICT["@PIVOT-SAVEPATH"] = '\nPivot summaries have been saved to:\n'
            for p in pivots:
                VAR_DICT["@PIVOT-SAVEPATH"] += f"\n* {OUTPUT_DIR + p}"
    elif len(pivots)==0:
        VAR_DICT["@PIVOT-SAVEPATH"] = ""
        VAR_DICT["@PIVOT-WRITING"] = ""

    ## DRAFT-DESIGNATION-NTE ------------------------------------------------ ##
    if "@OUTPUT-SAVEPATH" in VAR_DICT:
        if "DRAFT" in VAR_DICT["@OUTPUT-SAVEPATH"]:
            VAR_DICT['@DRAFT-DESIGNATION-NOTE'] = '\nNote the "DRAFT_" designation will be removed after review from stats.\n'
        else:
            VAR_DICT['@DRAFT-DESIGNATION-NOTE'] = ""

    ## CODE-SAVEPATH -------------------------------------------------------- ##
    CODE_DIR = YAML_PATH.rpartition("/")[0]
    if "process_data.py" in os.listdir(CODE_DIR):
        stem = CODE_DIR.partition("processing_scripts")[-1]
        link = "https://github.com/beatrixh/sdmc_adhoc/blob/main/processing_scripts" + stem + "/process_data.py"
        VAR_DICT["@CODE-SAVEPATH"] = link
    else:
        print(f"CODE (process_data.py) NOT FOUND IN {CODE_DIR}")

    ## DATA-DICTIONARY ------------------------------------------------------ ##
    dict_path = [d for d in OUTPUT_DIR_FILES if "dict" in d and ".xlsx" in d]
    if len(dict_path)==0:
        print("NO DATA DICTIONARY FOUND")
    else:
        if len(dict_path)>1:
            dict_path = np.sort(dict_path)[-1]
            print(f"WARNING: MULTIPLE DICTS. JUST TAKING MOST RECENT: {dict_path}")
        elif len(dict_path)==1:
            dict_path = dict_path[0]
        datadict = pd.read_excel(OUTPUT_DIR + dict_path)
        datadict = datadict.fillna("")

        inver = {value:key for (key,value) in constants.LDMS_RELABEL_DICT.items()}
        inver["drawdt"] = "drawdy, drawdm, drawdd"
        inver["spectype"] = "primstr, dervstr"

        ## LDMS-COLS
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

        ## HAND-MERGED-COLS
        hand_merged_cols = datadict.loc[datadict.source=="SDMC Background Materials"].variable_name.tolist()
        if len(hand_merged_cols) > 0:
            VAR_DICT["@HAND-MERGED-COLS"] = ""
            for col in hand_merged_cols:
                VAR_DICT["@HAND-MERGED-COLS"] += f"\n    + {col}"

        ## SDMC-PROCESSING-COLS
        processing_cols = ['sdmc_processing_datetime', 'sdmc_data_receipt_datetime', 'input_file_name']
        processing_cols = set(processing_cols).intersection(datadict.variable_name)
        if len(processing_cols) > 0:
            VAR_DICT["@SDMC-PROCESSING-COLS"] = "Merge on columns summarizing SDMC processing information."
            for col in processing_cols:
                VAR_DICT["@SDMC-PROCESSING-COLS"] += f"\n    + {col}"

    ## read in template, replace vals ----------------------------------------##
    template_path = os.path.dirname(__file__) + "/readme_template.md"
    with open(template_path, 'r') as f:
        template_text = f.read()

    print("Making the following assignments:")
    for key in VAR_DICT.keys():
        print(f"{key}: {VAR_DICT[key]}")
        template_text = template_text.replace(key, VAR_DICT[key])

    name = VAR_DICT["@TITLE"].split(" Data Processing")[0].replace(" ","_")
    timestamp = datetime.datetime.today().isoformat().replace(":","_")
    with open(f"{OUTPUT_DIR}{name}_README_{timestamp}.md", 'w') as f:
        f.write(template_text)

    html = markdown.markdown(template_text)

    # create data dict table
    html = html.replace("@DATA-DICTIONARY", format_table_in_html(datadict))

    # compile any remaining tables
    while "@TABLE-START" in html:
        a = html.find("@TABLE-START")
        b = html.find("@TABLE-STOP")

        table = html[a + len("@TABLE-START\n"):b]
        table = [i.split(",") for i in table.split("\n")]
        table = pd.DataFrame(columns=table[0], data=table[1:-1])

        html = html[:a] + "\n" + format_table_in_html(table) + "\n" + html[b + len("@TABLE-STOP"):]

    # html = "<style>\n*{font-family: sans-serif;}\n</style>\n" + html
    html = headertext + "<body>\n" + html + "</body></html>"

    print(f"this is the supposed name: {OUTPUT_DIR}{name}_README_{timestamp}.html")
    with open(f"{OUTPUT_DIR}{name}_README_{timestamp}.html", 'w') as f:
        f.write(html)

def format_table_in_html(mydict):
    table_html = "<table>\n"
    table_html += "<tr>\n"
    for col in mydict.columns:
        table_html += f"<th>{col}</th>\n"
    table_html += "</tr>"
    for row in range(len(mydict)):
        table_html += "<tr>\n"
        for col in range(mydict.shape[1]):
            table_html += f"<td>{mydict.iloc[row, col]}</td>\n"
        table_html += "</tr>\n"
    table_html += "</table>\n"
    return table_html

headertext = '<!DOCTYPE html>\n<html>\n<head>\n<style>\n*{font-family: sans-serif;}\ntable {\n  font-family: arial, sans-serif;\n  border-collapse: collapse;\n  width: 40%;\n}\n\ntd, th {\n  border: 1px solid #dddddd;\n  text-align: left;\n  padding: 8px;\n}\n\ntr:nth-child(even) {\n  background-color: #dddddd;\n}\n</style>\n</head>\n\n\n'

if __name__=="__main__":
    gen_README()
