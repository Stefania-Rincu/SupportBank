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

def read_file(file_name, extension):
    return {
        'csv': lambda: pd.read_csv(file_name),
        'json': lambda: pd.read_json(file_name)
    }[extension]()

def parse_date(date, extension):
    return {
        'csv': lambda: datetime.strptime(date, '%d/%m/%Y'),
        'json': lambda: date.date(),
    }[extension]()

def load_accounts(file_name):
    logging.info(f'Loading accounts from file: {file_name}')

    try:
        extension = file_name.split('.')[1]
        if extension not in ['csv', 'json']:
            logging.error('File format not supported')
            print('File format not supported')
            return None

        try:
            content = read_file(file_name, extension)

            columns_by_extension = {'csv': [('From', -1), ('To', 1)], 'json': [('FromAccount', -1), ('ToAccount', 1)]}
            accounts = {}

            for row_index, transaction_details in content.iterrows():
                try:
                    amount = float(transaction_details['Amount'])

                    parse_date(transaction_details['Date'], extension)

                    for direction, sign in columns_by_extension[extension]:
                        account = get_or_create_account(transaction_details[direction], accounts)
                        transaction = Transaction(transaction_details['Date'], transaction_details['Narrative'],
                                                  sign * amount)
                        account.add_transaction(transaction)

                except Exception as exception:
                    index = row_index
                    if extension == 'csv':
                        index += 2
                    logging.error(
                        f'Error on line: {index}. {exception}')

            return accounts
        except FileNotFoundError:
            logging.error('File not found')
            print('File not found')
        except Exception as exception:
            logging.error(exception)
    except IndexError:
        logging.error('No file extension')
        print('No file extension')

if __name__ == '__main__':
    logging.basicConfig(filename='SupportBank.log', filemode='w', level=logging.DEBUG)
    logging.info('Program started')

    read_input_file = True

    while True:
        logging.info('Waiting for a command...')

        if read_input_file:
            options = ('\nAvailable commands:\n'
                       '\tImport file [Filename] - import file\n'
                       '\tExit - stop the program\n')
        else:
            options = ('\nAvailable commands:\n'
                       '\tImport file [Filename] - import file\n'
                       '\tList All - show all accounts\n'
                       '\tList [Name] - show transactions for a user (example: List Todd)\n'
                       '\tExit - stop the program\n')

        command = input(f'{options}Enter command:')
        logging.info(f'Command: {command}')

        if command.lower() == 'exit':
            logging.info('Program ended')
            break

        if command.lower().startswith('import file '):
            file_name = command.strip()[11:].strip()
            accounts_from_file = load_accounts(file_name)
            if accounts_from_file:
                accounts = accounts_from_file
                read_input_file = False
        elif not read_input_file:
            if command.strip().lower() == 'list all':
                for account in accounts.values():
                    print(account)
            elif command.lower().startswith('list '):
                account_name = command.strip()[5:].strip().lower()

                if account_name in accounts:
                    print(accounts[account_name])
                    print('Transactions')
                    for transaction in accounts[account_name].transactions:
                        print(f'    {transaction}')
                else:
                    logging.warning(f'Account not found')
                    print('Account not found')
            else:
                logging.warning(f'Invalid command')
                print('Invalid command')
        else:
            print('Import a file first')
