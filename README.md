# sdmc tools

This package contains a collection of functions designed for the standard cleaning and processing of assay data by SDMC before the data is shared with stats.

## Installation
The package is hosted on Pypi and can be installed using pip: `pip install sdmc-tools`.

- python >= 3.8 is required. these functions might break with earlier python versions.
- The following packages are depenencies:
  - pandas
  - numpy
  - datetime
  - math
  - typing
  - markdown
  - sys
  - time

## Usage
### Data processing
---
Python functions and constants for data processing / prep.

The primary function is `standard_processing`:
```
import sdmc_tools.process as sdmc

outputs = sdmc.standard_processing(
    input_data = input_data,
    input_data_path="/path/to/input_data.xlsx", 
    guspec_col='guspec', 
    network='hvtn', 
    metadata_dict=hand_appended_metadata, 
    ldms=ldms 
)
```
To see the function signature and documentation, you can run `? sdmc.standard_processing` in a Python interpreter. Given `input_data`, the function does the following:
- merges on ldms, renames columns with standard labels
- adds a spectype column
- adds a drawdt column, drops drawdm, drawdd, drawdy
- for each (key,value) in the metadata dict creates a column of the name 'key' with values 'value'
- standardizes the 'ptid' and 'protocol' columns to be int-formatted strings
- merges on columns pertaining to sdmc processing
- rearranges columns into a standardized order
- converts column names "From This" -> "to_this" format

See https://github.com/beatrixh/sdmc-tools/blob/main/src/sdmc_tools/constants.py for the list of constants accessible.

A usage example is included below.

```
import pandas as pd
import sdmc_tools.process as sdmc # this contains the main data processing utilities
import sdmc_tools.constants as constants # this contains useful constants.

ldms = pd.read_csv(constants.LDMS_PATH_HVTN, usecols=constants.STANDARD_COLS) #read in ldms
ldms = ldms.loc[ldms.lstudy==302.] #subset ldms to the protocol of interest
```

*ldms*

![image](https://github.com/beatrixh/sdmc-tools/assets/40446299/17cfefaf-4332-471d-bee1-3bb2a1663b5e)

*input_data*

![image](https://github.com/beatrixh/sdmc-tools/assets/40446299/dbcc52df-03fb-4842-94f8-ee2a1624d717)
```
hand_appended_metadata = {
    'network': 'HVTN',
    'upload_lab_id': 'N4',
    'assay_lab_name': 'Name of Lab Here',
    'instrument': 'SpectraMax',
    'assay_type': 'Neutralizing Antibody (NAb)',
    'specrole': 'Sample',
}

outputs = sdmc.standard_processing(
    input_data = input_data, #a pandas dataframe containing input data
    input_data_path="/path/to/input_data.xlsx", #the path to the original input data
    guspec_col='guspec', #the name of the column containing guspecs within the input data
    network='hvtn', #the relevant network ('hvtn' or 'covpn')
    metadata_dict=hand_appended_metadata, #a dictionary of additional data to append as columns
    ldms=ldms #a pandas dataframe containing the ldms columns we want to merge from
)
```
*outputs*

![image](https://github.com/beatrixh/sdmc-tools/assets/40446299/7c06801c-7c45-4cbe-b4d4-6be6f172750d)
![image](https://github.com/beatrixh/sdmc-tools/assets/40446299/c18fb04e-e360-49c1-830a-eb94010dab33)

### Data dictionary creation
---
This is a command line tool; it creates a data dictionary for a set of processed outputs.

`gen-data-dict` takes two positional arguments: 
- the filepath where the outputs are stored,
- and the desired name of the resulting data dict.
```
gen-data-dict /path/to/outputs.txt name_of_dictionary.xlsx
```

If the dictionary does not already exist in the directory where the outputs live, it will then create
- an xlsx sheet in the same directory as the outputs, with a row for each variable in the outputs, and corresponding definitions for the standard vars. The variables unique to the specific outputs will need to be hand-edited.
- a .txt log in the same directory with notes about any non-standard variables that have been included, or any standard variables that have been omitted.

If a dictionary of the given name already exists, it will be updated to reflect the variables in the output sheet.

### README creation
---
This is a command line tool; given a set of processed outputs, it creates a .md file with documentation for how the outputs were created, and a correspdonding .html of the compiled .md.

`gen-readme` takes three positional arguments:
- the filepath to the directory where the outputs are stored
- the filepath to the raw input data from which the processed outputs were generated
- the author to attribute the readme to
```
gen-data-dict /path/to/outputs_dir/ /path/to/inputs_from_lab.xlsx "Beatrix Haddock"
```

It will then create
- a markdown file describing how the outputs were created, including notes of where the inputs are saved. Note that it will assume the processing was standard, so this will need to be corrected for any nonstandard processing. It will search the output directory for the processed data outputs, a pivot summary of the samples, and the processing code. If it doesn't find these there, it will not include notes on these in the markdown.
- an html file created via compiling the above markdown

`regen-readme` takes one positional argument:
- a filepath to the markdown to compile
```
regen-readme /path/to/my_markdown.md
```

It will then compile into an html file in the same directory and of the same name. If such an html file already exists, it will be overwritten.
