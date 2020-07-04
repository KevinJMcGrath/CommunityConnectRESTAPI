import logging

import api.app as api
import config
from utility import package_logger
from user_import import template_import, salesforce
import user_import


package_logger.initialize_logging()


def import_users(file_path):
    logging.getLogger()


    logging.info('New user onboarding started.')
    sym_client = BotClient(config.bot_config)

    user_dict = template_import.import_user_data(file_path)
    salesforce.import_salesforce_users(user_dict)
    user_import.onboard_users(user_dict, bot_client=sym_client)
    salesforce.update_contact_symphony_ids(user_dict)
    salesforce.send_welcome_email(user_dict)

    logging.info('New user onboarding complete.')


def run_api():
    api.start_app()


if __name__ == "__main__":
    run_api()