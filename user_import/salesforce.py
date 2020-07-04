import logging

from typing import List, Dict

from simple_salesforce import Salesforce

import config

from models.user import ImportedUser

if config.salesforce['is_sandbox']:
    sfdc = Salesforce(username=config.salesforce['username'], password=config.salesforce['password'],
                      security_token=config.salesforce['security_token'], domain='test')
else:
    sfdc = Salesforce(username=config.salesforce['username'], password=config.salesforce['password'],
                          security_token=config.salesforce['security_token'])
log = logging.getLogger()


def import_salesforce_single_user(user):
    company_id = get_company_id(user.company)

    if not company_id:
        return False, 'Unable to save Account to Salesforce'

    if not get_user(user, company_id):
        return False, 'Unable to save Contact to Salesforce'



def import_salesforce_users(user_dict: dict):
    return_dict = {}
    for company_name, user_list in user_dict.items():
        company_id = get_company_id(company_name)
        if company_id:
            return_list = []
            for user in user_list:
                if get_user(user, company_id):
                    return_list.append(user)

            return_dict[company_name] = return_list



def get_user(user_record: ImportedUser, company_id: str):
    user_id, acct_id = search_user(user_record.email)

    if user_id:
        log.info(f'{user_record.email} exists in SFDC with Id: {user_id}')
        user_record.sfdc_account_id = acct_id
        user_record.sfdc_id = user_id
        return True
    else:
        log.info(f'Creating Contact for email address: {user_record.email}')
        return insert_user(user_record, company_id)



def insert_user(user_record: ImportedUser, company_id: str):
    user_payload = {
        "AccountId": company_id,
        "FirstName": user_record.first_name,
        "LastName": user_record.last_name,
        "Email": user_record.email
    }

    result = sfdc.Contact.create(user_payload)

    if result['success']:
        user_record.sfdc_id = result['id']
        user_record.sfdc_account_id = company_id

        add_contact_roles(user_record)

        return True
    else:
        log.error('Error creating Contact')
        for err in result['errors']:
            log.error(err)

        return None


def update_contact_symphony_ids(user_dict: Dict[str, List[ImportedUser]]):
    log.info('Updating Contacts with Community Connect Ids')
    payload_list = []

    for user_list in user_dict.values():
        for user in user_list:
            payload_list.append({
                "Id": user.sfdc_id,
                "Community_Pod_Id__c": user.symphony_id
            })

    sfdc.bulk.Contact.update(payload_list)

def add_contact_roles(user_record: ImportedUser):
    pass


def search_user(email_address: str):
    soql = f"SELECT Id, AccountId FROM Contact WHERE Email ='{email_address}'"

    results = sfdc.query(soql)['records']

    if results:
        record = results[0]
        return record['Id'], record['AccountId']

    return None, None


def get_company_id(company_name: str):
    company_id = company_search(company_name)
    if not company_id:
        log.info(f'{company_name} does not exist. Creating Account in Salesforce.')
        company_id = insert_company(company_name)

    return company_id


def company_search(company_name: str):
    sosl_query = 'FIND {' + company_name + '} IN NAME FIELDS RETURNING Account(Id, Name)'
    results = sfdc.quick_search(company_name)['searchRecords']

    for res in results:
        if res['attributes']['type'] == 'Account':
            sfdc_id = res['Id']
            log.info(f'{company_name} found in Salesforce - Id: {sfdc_id}')
            return sfdc_id

    return None


def insert_company(company_name: str):
    company_payload = {
        'Name': company_name,
        'Type': 'Community Connect',
        'Industry': 'Financial Services',
        'Industry_Sub_Type__c': 'Private Equity',
        'Financial_Services_Category__c': 'Buy Side'
    }

    result = sfdc.Account.create(company_payload)

    if result['success']:
        return result['id']
    else:
        log.error('Error creating account')
        for err in result['errors']:
            log.error(err)

        return None


def send_welcome_email(user_dict: dict):
    pass