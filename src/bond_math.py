
#
"""
bond_math.py

Core fixed income pricing and analytics functions for BondPricer.


- Price bonds using flat yields, par yields, and bootstrapped spot curves using par yields and linear interpolation
- Calculate clean/dirty prices, accrued interest, and yield to maturity (YTM)


Functions:
    bond_cash_flows, coupon_schedule, bond_price_elementary, bond_price_flat,
    bond_price_from_par_yields, full_bond_price_from_par_yields, bootstrap_spot_rates,
    interpolate_par_yields, compute_ytm, _calculate_w, _get_last_coupon, _freq_to_compounding

Author: Fatima Ezzahra Jabiri
Created: 2026-02-22
"""
# bond_math.py
# Core fixed income tools for pricing

import numpy as np
import pandas as pd
from scipy.optimize import newton
from datetime import datetime
from src.cashflows import *
from src.discount_utils import * 




def _calculate_w(settlement_date, next_coupon_date, last_coupon_date, convention="actual/360"):
    numerator = get_year_fraction(settlement_date, next_coupon_date, convention)
    denominator = get_year_fraction(last_coupon_date, next_coupon_date, convention)
    return numerator / denominator


def _get_last_coupon(settlement_date, coupon_dates, freq):
    next_coupon = min([d for d in coupon_dates if d >= settlement_date])
    if freq ==1:
        last_coupon_year = next_coupon.year - 1
        last_coupon_month = next_coupon.month
        last_coupon_day = next_coupon.day
    elif freq == 2: 
        last_coupon_year = next_coupon.year
        last_coupon_month = next_coupon.month - 6
        if last_coupon_month <= 0:
            last_coupon_year -= 1
            last_coupon_month += 12
        last_coupon_day = next_coupon.day
    elif freq == 4:
        last_coupon_year = next_coupon.year
        last_coupon_month = next_coupon.month - 3
        if last_coupon_month <= 0:
            last_coupon_year -= 1
            last_coupon_month += 12
        last_coupon_day = next_coupon.day

    else:
        raise ValueError(f"Provide a valid {freq}: either 1, 2 or 4")            
    # For semiannual: subtract 6 months
    
    last_coupon = pd.Timestamp(year=last_coupon_year, month=last_coupon_month, day=last_coupon_day)
    return last_coupon


def _freq_to_compounding(freq):
    mapping = {1: "annual", 2: "semiannual", 4: "quarterly"}
    return mapping.get(freq, "semiannual")




def bootstrap_spot_curve(par_yields, compounding="semiannual"):
    freq_map = {"annual": 1, "semiannual": 2, "quarterly": 4, "continuous": 1}
    freq = freq_map.get(compounding, 2)

    # Convert par yields from % to decimal and parse tenors to year floats
    raw_yields = {tenor_to_years(k): v / 100 for k, v in par_yields.items()}
    raw_series = pd.Series(raw_yields)

    # Build full maturity timeline based on max tenor
    max_T = max(raw_series.index)
    step = 1 / freq
    full_index = np.arange(step, max_T + step, step).round(6)  # avoid float precision error
    full_yields = raw_series.reindex(full_index).interpolate() # linear interpolation 

    spot_rates = {}

    for T in full_index:
        y = full_yields.loc[T]
        if T <= 1.0:
            # For zero-coupon T-Bills, spot rate = par yield (already annualized)
            # Need to tackle the case 9m T-Bill in case of quarterly compounding
            spot_rates[T] = y
        else:
            N = int(T * freq) 
            C = y * 100 / freq # Here,  100 is used as Par value?
            coupon_sum = 0
            for i in range(1, N):
                t = i / freq
                r_i = spot_rates[t]
                df_i = spot_to_discount_factor(r_i, t, compounding)
                coupon_sum += C * df_i
            D_T = (100 - coupon_sum) / (100 + C) # What is D_T?
            r_T = discount_factor_to_spot(D_T, T, compounding)
            spot_rates[T] = r_T

    return pd.Series(spot_rates).sort_index()


