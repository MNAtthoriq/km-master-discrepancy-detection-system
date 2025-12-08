"""
Utility functions for KM Master Discrepancy Detection System
Contains setup logging and repetitive helper functions for analysis and visualization
"""

import logging
import config
import pandas as pd
import time

# setup logging
logger = logging.getLogger(__name__)

def setup_logging(
        log_file_path:str = None, 
        log_level:int = config.LOG_LEVEL,
        log_format:str = config.LOG_FORMAT, 
        log_date_format:str = config.LOG_DATE_FORMAT
    ) -> None:
    """
    Setup logging configuration.

    Parameters:
    -----------
    log_file_path : str, optional
        Path to the log file. If None, logs will only be printed to console.
    log_level : int
        Logging level.
    log_format : str
        Format of the log messages.
    log_date_format : str
        Format of the date in log messages.
    """
    # configure logging
    handlers = [logging.StreamHandler()] # console handler

    if log_file_path: # if log file path is provided
        import os
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True) # create directory if not exists
        handlers.append(logging.FileHandler(log_file_path)) # add file handler
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=log_date_format,
        handlers=handlers,
        force=True # force=True to override any existing logging configuration
    ) 

class DataTracker:
    def __init__(self, name:str = "DataTracker") -> None:
        '''
        Class to track data processing steps, row counts, and execution time.

        Parameters:
        -----------
        name : str
            Name of the data tracker instance.
        '''
        # initialize data tracker 
        self.name = name
        self.start_rows = None
        self.start_time = time.time()

        # initialize data storage
        self.steps = []
        self.rows = []
        self.timestamps = []

        logger.info(f"Initialized DataTracker for: [{self.name}]")

    def track(
            self, df:pd.DataFrame, step_name:str, 
            rows_unique:list = None
        ) -> None:
        '''
        Track a data processing step by recording the step name, current row count, and execution time.

        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame being processed.
        step_name : str
            Name of the processing step.
        rows_unique : list, optional
            List of column names to consider for unique row counting. 
            If None, total rows will be counted.
        '''
        # track data at each step
        current_time = time.time()
        if rows_unique:
            current_rows =  len(df[rows_unique].drop_duplicates())
        else:
            current_rows = len(df)

        # store start rows
        if self.start_rows is None:
            self.start_rows = current_rows

        # calculate elapsed time
        if len(self.timestamps) > 0:
            step_duration = current_time - self.timestamps[-1]
        else:
            step_duration = current_time - self.start_time
        
        cumulative_time = current_time - self.start_time

        # calculate row change
        if len(self.rows) > 0:
            prev_rows = self.rows[-1]
            change = current_rows - prev_rows
            change_pct = (change / prev_rows * 100) if prev_rows > 0 else 0
            retention_pct = (current_rows / self.start_rows * 100) if self.start_rows > 0 else 0
        else:
            change = 0
            change_pct = 0
            retention_pct = 100.0
        
        # store data
        self.steps.append(step_name)
        self.rows.append(current_rows)
        self.timestamps.append(current_time)

        # log progress
        logger.info(
            f"[{self.name}] Step: {step_name} | Rows: {current_rows:,} | "
            f"Change: {change:<+} ({change_pct:.2f}%) | Retention: {retention_pct:.2f}% | "
            f"Step Time: {step_duration:.2f}s | Cumulative Time: {cumulative_time:.2f}s"
        )

    def get_total_rows(self) -> int:
        '''
        Get total rows tracked at the last step.

        Returns:
        --------
        int
            Total rows at the last tracked step.
        '''
        if self.rows:
            return self.rows[-1]
        else:
            return 0
    
    def get_total_time(self) -> float:
        '''
        Get total execution time since the start.
        
        Returns:
        --------
        float
            Total execution time in seconds.
        '''
        if self.timestamps:
            return self.timestamps[-1] - self.start_time
        else:
            return time.time() - self.start_time
    
    def summary(self) -> pd.DataFrame:
        '''
        Generate a summary DataFrame of the tracked data processing steps.

        Returns:
        --------
        pd.DataFrame
            Summary DataFrame with step names, row counts, changes, retention percentages, and execution times.
        '''
        if not self.steps:
            logger.warning(f"[{self.name}] no data tracked yet.")
            return pd.DataFrame()
        
        # calculate time
        step_durations = []
        for i in range(len(self.timestamps)):
            if i == 0:
                duration = self.timestamps[i] - self.start_time
            else:
                duration = self.timestamps[i] - self.timestamps[i-1]
            step_durations.append(duration)
        
        cumulative_times = [t - self.start_time for t in self.timestamps]

        # recap data
        df_summary = pd.DataFrame({
            "Step": self.steps,
            "Row Counts": self.rows,
            "Change": [self.rows[i] - self.rows[i-1] if i > 0 else 0 for i in range(len(self.rows))],
            "Change (%)": [
                ((self.rows[i] - self.rows[i-1]) / self.rows[i-1] * 100) if i > 0 and self.rows[i-1] > 0 else 0 
                for i in range(len(self.rows))
            ],
            "Retained (%)": [
                (self.rows[i] / self.start_rows * 100) if self.start_rows > 0 else 0 
                for i in range(len(self.rows))
            ],
            "Duration (s)": step_durations,
            "Cumulative Time (s)": cumulative_times
        })

        # format dataframe
        df_summary["Change %"] = df_summary["Change (%)"].map("{:+.2f}%".format)
        df_summary["Retained %"] = df_summary["Retained (%)"].map("{:+.2f}%".format)
        df_summary["Duration (s)"] = df_summary["Duration (s)"].map("{:.2f}s".format)
        df_summary["Cumulative Time (s)"] = df_summary["Cumulative Time (s)"].map("{:.2f}s".format)

        logger.info(f"[{self.name}] DataTracker summary generated for {len(self.steps)} steps.")
        return df_summary
        
