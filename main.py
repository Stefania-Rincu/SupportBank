import pandas as pd

class Account:
    def __init__(self, name):
        self.name = name
        self.balance = 0
        self.transactions = []

    def add_transaction(self, transaction):
        self.balance += transaction.amount
        self.transactions.append(transaction)

    def __str__(self):
        return f'{self.name}, balance: {self.balance}'

class Transaction:
    def __init__(self, date, narrative, amount):
        self.date = date
        self.narrative = narrative
        self.amount = amount

    def __str__(self):
        return f'Date: {self.date}, Narrative: {self.narrative}, Amount: {self.amount}'

def get_or_create_account(name, accounts):
    if name.lower() not in accounts:
        accounts[name.lower()] = Account(name)
    return accounts[name.lower()]

def load_accounts_from_csv(csv_file):
    try:
        csv_content = pd.read_csv(csv_file)
    except FileNotFoundError:
        print('File not found')
        exit()
    except Exception as exception:
        print(f'Could not load CSV file. Exception: {exception}')
    accounts = {}

    for _, transaction_details in csv_content.iterrows():
        try:
            amount = float(transaction_details['Amount'])

            for direction, sign in [('From', -1), ('To', 1)]:
                account = get_or_create_account(transaction_details[direction], accounts)
                transaction = Transaction(transaction_details['Date'], transaction_details['Narrative'], sign * amount)
                account.add_transaction(transaction)
        except ValueError:
            print('Amount not a number')
            pass

    return accounts

if __name__ == '__main__':
    accounts = load_accounts_from_csv('Transactions2014.csv')

    while True:
        options = ('Available commands:\n'
                   '\tList All - show all accounts\n'
                   '\tList [Name] - show transactions for a user (example: List Todd)\n'
                   '\tExit - stop the program\n')
        command = input(f'{options}Enter command:')
        if command.lower() == 'exit':
            break
        if command.strip().lower() == 'list all':
            for account in accounts.values():
                print(account)
            print()
        elif command.lower().startswith('list '):
            account_name = command.strip()[5:].strip().lower()

            if account_name in accounts:
                print(accounts[account_name])
                print('Transactions')
                for transaction in accounts[account_name].transactions:
                    print(f'    {transaction}')
            else:
                print('Account not found')

            print()
        else:
            print('Invalid command')
            print()
