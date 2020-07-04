import csv
import logging

import models.security as sec

from models.user import ImportedUser

def import_user_data(file_path: str):
    user_dict = {}

    logging.info('Importing users from CSV and generating passwords. This will take a few moments...')
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            user = ImportedUser(row)
            user.password_set = sec.get_fresh_password_set()

            if user.company in user_dict:
                user_dict[user.company].append(user)
            else:
                user_dict[user.company] = [user]

    logging.info('New users successfully imported.')
    return user_dict