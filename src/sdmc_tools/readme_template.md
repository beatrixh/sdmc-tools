---
# @TITLE
## Author: @AUTHOR
## Date: @DATE
---

## Data Request

Ad hoc data processing is required to add merge on LDMS specimen metadata based on guspec, in addition to misc. metadata from the LUT and other study materials.

## Source Data

The script uses:

* Input data saved at @INPUT-DATA-PATH
* inputs from LDMS, @LDMS-PATH
* human-entered inputs from misc sources (LSP, LUT, etc.)

## Output Data

Processed output data is saved to:

* @OUTPUT-SAVEPATH

@QDATA-SAVEPATH

@PIVOT-SAVEPATH
@DRAFT-DESIGNATION-NOTE

## Relevant Code

The processing was done in a python notebook, and the code was resaved to the following file:

* @CODE-SAVEPATH

## Data Dictionary

@DATA-DICTIONARY

## Processing

* Read in input data
* Convert column names to lowercase, and replace spaces with underscores in both sheets: "Sample ID" -> "sample_id"
* Merge on LDMS columns and rename: @LDMS-COLS
* Add "drawdt" and "spectype" columns.
* Cast "ptid", and "protocol" to int-formatted strings (instead of floats)
* Merge on human-entered metadata, incl: @HAND-MERGED-COLS
* @SDMC-PROCESSING-COLS
* Reorder columns of both sheets.
* Write each sheet to a tab-delimited text file.
@PIVOT-WRITING

## Additional Notes

* None at present.
