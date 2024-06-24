import pandas as pd
from PyPDF2 import PdfReader
import numpy as np


def transaction_pdf_to_csv_phonepe(pdf_path):
    # creating list for the columns of DataFrame
    date = []
    time = []
    payment_type = []
    amount = []

    # creating the PdfReader Object
    reader = PdfReader(pdf_path)

    # extracting text from each page
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        text = page.extract_text()
        text_list = text[:text.index('Page')].split('\n')

        # only for the first page
        if i == 0:
            user = text_list[0]
            time_interval = text_list[1]
            text_list.remove(user)
            text_list.remove(time_interval)

        # extracting amount, name_details, payment_type column

        for i, word in enumerate(text_list):
            if ('₹' in word) or ('INR' in word) or ('Rs' in word):
                # appending elements to their resp. lists
                indi_name_detail = text_list[i + 1]
                indi_payment_type = text_list[i - 1]
                if indi_payment_type in ['debit','credit','DEBIT','CREDIT','Debit','Credit']:
                    payment_type.append(indi_payment_type)
                    amount.append(word)

                    # remove the extracted words from the text list
                    text_list.remove(word)
                    text_list.remove(indi_name_detail)
                    text_list.remove(indi_payment_type)
                else:
                    text_list.remove(word)

        # extracting date, time, account_used column
        for [i, word] in enumerate(text_list):
            if ',' in word:
                date.append(word)
                time.append(text_list[i + 1])
                

    # creating the DataFrame
    df = pd.DataFrame({
        'Date': date,
        'Time': time,
        'Type': payment_type,
        'Amount': amount
    })

    df['Amount'] = df['Amount'].str.replace('₹', '').str.replace(',', '').astype(np.float64).round(0).astype(np.int64)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df['Time'] = pd.to_datetime(df['Time'], format='%I:%M %p').dt.time

    # converting dataframe to csv
    df.to_csv('output.csv', index=False)


def expense_over_timeline(csv_path):
    df = pd.read_csv(csv_path)

    # If the date is in 'yyyy/mm/dd' format and time is in 'HH:MM:SS' format
    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%Y-%m-%d %H:%M:%S')

    df['Date'] = pd.to_datetime(df['Date'])

    df['year'] = df['Date'].dt.year
    df['month'] = df['Date'].dt.month
    df['day'] = df['Date'].dt.day
    df['day_of_week'] = df['Date'].dt.day_name()

    debit_df = df[df['Type'] in ['Debit','DEBIT']]
    credit_df = df[df['Type'] in ['Credit','CREDIT']]

    return debit_df, credit_df
