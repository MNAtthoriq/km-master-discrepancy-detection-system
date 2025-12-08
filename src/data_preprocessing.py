"""
Data Preprocessing for KM Master Discrepancy Detection
"""

from google_sheets_io import sheets_loader
import pandas as pd
import config
import logging   

# set up logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT) # get override from utils.py later (force=True)
logger = logging.getLogger(__name__)

def convert_to_op_code(
      df:pd.DataFrame, sheets_url:str, 
      sheets_name:str = config.CTOC_SHEETS_NAME, method:str = config.CTOC_METHOD_DEFAULT,
      left_on:str = config.CTOC_DF_OP_NAME, 
      right_on_0:str = config.CTOC_MASTER_OP_NAME, right_on_1:str = config.CTOC_MASTER_OP_CODE
    ) -> pd.DataFrame:
  """
  Rename Operating Point (OP) name to OP code by merging it with master OP data from Google Sheets.

  Example:
  OP name: 'Point Balikpapan Reguler' -> OP code: 'PBPNR'

  Parameters:
  -----------
  df : pd.DataFrame
    DataFrame containing OP name column.
  sheets_url : str
    URL of the Google Sheets.
  sheets_name : str
    Name of the Google Sheets.
  method : str
    Method of dealing with OP who doesn't use the OP Code. Can be either 'complete' or 'partial'. 
    'complete' will raise an error if there is an OP who doesn't use the OP Code, while 'partial' will drop the OP.
  left_on : str
    Name of the column in df containing OP name.
  right_on_0 : str
    Name of the column in master OP containing OP name.
  right_on_1 : str
    Name of the column in master OP containing OP code.

  Returns:
  --------
  pd.DataFrame
    DataFrame with OP name column changed to OP code.

  Raises:
  -------
  ValueError
    If method is not 'complete' or 'partial'.
    If method is 'complete' and unmapped OPs exist.
  """
  logger.info(f"Converting OP names to OP codes using method: {method}")

  # import data master op
  sh = sheets_loader(sheets_url)
  worksheet = sh.worksheet(sheets_name)
  df_master_op = pd.DataFrame(worksheet.get_all_records())  
  df_master_op = df_master_op[[right_on_0, right_on_1]].copy()

  logger.info(f"Loaded {len(df_master_op)} OP codes from sheets {sheets_name}")

  # convert op name to op code
  df_merged_0 = pd.merge(df, df_master_op, left_on=left_on, right_on=right_on_0, how='left')
  unmatched = df_merged_0[df_merged_0[right_on_1].isna()].copy()
  matched = df_merged_0[~df_merged_0[right_on_1].isna()].copy()

  # handle cases where OP name is already OP code
  if not unmatched.empty:
    unmatched_merged = pd.merge(
                          unmatched.drop(columns=[right_on_0, right_on_1]), 
                          df_master_op, left_on=left_on, right_on=right_on_1, how='left'
                        )
    df_merged = pd.concat([matched, unmatched_merged], ignore_index=True).drop(columns=[right_on_0, left_on])
  else:
    df_merged = df_merged_0.drop(columns=[right_on_0, left_on])

  df_merged = df_merged.rename(columns={right_on_1: left_on}).drop_duplicates().reset_index(drop=True)

  # handle unmapped OP codes
  if method == "complete":
    df_na = df_merged[df_merged[left_on].isna()].copy()
    if df_na.empty:
      logger.info("All OP names successfully converted to OP codes")

      return df_merged

    else:
      unmapped_ops = df_na[left_on].unique()
      logger.error(f"Unmapped OPs detected: {len(unmapped_ops)} items. Missing OPs: {unmapped_ops}")
      raise ValueError(
        f"{len(unmapped_ops)} unmapped OP(s) found: {unmapped_ops}."
        f"Please update sheets {sheets_name}: {sheets_url[:30]} [REDACTED]")

      return df

  elif method == "partial":
    rows_before = len(df_merged)
    df_merged = df_merged.dropna(subset=[left_on]).reset_index(drop=True)
    rows_after = len(df_merged)
    rows_dropped = rows_before - rows_after
    logger.info(f"Dropped {rows_dropped} rows with unmapped OP codes ({rows_dropped/rows_before*100:.2f}%)")

    return df_merged

  else:
    raise ValueError("method must be 'complete' or 'partial'")

