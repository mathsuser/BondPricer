# Basics of Bond Valuation

---

## I. Introduction

The estimation framework of the fair value of a fixed income security, namely a bond, consists of three steps:

1. Estimating the expected cashflows from the date of purchase to maturity
2. Estimating the appropriate discounting rates
3. Calculating the present value of these expected future cash flows

Among the fixed income securities there are the US treasury bonds which are issued by the US government. These USD denominated securities are commonly assumed to be default free and are therefore considered among the "safest" assets.

We shall be interested in the analysis of US treasury bonds with fixed coupons in this project. Therefore, we assume that default risk is zero, liquidity risk is zero, and cashflows are deterministic. Moreover, we assume that these bonds are not callable (option-free bonds).

In this setting, the least obvious step in determining the fair value is calculating the discounting rates. The following factors affect these rates:

1. Level of benchmark yields,
2. Risks that the market perceives the bondholder is exposed to,
3. The compensation the market expects to receive for these risks.

The minimum discount rate is the yield on US Treasuries. For riskier securities, a spread is added to compensate for additional risks such as default, liquidity, macroeconomic shocks, and other factors. This spread captures the risk premium.


**Goal:** Provide a systematic valuation framework for US Treasury bonds with fixed coupons and no embedded options.

---

## II. Core Concepts in Bond Valuation

### 1. Basic Concepts in Fixed Income Investing

#### Time value of money: 

A fundamental concept in finance — a dollar today is worth more than a dollar tomorrow because it can be invested to earn interest.

  **Example:** Receiving \$1 today and investing at 5% interest earns \$1.05 after one year. Conversely, receiving \$1 in a year is only worth \$0.9524 today if the discount rate is 5%:
  $PV = \frac{1}{1.05} = 0.9524$

#### Compounding and Discounting

In fixed income, two fundamental operations are used to value money over time:

- **Compounding** calculates the future value (FV) of a current sum.
- **Discounting** computes the present value (PV) of a known future amount.

Let’s define the core variables:

- \( t \): time in **years**
- \( r \): **nominal annual interest rate**
- \( k \): number of compounding periods per year (e.g., 1 for annual, 2 for semi-annual, 4 for quarter)


##### 1. Simple Interest

Simple interest assumes that interest is **not reinvested** over time:

\[
FV = PV \cdot (1 + r \cdot t)
\]
Therefore, $100 invested at at 5% interest for 3 years becomes 
\[
100 \cdot (1 + 0.05 \cdot 3) = 115.00
\]
This method is rarely used in fixed income pricing, but it’s helpful as an intuitive starting point.


##### 2. Discrete Compounding

When interest is compounded \( k \) times per year, we use:

\[
FV = PV \cdot \left(1 + \frac{r}{k} \right)^{k \cdot t}
\quad \text{or} \quad
PV = \frac{FV}{\left(1 + \frac{r}{k} \right)^{k \cdot t}}
\]

- \( r \) is still the annual rate
- For annual compounding (\( k = 1 \)):

\[
FV = 100 \cdot (1 + 0.05)^3 = 115.76
\]

- For quarterly compounding (\( k = 4 \)):

\[
FV = 100 \cdot \left(1 + \frac{0.05}{4} \right)^{12} \approx 116.14
\]

This is the standard convention in most bond markets.


##### 3. Continuous Compounding

As the number of compounding periods becomes infinite, we approach **continuous compounding**:

\[
FV = PV \cdot e^{r t}
\quad \Rightarrow \quad
100 \cdot e^{0.05 \cdot 3} \approx 116.18
\]

This is used in theoretical finance (e.g., derivatives and term structure modeling), but not in market practice for Treasuries.


##### 4. Effective Annual Rate (EAR)

The **Effective Annual Rate (EAR)** converts a nominal rate with compounding frequency \( k \) into a single annualized yield:

\[
EAR = \left(1 + \frac{r}{k} \right)^k - 1
\]