def result_summary(
        total_stores:int, validated_stores:int,
        stores_result:dict, times_result: dict
    ) -> None:
    '''
    Display a summary of the data processing results including store counts and execution times.

    Parameters:
    -----------
    total_stores : int
        Total number of stores analyzed.
    validated_stores : int
        Number of validated stores.
    stores_result : dict
        Dictionary of DataTracker instances for store recommendations by method.
    times_result : dict
        Dictionary of DataTracker instances for execution times by method.
    '''
    # calculate stores
    validated_stores_pct = (validated_stores / total_stores * 100) if total_stores > 0 else 0

    total_rec_stores = sum(stores.get_total_rows() for stores in stores_result.values())
    total_rec_stores_pct = (total_rec_stores / total_stores * 100) if total_stores > 0 else 0

    unprocessed_stores = total_stores - (validated_stores + total_rec_stores)
    unprocessed_stores_pct = (unprocessed_stores / total_stores * 100) if total_stores > 0 else 0

    total_time = sum(tracker.get_total_time() for tracker in times_result.values())

    # console summary
    BOLD = '\033[1m'
    RESET = '\033[0m'
    print(f"\n{BOLD} KM MASTER DISCREPANCY DETECTION SYSTEM SUMMARY {RESET}")
    # store summary
    print("\n" + "="*70)
    print(f"{BOLD}EXECUTION STORE SUMMARY{RESET}")
    print("="*70)
    print(f"{'Total Analyzed Stores':<30}: {total_stores:>8,} stores")
    print(f"{'Validated Stores':<30}: {validated_stores:>8,} stores ({validated_stores_pct:05.2f}%)")
    print("\nRecommendations by Method:")
    print("-"*70)
    for method_name, tracker in stores_result.items():
        method_stores = tracker.get_total_rows()
        method_stores_pct = (method_stores / total_stores * 100) if total_stores > 0 else 0
        print(f"{method_name:<30}: {method_stores:>8,} stores ({method_stores_pct:05.2f}%)")
    print("-"*70)
    print(f"{'Total Recommended Stores':<30}: {total_rec_stores:>8,} stores ({total_rec_stores_pct:05.2f}%)")
    print(f"\n{'Unprocessed Stores':<30}: {unprocessed_stores:>8,} stores ({unprocessed_stores_pct:05.2f}%)")
    # time summary
    print("\n" + "="*70)
    print(f"{BOLD}EXECUTION TIME SUMMARY{RESET}")
    print("="*70)
    for method_name, tracker in times_result.items():
        method_time = tracker.get_total_time()
        print(f"{method_name:<30}: {method_time:>8.2f} secs")
    print("-"*70)
    print(f"{'Total Execution Time':<30}: {total_time:>8.2f} secs ({total_time/60:05.2f} mins)\n")
    print("="*70 + "\n")

    logger.info(f"Displayed results summary: {total_stores:,} total stores, {validated_stores:,} validated stores, {total_rec_stores:,} recommended stores, {unprocessed_stores:,} unprocessed stores, total execution time {total_time:.2f} secs.")


    
    
