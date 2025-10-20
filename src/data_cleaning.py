"""
Data Preprocessing for KM Master Discrepancy Detection
"""

from data_loader import sheets_loader
import pandas as pd   
import os
from dotenv import load_dotenv

def op_code(df: pd.DataFrame, sheets_url: str, sheets_name: str='Master Kode OP', method: str='complete', left_on: str='OP', right_on_0: str='Operating Point', right_on_1: str='Kode OP') -> pd.DataFrame:
  """
  Rename Operating Point (OP) name to OP code by merging it with master op data from Google Sheets.
  Example:
  OP name: 'Point Balikpapan Reguler' -> OP code: 'PBPNR'

  Parameters:
  df (pd.DataFrame): DataFrame containing OP name column
  sheets_url (str): URL of the Google Sheets
  sheets_name (str): Name of the Google Sheets
  method (str): Method of dealing with OP who doesn't use the OP Code. Can be either 'complete' or 'partial'. 'complete' will raise an error if there is an OP who doesn't use the OP Code, while 'partial' will drop the OP.

  Returns:
  pd.DataFrame: DataFrame with OP name column renamed to OP code.

  Raises:
  ValueError: If method is not 'complete' or 'partial'.
  """
  # import data master op
  sh = sheets_loader(sheets_url)
  worksheet = sh.worksheet(sheets_name)
  df_master_op = pd.DataFrame(worksheet.get_all_records())

  # rename op name to op code
  df_merged_0 = pd.merge(df, df_master_op, left_on=left_on, right_on=right_on_0, how='left')
  unmatched = df_merged_0[df_merged_0[right_on_1].isna()].copy()
  matched = df_merged_0[~df_merged_0[right_on_1].isna()].copy()

  # if op name is already op code
  if not unmatched.empty:
    unmatched_merged = pd.merge(unmatched.drop(columns=[right_on_0, right_on_1]), df_master_op, left_on=left_on, right_on=right_on_1, how='left')
    df_merged = pd.concat([matched, unmatched_merged], ignore_index=True).drop(columns=[right_on_0, left_on])
  else:
    df_merged = df_merged_0.drop(columns=[right_on_0, left_on])

  df_merged = df_merged.rename(columns={right_on_1: left_on}).drop_duplicates().reset_index(drop=True)

  # if there is op code that is not in master op and want to repair it
  if method == 'complete':
    df_na = df_merged[df_merged[left_on].isna()].copy()
    if df_na.empty:
      print("There is no OP who doesn't use the OP Code")

      return df_merged

    else:
      print(f'Please crosscheck master op in sheet {sheets_name} at {sheets_url}')
      print('The following OP are not in master op:')
      for i in df_na[left_on].unique():
        print(i)

      return df

  # if there is op code that is not in master op and want to drop it
  elif method == 'partial':
    df_merged = df_merged.dropna(subset=[left_on]).reset_index(drop=True)

    return df_merged

  else:
    raise ValueError('method must be "complete" or "partial"')

