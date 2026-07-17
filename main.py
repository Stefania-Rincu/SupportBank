import pandas as pd
from datetime import datetime
import logging

class Account:
    def __init__(self, name):
        self.name = name
        self.balance = 0.0
        self.transactions = []

    def add_transaction(self, transaction):
        self.balance += transaction.amount
        self.transactions.append(transaction)

    def __str__(self):
        return f'{self.name}, balance: {"{:.2f}".format(self.balance)}'

class Transaction:
    def __init__(self, date, narrative, amount):
        self.date = date
        self.narrative = narrative
        self.amount = amount

    def __str__(self):
        return f'Date: {self.date}, Narrative: {self.narrative}, Amount: {"{:.2f}".format(self.amount)}'

def get_or_create_account(name, accounts):
    if name.lower() not in accounts:
        accounts[name.lower()] = Account(name)
    return accounts[name.lower()]

def load_accounts_from_csv(csv_file):
    logging.info(f'Loading accounts from CSV file: {csv_file}')

    try:
        csv_content = pd.read_csv(csv_file)
    except FileNotFoundError:
        logging.error(f'CSV file not found')
        exit()
    except Exception as exception:
        logging.error(exception)

    accounts = {}

    for row_index, transaction_details in csv_content.iterrows():
        try:
            amount = float(transaction_details['Amount'])

            try:
                datetime.strptime(transaction_details['Date'], '%d/%m/%Y')
            except ValueError:
                logging.error(
                    f'Error on line: {row_index + 2}. Expected a real date. Date value: {transaction_details["Date"]}')

            for direction, sign in [('From', -1), ('To', 1)]:
                account = get_or_create_account(transaction_details[direction], accounts)

                transaction = Transaction(transaction_details['Date'], transaction_details['Narrative'], sign * amount)
                account.add_transaction(transaction)
        except ValueError:
            logging.error(f'Error on line: {row_index + 2}. Amount not a number. Amount value: {transaction_details["Amount"]}')

    return accounts

if __name__ == '__main__':
    logging.basicConfig(filename='SupportBank.log', filemode='w', level=logging.DEBUG)
    logging.info('Program started')

    accounts = load_accounts_from_csv('DodgyTransactions2015.csv')

    while True:
        logging.info('Waiting for a command...')

        options = ('Available commands:\n'
                   '\tList All - show all accounts\n'
                   '\tList [Name] - show transactions for a user (example: List Todd)\n'
                   '\tExit - stop the program\n')
        command = input(f'{options}Enter command:')

        logging.info(f'Command: {command}')

        if command.lower() == 'exit':
            logging.info('Program ended')
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
                logging.warning(f'Account not found')

            print()
        else:
            logging.warning(f'Invalid command')
            print()