Used for comparing interest rates across different compounding schedules (e.g., 5% compounded monthly vs quarterly).


##### Summary Table: FV of $100 Over 3 Years at 5%

| Method                | Formula                             | Future Value |
|----------------------|-------------------------------------|--------------|
| Simple Interest       | \( 100 \cdot (1 + 0.05 \cdot 3) \)   | \$115.00     |
| Discrete Annual Comp. | \( 100 \cdot (1 + 0.05)^3 \)         | \$115.76     |
| Quarterly Compounding | \( 100 \cdot (1 + 0.0125)^{12} \)    | \$116.14     |
| Continuous Comp.      | \( 100 \cdot e^{0.05 \cdot 3} \)     | \$116.18     |

Even for short horizons, the compounding method leads to meaningful pricing differences — a critical consideration for long-duration bonds.


#### Bond conventions and day count basis: 

Bond valuation also depends on the method used to count days between payments. Conventions include:

  * **Actual/Actual** (used by US Treasuries)
  * **30/360** (common in corporate bonds)

  **Example:** Suppose a bond pays a 6% annual coupon semi-annually. If the last coupon date was January 1 and the settlement date is March 1:

  * **Actual/Actual** counts the exact number of days (59 days in this case).
    Accrued interest = $100 	\times 3\% 	\times \frac{59}{182} = 0.9725$

  * **30/360** assumes each month has 30 days (60 days total).
    Accrued interest = $100 	\times 3\% 	\times \frac{60}{180} = 1.00$

  This difference matters when settling trades and computing yield accurately.

  These influence accrued interest and yield calculations. For instance, interest accrued over a 31-day month differs under these methods.

#### Nominal vs. real returns:

  * **Nominal return** is the return without adjusting for inflation.
  * **Real return** adjusts for inflation to reflect true purchasing power.

  **Example:** If a bond yields 6% but inflation is 2%, the real return is:
  $r_{\text{real}} = \frac{1 + 0.06}{1 + 0.02} - 1 \approx 3.92\%$

#### Zero-coupon vs. coupon-bearing bonds:

  * A **zero-coupon bond** pays no periodic interest. It is issued at a discount and pays its full face value at maturity.

    **Example:** A 5-year zero-coupon bond priced at \$78.35 returns \$100 at maturity → implicit yield:
    $YTM = \left(\frac{100}{78.35}\right)^{1/5} - 1 = 5\%$

  * A **coupon-bearing bond** pays interest (coupon) periodically and returns principal at maturity. These bonds are less sensitive to interest rate changes due to earlier cash flows.


**Key Terminology**

| Term                    | Definition                                                      |
| ----------------------- | --------------------------------------------------------------- |
| Face Value (Par)        | Amount returned at maturity (usually \$100)                     |
| Coupon                  | Periodic interest payment (quoted annually, paid semi-annually) |
| Price                   | Current market price of the bond                                |
| Time to Maturity        | Time remaining until bond matures                               |


---


### 2. General Principles of Bond Pricing Using the DCF Model

At its core, bond pricing is an application of the **discounted cash flow (DCF)** principle. Each expected cash flow is discounted back to the present using an appropriate rate.

#### Present Value of a Single Future Payment

For a single future cash flow (CF) received at time \( t \), and assuming a constant annual discount rate \( i \), the present value is:

\[
PV(CF, 0) = \frac{CF}{(1 + i)^t}
\]


#### Present Value of a Level Annuity

If a bond pays a constant annual coupon \( C \) for \( N \) years, the present value is the sum of the annuity and the discounted face value (par):

\[
PV = C \cdot \frac{1 - (1 + i)^{-N}}{i} + \frac{\text{Par}}{(1 + i)^N}
\]

This assumes **annual payments** and a flat yield curve (constant discount rate).

#### Generalizing for Periodic Payments (e.g., Semi-Annual)

Let \( k \) be the number of coupon payments per year (e.g., \( k = 2 \) for semi-annual). Then the bond price becomes:

