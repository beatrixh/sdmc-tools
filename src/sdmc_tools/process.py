import pandas as pd
import numpy as np
import os
from typing import List, Union
import datetime
from sdmc_tools import constants

def standard_processing(
    input_data: pd.DataFrame,
    input_data_path: str,
    guspec_col: str,
    network: str,
    metadata_dict: dict,
    ldms: pd.DataFrame,
    ldms_usecols: List[str] = constants.STANDARD_COLS,
    ) -> pd.DataFrame:
    """
    INPUTS
    ------
    input_data: pd.DataFrame, long/desired format,
    input_data_path: str, filepath to the input data
    guspec_col: str, name of the global identifier (guspec) in input_data
    network: str, either "hvtn" or "covpn"
    metadata_dict: dict; keys are column names, values are column values
    ldms: pd.DataFrame, should contain guspec + all other desired vars to merge
    ldms_usecols: columns to merge on from ldms.

    OUTPUTS
    -------
    data formatted with the following merged on:
    - ldms columns
    - metadata from "metadata_dict"
    - sdmc processing info

    sorted in standard order
    """

    dh = DataHandler(
    input_data = input_data,
    guspec_col = guspec_col,
    network = network.lower()
    )
    dh.ldms = ldms.copy()

    # merge ldms
    dh.add_ldms(cols = ldms_usecols,
                incl_spec_type=True,
                map_drawdt=True,
                relabel=True,
                enforce_typing=True)

    dh.add_metadata(metadata_dict)
    dh.add_sdmc_processing_info(input_data_path=input_data_path)

    if guspec_col!="guspec":
        dh.processed_data = dh.processed_data.drop(columns=guspec_col)

    reorder = dh.reorder_cols(dh.processed_data.columns)

    return dh.processed_data[reorder]


