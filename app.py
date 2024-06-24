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

        debit_df, credit_df = helper.expense_over_timeline('output.csv')
        df = pd.concat([debit_df, credit_df], axis=0).sort_values('Datetime',ascending=False)
        df['Type'] = df['Type'].apply(lambda x: x.lower())

        if user_analysis == 'Overall Analysis':
            st.title('Overall Analysis')

            # variables
            no_transactions = df.shape[0]
            debit_transactions = debit_df.shape[0]
            credit_transactions = credit_df.shape[0]
            debit_amount = debit_df['Amount'].sum()
            credit_amount = credit_df['Amount'].sum()

            # based_data = st.selectbox('Choose Data for Analysis',['Full Data','Customize Data using limits','Custom Data Selection'])
            # if based_data=='Customize Data using limits':
            #     min_limit = st.number_input('Min Limit', min_value=0, value=0, format='%d')
            #     max_limit = st.number_input('Max Limit', format='%d')
            #     df[(df['Amount']<max_limit) | (df['Amount']>min_limit)]
            
            # tabular data
            st.table(pd.DataFrame({
                'Type':['No. of Transactions','Debits','Credits','Debit Amount','Credit Amount'],
                'Amount Details':[no_transactions,debit_transactions,credit_transactions,'₹ ' + str(float(debit_amount)),'₹ ' + str(float(credit_amount))]
            }))
            
            # plot expense over timeline
            fig = px.bar(df, x='Datetime', y='Amount', color='Type', color_discrete_sequence=['#1f77b4','#ff7f0e'])
            st.plotly_chart(fig)

        elif user_analysis=='Yearly Analysis':
            # title
            st.title('Yearly Analysis')

            yearly_expense = []
            for year in sorted(df['year'].unique()):
                debit_amount = df[(df['year']==year) & (df['Type']=='debit')]['Amount'].sum() # debit amount
                credit_amount = df[(df['year']==year) & (df['Type']=='credit')]['Amount'].sum() # credit amount
                yearly_expense.extend([(year, 'debit', debit_amount),
                                        (year, 'credit', credit_amount),
                                        (year, 'total', abs(credit_amount-debit_amount))])
                
            yearly_expense_df = pd.DataFrame({
                        'year':[str(yearly_expense[i][0]) for i in range(len(yearly_expense))],
                        'type':[yearly_expense[i][1] for i in range(len(yearly_expense))],
                        'amount':[yearly_expense[i][2] for i in range(len(yearly_expense))]
                            })
            
            # tabular data
            st.table(pd.DataFrame({
                'Year':yearly_expense_df['year'].unique(),
                'Debit':['₹ '+ str(i) for i in yearly_expense_df[yearly_expense_df['type']=='debit']['amount'].values],
                'Credit':['₹ '+ str(i) for i in yearly_expense_df[yearly_expense_df['type']=='credit']['amount'].values],
                'Total':['₹ '+ str(i) for i in yearly_expense_df[yearly_expense_df['type']=='total']['amount'].values]
            }))
            
            # plot for yearly expense
            fig = px.histogram(yearly_expense_df,x='year',y='amount',color='type',barmode='group')
            st.plotly_chart(fig)

        elif user_analysis=='Monthly Analysis':
            # title
            st.title('Monthly Analysis')

            monthly_expense = []
            for year in sorted(df['year'].unique()):
                for month in sorted(df[(df['year']==year)]['month'].unique()):
                    debit_amount = df[(df['year']==year) & (df['Type']=='debit') & (df['month']==month)]['Amount'].sum() # debit amount
                    credit_amount = df[(df['year']==year) & (df['Type']=='credit') & (df['month']==month)]['Amount'].sum() # credit amount
                    x_label = str(year)+'_'+str(month)
                    monthly_expense.extend([(x_label, 'debit', debit_amount),
                                            (x_label, 'credit', credit_amount),
                                            (x_label, 'total', abs(credit_amount-debit_amount))])
                    

            monthly_expense_df = pd.DataFrame({
                        'year_month':[monthly_expense[i][0] for i in range(len(monthly_expense))],
                        'type':[monthly_expense[i][1] for i in range(len(monthly_expense))],
                        'amount':[monthly_expense[i][2] for i in range(len(monthly_expense))]
                            })
            
            # tabular data
            st.table(pd.DataFrame({
                'Year_Month':monthly_expense_df['year_month'].unique(),
                'Debit':['₹ '+ str(i) for i in monthly_expense_df[monthly_expense_df['type']=='debit']['amount'].values],
                'Credit':['₹ '+ str(i) for i in monthly_expense_df[monthly_expense_df['type']=='credit']['amount'].values],
                'Total':['₹ '+ str(i) for i in monthly_expense_df[monthly_expense_df['type']=='total']['amount'].values]
            }))
            
            # plot for monthly expense
            fig = px.histogram(monthly_expense_df,x='year_month',y='amount',color='type',barmode='group')
            st.plotly_chart(fig)

        elif user_analysis=='Weekly Analysis':
            # title
            st.title('Weekly Analysis')
            
            days_of_week = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
            weekly_expense = []

            for day in days_of_week:
                debit_amount = df[(df['day_of_week']==day) & (df['Type']=='debit')]['Amount'].sum() # debit amount
                credit_amount = df[(df['day_of_week']==day) & (df['Type']=='credit')]['Amount'].sum() # credit amount
                weekly_expense.extend([(day, 'debit', debit_amount),
                                (day, 'credit', credit_amount),
                                (day, 'total', abs(credit_amount-debit_amount))])
                
            weekly_expense_df = pd.DataFrame({
                        'day':[weekly_expense[i][0] for i in range(len(weekly_expense))],
                        'type':[weekly_expense[i][1] for i in range(len(weekly_expense))],
                        'amount':[weekly_expense[i][2] for i in range(len(weekly_expense))]
                            })
            
            # tabular data
            st.table(pd.DataFrame({
                'Day':weekly_expense_df['day'].unique(),
                'Debit':['₹ '+ str(i) for i in weekly_expense_df[weekly_expense_df['type']=='debit']['amount'].values],
                'Credit':['₹ '+ str(i) for i in weekly_expense_df[weekly_expense_df['type']=='credit']['amount'].values],
                'Total':['₹ '+ str(i) for i in weekly_expense_df[weekly_expense_df['type']=='total']['amount'].values]
            }))
                
            # plot for monthly expense
            fig = px.histogram(weekly_expense_df,x='day',y='amount',color='type',barmode='group')
            st.plotly_chart(fig)

        os.remove('output.csv')

    except Exception as e:
        st.error(f"Error in Reading PDF file: {e}")