def correct_scientific_notation(
      df:pd.DataFrame, sheets_url:str,
      sheets_name:str = config.CSN_SHEETS_NAME,
      df_column_0:str = config.CSN_DF_OP_CODE, df_column_1:str = config.CSN_DF_KM_MASTER,
      df_column_2:str = config.CSN_DF_TOKO_SAINTIFIK, df_column_3:str = config.CSN_DF_TOKO_BENAR,
      master_column_0:str = config.CSN_MASTER_OP_CODE, master_column_1:str = config.CSN_MASTER_KM_MASTER,
      master_column_2:str = config.CSN_MASTER_TOKO_SAINTIFIK, master_column_3:str = config.CSN_MASTER_TOKO_BENAR
    ) -> pd.DataFrame:
  """
  Change the store code that changes due to scientific format when exporting from database to the actual store code.
  
  Example:
  Store code: '8.00E+34' -> Store code: '8E34'

  Parameters:
  -----------
  df : pd.DataFrame
    DataFrame containing 'Toko Benar' column.
  sheets_url : str
    URL of the Google Sheets.
  sheets_name : str
    Name of the Google Sheets.
  df_column_0 : str
    Name of the column containing OP code.
  df_column_1 : str
    Name of the column containing KM Master.
  df_column_2 : str
    Name of the column containing Toko Saintifik.
  df_column_3 : str
    Name of the column containing Toko Benar.
  master_column_0 : str
    Name of the column containing OP code in master toko.
  master_column_1 : str
    Name of the column containing KM Master in master toko.
  master_column_2 : str
    Name of the column containing Toko Saintifik in master toko.
  master_column_3 : str
    Name of the column containing Toko Benar in master toko.

  Returns:
  --------
  pd.DataFrame
    DataFrame with store codes fixed.
  
  Raises:
  -------
  TypeError
    If any of the specified columns are not of string type.
  """
  logger.info("Starting scientific notation correction for store codes")

  # check data types for df
  for col in [df_column_0, df_column_1, df_column_2, df_column_3]:
    if df[col].dtype != 'object':
      raise TypeError(f"Column '{col}' must be string type, got {df[col].dtype}")
    
  # import master store data
  sh = sheets_loader(sheets_url)
  worksheet = sh.worksheet(sheets_name)
  df_master = pd.DataFrame(worksheet.get_all_values())
  df_master.columns = df_master.iloc[0]
  df_master = df_master[1:]
  df_master = df_master.reset_index(drop=True)
  df_master = df_master[[master_column_0, master_column_1, master_column_2, master_column_3]].copy()

  logger.info(f"Loaded {len(df_master)} store mappings from sheets {sheets_name}")

  # check data types for df_master
  for col in [master_column_0, master_column_1, master_column_2, master_column_3]:
    if df_master[col].dtype != 'object':
      raise TypeError(f"Master column '{col}' must be string type, got {df_master[col].dtype}")

  # count data that has a store with the symbol ',' or '.' (scientific notation, example: 8.00E+34)
  df_comma = df[df[df_column_3].astype(str).str.contains(r'\,')].copy()
  df_period = df[df[df_column_3].astype(str).str.contains(r'\.')].copy()
  rows_comma = len(df_comma)
  rows_period = len(df_period)

  logger.info(f"Found {rows_comma} stores with comma delimiter, {rows_period} with period delimiter")

  # rename scientific notation to store code
  # if scientific code with delimiter ',' example 8,00E+34
  if rows_comma > 0:
    mapping = {
      (row[master_column_0], row[master_column_1], row[master_column_2].replace(".", ",")): 
      row[master_column_3] for _, row in df_master.iterrows()
    }
    df[df_column_3] = df.apply(
      lambda r: mapping.get((r[df_column_0], r[df_column_1], r[df_column_2]), r[df_column_3]),
      axis=1
    )
  # if scientific code with delimiter '.' example 8.00E+34
  elif rows_period > 0:
    mapping = {
      (row[master_column_0], row[master_column_1], row[master_column_2].replace(",", ".")): 
      row[master_column_3] for _, row in df_master.iterrows()
    }
    df[df_column_3] = df.apply(
      lambda r: mapping.get((r[df_column_0], r[df_column_1], r[df_column_2]), r[df_column_3]),
      axis=1
    )

  # store a list of store codes in df_master that is not scientific to avoid repeating master fixes
  not_scientific_list = list(df_master[df_master[master_column_3].astype(str).str.contains(r'\.')][master_column_3])

  # check for remaining scientific notation
  df_comma_period = df[df[df_column_3].astype(str).str.contains(r'\,|\.')].copy()
  df_comma_period = df_comma_period[~df_comma_period[df_column_3].isin(not_scientific_list)].copy()
  rows_comma_period = len(df_comma_period)
  sample_comma_period = df_comma_period[df_column_3].head(5).tolist()

  if rows_comma_period > 0:
    logger.warning(
    f"Found {rows_comma_period} invalid store codes containing '.' or ','. "
    f"Sample: {sample_comma_period}")
    raise ValueError(
        f"{rows_comma_period} invalid store codes contain '.' or ','. "
        f"Please update sheets {sheets_name}: {sheets_url[:30]} [REDACTED]")

  else:
    logger.info("All store codes successfully corrected.")

  return df

if __name__ == "__main__":
  from dotenv import load_dotenv
  import os

  # get environment variables
  env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
  load_dotenv(env_path)
  sheets_url = os.getenv("SHEETS_URL")

  # get data
  data_path = os.path.join(os.path.dirname(__file__), "..", "data", "1. Operational Data - Januari 2025.csv")
  df = pd.read_csv(data_path, sep=';', low_memory=False, dtype=str)

  # # run
  df = convert_to_op_code(df, sheets_url)
  print(correct_scientific_notation(df, sheets_url))