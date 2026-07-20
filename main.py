import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import logging
import os

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

def read_csv(file_name):
    content = pd.read_csv(file_name)
    content['Date'] = content['Date'].apply(lambda date: datetime.strptime(date, '%d/%m/%Y'))
    return content

def read_json(file_name):
    content = pd.read_json(file_name)
    content['Date'] = content['Date'].apply(lambda date: date.date())
    content = content.rename(columns={'ToAccount': 'To', 'FromAccount': 'From'})
    return content

def read_xml(file_name):
    with open(file_name, encoding='utf8') as f:
        xml = f.read()

    return BeautifulSoup(xml, 'xml')

def read_file(file_name, extension):
    return {
        'csv': lambda: read_csv(file_name),
        'json': lambda: read_json(file_name),
        'xml': lambda: read_xml(file_name)
    }[extension]()

def process_transaction(row_index, accounts, details):
    try:
        amount = float(details['Amount'])
        date = details['Date']

        for name, sign in [(details['To'], 1), (details['From'], -1)]:
            account = get_or_create_account(name, accounts)
            transaction = Transaction(date, details['Narrative'], sign * amount)
            account.add_transaction(transaction)

    except Exception as exception:
        logging.error(
            f'Error on line: {row_index + 1}. {exception}')

def parse_csv_and_json(content, accounts):
    for row_index, transaction_details in content.iterrows():
        process_transaction(row_index, accounts, transaction_details)

    return accounts

def parse_xml(content, accounts):
    all_transactions = content.find_all('SupportTransaction')

    for row_index, transaction in enumerate(all_transactions):
        try:
            date = transaction['Date']
            date = pd.to_datetime(int(date), unit='D', origin='1900-01-01').date()

            parties = transaction.find('Parties')
            if parties is not None:
                to_account = parties.find('To').text
                from_account = parties.find('From').text
            else:
                raise Exception('Parties not found')

            narrative = transaction.find('Description')
            if narrative:
                narrative = narrative.text
            else:
                raise Exception('Narrative not found')

            amount = transaction.find('Value')
            if amount:
                amount = amount.text
            else:
                raise Exception('Amount not found')

            details = {
                'Date': date,
                'To': to_account,
                'From': from_account,
                'Narrative': narrative,
                'Amount': amount
            }
            process_transaction(row_index, accounts, details)

        except Exception as exception:
            logging.error(f'Error on line: {row_index + 1}. {exception}')

    return accounts

def process_file_content(extension, content):
    accounts = {}

    return {
        'csv': lambda: parse_csv_and_json(content, accounts),
        'json': lambda: parse_csv_and_json(content, accounts),
        'xml': lambda: parse_xml(content, accounts)
    }[extension]()

def check_extension(file_name):
    extension = file_name.split('.')[1]
    if extension not in ['csv', 'json', 'xml']:
        logging.error('File format not supported')
        print('File format not supported')
        return None
    return extension

def load_accounts(file_name):
    logging.info(f'Loading accounts from file: {file_name}')

    try:
        extension = check_extension(file_name)
        try:
            content = read_file(file_name, extension)
            return process_file_content(extension, content)

        except FileNotFoundError:
            logging.error('File not found')
            print('File not found')
        except Exception as exception:
            logging.error(exception)
    except IndexError:
        logging.error('No file extension')
        print('No file extension')

def write_transactions(file_name, content):
    extension = check_extension(file_name)
    if extension:
        if os.path.exists(file_name):
            logging.info(f'File {file_name} already exists.')

            command = input(f'File already exists. Overwrite? (y/n):')
            logging.info(f'Command: {command}')

            if command.lower() == 'y':
                pass

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
            elif command.lower().startswith('export file '):
                file_name = command.strip()[11:].strip()
            else:
                logging.warning(f'Invalid command')
                print('Invalid command')
        else:
            print('Import a file first')