\[
\text{Bond Price} = \sum_{t=1}^{kN} \frac{C}{\left(1 + \frac{i}{k}\right)^t} + \frac{\text{Par}}{\left(1 + \frac{i}{k} \right)^{kN}}
\]

Where:
- \( C \): periodic coupon (e.g., semi-annual = annual coupon × 0.5)
- \( i \): quoted **annual** interest rate
- \( k \): number of periods per year
- \( N \): years to maturity


**Market Convention**: To compute the periodic discount rate, one divides the annual rate by \( k \). This is **not a result of math**, but a pricing convention.


####  Walkthrough Example

Consider a bond with the following characteristics:
- Time to maturity = 4 years  
- Par = \$100  
- Annual coupon = 6% (i.e., \$6/year or \$3 every 6 months)  
- Market yield = 7% annual, compounded semi-annually → periodic rate = 3.5%  
- Total payments = \( 2 \times 4 = 8 \)

Then:

\[
\text{Price} = \sum_{t=1}^{8} \frac{3}{(1.035)^t} + \frac{100}{(1.035)^8}
\approx 3 \cdot 6.4632 + 100 \cdot 0.7594 = 19.39 + 75.94 = 95.33
\]

We say that this bond sells **below par** because the coupon (6%) is less than the market yield (7%).


### 3. The DCF Model and the Concept of Yield Curve

The **traditional DCF approach** uses a **single discount rate** for all future cash flows. This is a simplification that assumes a flat yield curve.

However, each cash flow has a different time horizon. The more accurate approach is to treat a bond as a collection of **zero-coupon bonds** (ZCBs), each discounted at its own **spot rate**.


* **Yield Curve Shapes**

The **yield curve** reflects how interest rates vary with maturity. It can be:

1. **Flat**: short- and long-term rates are equal  
2. **Upward-sloping**: longer maturities have higher yields (normal case)  
3. **Inverted**: short-term yields exceed long-term ones (possible recession signal)


* **Why Use the Yield Curve?**

Each cash flow \( CF_t \) at time \( t \) should be discounted with its own spot rate \( s(t) \):

\[
\text{Bond Price} = \sum_{t=1}^{n} \frac{CF_t}{(1 + s(t))^t}
\quad \text{or} \quad
= \sum_{t=1}^{n} CF_t \cdot e^{-s(t)t} \quad \text{(if using continuous compounding)}
\]


* **Remarks:** 

- The U.S. Treasury **only issues zero-coupon bonds for maturities <= 1Y** (e.g., 3-month, 6-month bills).
- For longer maturities, the yield curve must be **bootstrapped** using coupon-bearing bonds.
- Dealers construct synthetic ZCBs to extract spot rates for use in pricing and risk models.

---

* **Treasury Maturities (On-the-Run Securities)**: 

Recall that **on-the-run** securities are the most recently issued U.S. Treasury securities of a particular maturity.

For example, the most recent 10-year Treasury bond issued by the U.S. government is called the on-the-run 10Y. All previous 10Y bonds still in circulation are called off-the-run.

The U.S. Treasury issues securities with maturities of:

- **Bills**: 1M, 3M, 6M, 1Y (zero-coupon)
- **Notes/Bonds**: 2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y (coupon-bearing)

To build a complete **yield curve**, interpolation and bootstrapping are required. This allows discounting every cash flow precisely at its correct maturity.

---

### 4. Understanding Yields and Rates

#### Yield to Maturity (YTM)

The **Yield to Maturity (YTM)** is the internal rate of return (IRR) of a bond. It is the single discount rate that equates the **present value of all future cash flows** (coupons + face value) to the **current market price**.

\[
P = \sum_{t=1}^{n} \frac{C}{(1 + y)^t} + \frac{F}{(1 + y)^n}
\]

Where:

- \( P \): current price
- \( C \): periodic coupon
- \( F \): face value (par)
- \( n \): number of periods until maturity
- \( y \): YTM to be solved numerically

YTM assumes:

