## ---------------------------------------------------------------------------##
# Author: Beatrix Haddock
# Date: 04/26/2024
# Purpose:  Compile md to html
# INPUTS:   - md
# OUTPUTS:  - html
## ---------------------------------------------------------------------------##
import markdown
import sys

MD_PATH = sys.argv[1]

def regen_README():
    OUTPUT_DIR = MD_PATH.rpartition("/")[0] + "/"
    if len(OUTPUT_DIR)==1:
        OUTPUT_DIR = ""
    name = MD_PATH.split("/")[-1].split(".")[0]
    with open(MD_PATH, 'r') as f:
        md_text = f.read()

    html = markdown.markdown(md_text)
    html = "<style>\n*{font-family: sans-serif;}\n</style>\n" + html
    print(OUTPUT_DIR)

    with open(OUTPUT_DIR + name + ".html", 'w') as f:
        f.write(html)
