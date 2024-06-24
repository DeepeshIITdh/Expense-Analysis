import streamlit as st
import helper
import pandas as pd 
import plotly.express as px
import os 

# Sidebar 
st.sidebar.title('Expenses Analysis')

# select upi app
# for the future purpose we can add more methods
upi_app = st.sidebar.selectbox('Select Your UPI payment App', ('PhonePe', 'PayTm', 'BharatPe', 'AmazonPay'))

# File uploader widget
uploaded_file = st.sidebar.file_uploader(f"Upload your {upi_app} Transaction Statement PDF", type="pdf")

# mode for the analysis
user_analysis = st.sidebar.radio(label='', options=('Overall Analysis', 'Yearly Analysis', 'Monthly Analysis', 'Weekly Analysis'))

if uploaded_file != None:
    try:
        if upi_app == 'PhonePe':
            helper.transaction_pdf_to_csv_phonepe(pdf_path=uploaded_file)
        else:
            st.error(f'{upi_app} is not available')

        if user_analysis == 'Overall Analysis':
            st.title('Overall Analysis')
            debit_df, credit_df = helper.expense_over_timeline('output.csv')
            df = pd.concat([debit_df, credit_df], axis=0).sort_values('Datetime',ascending=False)

            # variables
            no_transactions = df.shape[0]
            debit_transactions = debit_df.shape[0]
            credit_transactions = credit_df.shape[0]
            debit_amount = debit_df['Amount'].sum()
            credit_amount = credit_df['Amount'].sum()

            

            # plot expense over timeline
            fig = px.bar(debit_df, x='Datetime', y='Amount')
            st.plotly_chart(fig)

        os.remove('output.csv')

    except Exception as e:
        st.error(f"Error reading PDF file: {e}")