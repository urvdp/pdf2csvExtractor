import os
import sys

import numpy as np
import tabula
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame

from config import Config

def format_bank_pdf(df: pd.DataFrame) -> pd.DataFrame:
    # Regex to capture something like 'dd.mm.yyyy' and then the rest
    date_pattern = r'(\d{2}\.\d{2}\.\d{4})\s*(.*)'

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
    df['cost'] = df['cost'].str.replace('.', '', regex=False)

    # convert to float
    df['cost'] = df['cost'].str.replace(',', '.', regex=False).astype(float)
    df['cost'] = df['cost'].abs()

    df.insert(2, "category", "")

    return df



def main():
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

    # Example using tabula-py to extract tables from a PDF
    tables = tabula.read_pdf(pdf_file, pages='all', stream=True)
    print(f"Tables found: {len(tables)}")
    #csv_table = tabula.convert_into(pdf_file, csv_file, output_format="csv", pages='all')

    df = pd.DataFrame()
    for table in tables:
        df = pd.concat([df, format_bank_pdf(table)], ignore_index=True)

    df.to_csv(csv_file, index=False, decimal=',')

    if False:
        df = tables[0]
        #tables[0].to_csv(csv_file, index=False)
        print(f"columns: {tables[0].columns}")
        # rename colums


        df.to_csv(csv_file, index=False, decimal=',')
        print(f"CSV saved as {csv_file}")
        tables[1].to_csv("table_2.csv", index=False, decimal=',')
        print(f"columns table 2: {tables[1].columns}")
    else:
        print("No tables found in the PDF.")


if __name__ == "__main__":
    main()
