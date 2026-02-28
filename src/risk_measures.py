from src.bond_math import *
import pandas as pd
import numpy as np

# --- Risk & Scenario Tools (TBD) ---
#bond_duration()
#bond_convexity()
#price_change_due_to_rate_shift()

# Implementing functions for effective duration and convexity under constant yield assumption

def effective_duration(price_minus, price_plus, price_0, delta_y=0.01):
    """
    Computes effective duration using finite difference.
    """
    return (price_minus - price_plus) / (2 * price_0 * delta_y)

def effective_convexity(price_minus, price_0, price_plus, delta_y=0.01):
    """
    Computes effective convexity using finite difference.
    """
    return (price_minus + price_plus - 2 * price_0) / (price_0 * delta_y**2)


def macaulay_duration(flows, discount_rate):
    """
    Computes the Macaulay Duration of a sequence of cash flows, given a per-period discount rate (e.g., 3% is 6% for semiannual).
    """
    discounted_flows = discount(flows.index, discount_rate)*pd.DataFrame(flows)
    weights = discounted_flows/discounted_flows.sum()
    return np.average(flows.index, weights=weights.iloc[:,0])


def modified_duration(macaulay_duration, discount_rate, coupons_per_year):
    """
    Computes the Modified Duration from the Macaulay Duration.
    
    Parameters:
    - macaulay_duration: duration in periods
    - discount_rate: annual yield (e.g., 0.07 for 7%)
    - coupons_per_year: number of coupon payments per year (e.g., 2)
    """
    per_period_rate = discount_rate / coupons_per_year
    return macaulay_duration / (1 + per_period_rate)

# Function to compute price change using duration and convexity approximation
def price_change_approx(duration, convexity, delta_y):
    """
    Estimates percentage price change using duration and convexity adjustment.

    Parameters:
    - duration: Modified or effective duration
    - convexity: Effective convexity
    - delta_y: Yield change (as decimal, e.g., 0.01 for 1%)

    Returns:
    - Estimated percentage price change (in %)
    """
    return -duration * delta_y + 0.5 * convexity * delta_y ** 2



def bond_total_return(monthly_prices, principal, coupon_rate, coupons_per_year):
    """
    Computes the total return of a Bond based on monthly bond prices and coupon payments
    Assumes that dividends (coupons) are paid out at the end of the period (e.g. end of 3 months for quarterly div)
    and that dividends are reinvested in the bond
    """
    coupons = pd.DataFrame(data = 0, index=monthly_prices.index, columns=monthly_prices.columns)
    t_max = monthly_prices.index.max()
    pay_date = np.linspace(12/coupons_per_year, t_max, int(coupons_per_year*t_max/12), dtype=int)
    coupons.iloc[pay_date] = principal*coupon_rate/coupons_per_year
    total_returns = (monthly_prices + coupons)/monthly_prices.shift()-1
    return total_returns.dropna()


def calculate_holding_return(
    bond,
    flows,
    reinvest_coupons=False,
    reinvest_rate=None,
    convention="actual/365.25"
):
    """
    Computes the holding period return for a bond with optional reinvestment of coupons.

    Parameters:
        bond (BondInput): Bond object with metadata
        flows (pd.Series): Future cash flows (datetime index)
        dirty_price (float): Purchase price (clean + accrued)
        reinvest_coupons (bool): Whether coupons are reinvested
        reinvest_rate (float or None): Annual reinvestment rate. If None, defaults to bond's coupon rate.
        convention (str): Day count basis (only 'actual/365.25' supported for now)

    Returns:
        dict: PnL breakdown and return metrics
    """
    def year_frac(start, end):
        return get_year_fraction(start, end, convention)

    # Filter only future flows
    flows = flows[flows.index > bond.settlement_date]

    # Use bond coupon rate as default reinvestment rate
    reinvest_rate = reinvest_rate if reinvest_rate is not None else bond.coupon_rate
    m = bond.coupon_freq
    i = reinvest_rate / m

    # Track return components
    total_coupon = 0.0
    reinvested_interest = 0.0
    reinvestment_value = 0.0

    final_cf_date = flows.index[-1]
    final_payment = flows.iloc[-1]

    # Reinvest all but final coupon
    for dt, amt in flows.iloc[:-1].items():
        t_remaining = year_frac(dt, final_cf_date)
        n = int(round(t_remaining * m))
        if reinvest_coupons:
            fv = amt * ((1 + i)**n)
            reinvestment_value += fv
            reinvested_interest += fv - amt
        else:
            reinvestment_value += amt    
        total_coupon += amt

    # Handle final coupon (no reinvestment) - Rmk: generate_cash_flows() already adds principal to final payment
    #final_coupon = bond.notional * bond.coupon_rate / m
    expected_coupon = bond.notional * bond.coupon_rate / m
    final_coupon = min(final_payment, expected_coupon)
    final_principal = final_payment - final_coupon   

    total_coupon += final_coupon
    reinvestment_value += final_coupon
    final_principal = final_payment - final_coupon

    # Clean price paid
    clean_price_paid = bond.price_clean * bond.notional / 100


    # Dirty price paid (clean + accrued interest)
    accrued_interest_paid = compute_accrued_interest(bond, convention)

    dirty_price = clean_price_paid + accrued_interest_paid

    total_cash = final_principal + reinvestment_value
    T = year_frac(bond.settlement_date, final_cf_date)
    annualized_return = (total_cash / dirty_price)**(1 / T) - 1



    # Accrued interest paid
    accrued_interest_paid = dirty_price - clean_price_paid

    # Attribution components
    capital_gain = final_principal - clean_price_paid
    net_coupon_income = total_coupon - accrued_interest_paid
    pnl = capital_gain + net_coupon_income + reinvested_interest

    return {
        "Total Cash": total_cash,
        "Dirty Price Paid": dirty_price,
        "Clean Price Paid": clean_price_paid,
        "Accrued Interest Paid": accrued_interest_paid,
        "Capital Gain": capital_gain,
        "Net Coupon Income": net_coupon_income,
        "Reinvestment Interest": reinvested_interest,
        "Reinvestment FV": reinvestment_value,
        "PnL": pnl,
        "PnL Attribution": {
            "Capital Gain": capital_gain,
            "Net Income (Coupons - Accrual)": net_coupon_income,
            "Reinvestment Interest": reinvested_interest
        },
        "Holding Period Return (%)": (total_cash / dirty_price - 1) * 100,
        "Annualized Return (%/year)": annualized_return * 100,
        "Holding Period (Years)": T
    }