- Bond is held to maturity
- All coupons are reinvested at the same YTM

#### Par Yield vs. Spot Rate


##### Spot Rate (\( s_T \))

- The spot rate \( s_T \) is the interest rate used to discount a **single** cash flow at time \( T \).
- Derived from zero-coupon bond prices or by **bootstrapping** coupon-bearing bonds.
- Used to discount **each individual cash flow**.

\[
\text{Price of 1-period zero} = \frac{1}{1 + s_1}
\qquad
\text{Price of 2-period zero} = \frac{1}{(1 + s_2)^2}
\]

General DCF pricing with spot rates:

\[
P = \sum_{t=1}^n \frac{C}{(1 + s_t)^t} + \frac{F}{(1 + s_n)^n}
\]


##### Par Yield \( y_T^{\text{par}} \)

- The par yield is the **coupon rate** that would price a bond **at par** (\( P = 100 \)) for a given maturity.
- It is a **weighted average of spot rates** over the bond's lifetime.

Formally, for semiannual coupon bonds:

\[
100 = \sum_{t=1}^{2T} \frac{c}{(1 + s_t/2)^t} + \frac{100}{(1 + s_{2T}/2)^{2T}} 
\Rightarrow c = y_T^{\text{par}} \cdot 100
\]

\[
\boxed{
\text{Par Yield} = \text{Weighted average of spot rates}
}
\]



**Remark:**


Spot rates allow for **accurate DCF valuation**, while par yields are useful for market summaries and comparisons.



### 5. Bootstrapping the Yield Curve

#### Why Bootstrapping?

Most bonds are **not** zero-coupon. In order to construct spot rates for all maturities, we must extract them from the prices of **coupon-bearing bonds** — this process is called **bootstrapping**.

In order to illustrate the bootstrapping step, consider a 2Y coupon bearing bond paying coupons semi-annually. To calculate the present value of this bond, one needs the spot rates: \( s_{0.5}, s_{1}, s_{1.5}, s_{2} \).  Two examples are considered below: 
- Example 1: All par yields (in annual terms) are observed.
- Example 2: The par yield of the 1.5Y US Treasury is missing. 



#### Bootstrapping Spot Rates — Example 1: Full Data Available

We are given the following **par yield curve** from on-the-run Treasuries. All bonds are priced at par, and all rates are reported as **bond-equivalent yields (BEY)**.

| Period | Maturity (Years) | Par Yield (BEY %) | Price   | Spot Rate (BEY %) |
|--------|------------------|-------------------|---------|-------------------|
| 1      | 0.5              | 3.00              | —       | 3.0000            |
| 2      | 1.0              | 3.30              | —       | 3.3000            |
| 3      | 1.5              | 3.50              | 100.00  | 3.5053            |
| 4      | 2.0              | 3.90              | 100.00  | 3.9164            |

Let us now derive the **spot rates** for the 1.5Y and 2.0Y bonds using the known earlier spot rates.


##### Step 1: Derive Initial Spot Rates from 0.5Y and 1Y

**0.5-Year Bond**  
Quoted yield (BEY) = 3.00% ⇒ semiannual spot rate:

\[
s_{0.5} = \frac{3.00\%}{2} = 1.50\% = 0.0150
\]

**1-Year Bond**  
Quoted yield (BEY) = 3.30% ⇒ semiannual spot rate:

\[
s_{1.0} = \frac{3.30\%}{2} = 1.65\% = 0.0165
\]

These spot rates can be used directly to discount the first cash flows in the bootstrapping of longer maturities.


##### Step 2: Derive the 1.5-Year Spot Rate

Coupon = 3.5% annually → \$1.75 semiannually.  
Cash flows for the 1.5Y bond:

| Time (Years) | Cash Flow (\$) |
|--------------|----------------|
| 0.5          | 1.75           |
| 1.0          | 1.75           |
| 1.5          | 101.75         |

