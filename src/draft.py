# For a generic Bond Class: 
def generate_coupon_dates(bond: BondInput):
    coupon_dates = []
    for year in range(bond.settlement_date.year, bond.maturity_date.year + 1):
        for mmdd in bond.coupon_days:
            coupon_date = pd.to_datetime(f"{year}-{mmdd}")
            if bond.settlement_date < coupon_date <= bond.maturity_date:
                coupon_dates.append(coupon_date)
    return pd.to_datetime(coupon_dates)

def generate_cash_flows(bond: BondInput):
    coupon_dates = generate_coupon_dates(bond)
    flows = pd.Series(bond.notional * bond.coupon_rate / bond.coupon_freq, index=coupon_dates)
    flows.iloc[-1] += bond.notional  # Add principal to final payment
    return flows


def compute_accrued_interest(bond: BondInput, convention="actual/365.25") -> float:
    """
    Computes accrued interest as of the settlement date using specified day count convention.
    """
    coupon_dates = generate_coupon_dates(bond)
    first_coupon = min(coupon_dates)

    if bond.settlement_date < first_coupon:
        last_coupon = bond.issue_date
    else:
        last_coupon = max([d for d in coupon_dates if d <= bond.settlement_date])

    accrual_fraction = get_year_fraction(last_coupon, bond.settlement_date, convention)
    accrued_interest = bond.coupon_rate * bond.notional * accrual_fraction

    return accrued_interest


def print_bond_summary(bond, results):
    """
    Prints a structured summary of bond characteristics and return analysis.
    Supports both H2M and early sale scenarios.
    """
    sold_before_maturity = 'Sale Clean Price' in results

    print(f"\nBond Summary - {bond.identifier}")
    print("-" * 31)
    print(f"Issue Date:        {bond.issue_date.date()}")
    print(f"Settlement Date:   {bond.settlement_date.date()}")

    if not sold_before_maturity:
        print(f"Maturity Date:     {bond.maturity_date.date()}")

    print(f"Coupon:            {bond.coupon_rate*100:.2f}% (paid {bond.coupon_freq}x per year)")
    print(f"Clean Price Paid:  ${results['Clean Price Paid']:,.6f}")
    print(f"Accrued Interest:  ${results['Accrued Interest Paid']:,.6f}")
    print(f"Dirty Price Paid:  ${results['Dirty Price Paid']:,.6f}")
    print(f"Notional:          ${bond.notional:,.0f}")

    print("\n----- Performance -----")
    print(f"Holding Period:         {results['Holding Period (Years)']:.2f} years")
    
    if sold_before_maturity:
        print(f"Sale Clean Price:       ${results['Sale Clean Price']:,.2f}")
        print(f"Sale Accrued Interest:  ${results['Sale Accrued Interest']:,.2f}")
        print(f"Dirty Sale Price:       ${results['Dirty Sale Price']:,.2f}")
        print(f"Total Proceeds:         ${results['Total Cash']:,.2f}")
    else:
        print(f"Total Cash Received:    ${results['Total Cash']:,.2f}")

    print(f"Total PnL:              ${results['PnL']:,.2f}")
    print(f"Holding Period Return:  {results['Holding Period Return (%)']:.2f}%")
    print(f"Annualized Return:      {results['Annualized Return (%/year)']:.2f}%")

    print("\n----- PnL Attribution -----")
    print(f"Capital Gain/Loss:      ${results['PnL Attribution']['Capital Gain']:,.2f}")
    print(f"Net Coupon Income:      ${results['PnL Attribution']['Net Income (Coupons - Accrual)']:,.2f}")
    print(f"Reinvestment Interest:  ${results['PnL Attribution']['Reinvestment Interest']:,.2f}")
