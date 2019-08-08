import pandas
import argparse
import matplotlib.pyplot as plots

COLUMN_NAMES = ['Date', 'Amount', 'Description', '1', '2', '3', '4', '5']


def parse_raw_file(file_name):
    df = pandas.read_csv(file_name, header=None, names=COLUMN_NAMES, skip_blank_lines=True)
    df['Date'] = pandas.to_datetime(df.Date, dayfirst=True)
    return df


def summarize(df, max_columns=3, show_plot=False):
    grouped = df.groupby([df['Date'].dt.strftime('%Y.%m'), df['Category']])['Amount'] \
        .sum().unstack(fill_value=0.0)
    grouped.loc['Average'] = grouped.mean()
    grouped.sort_values(grouped.last_valid_index(), axis=1, inplace=True)
    grouped = grouped.iloc[:, 0:max_columns]
    grouped['Total'] = grouped.sum(axis=1)

    print(grouped)
    if show_plot:
        grouped.plot()
        plots.show()


def select_month_category(df, date_str, category):
    selected = df.loc[(df['Date'].dt.strftime('%Y.%m') == date_str) & (df['Category'] == category)]
    print(selected.to_string(index=False, columns=['Date', 'Amount', 'Description']))


def print_unknown(df):
    selected = df.loc[df['Category'] == 'Other']
    selected = selected.groupby(['Description'], as_index=False)['Amount'].sum()
    selected.sort_values('Amount', inplace=True)
    print(selected.to_string(index=False, columns=['Amount', 'Description']))


def categorize(df):
    categories = {
        'Food and chemistry': ['COLES', 'WOOLWORTH', 'ALDI', 'CHEMIST', 'MCDONALDS',
                               'KITCHEN', 'KAZACHOK', 'BUTCHER', 'SEAFOOD', 'PIZZA', 'MARROO',
                               'EUROPA', 'COSTCO WHOLESALE', 'MOORABBIN WSALE FFM', 'BLAHNIK',
                               'FHLL GROUP'],
        'Rent': ['BARRY', 'DEFT'],
        'Internet': ['SPINTEL'],
        'Electricity, gas and water': ['AGL', 'WATER'],
        'Phone': ['VODAFONE', 'KOGAN'],
        'Furniture and clothes': ['IKEA', 'KMART', 'BIG W', 'ALIEXPRESS', 'TARGET', 'SHOEMAKERS',
                                  'PAULS WAREHOUSE', 'SAVERS', 'REJECT SHOP', 'BEST AND LESS'],
        'Electronics': ['JB HI FI', 'GOODGUYS', 'OFFICEWORKS', 'HARVEY NORMAN'],
        'Transport': ['TRANSPORT', 'UBER', 'MYKI'],
        'Salary': ['SALARY', 'ATO'],
        'Medicine': ['NIB', 'AVERGUN', 'CLINICAL LABS', 'RADIOLOGY', 'MASSAGE', 'PHARMACY',
                     'HEALTH'],
        'Fun': ['LUNA PARK', 'DON TATNELL', 'ZOO', 'HOBBIES', 'BCF', 'GAINFUL', 'MYUNA'],
        'Cash': ['ANZ ATM'],
        'To Mariia': ['MARIIA'],
        'Tools': ['BIKES', 'BUNNINGS'],
        'Savings': ['ANZ M-BANKING FUNDS TFER TRANSFER'],
        'Ignore': ['ACCOUNT SERVICING FEE', 'DEBIT INTEREST CHARGED'],
        'Car': ['FUEL', 'LINKT', 'CITYLINK', 'ROADS', '17126', 'TOYOTA', 'AUTO',
                'CITY OF GREATER DAND', 'PARKIN', 'ROOF RACK', 'BINGLE', 'VICROADS'],
        'Car itself': ['MAYSARAH'],
        'Visas and other Gov': ['AFFAIRS', 'BUPA MEDICAL VISA', 'DEPARTMENT OF HOME'],
        'Travel and tickets': ['BOOKING.COM', 'AIRBNB', 'QATAR']
    }

    df['Category'] = 'Other'
    for category, substrings in categories.items():
        df.loc[df['Description'].str.contains('|'.join(substrings)), 'Category'] = category

    return df

    # delta = df['Date'].iloc[0] - df['Date'].iloc[-1]
    # print(df.groupby(['Category'])[['Amount']].sum().sort_values('Amount') / delta.days * 365 / 12)


def merge(input1, input2, output):
    df1 = parse_raw_file(input1)
    df2 = parse_raw_file(input2)
    df_out = pandas.concat([df1, df2], ignore_index=True)
    df_out.sort_values(by='Date', ascending=False).to_csv(output, header=False, index=False)


def experiment(input_file):
    df = parse_raw_file(input_file)
    df['Date'] = pandas.to_datetime(df.Date, dayfirst=True)
    df.reset_index().sort_values(by=['index', 'Date'], ascending=[True, False]).set_index('index').rename_axis(None)
    print(df)


def write_to_file(df, file_name):
    df.to_csv(file_name, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process expenses on ANZ statements.')
    parser.add_argument('mode', help='Define a mode. Options: analyze, merge ...')
    parser.add_argument('-i', '--input', dest='input_files', nargs='+', help='Input file(s) to process')
    parser.add_argument('-o', '--output', dest='output_files', nargs='+', help='Output file(s)')
    args = parser.parse_args()

    print('Processing file in mode "{}"'.format(args.mode))
    if args.mode == 'analyze':
        analyze_file(args.input_files[0])
    elif args.mode == 'merge':
        merge(args.input_files[0], args.input_files[1], args.output_files[0])
    elif args.mode == 'experiment':
        experiment(args.input_files[0])