Known:
- \( z_1 = 3.00\% \Rightarrow 0.0150 \)
- \( z_2 = 3.30\% \Rightarrow 0.0165 \)

\[
P = \frac{1.75}{(1 + z_1)^1} + \frac{1.75}{(1 + z_2)^2} + \frac{101.75}{(1 + z_3)^3}
\]

\[
100 = \frac{1.75}{1.0150} + \frac{1.75}{(1.0165)^2} + \frac{101.75}{(1 + z_3)^3}
\]

\[
100 = 1.7241 + 1.6936 + \frac{101.75}{(1 + z_3)^3}
\Rightarrow \frac{101.75}{(1 + z_3)^3} = 96.5822
\]

\[
(1 + z_3)^3 = \frac{101.75}{96.5822} = 1.05351
\Rightarrow z_3 = (1.05351)^{1/3} - 1 \approx 0.017527
\]

\[
\boxed{
\text{Annualized spot rate} = 2 \cdot z_3 = \textbf{3.5053\%}
}
\]


##### Step 3: Derive the 2.0-Year Spot Rate

Coupon = 3.9% annually → \$1.95 semiannually.  
Cash flows for the 2Y bond:

| Time (Years) | Cash Flow (\$) |
|--------------|----------------|
| 0.5          | 1.95           |
| 1.0          | 1.95           |
| 1.5          | 1.95           |
| 2.0          | 101.95         |

Known:
- \( z_1 = 0.0150 \)
- \( z_2 = 0.0165 \)
- \( z_3 = 0.017527 \)

\[
P = \sum_{t=1}^{3} \frac{1.95}{(1 + z_t)^t} + \frac{101.95}{(1 + z_4)^4} = 100
\]

Calculate first three terms:

\[
\frac{1.95}{1.0150} + \frac{1.95}{(1.0165)^2} + \frac{1.95}{(1.017527)^3}
= 1.9214 + 1.8871 + 1.8537 = 5.6622
\]

\[
\frac{101.95}{(1 + z_4)^4} = 100 - 5.6622 = 94.3378
\Rightarrow (1 + z_4)^4 = \frac{101.95}{94.3378} = 1.08014
\Rightarrow z_4 = (1.08014)^{1/4} - 1 \approx 0.019582
\]

\[
\boxed{
\text{Annualized spot rate} = 2 \cdot z_4 = \textbf{3.9164\%}
}
\]


**Conclusion**:  
This example shows how spot rates are extracted from par-priced coupon bonds, assuming **semiannual compounding**. Each step uses previously bootstrapped spot rates to discount earlier flows, isolating the next unknown rate.

This is the **benchmark bootstrapping case** — used when each maturity has a directly observable bond (on-the-run).

#### Bootstrapping Spot Rates — Example 2: Interpolation Needed

Suppose we are given par yield data for 0.5Y, 1.0Y, and 2.0Y Treasuries, but **no bond is issued at 1.5Y**. To bootstrap the spot rate at 2.0Y, we must first **interpolate** the missing 1.5Y point and treat it as if it were a par bond.


##### Given Par Yield Curve (Observed On-the-Run)

| Period | Maturity (Years) | Par Yield (BEY %) | Price   | Spot Rate (BEY %) |
|--------|------------------|-------------------|---------|-------------------|
| 1      | 0.5              | 3.00              | —       | 3.0000            |
| 2      | 1.0              | 3.30              | —       | 3.3000            |
| 3      | 1.5              | (not observed)    | —       | —                 |
| 4      | 2.0              | 3.90              | 100.00  | —                 |


##### Step 1: Interpolate the 1.5-Year Par Yield

We linearly interpolate the **BEY** between the 1Y and 2Y yields:

\[
y_{1.5} = 3.30\% + \frac{1.5 - 1.0}{2.0 - 1.0} \cdot (3.90\% - 3.30\%) = 3.60\%
\]

Use this as the **coupon rate** for a synthetic par bond maturing in 1.5 years.


##### Step 2: Construct Cash Flows of Synthetic 1.5Y Bond

