import requests
import json
from BeemAfrica import Authorize, OTP
import BeemAfrica as BM
from rsa import verify


# request class

class req:
    pin = ''
    phone = ''

    def otp_req(self, phone):
        URL = 'https://apiotp.beem.africa/v1/request'
        content_type = 'application/json'
        secrete_key = "OTczOTM2MjQwN2Y4YzM5ZDA2Zjc4Y2YyNTQ0NjA3ODQ5Y2U3NzIyZTk4ZjkxYmY0ODg2NDBlNWQxMDczZWI2Yw=="
        api_key = 'e651190c432fa4d3'
        Authorize(api_key, secrete_key)
        req.phone = self.phone_repr(phone)
        print(phone)
        first_request = requests.post(url=URL, data=json.dumps({
            "appId": 181,
            'source_addr': 'PORTAL',
            "msisdn": self.phone_repr(phone)
        }),

                                      headers={
                                          'Content-Type': content_type,
                                          'Authorization': 'Basic ' + api_key + ':' + secrete_key,
                                      },
                                      auth=(api_key, secrete_key), verify=False)

        print(first_request.status_code)
        print(first_request.json())
        data = first_request.json()
        req.pin = pin = data['data']['pinId']
        print(pin)
        ver = data['data']['message']['code']
        if ver == 100:

            return True
        else:
            return False

    def verfy(self, pin):
        print(req.pin)
        data = OTP.verify(pin_id=self.pin, pin=pin)
        print(data)
        valid = data['data']['message']['code']
        if valid == 117:

            return True
        else:
            return False


    def phone_repr(self, phone):
        new_number = ""
        if phone != "":
            for i in range(phone.__len__()):
                if i == 0:
                    pass
                else:
                    new_number = new_number + phone[i]
            number = "255" + new_number
            public_number = number
            return public_number

# req.otp_req(req(), '0715700411')
# secrete_key = "ZGVmNWVkMzYxZmRhNWQ3MjM3NDhkMThmMWFkYzg4ZTM0ZGUwMjZmMGZjYTkzNWNkODRkMzFiMWJkZmM0M2JmYw=="
# api_key = '8ccab9418dedde47'
# Authorize(api_key, secrete_key)
# data = OTP.verify('fa82a88f-0f0c-437b-bc5a-3747a45d05dd', '766507')
# print(data)

# secrete_key = "OTczOTM2MjQwN2Y4YzM5ZDA2Zjc4Y2YyNTQ0NjA3ODQ5Y2U3NzIyZTk4ZjkxYmY0ODg2NDBlNWQxMDczZWI2Yw=="
# api_key = 'e651190c432fa4d3'
# Authorize(api_key, secrete_key)
# data = OTP.send_otp('255715700411', 2176)
# print(data)

