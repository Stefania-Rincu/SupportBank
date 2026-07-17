import pandas as pd

class Account:
    def __init__(self, name):
        self.name = name
        self.balance = 0
        self.transactions = []

    def __str__(self):
        return f'{self.name}, balance: {self.balance}'

class Transaction:
    def __init__(self, date, narrative, amount):
        self.date = date
        self.narrative = narrative
        self.amount = amount

    def __str__(self):
        return f'Date: {self.date}, Narrative: {self.narrative}, Amount: {self.amount}'

def process_transaction(account, amount, date, narrative):
    account.balance += amount
    transaction = Transaction(date, narrative, amount)
    account.transactions.append(transaction)
    return account

def create_account_and_process_transactions(name, transactions, group_attribute):
    account = Account(name)

    for _, transaction_details in transactions.iterrows():
        amount = int(transaction_details['Amount'])

        if group_attribute == 'From':
            amount *= -1

        process_transaction(account, amount, transaction_details['Date'], transaction_details['Narrative'])

    return account

def process_csv(csv_file):
    csv_content = pd.read_csv(csv_file)
    accounts = []

    for column_name in ['From', 'To']:
        grouped_transactions = csv_content.groupby(column_name)
        for name, transactions in grouped_transactions:
            accounts.append(create_account_and_process_transactions(name, transactions, column_name))

    return accounts

if __name__ == '__main__':
    accounts = process_csv('Transactions2014.csv')

    while True:
        command = input('Enter command: ')
        if command.lower() == 'list all':
            for account in accounts:
                print(account)
            print()
        elif command.lower().startswith('list '):
            account_exists = False
            account_name = command.split(' ')[1]

            for account in accounts:
                if account.name.lower() == account_name.lower():
                    print(account)
                    print('Transactions')
                    for transaction in account.transactions:
                        print(f'    {transaction}')
        else:
            break