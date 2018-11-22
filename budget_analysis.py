# Made to be compatible with a csv file downloaded from mint.com

import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

def createPlots(my_dict,  df):

    #determine if its a monthly, yearly, or range analysis



    N = 3
    ind = np.arange(N)    # the x locations for the groups [0 1 2 3 4]
    width = 0.35       # the width of the bars: can also be len(x) sequence

    # fig is the background, ax is the actual plot. xxx number format is height, width, selection
    fig, (ax1, ax2) = plt.subplots(2, 1)
    # first plot will compare expenses and income
    # Axes.bar(x, height, width=0.8, bottom=None, *, align='center', data=None, **kwargs)
    ax1.bar([0, 1], [my_dict['Income'], -my_dict['Expenses']], width=width, color=['green', 'red'])
    plt.sca(ax1)
    plt.xticks(range(2), ['Income', 'Expenses'])
    plt.ylabel('Amount ($)')
    month_name = df.loc[0, "Date"].strftime("%B")
    plt.title('Net gain/loss in %s is $%.2f.' % (month_name, my_dict['Net Change']))
    ax1.text(0, my_dict['Income']/2, '$%.2f' % my_dict['Income'], horizontalalignment='center', verticalalignment='center')
    ax1.text(1, -my_dict['Expenses']/2,  '$%.2f' %
             my_dict['Expenses'], horizontalalignment='center', verticalalignment="center")
    # label with the values and the difference

    main_expenses = pd.DataFrame(data={'Expenses': [-my_dict['Shopping'], -my_dict['Groceries'], -my_dict['Restaurants'], -my_dict['Life Costs'], -my_dict['Other']]}, index=[
                                 'Shopping', 'Groceries', 'Restaurants', 'Life Costs', 'Other'])
    main_expenses.sort_values(by='Expenses', inplace=True)
    main_expenses.plot(ax=ax2, kind='barh')

    # plt.legend((shopping_bar[0], groceries_bar[0], restaurants_bar[0]), ('Shopping', 'Groceries', 'Restaurant'))
    plt.show()

def doAnalysis(df):
    income = df[df['Amount'] > 0].Amount.sum()
    expenses = df[df['Amount'] < 0].Amount.sum()
    invested = df[df['Category'] == "Investment"].Amount.sum()
    shopping = df[df['Category'] == "Shopping"].Amount.sum()
    life_cost_tags = ['Pharmacy', 'Home Improvement', 'Doctor', 'Gas & Fuel']
    life_costs = df[df.Category.isin(life_cost_tags)].Amount.sum()
    groceries_tags = ['Groceries']
    groceries = df[df['Category'] == "Groceries"].Amount.sum()
    restaurant_tags = ["Restaurants", "Alcohol & Bars", "Fast Food", "Coffee Shops"]
    restaurants = df[df.Category.isin(restaurant_tags)].Amount.sum()

    other = expenses - shopping - groceries - restaurants - life_costs
    net_change = df.Amount.sum()
    my_dict = {'Income': income, 'Expenses': expenses, 'Net Change': net_change, 'Invested': invested, 'Shopping': shopping, 'Groceries': groceries, 'Restaurants': restaurants, 'Life Costs': life_costs, 'Other': other}
    for key, value in my_dict.items():
        my_dict[key] = round(value, 2)
    return(my_dict)

def monthExpenses(month, year, df):
    # dates is a nested list format [[month, year], [month2, year2], [month3]]
    # if a year is left out, the previously used year is kept. If no year is ever given the current year is used.

    # sums for each category
    first_day = datetime(year=year, month=month, day=1)
    next_month = first_day.replace(day=28) + timedelta(days=4)  # this will never fail
    last_day = next_month - timedelta(days=next_month.day)
    # trim the df down to just the specified month

    df = df[df['Date'] > first_day]
    df = df[df['Date'] < last_day]
    df.reset_index(inplace=True, drop = True)

    my_dict = doAnalysis(df)
    createPlots(my_dict, df)
    # return most_expensive

def rangeAnalysis(start, end, df):
    #start and end should be  datetime objects
    df = df[df['Date'] > start]
    df = df[df['Date'] < end]
    df.reset_index(inplace=True)

    my_dict = doAnalysis(df)
    createPlots(my_dict, df)

PATH = '/Users/biver/Documents/transactions.csv'
transactions = pd.read_csv(PATH)
# Fix a weird naming error
transactions.rename(index=int, columns={" Amount ": "Amount"}, inplace=True)
# convert the dates from str to datetime
print(transactions.index.tolist())
transactions.Date = pd.to_datetime(transactions.Date, format =  "%m/%d/%Y")
for i, row in transactions.iterrows():
    # format the amounts
    amount = row.loc['Amount']
    amount = amount.replace(" ", "")  # strip whitespace
    amount = amount.replace("$", "")  # strip symbol
    amount = amount.replace(",", "")
    amount = round(float(amount), 2)
    if row.loc['Transaction Type'] == 'debit':
        amount = -amount
    transactions.loc[i, 'Amount'] = amount
    # catch the investments
    if(transactions.loc[i, 'Description'] == "Acorns Investing Transfer"):
        transactions.loc[i, 'Category'] = "Investment"
    # ignore transfers between checking and savings accounts
    internal_transfers = ['Transfer to CPC CHECKING', 'Transfer from CPC CHECKING',
                          'Transfer to CPC SAVINGS', 'Transfer from CPC SAVINGS']
    if row.loc['Description'] in internal_transfers:
        transactions.drop(index=i, inplace=True)


    # PUT SPECIFIC CATCHES HERE
    if row.loc['Description'] == 'Achilles':
        transactions.loc[i, 'Category'] = 'Resataurants'
    if row.loc['Description'] == '7-Eleven':
        transactions.loc[i, 'Category'] = 'Groceries'
    if row.loc['Description'] == 'Serive Fee Reversal':
        # transactions.loc[i, 'Category'] = 'Resataurants'
        pass


transactions.drop(inplace=True, columns=['Labels', 'Notes',
                                         'Original Description', 'Transaction Type'])
transactions.reset_index(inplace=True, drop=True)

start = datetime(2018, 6, 1)
end = datetime.now()

rangeAnalysis(start, end, transactions)