Par yield = 3.60% annual ⇒ semiannual coupon = \$1.80

| Time (Years) | Cash Flow |
|--------------|-----------|
| 0.5          | 1.80      |
| 1.0          | 1.80      |
| 1.5          | 101.80    |

Use known spot rates:
- \( z_1 = 0.0150 \)
- \( z_2 = 0.0165 \)

##### Step 3: Solve for 1.5-Year Spot Rate \( z_3 \)

\[
P = \frac{1.80}{(1 + z_1)^1} + \frac{1.80}{(1 + z_2)^2} + \frac{101.80}{(1 + z_3)^3}
\]

\[
100 = \frac{1.80}{1.0150} + \frac{1.80}{(1.0165)^2} + \frac{101.80}{(1 + z_3)^3}
= 1.7736 + 1.7415 + \frac{101.80}{(1 + z_3)^3}
\Rightarrow \frac{101.80}{(1 + z_3)^3} = 100 - 3.5151 = 96.4849
\]

\[
(1 + z_3)^3 = \frac{101.80}{96.4849} \approx 1.05506
\Rightarrow z_3 = (1.05506)^{1/3} - 1 \approx 0.017527
\Rightarrow \boxed{\text{Annualized BEY} = 2 \cdot z_3 = \textbf{3.5053\%}}
\]


##### Step 4: Use \( z_3 \) to Derive the 2-Year Spot Rate

Cash flows for 2Y bond (coupon = 3.9%):

| Time | Cash Flow |
|------|-----------|
| 0.5  | 1.95      |
| 1.0  | 1.95      |
| 1.5  | 1.95      |
| 2.0  | 101.95    |

\[
P = \sum_{t=1}^{3} \frac{1.95}{(1 + z_t)^t} + \frac{101.95}{(1 + z_4)^4}
\]

\[
= 1.9214 + 1.8871 + 1.8537 = 5.6622
\Rightarrow \frac{101.95}{(1 + z_4)^4} = 100 - 5.6622 = 94.3378
\Rightarrow (1 + z_4)^4 = \frac{101.95}{94.3378} = 1.08014
\Rightarrow z_4 = (1.08014)^{1/4} - 1 \approx 0.019582
\Rightarrow \boxed{\text{Annualized BEY} = 3.9164\%}
\]

**Conclusion**:  
When no on-the-run bond exists at a specific maturity (like 1.5Y), interpolate the **par yield**, simulate a **synthetic bond**, and proceed with standard bootstrapping. This is the realistic scenario in most real-world term structure models.


### 6. Implementation and Practical Aspects

Building a robust bond pricing engine requires attention to **market conventions**, **interpolation methodology**, and **data availability**. Below is a high-level view of the steps involved:

#### Required Inputs:

- **Par yield curve** at the valuation date (daily par yields or zero curve)
- **Bond-specific parameters**: coupon rate, issue and maturity dates, frequency, etc.
- **Conventions**: day count basis (e.g., Actual/Actual), settlement lag, compounding rules

#### Interpolation and Bootstrapping Process

1. **Interpolation of missing maturities**:
   - A **linear interpolation** method is used between adjacent observed par yields
   - While more advanced methods exist (e.g., cubic splines, Nelson-Siegel), we use linear for simplicity and transparency

2. **Cash flow generation**:
   - For each bond, compute the **coupon schedule** from settlement to maturity
   - Generate the full stream of **expected cash flows**

3. **Spot rate derivation**:
   - Use previously bootstrapped spot rates to discount known flows
   - Solve iteratively for the unknown spot rate that aligns PV with market price

4. **Fallback or proxy**:
   - If market data is not available for a specific day or tenor, fallback logic selects a close proxy (e.g., previous business day)

#### Summary of Implementation Flow

- Fetch market yields or use fallback
- Generate coupon and cash flow schedule
- Interpolate missing yields
- Bootstrap spot rates sequentially
- Price bonds using derived spot rates
