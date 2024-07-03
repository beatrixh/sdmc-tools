## ---------------------------------------------------------------------------##
# Author: Beatrix Haddock
# Date: 04/26/2024
# Purpose:  Compile md to html
# INPUTS:   - md
# OUTPUTS:  - html
## ---------------------------------------------------------------------------##
import markdown
import pandas as pd
import sys

MD_PATH = sys.argv[1]
DICT_PATH = sys.argv[2]

def regen_README():
    OUTPUT_DIR = MD_PATH.rpartition("/")[0] + "/"
    if len(OUTPUT_DIR)==1:
        OUTPUT_DIR = ""
    name = MD_PATH.split("/")[-1].split(".")[0]
    with open(MD_PATH, 'r') as f:
        md_text = f.read()

    datadict = pd.read_excel(DICT_PATH).fillna("")

    html = markdown.markdown(md_text)

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


    # add formatting
    html = headertext + "<body>\n" + html + "</body></html>"

    with open(OUTPUT_DIR + name + ".html", 'w') as f:
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
    regen_README()