def calculate_partial_holding_return(
    bond,
    flows,
    sale_date,
    sale_clean_price,
    reinvest_coupons=False,
    reinvest_rate=None,
    convention="actual/365.25"
):
    """
    Computes holding period return when bond is sold before maturity.

    Parameters:
        bond (BondInput): Bond metadata object
        flows (pd.Series): Cash flows (datetime index)
        dirty_price (float): Purchase price (clean + accrued)
        sale_date (datetime): Exit date
        sale_clean_price (float): Exit clean price
        reinvest_coupons (bool): Whether to reinvest received coupons
        reinvest_rate (float or None): Annual reinvestment rate (defaults to bond coupon rate)
        convention (str): Day count convention

    Returns:
        dict: PnL components and return metrics
    """
    def year_frac(start, end):
        return get_year_fraction(start, end, convention)

    reinvest_rate = reinvest_rate if reinvest_rate is not None else bond.coupon_rate
    m = bond.coupon_freq
    i = reinvest_rate / m

    # Filter flows strictly between settlement and sale date
    received_flows = flows[(flows.index > bond.settlement_date) & (flows.index <= sale_date)]

    reinvestment_value = 0.0
    reinvested_interest = 0.0
    total_coupon = 0.0

    for dt, amt in received_flows.items():
        t_remaining = year_frac(dt, sale_date)
        n = int(round(t_remaining * m))
        if reinvest_coupons:
            fv = amt * ((1 + i) ** n)
            reinvestment_value += fv
            reinvested_interest += fv - amt
        else:
            reinvestment_value += amt
        total_coupon += amt

    # Sale proceeds (clean + accrued)
    sale_clean = sale_clean_price * bond.notional / 100
    last_cf_before_sale = flows[flows.index <= sale_date].index.max()
    accrued_days = (sale_date - last_cf_before_sale).days
    days_in_period = 365.25 / m
    accrued_interest_sale = bond.notional * bond.coupon_rate / m * accrued_days / days_in_period
    dirty_sale_price = sale_clean + accrued_interest_sale

    total_cash = dirty_sale_price + (reinvestment_value if reinvest_coupons else total_coupon)
    T = year_frac(bond.settlement_date, sale_date)

    # Purchase price components
    clean_price_paid = bond.price_clean * bond.notional / 100

    # Dirty price paid (clean + accrued interest)

    accrued_interest_paid = compute_accrued_interest(bond, convention)
    dirty_price = clean_price_paid + accrued_interest_paid

    #accrued_interest_paid = dirty_price - clean_price_paid

    capital_gain = sale_clean - clean_price_paid

    net_coupon_income = total_coupon - accrued_interest_paid + accrued_interest_sale

    pnl = capital_gain + net_coupon_income + reinvested_interest

    return {
        "Total Cash": total_cash,
        "Sale Clean Price": sale_clean,
        "Sale Accrued Interest": accrued_interest_sale,
        "Dirty Sale Price": dirty_sale_price,
        "Clean Price Paid": clean_price_paid,
        "Dirty Price Paid": dirty_price,
        "Accrued Interest Paid": accrued_interest_paid,
        "Capital Gain": capital_gain,
        "Net Coupon Income": net_coupon_income,
        "Reinvestment Interest": reinvested_interest,
        "Reinvestment FV": reinvestment_value,
        "PnL": pnl,
        "PnL Attribution": {
            "Capital Gain": capital_gain,
            "Net Income (Coupons - Accrual)": net_coupon_income,
            "Reinvestment Interest": reinvested_interest
        },
        "Holding Period Return (%)": (total_cash / dirty_price - 1) * 100,
        "Annualized Return (%/year)": ((total_cash / dirty_price) ** (1 / T) - 1) * 100,
        "Holding Period (Years)": T
    }
