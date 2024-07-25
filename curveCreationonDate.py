import QuantLib as ql
import pandas as pd
import numpy as np
import datetime as dt
import plotly.express as px

df = pd.read_csv('Data\\bond_data.csv')
df['date'] = pd.to_datetime(df['date'],dayfirst=True).dt.date
depo_rates = pd.read_csv('Data\\depo_data.csv')
depo_rates['date'] = pd.to_datetime(depo_rates['date'], dayfirst=True).dt.date
curveDates = df['date'].unique()
curveDict = dict.fromkeys(curveDates, None)

date = dt.date(2024,7,23)

calc_date = ql.Date(date.strftime('%Y-%m-%d'), '%Y-%m-%d')
data = df[(df['date'] == date)]
dataDepo = depo_rates[depo_rates['date'] == date]
ql.Settings.instance().evaluationDate = calc_date

maturities = data['yearsToMaturity'].tolist()
maturities_depo = dataDepo['yearsToMaturity'].tolist()
maturities_depo = [ql.Period(round(m*365), ql.Days) for m in maturities_depo]
rates_depo = dataDepo['rate'].tolist()
prices = data['price'].tolist()
coupons = data['coupon'].tolist()
maturities = [ql.Period(round(m*365), ql.Days) for m in maturities]
calendar = ql.Canada()
day_count = ql.ActualActual(ql.ActualActual.ISMA)
business_convention = ql.Following
end_of_month = False
settlement_days = 1
face_amount = 100
coupon_frequency = ql.Period(ql.Semiannual)

print("rates_deop: ", rates_depo)
print("maturities_depo: ", maturities_depo)
print("bond prices: ", prices)
print("bond coupons: ", coupons)
print("bond maturities: ", maturities)

depo_helpers = [ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(r/100.0)),
m,
settlement_days,
calendar,
business_convention,
end_of_month,
day_count)
for r, m in zip(rates_depo, maturities_depo)]

bond_helpers = []

for p, c , m in zip(prices, coupons, maturities):
    schedule = ql.Schedule(calc_date,
        calc_date + m,
        coupon_frequency,
        calendar,
        business_convention,
        business_convention,
        ql.DateGeneration.Backward,
        True)
    bond_helper = ql.FixedRateBondHelper(ql.QuoteHandle(ql.SimpleQuote(p)),
    settlement_days,
    face_amount,
    schedule,
    [c],
    day_count,
    business_convention,
    )
    bond_helpers.append(bond_helper)
    
rate_helpers = depo_helpers+bond_helpers 

crv = ql.PiecewiseCubicZero(calc_date,
    rate_helpers,
    day_count)

yc = crv
start = 0
stop = 30
step = 0.25
sequence = np.arange(start, stop+step, step)
points = []

compounding = ql.Continuous
freq = ql.Semiannual

for date in sequence:
   points.append(yc.zeroRate(date, compounding, freq).rate()*100)

df_2 = pd.DataFrame(list(zip(sequence, points)), columns=["year", "rate"])

fig2 = px.line(df_2, x='year', y='rate')
fig2.show()