import time
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import numpy_financial as npf
from millify import prettify

st.set_page_config(
    page_title='Compound Interest'
    , page_icon='💰'
    , layout='centered'
    , initial_sidebar_state='auto'
)

st.title('💵 Compound Interest Example 💵')
st.write('*Curious about how much you will earn depending on what you invest? Use this app to figure it out!*')

with st.form(key='form1'):
    start_year = st.number_input('Year that you intend to start investing', min_value=2021, value=2021)
    initial_investment = st.number_input('Amount of money that you have available to invest initially', min_value=0,
                                         value=0)
    monthly_contribution = st.number_input('Amount that you plan to invest every month', min_value=0, value=1000)
    length_of_time = st.number_input('Length of time, in years, that you plan to investing', min_value=0, value=20)
    interest_rate = st.number_input('Your estimated annual interest rate (enter as %)', min_value=0.0, value=8.0,
                                    step=.1)
    submit_button = st.form_submit_button(label='Submit')

amount_earned = [initial_investment]
amount_contributed = [initial_investment]
yearly_contribution = (12 * monthly_contribution) + initial_investment
length_of_time = int(length_of_time)
start_year = int(start_year)

for i in range(0, length_of_time):
    amount_earned.append(npf.fv(rate=(interest_rate / 100) / 12, nper=(i + 1) * 12, pmt=-monthly_contribution,
                                pv=-initial_investment))
    amount_contributed.append(yearly_contribution)
    yearly_contribution += 12 * monthly_contribution

index = list(range(start_year, length_of_time + 1 + start_year))

df = pd.DataFrame({'Amount Contributed': amount_contributed
                      , 'Amount Earned': amount_earned
                   }, index=index)

df.reset_index(inplace=True)

df.rename(columns={'index': 'Year'}, inplace=True)
df.Year = df.Year.astype(str)

df = df.melt(id_vars='Year', value_vars=['Amount Contributed', 'Amount Earned'], var_name='Amount',
             value_name='Cash Value')

base = alt.Chart(df).mark_line().encode(
    x=alt.X('1:O', axis=alt.Axis(title='Year')),
    y=alt.Y('0:Q', axis=alt.Axis(format='$', title='Cash Value')),

)


def plot_animation(df):
    lines = alt.Chart(df).mark_line().encode(
        x=alt.X('Year', axis=alt.Axis(title='Year')),
        y=alt.Y('Cash Value:Q', axis=alt.Axis(format='$', title='Cash Value')),
        color='Amount',
        strokeDash='Amount',
        tooltip=['Year', 'Cash Value']
    )
    return lines


N = df.shape[0]  # number of elements in the dataframe
burst = 10  # number of elements (months) to add to the plot
size = burst  # size of the current dataset

if submit_button:
    status_text = st.empty()

    with st.spinner('Wait for it...'):
        st.write('### Total Savings')
        line_plot = st.altair_chart(base)

        for i in range(1, N+2):
            step_df = df.iloc[0:size]
            lines = plot_animation(step_df)

            line = lines.mark_line()
            points = lines.mark_point(filled=True, size=40)
            chart = (line + points).interactive().properties(
                width=875,
                height=500
            )

            line_plot = line_plot.altair_chart(chart)
            size = i + burst
            if size >= N:
                size = N - 1
            time.sleep(0.1)

    total_contribution = round(df.loc[df['Amount'] == 'Amount Contributed']['Cash Value'].max(),2)
    total_earnings = round(df.loc[df['Amount'] == 'Amount Earned']['Cash Value'].max(),2)

    status_text.success(f'''In **{length_of_time}** Years you will have contributed **${prettify(total_contribution)}** 
    but will have earned **${prettify(total_earnings)}**''')
    st.balloons()