def change_scientific_notation(df: pd.DataFrame,
                              sheets_url: str,
                              sheets_name: str='Master Saintifik Toko',
                              df_column_0: str= 'OP', df_column_1: str= 'KM Master',
                              df_column_2: str= 'Toko', df_column_3: str= 'Toko',
                              master_column_0: str= 'Kode OP', master_column_1: str= 'KM Master',
                              master_column_2: str= 'Toko Saintifik', master_column_3: str= 'Toko Benar'):
  """
  Change the store code that changes due to scientific format when exporting from database to the actual store code.
  Example:
  Store code: '8.00E+34' -> Store code: '8E34'

  Parameters:
  df (pd.DataFrame): DataFrame containing 'Toko Benar' column
  df_column_0 (str): Name of the column containing OP code
  df_column_1 (str): Name of the column containing KM Master
  df_column_2 (str): Name of the column containing Toko Saintifik
  df_column_3 (str): Name of the column containing Toko Benar
  sheets_url (str): URL of the Google Sheets
  sheets_name (str): Name of the Google Sheets
  master_column_0 (str): Name of the column containing OP code in master toko
  master_column_1 (str): Name of the column containing KM Master in master toko
  master_column_2 (str): Name of the column containing Toko Saintifik in master toko
  master_column_3 (str): Name of the column containing Toko Benar in master toko

  Returns:
  pd.DataFrame: DataFrame with 'Toko Benar' column containing store codes
  """
  # Check data types for df
  for col in [df_column_0, df_column_1, df_column_2, df_column_3]:
    if df[col].dtype != 'object':
      raise TypeError(f"Column '{col}' must be string type, got {df[col].dtype}")
    
  # import data master toko
  sh = sheets_loader(sheets_url)
  worksheet = sh.worksheet(sheets_name)
  df_master = pd.DataFrame(worksheet.get_all_values())
  df_master.columns = df_master.iloc[0]
  df_master = df_master[1:]
  df_master = df_master.reset_index(drop=True)

  # Check data types for df_master
  for col in [master_column_0, master_column_1, master_column_2, master_column_3]:
    if df_master[col].dtype != 'object':
      raise TypeError(f"Master column '{col}' must be string type, got {df_master[col].dtype}")

  # count data that has a store with the symbol ',' or '.' (scientific notation, example: 8.00E+34)
  df_comma = df[df[df_column_3].astype(str).str.contains(r'\,')].copy()
  df_period = df[df[df_column_3].astype(str).str.contains(r'\.')].copy()
  rows_comma = len(df_comma)
  rows_period = len(df_period)

  # rename scientific notation to store code
  # if scientific code with delimiter ',' example 8,00E+34
  if rows_comma > 0:
    mapping = {
      (row[master_column_0], row[master_column_1], row[master_column_2].replace(".", ",")): row[master_column_3] for _, row in df_master.iterrows()
      }
    df[df_column_3] = df.apply(
      lambda r: mapping.get((r[df_column_0], r[df_column_1], r[df_column_2]), r[df_column_3]),
      axis=1
    )
  # if scientific code with delimiter '.' example 8.00E+34
  elif rows_period > 0:
    mapping = {
      (row[master_column_0], row[master_column_1], row[master_column_2].replace(",", ".")): row[master_column_3] for _, row in df_master.iterrows()
      }
    df[df_column_3] = df.apply(
      lambda r: mapping.get((r[df_column_0], r[df_column_1], r[df_column_2]), r[df_column_3]),
      axis=1
    )

  # store a list of store codes in df_master that is not scientific to avoid repeating master fixes
  not_scientific_list = list(df_master[df_master[master_column_3].astype(str).str.contains(r'\.')][master_column_3])

  # count data that has stores with the symbol ',' or '.'
  df_comma_period = df[df[df_column_3].astype(str).str.contains(r'\,|\.')].copy()
  # count rows with stores not in not_scientific_list
  df_comma_period = df_comma_period[~df_comma_period[df_column_3].isin(not_scientific_list)].copy()
  rows_comma_period = len(df_comma_period)

  if rows_comma_period > 0:
    print(f'Please crosscheck master toko in sheet {sheets_name} at {sheets_url}')
    print("The following store that still has the symbols ',' and '.':")
    print(df_comma_period)

  else:
    print('Store codes have been fixed')

  return df

if __name__ == "__main__":
  import gdown 

  # get environment variables
  env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
  load_dotenv(env_path)
  sheets_url = os.getenv("SHEETS_URL")
  opr_ids = os.getenv("GDOWN_IDS_OPERATIONAL").split(',')

  # get data
  data_path = os.path.join(os.path.dirname(__file__), "..", ".data\\")
  gdown.download(id=opr_ids[0], output=data_path)
  df = pd.read_csv(os.path.join(data_path,"1. KM Master Nasional - Januari 2025.csv"), sep=';', low_memory=False, dtype=str)

  # # run
  df = op_code(df, sheets_url)
  print(change_scientific_notation(df, sheets_url))