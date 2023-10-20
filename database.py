class FireBase:
    def Register_user(self, phone, username, password):
        import firebase_admin
        firebase_admin._apps.clear()
        from firebase_admin import credentials, initialize_app, db
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
                initialize_app(cred, {'databaseURL': 'https://farmzon-abdcb.firebaseio.com/'})
                store = db.reference("Gerente").child("Company").child(phone).child('Info_Company')
                store.set({
                    "Total_earnings": 0,
                    "Total_sms": 10,
                    "Total_buyers": 0,
                    "Today_transactions": 0,
                    "Net_earnings": 0,
                })
                store = db.reference("Gerente").child("Company").child(phone).child('User_Info')
                store.set({
                    "user_name": username,
                    "user_phone": phone,
                    "user_password": password,
                })
            except:
                return "No Internet!"

    def get_user(self, phone):
        import firebase_admin
        firebase_admin._apps.clear()
        from firebase_admin import credentials, initialize_app, db
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
                initialize_app(cred, {'databaseURL': 'https://farmzon-abdcb.firebaseio.com/'})
                store = db.reference("Gerente").child("Company").child(phone)
                stores = store.get()
                return stores
            except:
                return "No Internet!"

    def add_buyer(self, data, phone):
        import firebase_admin
        firebase_admin._apps.clear()
        from firebase_admin import credentials, initialize_app, db
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
                initialize_app(cred, {'databaseURL': 'https://farmzon-abdcb.firebaseio.com/'})
                print("again!!!!!!!!!", data)
                for x, y in data.items():
                    store = db.reference("Gerente").child("Company").child(phone).child('Buyers').child(y)
                    store.set({
                        "buyer_name": x,
                        "buyer_number": y,
                        "total_spending": "0",
                        "total_product": "0",
                        "location_region": "0"
                    })
                    print("Done!!!!")
            except:
                return "No Internet!"
