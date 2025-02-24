# Description

This CLI program takes a pdf and extracts the tables in the pdf to a csv-file.
E. g. you can use this program to read your bank account expenses from the last month and automatically
convert the date, cost and description to csv to use it in your housekeeping book.
Until now it was only tested with the bank account statements received by Sparkasse.

# Usage

The first CLI argument is the pdf file from which is read from. 
The second file specifies the csv file path where the exported file should be stored.

````bash
python pdf2csv.py C:\Users\Jan\Documents\03_me_Dokumente\Finanzen\Kontoauszüge\2025\Konto_1000883518-Auszug_2025_0001.PDF jan25_1.csv
````

# Installation

I use conda:
````bash
conda create -n env
````

Activate your conda env
````bash
conda activate env
````

Then use pip to install the required packages of this project:
````bash
pip install -r requirements.txt
````

## Windows

In general, the jpype package needs an installed Java JDK.
On Windows download a Java JDK and then you need to specify the `JAVA_HOME`path.
````bash
 $env:JAVA_HOME = "C:\Program Files\Java\jdk-23"
````
You can test if it was succesfull:
````bash
echo $env:JAVA_HOME
````