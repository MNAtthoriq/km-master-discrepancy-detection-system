"""
Utility functions for KM Master Discrepancy Detection System
Contains setup logging and repetitive helper functions for analysis and visualization
"""

import logging
import config
import pandas as pd
import time
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import seaborn as sns

# setup logging
logging.basicConfig(
    level=config.LOG_LEVEL, format=config.LOG_FORMAT
) # get override from utils.py later (force=True)
logger = logging.getLogger(__name__)

def setup_logging(
    log_file_path:str = config.LOGS_PATH, 
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

def mask_numeric_value(
    value,
    mask_char:str = '*',
    symbols_to_preserve:tuple = config.SYMBOLS_TO_PRESERVE,
    hide_values:bool = config.HIDE_VALUES
) -> str:
    """
    Mask numeric values for data privacy while preserving ALL structure.

    Parameters:
    -----------
    value : int, float, or str
        Numeric value to mask.
    mask_char : str
        Character to use for masking.
    symbols_to_preserve : tuple
        Symbols to preserve when checking for zero values.

    Returns:
    --------
    str
        Masked numeric value as a string.
    """
    # Handle None or empty and if hide_values is False
    if value is None:
        return str(value)

    # Convert to string
    value_str = str(value).strip()

    if value_str == '' or not hide_values:
        return value_str

    # Check if value is zero (preserve zeros with all symbols)
    # Remove all symbols to check numeric value
    numeric_only = value_str
    for symbol in symbols_to_preserve:
        numeric_only = numeric_only.replace(symbol, '')

    try:
        if float(numeric_only) == 0:
            return value_str  # Keep original format for zeros
    except ValueError:
        pass

    # Mask all digits, preserve everything else (signs, commas, periods, %, spaces)
    masked = ''.join(
        mask_char if c.isdigit() else c
        for c in value_str
    )

    return masked 

def filter_iqr(
    df:pd.DataFrame, column:str = config.IQR_COLUMN, 
    lower_constant:float = config.LOWER_IQR_CONSTANT, 
    upper_constant:float = config.UPPER_IQR_CONSTANT
) -> tuple:
    '''
    Apply IQR filtering to a DataFrame column to remove outliers.

    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame.
    column : str
        Column name to apply IQR filtering on.
    lower_constant : float
        Constant to multiply with IQR for lower bound.
    upper_constant : float 
        Constant to multiply with IQR for upper bound.
    
    Returns:
    --------
    tuple
        Filtered DataFrame, Q1, Q3, IQR, lower bound, upper bound.
    '''
    logger.info(f"Applying IQR filter on column '{column}' with constants: lower={lower_constant}, upper={upper_constant}")

    # calculate Q1, Q3, and IQR
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    # calculate bounds
    lower_bound = Q1 - (lower_constant * IQR)
    upper_bound = Q3 + (upper_constant * IQR)

    # filter dataframe
    df_filtered = df[
        (df[column] >= lower_bound) & (df[column] <= upper_bound)
    ].copy()

    rows_before = len(df)
    rows_after = len(df_filtered)
    rows_removed = rows_before - rows_after
    pct_removed = (rows_removed / rows_before * 100) if rows_before > 0 else 0

    logger.info(f"IQR filter applied on '{column}': {mask_numeric_value(f'{rows_removed:,}')} rows removed ({pct_removed:.2f}%)")
    
    return df_filtered, Q1, Q3, IQR, lower_bound, upper_bound

def plot_outlier(
    df:pd.DataFrame, name:str = "Main Method",
    column:str = config.IQR_COLUMN, 
    lower_constant:float = config.LOWER_IQR_CONSTANT, 
    upper_constant:float = config.UPPER_IQR_CONSTANT,
    lower_zoom_constant:float = config.LOWER_ZOOM_CONSTANT, 
    upper_zoom_constant:float = config.UPPER_ZOOM_CONSTANT,
    hide_values:bool = config.HIDE_VALUES
) -> None:
    '''
    Plot outlier detection using IQR method for a DataFrame column.

    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame.
    name : str
        Name of the method or dataset.
    column : str
        Column name to plot outlier detection on.
    lower_constant : float
        Constant to multiply with IQR for lower bound.
    upper_constant : float 
        Constant to multiply with IQR for upper bound.
    lower_zoom_constant : float
        Constant to determine zoomed area lower limit.
    upper_zoom_constant : float
        Constant to determine zoomed area upper limit.
    hide_values : bool
        Whether to hide numeric values on the plot.
    '''
    logger.info(f"Plotting outlier detection for '{name}' on column '{column}' for '{name}'")

    _, Q1, Q3, IQR, lower_bound, upper_bound = filter_iqr(
        df, column, lower_constant, upper_constant
    )
    lower_zoom = Q1 - (lower_zoom_constant * IQR)
    upper_zoom = Q3 + (upper_zoom_constant * IQR)

    # set zoomed dataframe
    df_zoom = df[(df[column] >= lower_zoom) & (df[column] <= upper_zoom)].copy()

    # set colors and style
    colors = sns.color_palette("deep")
    bg_color = "#F9F9F9"
    sns.set_style("white", {'figure.facecolor': bg_color})
    plt.rcParams['font.family'] = "serif"

    # create figure and gridspec
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(16, 28, figure=fig, hspace=0.3, wspace=0.4)

    # make axes
    ax_text = fig.add_subplot(gs[:2,:])
    ax_zoom = fig.add_subplot(gs[2:,:19])
    ax_legend = fig.add_subplot(gs[2:9,19:])
    ax_full = fig.add_subplot(gs[9:15,19:])

    # ax text
    # add text
    ax_text.text(
        0.5, 0.7, 'IQR Method for Outlier Detection', 
        transform=ax_text.transAxes,
        ha='center', va='center', 
        fontsize=20, fontweight='bold'
    )
    ax_text.text(
        0.5, 0.35, f'{name}',
        transform=ax_text.transAxes,
        ha='center', va='center', fontsize=20
    )
    # set background and hide axes
    ax_text.set_facecolor(bg_color)
    sns.despine(ax=ax_text, left=True, bottom=True)
    ax_text.xaxis.set_visible(False)
    ax_text.yaxis.set_visible(False)

    # ax zoom
    # kde plot
    sns.kdeplot(data=df_zoom, x=column, ax=ax_zoom, fill=True, color=colors[4])
    # add lines for bounds
    ax_zoom.axvline(lower_bound, color=colors[3], linestyle='dashed', linewidth=1.5)
    ax_zoom.axvline(upper_bound, color=colors[3], linestyle='dashed', linewidth=1.5)
    # set labels and limits
    ax_zoom.yaxis.set_visible(False)
    ax_zoom.set_xlim(ax_zoom.get_xlim())
    ax_zoom.set_xlabel(column, fontsize=12)
    # hide x tick labels if configured
    if hide_values:
        ax_zoom.set_xticklabels([])
    # Add transparent black boxes for outlier regions
    ax_zoom.axvspan(ax_zoom.get_xlim()[0], lower_bound, alpha=0.2, color=colors[3])
    ax_zoom.axvspan(upper_bound, ax_zoom.get_xlim()[1], alpha=0.2, color=colors[3])
    # add title as box
    ax_zoom.text(
        0.117, 0.95,
        "Zoomed Distribution",
        ha='center',
        va='center',
        transform=ax_zoom.transAxes,
        bbox=dict(facecolor="white", edgecolor="black", boxstyle="round")
    )

    # ax legend
    # create legend
    legend_elements = [
    Line2D([0], [0], color=colors[3], linestyle='dashed', linewidth=1.5, 
           label=f'Lower Bound: {mask_numeric_value(f"{lower_bound:,.1f}")} KM\n   (k = {lower_constant:.2f})'),
    Line2D([0], [0], color=colors[3], linestyle='dashed', linewidth=1.5, 
           label=f'Upper Bound: {mask_numeric_value(f"{upper_bound:,.1f}")} KM\n   (k = {upper_constant:.2f})'),
    Patch(facecolor=colors[3], alpha=0.2, label='Outlier Region'),
    ] 
    ax_legend.legend(handles=legend_elements, loc='center', fontsize=12, frameon=True,
            fancybox=True, shadow=True, title='Legends\n', title_fontsize=12).get_title().set_fontweight('bold')
    # set background and hide axes
    ax_legend.set_facecolor(bg_color)
    sns.despine(ax=ax_legend, left=True, bottom=True)
    ax_legend.xaxis.set_visible(False)
    ax_legend.yaxis.set_visible(False)

    # ax full
    # kde plot
    sns.kdeplot(data=df, x=column, ax=ax_full, fill=True, color=colors[4])
    # add lines for bounds
    ax_full.axvline(lower_bound, color=colors[3], linestyle='dashed', linewidth=1.5)
    ax_full.axvline(upper_bound, color=colors[3], linestyle='dashed', linewidth=1.5)
    # set labels and limits
    ax_full.yaxis.set_visible(False)
    ax_full.set_xlim(ax_full.get_xlim())
    ax_full.set_xlabel(column, fontsize=12)
    # hide x tick labels if configured
    if hide_values:
        ax_full.set_xticklabels([])
    # Add transparent black boxes for outlier regions
    ax_full.axvspan(ax_full.get_xlim()[0], lower_bound, alpha=0.2, color=colors[3])
    ax_full.axvspan(upper_bound, ax_full.get_xlim()[1], alpha=0.2, color=colors[3])
    # add title as box
    ax_full.text(
        0.2, 0.9,
        "Full Distribution",
        ha='center',
        va='center',
        transform=ax_full.transAxes,
        bbox=dict(facecolor="white", edgecolor="black", boxstyle="round")
    )

    # show plot
    plt.show()

    logger.info(f"Outlier detection plot generated for '{name}' on column '{column}' for '{name}'")

def pivot_and_remove_low_freq_stores(
    df:pd.DataFrame, 
    count_toko:int = config.COUNT_TOKO
) -> pd.DataFrame:
    '''
    Create a pivot table and remove low-frequency stores.

    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame.
    count_toko : int
        Minimum frequency threshold to keep a store.
    
    Returns:
    --------
    pd.DataFrame
        Filtered pivot table DataFrame.
    '''
    # validate column in dataframe
    required_columns = ['OP', 'Toko', 'Kode Zona', 'KM Master', 'KM Tempuh']
    for col in required_columns:
        if col not in df.columns:
            logger.exception(f"Column '{col}' not found in DataFrame.")
            raise ValueError(f"Column '{col}' not found in DataFrame.")
        
    # create pivot table
    pivot_table = pd.pivot_table(
        df, index=['OP', 'Toko', 'Kode Zona'],
        values=['KM Master', 'KM Tempuh'],
        aggfunc={
            'Toko': 'count',
            'KM Master': 'mean',
            'KM Tempuh': 'mean'
        }
    )
    
    # format pivot table
    pivot_table = pivot_table.rename(columns={'Toko': 'Freq Toko'}).reset_index()
    pivot_table = pivot_table[
        ['OP', 'Toko', 'Kode Zona', 'Freq Toko', 'KM Master', 'KM Tempuh']
    ]
    pivot_table['KM Tempuh'] = pivot_table['KM Tempuh'].round()

    logger.info(f"Pivot table created: {mask_numeric_value(f'{len(pivot_table[['OP', 'Toko']].drop_duplicates()):,}')} unique stores")

    # remove low-frequency stores
    pivot_table_filtered = pivot_table[pivot_table['Freq Toko'] > count_toko].copy()

    logger.info(f"After removing low-frequency stores with frequency <= {count_toko}: {mask_numeric_value(f'{len(pivot_table_filtered[['OP', 'Toko']].drop_duplicates()):,}')} unique stores")

    return pivot_table_filtered

def get_unique_stores(
    df:pd.DataFrame, 
    columns:list = config.UNIQUE_STORE_COLUMNS
) -> tuple:
    '''
    Get unique store combinations from a DataFrame.

    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame.
    columns : list
        List of column names to consider for unique store combinations.
    
    Returns:
    --------
    tuple
        Tuple of unique store combinations.
    '''
    # validate columns
    for col in columns:
        if col not in df.columns:
            logger.exception(f"Column '{col}' not found in DataFrame.")
            raise ValueError(f"Column '{col}' not found in DataFrame.")
        
    return tuple(map(tuple, df[columns].drop_duplicates().values))

def get_diff_unique_stores(
    df1:pd.DataFrame, df2:pd.DataFrame, 
    columns:list = config.UNIQUE_STORE_COLUMNS
) -> tuple:
    '''
    Get the difference in unique store combinations between two DataFrames.

    Parameters:
    -----------
    df1 : pd.DataFrame
        First input DataFrame.
    df2 : pd.DataFrame
        Second input DataFrame.
    columns : list
        List of column names to consider for unique store combinations.
    
    Returns:
    --------
    tuple
        Tuple of unique store combinations present in df1 but not in df2.
    '''
    # validate columns
    for col in columns:
        if col not in df1.columns:
            logger.exception(f"Column '{col}' not found in first DataFrame.")
            raise ValueError(f"Column '{col}' not found in first DataFrame.")
        if col not in df2.columns:
            logger.exception(f"Column '{col}' not found in second DataFrame.")
            raise ValueError(f"Column '{col}' not found in second DataFrame.")
        
    # get unique stores from both dataframes    
    set1 = set(get_unique_stores(df1, columns))
    set2 = set(get_unique_stores(df2, columns))

    return tuple(set1 - set2)

class DataTracker:
    def __init__(
        self, name:str = "DataTracker"
    ) -> None:
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

        # hide values if configured
        display_rows = mask_numeric_value(f"{current_rows:,}")
        display_change = mask_numeric_value(f"{change:+,}")

        # log progress
        logger.info(
            f"[{self.name}] Step: {step_name} | Counts: {display_rows} | "
            f"Change: {display_change} ({change_pct:+.2f}%) | Retention: {retention_pct:.2f}% | "
            f"Step Time: {step_duration:.2f}s | Cumulative Time: {cumulative_time:.2f}s"
        )

    def get_final_rows(self) -> int:
        '''
        Get the final row count tracked.

        Returns:
        --------
        int
            Final row count.
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
            "Counts": self.rows,
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
        df_summary["Counts"] = df_summary["Counts"].apply(
            lambda x: mask_numeric_value(f"{x:,}")
        )
        df_summary["Change"] = df_summary["Change"].apply(
            lambda x: mask_numeric_value(f"{x:+,}")
        )
        df_summary["Change (%)"] = df_summary["Change (%)"].map("{:+.2f}".format)
        df_summary["Retained (%)"] = df_summary["Retained (%)"].map("{:.2f}".format)
        df_summary["Duration (s)"] = df_summary["Duration (s)"].map("{:.2f}".format)
        df_summary["Cumulative Time (s)"] = df_summary["Cumulative Time (s)"].map("{:.2f}".format)

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
    hide_values : bool
        Whether to hide numeric values in the summary.
    '''
    # calculate stores
    validated_stores_pct = (
        (validated_stores / total_stores * 100) if total_stores > 0 else 0
    )

    total_rec_stores = (
        sum(stores.get_final_rows() for stores in stores_result.values())
    )
    total_rec_stores_pct = (
        (total_rec_stores / total_stores * 100) if total_stores > 0 else 0
    )

    unprocessed_stores = total_stores - (validated_stores + total_rec_stores)
    unprocessed_stores_pct = (
        (unprocessed_stores / total_stores * 100) if total_stores > 0 else 0
    )

    total_time = sum(tracker.get_total_time() for tracker in times_result.values())

    # console summary
    BOLD = '\033[1m'
    RESET = '\033[0m'
    print(f"\n{BOLD} KM MASTER DISCREPANCY DETECTION SYSTEM SUMMARY {RESET}")
    # store summary
    print("\n" + "="*70)
    print(f"{BOLD}EXECUTION STORE SUMMARY{RESET}")
    print("="*70)
    print(f"{'Total Analyzed Stores':<30}: {f"{mask_numeric_value(f"{total_stores:,}"):>8}"} stores")
    print(f"{'Validated Stores':<30}: {f"{mask_numeric_value(f"{validated_stores:,}"):>8}"} stores ({validated_stores_pct:05.2f}%)")
    print("\nRecommendations by Method:")
    print("-"*70)
    for method_name, tracker in stores_result.items():
        method_stores = tracker.get_final_rows()
        method_stores_pct = (
            (method_stores / total_stores * 100) if total_stores > 0 else 0
        )
        print(f"{method_name:<30}: {f"{mask_numeric_value(f"{method_stores:,}"):>8}"} stores ({method_stores_pct:05.2f}%)")
    print("-"*70)
    print(f"{'Total Recommended Stores':<30}: {f"{mask_numeric_value(f"{total_rec_stores:,}"):>8}"} stores ({total_rec_stores_pct:05.2f}%)")
    print(f"\n{'Unprocessed Stores':<30}: {f"{mask_numeric_value(f"{unprocessed_stores:,}"):>8}"} stores ({unprocessed_stores_pct:05.2f}%)")
    # time summary
    print("\n" + "="*70)
    print(f"{BOLD}EXECUTION TIME SUMMARY{RESET}")
    print("="*70)
    for method_name, tracker in times_result.items():
        method_time = tracker.get_total_time()
        print(f"{method_name:<30}: {method_time:>8.2f} secs")
    print("-"*70)
    print(f"{'Total Execution Time':<30}: {total_time:>8.2f} secs ({total_time/60:05.2f} mins)\n")

    logger.info(f"Displayed results summary: {mask_numeric_value(f'{total_stores:,}')} total stores, {mask_numeric_value(f'{validated_stores:,}')} validated stores, {mask_numeric_value(f'{total_rec_stores:,}')} recommended stores, {mask_numeric_value(f'{unprocessed_stores:,}')} unprocessed stores, total execution time {total_time:.2f} secs.")

if __name__ == "__main__":
    pass