def interpolate_par_yields(par_df, freq = 2): 
    """
    Interpolate par yields to get values at every coupon period. 
    
    Parameters: 
    par_df: pd.DataFrame
        DataFrame with tenor_years as index and 'par_yield' column
    freq : int

    Returns
    pd.DataFrame: Complete par yield curve at every (1/freq) year. 
    """

    # Get min and max tenor
    min_tenor = par_df.index.min()
    max_tenor = par_df.index.max()

    # Create array of all tenors at coupon frequency intervals

    step = 1 / freq
    all_tenors = np.arange(min_tenor, max_tenor + step, step)
    all_tenors = np.round(all_tenors, 4)

    # Interpolate par yields at all tenors
    standard_tenors = par_df.index.values
    standard_yields = par_df['par_yield'].values

    interpolated_yields = np.interp(all_tenors, standard_tenors, standard_yields)
    
    # return DataFrame

    return pd.DataFrame({'tenor_years': all_tenors, 
                         'par_yield': interpolated_yields}).set_index('tenor_years')
    


def bootstrap_spot_rates(par_yields_df, freq = 2):
    """
    Bootstrap spot rates from a set of par yields.

    Parameters: 
    par_yields_df: pd.DataFrame
        DataFrame with tenors_years as index and 'par_yield' column

    freq: int
        Coupon frequency per year
    
    """
    all_tenors = par_yields_df.index.values
    all_par_yields = par_yields_df['par_yield'].values

    # Filter par_yields to remove those with tenors less that than of the compoundig freq

    par_yields = []
    tenors = []
    for t, c in zip(all_tenors, all_par_yields):
        if t >=  (1/freq):
            tenors.append(t)
            par_yields.append(c)

    # First tenor: par_yield = spot_rate (T-bill assumption)
    n_tenors = len(tenors)
    spot_rates = np.zeros(n_tenors)  
    spot_rates[0] = par_yields[0]
    for i in range(1, n_tenors): 
        ti = tenors[i]
        ci = par_yields[i]
        n_periods = int(round(ti * freq))
        coupon = ci / freq
        if (ti <1):
            spot_rates[i] = par_yields[i]
        else: 
            pv_coupons = 0.0
            for j in range(1, n_periods):
                s_j = spot_rates[j-1]

                discount_factor = (1 + s_j/freq)**j

                pv_coupons += coupon /discount_factor

            # Solve for spot rate at tenor T
            
            final_payment = 1 + coupon
            remaining_pv = 1 - pv_coupons
            discount_factor_ti = final_payment / remaining_pv
            s_ti = freq * (discount_factor_ti**(1/n_periods) - 1)

            spot_rates[i] = s_ti

    return pd.DataFrame({'tenor_years': tenors,
                         'spot_rate':spot_rates}).set_index('tenor_years')             


def bond_price_from_par_yields(maturity, par_yields, principal=100, coupon_rate = 0.0, freq = 2):

        """
        Computes the price of a bond using a bootstrapped spot rate curve derived from par yields.
    
        Objective:
            Price a coupon bond by discounting each cash flow at its corresponding spot rate, where spot rates are obtained by bootstrapping from a set of par yields.

        Methodology:
            1. Generate the bond's cash flow schedule using maturity, principal, coupon rate, and frequency.
            2. Filter the par yields to include only those with tenors less than or equal to the bond's maturity.
            3. Interpolate the par yields to obtain yields at all coupon periods.
            4. Bootstrap the spot rate curve from the interpolated par yields.
            5. For each cash flow, assign the appropriate spot rate (by matching or interpolating on time).
            6. Calculate the discount factor for each cash flow using the spot rate and compounding convention.
            7. Compute the present value (PV) of each cash flow and sum to get the bond price.

        Parameters:
            maturity (float):
                Bond maturity in years.
            par_yields (pd.DataFrame or pd.Series):
                Par yields indexed by tenor (years). Should have a 'par_yield' column if DataFrame.
            principal (float, optional):
                Face value of the bond. Default is 100.
            coupon_rate (float, optional):
                Annual coupon rate (as a decimal, e.g., 0.05 for 5%). Default is 0.0.
            freq (int, optional):
                Number of coupon payments per year (e.g., 2 for semiannual). Default is 2.

        Returns:
            bond_price (float):
                Present value (price) of the bond.
            cash_flows (pd.DataFrame):
                DataFrame with cash flows, times, spot rates, discount factors, and PVs for each payment.
        """

        # Build the cashflows schedule
        cash_flows = bond_cash_flows(maturity, principal, coupon_rate, freq)

        # Determine the required par_yields by filtering tenors less than the maturity of the bond. 
        mask = par_yields.index <= maturity
        par_yields_filtered = par_yields[mask]

        # Interpolate par yields and bootstrap spot rates
        par_df = interpolate_par_yields(par_yields_filtered, freq)
        spot_rates = bootstrap_spot_rates(par_df, freq)

        # Get the associated spot_rate for each cash flow
        cash_flows['spot_rate'] = cash_flows['time_years'].apply(lambda t: spot_rates.loc[round(t, 4), 'spot_rate'])

        # Calculate the discount factor using compounding string
        compounding = _freq_to_compounding(freq)
        cash_flows['discount_factor'] = spot_to_discount_factor(
            cash_flows['spot_rate'],
            cash_flows['time_years'],
            compounding=compounding
        )

        # Calculate the pv of cashflows
        cash_flows['pv'] = cash_flows['discount_factor'] * cash_flows['cash_flow']
        cash_flows['pv'] = cash_flows['pv'].round(4)
        bond_price = cash_flows['pv'].sum()
        return bond_price, cash_flows




