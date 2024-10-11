import json
import requests
import certifi
import ssl

ctx = ssl.create_default_context(cafile=certifi.where())


def phone_repr(phone):
    new_number = ""
    if phone != "" and len(phone) != 9:
        for i in range(phone.__len__()):
            if i == 0:
                pass
            else:
                new_number = new_number + phone[i]
        number = "255" + new_number
        public_number = number
        return public_number
    return False


def send_sms(phone_company, sms):
    URL = 'https://apisms.beem.africa/v1/send'
    content_type = 'application/json'
    source_addr = 'INFO'
    # secrete_key = "ZjRjNjU4MmM1NTM2ODY1YWYwOGI1YzhmZjJjYmFkZDcwM2U4NGFkYTlhNzNhNjJiOWVlMmNmYzc5NTJhYjkyZQ=="
    secrete_key = "ZGVmNWVkMzYxZmRhNWQ3MjM3NDhkMThmMWFkYzg4ZTM0ZGUwMjZmMGZjYTkzNWNkODRkMzFiMWJkZmM0M2JmYw=="
    # secrete_key = "YmE1NmRmNzVmY2JhN2RjYmI0ZGU1OTJlMzFlNWU4MDdhYzQ2MWNlNWVmZDVkNWFkNzYxOWUyNjRmNGNmYmNiNQ=="
    # api_key = '0188a7cf7ff88579'
    api_key = '8ccab9418dedde47'
    # api_key = 'b7a0b864387611b6'
    phonee = phone_repr(phone_company)
    if phonee:
        apikey_and_apisecret = api_key + ':' + secrete_key

        """sms = f'SHOPPY You have an order from{phone}, 
                       f'product name {product}, quantity {quantity} '
                       f'customer location {location}'"""

        first_request = requests.post(url=URL, data=json.dumps({
            'source_addr': 'PORTAL',
            'schedule_time': '',
            'encoding': '0',
            'message': sms,
            'recipients': [
                {
                    'recipient_id': 1,
                    'dest_addr': phonee,
                }
            ],
        }),

                                      headers={
                                          'Content-Type': content_type,
                                          'Authorization': 'Basic ' + api_key + ':' + secrete_key,
                                      },
                                      auth=(api_key, secrete_key), verify=certifi.where())

        print(first_request.status_code)
        print(first_request.json())
        return (first_request.json())
    else:
        return False


# send_sms('0715700411', 'vimbweta vya uwanjani')
# phones = ['0718764755', '0687613092']
# for i in phones:
#     send_sms(i, "Testing company names bulk sms!!")

