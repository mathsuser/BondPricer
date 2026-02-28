"""
discount_utils.py

Core discounting, compounding, and date convention utilities for BondPricer.

- Compute discount factors and present values for cash flows
- Convert between spot rates, discount factors, and compounding conventions
- Handle day count conventions and tenor conversions

Functions: discount, present_value, spot_to_discount_factor, discount_factor_to_spot,
    get_year_fraction, tenor_to_years, inst_to_ann, ann_to_inst

Author: Fatima Ezzahra Jabiri
Created: 2026-02-22
"""
import numpy as np
import pandas as pd
from datetime import datetime

# --- Discounting & Compounding & Conventions ---

def discount(t, r):
    """
    Compute the price of a pure discount bond that pays a dollar at time period t
    and r is the per-period interest rate
    returns a |t| x |r| Series or DataFrame
    r can be a float, Series or DataFrame
    returns a DataFrame indexed by t
    """
    discounts = pd.DataFrame([(r+1)**-i for i in t])
    discounts.index = t
    return discounts

def present_value(cash_flows, r):
    """
    Compute the present value of a sequence of cash flows given by the time (as an index) and amounts
    r can be a scalar, or a Series or DataFrame with the number of rows matching the num of rows in flows
    """
    dates = cash_flows.index
    discounts = discount(dates, r)
    return discounts.multiply(cash_flows, axis='rows').sum()

def inst_to_ann(r):
    """
    Convert an instantaneous interest rate to an annual interest rate
    """
    return np.expm1(r)

def ann_to_inst(r):
    """
    Convert an annual interest rate to an instantaneous interest rate
    """
    return np.log1p(r)

def tenor_to_years(tenor_str):
    """
    Converts tenor strings like 'US3M', 'US2Y' to number of years.
    """
    if 'M' in tenor_str:
        return int(tenor_str.strip('USM')) / 12
    elif 'Y' in tenor_str:
        return int(tenor_str.strip('USY'))
    else:
        raise ValueError(f"Unknown tenor format: {tenor_str}")

def get_year_fraction(start: datetime, end: datetime, convention: str = "actual/360") -> float:
    days = (end - start).days
    

    if convention == "actual/365":
        return days / 365
    elif convention == "actual/365.25":
        return days / 365.25
    elif convention == "actual/360":
        return days / 360
    elif convention == "30/360":
        # U.S. 30/360 day count convention
        d1, d2 = start.day, end.day
        m1, m2 = start.month, end.month
        y1, y2 = start.year, end.year

        d1 = min(d1, 30)
        d2 = 30 if d1 == 30 else min(d2, 30)

        days_360 = 360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)
        return days_360 / 360
    elif convention == "actual/actual":
        # ISDA actual/actual: sum partial years
        total = 0.0
        current = start
        while current < end:
            year_end = datetime(current.year + 1, 1, 1)
            period_end = min(year_end, end)
            days_in_period = (period_end - current).days
            days_in_year = 366 if current.year % 4 == 0 and (current.year % 100 != 0 or current.year % 400 == 0) else 365
            total += days_in_period / days_in_year
            current = period_end
        return total
    else:
        raise ValueError(f"Unsupported day count convention: {convention}")


def spot_to_discount_factor(r, T, compounding="semiannual"):
    """
    Converts annualized spot rate to discount factor for a given maturity T (in years).
    """
    if compounding == "annual":
        return 1 / (1 + r)**T
    elif compounding == "semiannual":
        return 1 / (1 + r / 2)**(2 * T)
    elif compounding == "quarterly":
        return 1 / (1 + r / 4)**(4 * T)
    elif compounding == "continuous":
        return np.exp(-r * T)
    else:
        raise ValueError(f"Unsupported compounding: {compounding}")

def discount_factor_to_spot(D, T, compounding="semiannual"):
    """
    Converts discount factor to annualized spot rate using specified compounding.
    """
    if compounding == "annual":
        return (1 / D)**(1 / T) - 1
    elif compounding == "semiannual":
        return 2 * ((1 / D)**(1 / (2 * T)) - 1)
    elif compounding == "quarterly":
        return 4 * ((1 / D)**(1 / (4 * T)) - 1)
    elif compounding == "continuous":
        return -np.log(D) / T
    else:
        raise ValueError(f"Unsupported compounding: {compounding}")