class DataHandler:
    def __init__(
        self,
        input_data: pd.DataFrame,
        guspec_col: str,
        network: str,
        input_data_path: str = None,
    ):
        if not guspec_col in input_data.columns:
            raise Exception(f"'{guspec}' must be a column in input_data")
        if network not in ["hvtn", "covpn"]:
            raise ValueError("network must be 'hvtn' or 'covpn'")
        self.input_data = input_data
        self.guspec_col = guspec_col
        self.input_data_path = input_data_path
        self.network = network
        self.ldms = None
        self.processed_data = input_data

    def load_ldms(
        self,
        usecols: List[str] = constants.STANDARD_COLS,
        use_fake_ldms = False,
    ):
        """
        load network-specific ldms dataset
        store in self.ldms
        subset down to guspecs in self.input_data
        """
        if self.network=="hvtn":
            path = constants.LDMS_PATH_HVTN
        elif self.network=="covpn":
            path = constants.LDMS_PATH_COVPN
        else:
            raise ValueError("self.network must be 'hvtn' or 'covpn'")

        if use_fake_ldms:
            path = constants.FAKE_LDMS

        #check usecols are valid columns
        missings = set(usecols).difference(constants.LDMS_COLUMNS)
        if len(missings) > 0:
            raise Exception(f"The following aren't LDMS cols: {missings}")

        if "guspec" not in usecols:
            usecols += ["guspec"]
        ldms = pd.read_csv(path, usecols=usecols)

        # subset to applicable guspecs
        guspecs = list(set(self.input_data[self.guspec_col]))
        if not set(guspecs).issubset(ldms.guspec):
            raise Exception("input data guspecs not in ldms")
        else:
            ldms = ldms.loc[ldms.guspec.isin(guspecs)]

        self.ldms = ldms

    def _map_spectype(self, x):
        """
        Add a spectype column
        """
        try:
            return constants.SPEC_TYPE_DEFN_MAP[x.primstr, x.dervstr]
        except:
            print(f"{x.primstr}, {x.dervstr} missing from spec map!")
            return "MISSING FROM MAP"

    def add_ldms(
        self,
        cols: List[str],
        incl_spec_type: bool = True,
        map_drawdt: bool = True,
        relabel: bool = True,
        enforce_typing = True
    ):
        """
        Merge self.ldms onto self.processed_data
        Optionally add spec_type and drawdt columns
        Optionally relabel with standard relabelling names
        """
        if not cols:
            cols = constants.STANDARD_COLS
        if not "guspec" in cols:
            cols += ["guspec"]
        if not isinstance(self.ldms, pd.DataFrame):
            self.load_ldms(usecols=cols)

        #if cols missing from loaded cols, reload all
        not_loaded = set(cols).difference(self.ldms.columns)
        if len(not_loaded) > 0:
            self.load_ldms(usecols=cols)

        ldms = self.ldms[cols].copy()

        if incl_spec_type:
            if set(['primstr', 'dervstr']).issubset(ldms.columns):
                ldms.loc[ldms.dervstr.isna(), "dervstr"] = "N/A"
                ldms["spectype"] = ldms.apply(lambda x: self._map_spectype(x), axis=1)
            else:
                raise Exception("Need to pull primstr and dervstr for spectype")

        if map_drawdt:
            ldms["drawdt"] = ldms.apply(
                lambda x: datetime.date(x.drawdy, x.drawdm, x.drawdd).isoformat(), axis=1
            )
            ldms = ldms.drop(columns=["drawdy", "drawdm", "drawdd"])

        if enforce_typing:
            for col in ['txtpid', 'lstudy']:
                if col in ldms.columns:
                    ldms[col] = ldms[col].astype(int).astype("string")
            if 'vidval' in ldms.columns:
                ldms.vidval = ldms.vidval.astype("string")

        if relabel:
            ldms = ldms.rename(columns=constants.LDMS_RELABEL_DICT)

        # merge ldms on
        self.processed_data = self.processed_data.merge(
            ldms,
            left_on=self.guspec_col,
            right_on="guspec",
            how="left"
        )

    def add_metadata(self, metadata: dict):
        """
        INPUT: dictionary of column names and values.
        INPUT EXAMPLE: {"upload_lab_id": "DG",
                        "assay_lab_name": "Geraghty Lab (FHCRC)",
                        "instrument": "Illumina NGS"}
        FUNCTION: adds corresponding columns to self.processed_data
        """
        already_exists = set(metadata.keys()).intersection(self.processed_data.columns)
        if already_exists:
            print(f"The following cols are already in processed_data: {already_exists}; replacing")
            self.processed_data = self.processed_data.drop(columns=already_exists)
        metadata = pd.DataFrame({i: [metadata[i]] for i in metadata.keys()})
        self.processed_data = self.processed_data.merge(metadata, how = 'cross')

    def add_sdmc_processing_info(self, input_data_path: str):
        """
        Adds sdmc_processing_datetime, sdmc_data_receipt_datetime, and
        input_file_name cols to self.processed_data
        - sdmc_processing_datetime: current time
        - sdmc_data_receipt_datetime: read from input_data_path timestamp
        - input_file_name: read from input_data_path
        """
        # if both are not None, check if they're the same
        if self.input_data_path and input_data_path:
            if self.input_data_path != input_data_path:
                print(f"Note self.input_data_path != input_data_path. Replacing {self.input_data_path} with new input_data_path.")

        # if input_data_path not None, trust that one:
        if input_data_path:
            self.input_data_path = input_data_path

        if not os.path.exists(self.input_data_path):
            raise Exception(f"{self.input_data_path} not a valid filepath.")

        sdmc_processing_datetime = datetime.datetime.now().replace(microsecond=0).isoformat()
        data_receipt_datetime = datetime.datetime.fromtimestamp(os.path.getmtime(self.input_data_path)).replace(microsecond=0).isoformat()

        sdmc_metadata = pd.DataFrame({
            "sdmc_processing_datetime": [sdmc_processing_datetime],
            # "sdmc_processing_version": [1.0],
            "sdmc_data_receipt_datetime": [data_receipt_datetime],
            "input_file_name": [input_data_path.split("/")[-1]],
        })

        # if these columns are already in processed_data, drop and replace
        already_exists = set(sdmc_metadata.columns).intersection(self.processed_data.columns)
        self.processed_data = self.processed_data.drop(columns=already_exists)

        # add processing metadata columns
        self.processed_data = self.processed_data.merge(sdmc_metadata, how="cross")

    def reorder_cols(self, input_cols: List[str]) -> List[str]:
        usecols = []
        for col in constants.STD_PREFACE_COLS:
            if col in input_cols:
                usecols += [col]
        for col in np.sort(list(set(input_cols).difference(
        constants.STD_PREFACE_COLS + constants.STD_POSTFACE_COLS
        ))):
            usecols += [col]

        for col in constants.STD_POSTFACE_COLS:
            if col in input_cols:
                usecols += [col]

        return usecols