def bond_price_elementary(maturity, principal=100, coupon_rate = 0.0, freq = 2, interest_rate = 0.03):
    """
    Computes the price of a bond on the coupon payment date (i.e., the next coupon payment is one full period away).
    Assumes that interest_rate is constant over time and is given par annum. 
    
    """
    cash_flows = bond_cash_flows(maturity, principal, coupon_rate, freq)

    per_period_rate = interest_rate / freq

    cash_flows['discount_factor'] = discount(cash_flows['cash_flow'].index, per_period_rate)

    price = present_value(cash_flows['cash_flow'], per_period_rate)

    if isinstance(price, pd.Series) or isinstance(price, pd.DataFrame):
        price = price.squeeze()
    return price, cash_flows


def bond_price_flat(maturity_date, coupon_days = ["01-15", "07-15"],  settlement_date = pd.Timestamp.today(),   principal=100, coupon_rate = 0.0, freq = 2, interest_rate = 0.03, convention = "actual/360"):
    """
    Computes the full (dirty) price, clean price, and accrued interest of a bond between coupon payment dates.

    Returns:
    dirty_price (float): Present value of all future cash flows (including accrued interest).
    clean_price (float): Dirty price minus accrued interest.
    accrued (float): Accrued interest since last coupon.

    Notes:
    - Uses robust period fraction calculation for accrual.
    - Handles coupon schedules, conventions, and vectorized discounting.
    """
    schedule =coupon_schedule(settlement_date, maturity_date, coupon_days, principal, coupon_rate, freq)
    coupon_dates = schedule.index
    
    first_coupon_date = min(coupon_dates)
    last_coupon_date = _get_last_coupon(settlement_date, coupon_dates, freq)
    w_periods = _calculate_w(settlement_date, first_coupon_date, last_coupon_date, convention)

    n_coupons = len(coupon_dates)
    
    coupon_times = np.arange(0, n_coupons, dtype=float) + w_periods
    
    discounts = discount(coupon_times, interest_rate/freq)
    dirty_price = discounts.multiply(schedule.values, axis='rows').sum()
    if isinstance(dirty_price, pd.Series) or isinstance(dirty_price, pd.DataFrame):
        dirty_price = dirty_price.squeeze()
        if hasattr(dirty_price, 'item'):
            dirty_price = dirty_price.item()


    # Compute accrual: 
    coupon_payment = (coupon_rate/freq) * principal 
    accrued = coupon_payment * (1 - w_periods)
    # Deduce Clean Price
    clean_price = dirty_price - accrued

    price = {"Dirty Price": dirty_price, 
             "Clean Price": clean_price,
             "Accrual": accrued}
    return pd.Series(price).to_frame()



