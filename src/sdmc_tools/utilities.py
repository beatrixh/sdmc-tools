import pandas as pd

def std_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    input: df, a pd.DataFrame
    output: df, the same pd.DataFrame with reformatted column names
    example: "Sample ID" -> "sample_id"
    """
    df.columns = [i.lower().replace(" ","_") for i in df.columns]
    return df
