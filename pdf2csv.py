import os
import sys

import numpy as np
import tabula
import pandas as pd

from config import Config

# Regex to capture something like 'dd.mm.yyyy' and then the rest
date_pattern = r'(\d{2}\.\d{2}\.\d{4})\s*(.*)'

def format_bank_pdf(df: pd.DataFrame) -> pd.DataFrame:

    df.rename(columns={
        'Datum Erläuterung': 'date_explanation',
        'Unnamed: 0': 'Ignore_0',
        'Unnamed: 1': 'Ignore_1',
        'Betrag Soll EUR': 'cost',
        'Betrag Haben EUR': 'income'
    }, inplace=True)
    df[['date', 'explanation']] = df['date_explanation'].str.extract(date_pattern)
    df['explanation'] = df['explanation'].str.strip()
    df['date'] = df['date'].str.strip()
    df.drop(columns=['date_explanation', 'Ignore_0', 'income'], inplace=True)
    if 'Ignore_1' in df.columns:
        df.drop(columns=['Ignore_1'], inplace=True)

    df[['date', 'explanation', 'cost']] = df[['date', 'explanation', 'cost']].replace(r'^\s*$', np.nan, regex=True)
    df = df.dropna(subset=['cost'], how='all')
    df = df[['date', 'cost', 'explanation']]
    # remove all dots
    df['cost'] = df['cost'].astype(str)
    df['cost'] = df['cost'].str.replace('.', '', regex=False)

    # convert to float
    df['cost'] = df['cost'].str.replace(',', '.', regex=False).astype(float)
    df['cost'] = df['cost'].abs()

    df.insert(2, "category", "")

    return df

def format_credit_card_pdf(df: pd.DataFrame) -> pd.DataFrame:
    date_col = df.columns[0]
    date_col_booking = df.columns[1]
    explanation_col = df.columns[2]
    cost_col = df.columns[3]
    df.rename(columns={
        date_col: 'date',
        date_col_booking: 'date_booking',
        explanation_col: 'explanation',
        cost_col: 'cost'
    }, inplace=True)
    df.drop(columns=['date_booking'], inplace=True)
    # insert none in empty colums
    df[['date', 'explanation', 'cost']] = df[['date', 'explanation', 'cost']].replace(r'^\s*$', np.nan, regex=True)
    # convert date to datetime
    date_format = "%d.%m.%y"
    df['date'] = pd.to_datetime(df['date'], format=date_format, errors='coerce')
    # drop rows with all NaN values
    df = df.dropna(subset=['cost'], how='all')
    df = df.dropna(subset=['date'], how='all')
    # convert to desired day format
    df['date'] = df['date'].dt.strftime('%d.%m.%Y')

    # get only costs and remove positive values
    df_filtered = df[df['cost'].str.strip().str.endswith('-')]
    df_filtered.loc[:, 'cost'] = df_filtered['cost'].str.replace('-', '', regex=False)
    df_filtered.loc[:, 'cost'] = df_filtered['cost'].str.strip()

    # rearrange columns
    df_filtered = df_filtered[['date', 'cost', 'explanation']]
    # insert category column
    df_filtered.insert(2, "category", "")

    return df_filtered

def main():
    is_credit_card = False
    if not Config.dev and len(sys.argv) < 3:
        print("Usage: python pdf2csv.py input.pdf output.csv")
        sys.exit(1)
    else:
        if not Config.dev:
            pdf_file = sys.argv[1]
            csv_file_path = sys.argv[2]
        else:
            pdf_file = Config.pdf_path
            csv_file_path = Config.csv_path

    if '-c' in sys.argv:
        # using credit card config
        print("### Using credit card config ###")
        is_credit_card = True

    csv_path = os.path.dirname(csv_file_path)
    csv_file = os.path.basename(csv_file_path)
    print(f"PDF file: {pdf_file}")
    print(f"CSV path: {csv_path}")
    print(f"CSV file: {csv_file}")

    if not csv_path == "" and not os.path.exists(csv_path):
        print(f"Directory {csv_path} does not exist.")
        sys.exit(1)

    if not os.path.exists(csv_file):
        print(f"Creating file {csv_file}.")
        with open(csv_file, 'w') as f:
            pass

    if is_credit_card:
        tables = tabula.read_pdf(pdf_file, pages='all',
                                 area=[350, 30, 650, 580],
                                 columns=[80, 120, 510, 580]) # custom values for credit card pdf
    else:
        tables = tabula.read_pdf(pdf_file, pages='all', stream=True)
    print(f"Tables found: {len(tables)}")

    df = pd.DataFrame()
    for table in tables:
        if is_credit_card:
            df = pd.concat([df, format_credit_card_pdf(table)], ignore_index=True)
        else:
            df = pd.concat([df, format_bank_pdf(table)], ignore_index=True)

    df.to_csv(csv_file, index=False, decimal=',')
    print(f"CSV file written to {csv_path}{csv_file}")


if __name__ == "__main__":
    main()