def full_bond_price_from_par_yields(maturity_date, par_yields, coupon_days = ["01-15", "07-15"],  settlement_date = pd.Timestamp.today(),   principal=100, coupon_rate = 0.0, freq = 2, convention = "actual/360"): 

    """
    Computes the full (dirty) price, clean price, and accrued interest of a bond using a bootstrapped spot rate curve from par yields, for any settlement date (including between coupon payments).

    Objective:
        Price a coupon bond at any settlement date by discounting each cash flow at its corresponding spot rate (bootstrapped from par yields), and compute both dirty and clean prices, including accrued interest.

    Methodology:
        1. Generate the bond's coupon schedule and cash flows from settlement to maturity, using the provided coupon dates and frequency.
        2. Calculate the year fraction to each cash flow from the settlement date, using the specified day count convention.
        3. Filter and interpolate the par yields to cover all required tenors up to the bond's maturity.
        4. Bootstrap the spot rate curve from the interpolated par yields.
        5. For each cash flow, assign the appropriate spot rate (by matching or interpolating on time).
        6. Calculate the discount factor for each cash flow using the spot rate and compounding convention.
        7. Compute the present value (PV) of each cash flow and sum to get the dirty price.
        8. Calculate accrued interest and subtract from dirty price to obtain the clean price.

    Parameters:
        maturity_date (datetime or str):
            Bond maturity date.
        par_yields (pd.DataFrame or pd.Series):
            Par yields indexed by tenor (years). Should have a 'par_yield' column if DataFrame.
        coupon_days (list of str, optional):
            List of coupon payment dates in 'MM-DD' format. Default is ["01-15", "07-15"].
        settlement_date (datetime or str, optional):
            Settlement date for pricing. Default is today.
        principal (float, optional):
            Face value of the bond. Default is 100.
        coupon_rate (float, optional):
            Annual coupon rate (as a decimal, e.g., 0.05 for 5%). Default is 0.0.
        freq (int, optional):
            Number of coupon payments per year (e.g., 2 for semiannual). Default is 2.
        convention (str, optional):
            Day count convention for year fraction calculations (e.g., 'actual/360', 'actual/actual'). Default is 'actual/360'.

    Returns:
        price (pd.DataFrame):
            DataFrame with Dirty Price, Clean Price, and Accrual.
        cash_flows (pd.DataFrame):
            DataFrame with cash flows, times, spot rates, discount factors, and PVs for each payment.
    """

    # Build the coupon schedule
    schedule =coupon_schedule(settlement_date, maturity_date, coupon_days, principal, coupon_rate, freq)
    cash_flows = schedule.to_frame('cash_flow')
    
    coupon_dates = schedule.index

    maturity_years = get_year_fraction(settlement_date, maturity_date, convention)

    first_coupon_date = min(coupon_dates)
    last_coupon_date = _get_last_coupon(settlement_date, coupon_dates, freq)
    w_periods = _calculate_w(settlement_date, first_coupon_date, last_coupon_date, convention)

    n_coupons = len(coupon_dates)
    coupon_times = np.arange(0, n_coupons, dtype=float) + w_periods
    cash_flows['time_years'] = [get_year_fraction(settlement_date, dt, convention) for dt in coupon_dates]

    # Build the spot rates curve by bootstrapping par yields 
    mask = par_yields.index <= maturity_years
    par_yields_filtered = par_yields[mask]
    par_df = interpolate_par_yields(par_yields_filtered, freq)
    spot_rates = bootstrap_spot_rates(par_df, freq)

    def _get_spot_rate_for_time(t, spot_rates):
        # Interpolate if t is not exactly in the index
        if t in spot_rates.index:
            return spot_rates.loc[t]
        else:
            return np.interp(t, spot_rates.index, spot_rates.values)

    # If spot_rates is a DataFrame, convert to Series:
    if isinstance(spot_rates, pd.DataFrame):
        spot_rates = spot_rates['spot_rate']

    cash_flows['spot_rate'] = cash_flows['time_years'].apply(lambda t: _get_spot_rate_for_time(t, spot_rates))

    # Calculate the discount factor using compounding string
    compounding = _freq_to_compounding(freq)
    cash_flows['discount_factor'] = spot_to_discount_factor(
        cash_flows['spot_rate'],
        coupon_times,
        compounding=compounding
    )

    # Calculate the pv of cashflows and the dirty price
    cash_flows['pv'] = cash_flows['discount_factor'] * cash_flows['cash_flow']
    cash_flows['pv'] = cash_flows['pv'].round(4)
    dirty_price = cash_flows['pv'].sum()

    # Compute accrual: 
    coupon_payment = (coupon_rate/freq) * principal 
    accrued = coupon_payment * (1 - w_periods)
    # Deduce Clean Price
    clean_price = dirty_price - accrued

    price = {"Dirty Price": dirty_price, 
             "Clean Price": clean_price,
             "Accrual": accrued}
    return pd.Series(price).to_frame(), cash_flows




def compute_ytm(price_dirty, cash_flows, valuation_date, freq=2, guess=0.05, convention="actual/365.25"):
    """
    Computes the YTM (annualized) using the provided day count convention.
    """
    def year_frac(start, end):
        return get_year_fraction(start, end, convention)

    def npv(y):
        return sum([
            cf / (1 + y / freq)**(year_frac(valuation_date, dt) * freq)
            for dt, cf in cash_flows.items()
            if dt > valuation_date
        ]) - price_dirty

    return newton(npv, guess)




