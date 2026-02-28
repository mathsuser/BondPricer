
import pandas as pd
from src.cashflows import *
from src.bond_math import *

class BondInput:
    def __init__(self, 
                 identifier: str,
                 issue_date: str,
                 maturity_date: str,
                 settlement_date: str,
                 coupon_rate: float,
                 notional: float,
                 freq: int = 2,
                 market_price: float = None,
                 coupon_days: list = None):
        self.identifier = identifier
        self.issue_date = pd.to_datetime(issue_date)
        self.maturity_date = pd.to_datetime(maturity_date)
        self.settlement_date = pd.to_datetime(settlement_date)
        self.coupon_rate = coupon_rate
        self.notional = notional
        self.freq = freq
        self.coupon_days = coupon_days or ["05-15", "11-15"]
        self.market_price = market_price

    def display_bond(self, results=None):
        """
        Prints a summary of the bond with optional pricing and return details.

        Parameters:
            accrued_interest (float or None): If provided, shown in summary
            dirty_price (float or None): If provided, shown in summary
            results (dict or None): H2M return analysis output
        """
        print(f"\nBond Summary - {self.identifier}")
        print("-------------------------------")
        print(f"Issue Date:        {self.issue_date.date()}")
        print(f"Settlement Date:   {self.settlement_date.date()}")
        print(f"Maturity Date:     {self.maturity_date.date()}")
        print(f"Coupon:            {self.coupon_rate * 100:.2f}% (paid {self.freq}x per year)")
        print(f"Notional:          ${self.notional:,.0f}")
        print(f"Observed Price:       ${self.market_price:,.6f}" if self.market_price is not None else "Observed Price:       -")
        print("-------------------------------")

        if results:
            print(f"\nTotal Cash at Maturity: ${results['Total Cash']:,.2f}")
            print(f"PnL (H2M):              ${results['PnL']:,.2f}")
            print(f"Annualized Return:      {results['Annualized Return'] * 100:.2f}%")
        


class Bond(BondInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def cash_flows(self):

        """
        Uses the coupon_schedule to return the schedule of coupon and principal payments for a bond as a Series indexed by payment date.
        """

        cf = coupon_schedule(self.settlement_date, self.maturity_date, self.coupon_days, self.notional, self.coupon_rate, self.freq)
        return cf


 

    def price(self, par_yields=None, interest_rate = 0.03, convention = "actual/360"):
        """
        Calls the pricers in bond_math.py to price the bond. It returns clean price, dirty price and accrued interest
        """
        

        if par_yields is None: 
            # Fallback to flat yield

            price_df = bond_price_flat(self.maturity_date, self.coupon_days,  self.settlement_date,  self.notional, self.coupon_rate, self.freq, interest_rate, convention)

        else: 
            # use the par_yields. 
            price_df = full_bond_price_from_par_yields(self.maturity_date, par_yields, self.coupon_days,  self.settlement_date,  self.notional, self.coupon_rate, self.freq, convention)

        return price_df
    




            