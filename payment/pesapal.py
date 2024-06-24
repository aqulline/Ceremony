import webbrowser

import requests


def pay_premium(email, phone):
    url = "https://pay.pesapal.com/v3/api/Auth/RequestToken"
    payload = {
        "consumer_key": "7CMPHDfJsmmyCi28qHZl0KjnyXFbL623",
        "consumer_secret": "FEEoFunywOE/bPHaFlA4Y0EQRDw="
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=payload, headers=headers)

    auth_token = response.json()['token']
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")
    print(f"Token: {auth_token}")

    url2 = "https://pay.pesapal.com/v3/api/Transactions/SubmitOrderRequest"
    import time
    ids = str(time.time().real)
    ids = ids.replace('.', '')
    payload = {
        "id": ids,
        "currency": "TZS",
        "amount": "5000",
        "description": "I want my money",
        "callback_url": "http://localhost:3000/servers/callback",
        "notification_id": "303bc9af-31f4-4dca-b76f-dd161cd8b20e",
        "billing_address": {
            "email_address": email,
            "phone_number": phone,
            "country_code": "TZ",
            "first_name": "",
            "middle_name": "",
            "last_name": "",
            "line_1": "",
            "line_2": "",
            "city": "",
            "state": "",
            "postal_code": "",
            "zip_code": ""
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {auth_token}'  # Replace YOUR_ACCESS_TOKEN with your actual access token
    }

    response = requests.post(url2, json=payload, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    pay_url = response.json()['redirect_url']
    webbrowser.open(pay_url)
