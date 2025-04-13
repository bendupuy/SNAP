
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load cleaned dataset
@st.cache_data
def load_data():
    df = pd.read_csv("snap_1989_2025_monthly_2025_1.csv")
    df = df.dropna(subset=[
        'pop_urban_2010', 'pop_rural_2010', 'totpop_2010',
        'pct_pop_urban_2010', 'pct_pop_rural_2010',
        'region', 'region_name', 'divis', 'divis_name'
    ])
    df = df[(df['benperhh'] >= 0) & (df['benperp'] >= 0)]
    df['date'] = pd.to_datetime(df[['year', 'monthno']].assign(day=1))
    return df

df = load_data()

# Sidebar filters
st.sidebar.title("Filters")
state = st.sidebar.selectbox("Select a State", sorted(df['state'].unique()))
min_date, max_date = df['date'].min(), df['date'].max()
date_range = st.sidebar.slider("Select Date Range", min_value=min_date, max_value=max_date,
                               value=(min_date, max_date), format="MMM YYYY")

# Filtered Data
state_data = df[(df['state'] == state) & (df['date'].between(*date_range))]
national_data = df[df['date'].between(*date_range)].groupby('date')[['benperhh', 'benperp']].mean().reset_index()

# Title
st.title("📊 SNAP Benefit Trends")
st.markdown(f"Explore how **{state}**'s SNAP benefits per household and per person compare to the **national average**.")

# Plotting
fig, ax = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Benefits per household
ax[0].plot(state_data['date'], state_data['benperhh'], label=f'{state}', linewidth=2)
ax[0].plot(national_data['date'], national_data['benperhh'], label='National Avg', linestyle='--')
ax[0].set_ylabel("Benefit per Household ($)")
ax[0].legend()
ax[0].set_title("SNAP Benefit per Household")

# Benefits per person
ax[1].plot(state_data['date'], state_data['benperp'], label=f'{state}', linewidth=2)
ax[1].plot(national_data['date'], national_data['benperp'], label='National Avg', linestyle='--')
ax[1].set_ylabel("Benefit per Person ($)")
ax[1].set_xlabel("Date")
ax[1].legend()
ax[1].set_title("SNAP Benefit per Person")

st.pyplot(fig)

# Summary
def pct_change(start, end):
    return ((end - start) / start) * 100 if start != 0 else 0

st.subheader("📈 Summary")
if not state_data.empty:
    start_hh = state_data.iloc[0]['benperhh']
    end_hh = state_data.iloc[-1]['benperhh']
    start_p = state_data.iloc[0]['benperp']
    end_p = state_data.iloc[-1]['benperp']
    st.markdown(f"**{state}:**")
    st.markdown(f"- Household benefit increase: **{pct_change(start_hh, end_hh):.1f}%**")
    st.markdown(f"- Person benefit increase: **{pct_change(start_p, end_p):.1f}%**")

    nat_start_hh = national_data.iloc[0]['benperhh']
    nat_end_hh = national_data.iloc[-1]['benperhh']
    nat_start_p = national_data.iloc[0]['benperp']
    nat_end_p = national_data.iloc[-1]['benperp']
    st.markdown(f"**National Average:**")
    st.markdown(f"- Household benefit increase: **{pct_change(nat_start_hh, nat_end_hh):.1f}%**")
    st.markdown(f"- Person benefit increase: **{pct_change(nat_start_p, nat_end_p):.1f}%**")

else:
    st.warning("No data for selected date range.")
