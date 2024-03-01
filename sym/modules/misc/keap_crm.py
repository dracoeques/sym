import os
import requests


def achieve_api_goal(payload):
    crm_access_key = os.environ.get("CRM_ACCESS_KEY")

    headers = {
        "X-Keap-API-Key": crm_access_key,
        'content-type': 'application/json',
    }

    #validate payload parameters
    if "integration" not in payload:
        return {},"Error: 'integration' not provided"
    if "call_name" not in payload:
        return {},"Error: 'call_name' not provided"
    if "contact_id" not in payload:
        return {},"Error: 'contact_id' not provided"
    

    url = f"https://api.infusionsoft.com/crm/rest/v1/campaigns/goals/{payload['integration']}/{payload['call_name']}"

    crm_payload = {
        "contact_id": payload["contact_id"],
    }
    x = requests.post(url, json=crm_payload, headers=headers)
    
    response_payload = x.json()

    #TODO: validate response
    return response_payload, None


def get_contact(contact_id, optional_properties="custom_fields"):
   
    url = f"https://api.infusionsoft.com/crm/rest/v1/contacts/{contact_id}"

    crm_access_key = os.environ.get("CRM_ACCESS_KEY")

    headers = {
        "X-Keap-API-Key": crm_access_key,
        'content-type': 'application/json',
    }

    x = requests.get(url, headers=headers, params={"optional_properties":optional_properties})
    response_payload = x.json()

    return response_payload, None

def get_contact_id_by_email(payload):
    """ Given an email, get their contact id"""
    
    #validate payload parameters
    if "email" not in payload:
        return {},"Error: 'email' not provided"
    
    email = payload["email"]
    url = f"https://api.infusionsoft.com/crm/rest/v1/contacts"

    crm_access_key = os.environ.get("CRM_ACCESS_KEY")

    headers = {
        "X-Keap-API-Key": crm_access_key,
        'content-type': 'application/json',
    }

    x = requests.get(url, headers=headers, params={"email":email})
    response_payload = x.json()

    return response_payload, None



def create_contact(payload):

    
    url = "https://api.infusionsoft.com/crm/rest/v1/contacts"
    crm_access_key = os.environ.get("CRM_ACCESS_KEY")

    headers = {
        "X-Keap-API-Key": crm_access_key,
        'content-type': 'application/json',
    }

    #validate payload parameters
    if "email" not in payload:
        return {},"Error: 'email' not provided"
    
    crm_payload = {
        "email_addresses": [
            {
            "email": payload["email"],
            "field": "EMAIL1",
            }
        ]
    }
    x = requests.post(url, json=crm_payload, headers=headers)
    response_payload = x.json()

    return response_payload, None


def get_custom_fields():

    url = f"https://api.infusionsoft.com/crm/rest/v1/contacts/model"
    crm_access_key = os.environ.get("CRM_ACCESS_KEY")

    headers = {
        "X-Keap-API-Key": crm_access_key,
        'content-type': 'application/json',
    }

    x = requests.get(url, headers=headers)
    response_payload = x.json()
    return response_payload, None


def get_custom_field_by_name(name):
    """ Get a custom field by name 
        useful since assigning a custom field requires the id
    """
    url = f"https://api.infusionsoft.com/crm/rest/v1/contacts/model"
    crm_access_key = os.environ.get("CRM_ACCESS_KEY")

    headers = {
        "X-Keap-API-Key": crm_access_key,
        'content-type': 'application/json',
    }

    x = requests.get(url, headers=headers)
    response_payload = x.json()

    field = None
    for cf in response_payload["custom_fields"]:
        if cf["label"] == name:
            field = cf
            break

    return field, None

def create_custom_field(payload):

    url = "https://api.infusionsoft.com/crm/rest/v1/contacts/model/customFields"
    crm_access_key = os.environ.get("CRM_ACCESS_KEY")

    headers = {
        "X-Keap-API-Key": crm_access_key,
        'content-type': 'application/json',
    }

    if "field_type" not in payload:
        return {}, "field type not provided"
    if "label" not in payload:
        return {}, "label not provided"

    # crm_payload = {
    #     "field_type": "Text",
    #     "label": "love_coach_report_01_23_2024",
    # }

    crm_payload = {
        "field_type": payload["field_type"],
        "label":payload["label"],
    }

    x = requests.post(url, json=crm_payload, headers=headers)
    response_payload = x.json()
    return response_payload, None


def assign_custom_field(payload):
    """ Given this user, assign a custom field value for them
    
        https://developer.infusionsoft.com/docs/rest/#tag/Contact/operation/updatePropertiesOnContactUsingPATCH
    """

    if "contact_id" not in payload:
        return {}, "contact_id not provided"
    if "custom_field_id" not in payload:
        return {}, "custom_field_id not provided"
    if "content" not in payload:
        return {}, "content not provided"

    contact_id = payload["contact_id"]

    url = f"https://api.infusionsoft.com/crm/rest/v1/contacts/{contact_id}?update_mask=custom_fields"

    crm_payload = {
        "custom_fields": [
            {
                "id": payload["custom_field_id"],
                "content": payload["content"],
            }
        ],
    }

    crm_access_key = os.environ.get("CRM_ACCESS_KEY")

    headers = {
        "X-Keap-API-Key": crm_access_key,
        'content-type': 'application/json',
    }
    
    x = requests.patch(url, json=crm_payload, headers=headers)
    print(x.status_code)
    response_payload = x.json()
    return response_payload, None