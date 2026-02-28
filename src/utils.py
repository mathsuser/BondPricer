import pandas as pd
import warnings


def load_yield_curve_data(data_path = '../data/par-yield-curve-rates-1990-2023.csv'):
    """
    Loads US Treasury par yields from Excel and formats them into a clean DataFrame.

    Returns:
        pd.DataFrame: DataFrame indexed by datetime with columns as tenors
    """
    yields_df = pd.read_csv(data_path, index_col = 'date')
    yields_df.index = pd.to_datetime(yields_df.index)
    yields_df.index.name = 'Date'
    yields_df= yields_df.apply(pd.to_numeric, errors = 'coerce')
    # The yields are in %. 
    
    warnings.warn("Warning: the par yields are in %!")
    return yields_df



def get_yields_on_date(yields_df, target_date):
    """
    Pulls Treasury yields on a given date, or nearest previous date if unavailable.
    
    Returns:
        yields (pd.Series): available par_yields_df compatible with downstream modules
        missing (list): list of tenors with missing data
        used_date (pd.Timestamp): actual date used
    """
    
    target_date = pd.to_datetime(target_date)
    if target_date in yields_df.index:
        used_date = target_date
    else:
        # fallback to previous available date
        available_dates = yields_df.index[yields_df.index <= target_date]
        if available_dates.empty:
            raise ValueError("No available data before the requested date.")
        used_date = available_dates[-1]
        print(f"No data for {target_date.date()}, using previous available date: {used_date.date()}")

    yields = yields_df.loc[used_date].to_frame('par_yield')
    yields['par_yield'] = yields['par_yield']/100
    tenors = yields.index.to_list()
    tenor_year = [
        round(float(s.split()[0]), 2) / 12 if s.endswith("mo") else round(float(s.split()[0]),2)
        for s in tenors]  
    yields['tenor_years'] = tenor_year
    yields.set_index('tenor_years', inplace=True)    
    yields.index.name = 'tenor_years'
    available = yields.dropna()
    missing = list(yields[yields['par_yield'].isna()].index.round(2))
    
    print(f"\n Yield Curve for {used_date.date()} (original request: {target_date.date()}):")
    print("Available tenors:")
    print(available)

    if missing:
        print("\n Missing tenors:")
        print(missing)

    warnings.warn("The yields have been converted to decimals. ")    
    
    return available, missing, pd.Timestamp(used_date)
