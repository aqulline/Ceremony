import random


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
                    "bill_payment": 0,
                    "Total_buyers": 0,
                    "Special_buyers": 0,
                    "Total_Delivered": 0,
                    "Today_delivered": 0,
                    "Today_orders": 0,
                    "Total_orders": 0,
                    "Total_products": 0
                })
                store = db.reference("Gerente").child("Company").child(phone).child('User_Info')
                store.set({
                    "user_name": username,
                    "user_phone": phone,
                    "user_password": password,
                    "premium": False,
                    "payment_token": "56b34450-f865-4b98-a085-dd15f3f2791a",
                    "direct_url": "https://pay.pesapal.com/iframe/PesapalIframe3/Index?OrderTrackingId=56b34450-f865-4b98-a085-dd15f3f2791a",
                    "premium_payment_token": "",
                    "premium_payment_url": "",
                    "subscription_date": "",
                    "end_of_subscription": ""
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

    def add_products(self, product_name, phone, product_letter):
        import firebase_admin
        firebase_admin._apps.clear()
        from firebase_admin import credentials, initialize_app, db
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
                initialize_app(cred, {'databaseURL': 'https://farmzon-abdcb.firebaseio.com/'})
                store = db.reference("Gerente").child("Company").child(phone).child('Products').child(product_letter)
                store.set(
                    {
                        "products_count": 0,
                        "product_letter": product_letter,
                        "product_price": 0,
                        "product_name": product_name
                    }
                )
                company = db.reference("Gerente").child("Company").child(phone).child('Info_Company')
                company_info = company.get()
                if company_info:
                    product_count = company_info.get('Total_products', 0) + 1
                    company.update({
                        "Total_products": product_count
                    })
            except:
                return "No Internet!"

    def generate_item_id(self, product_letter):
        prefix = random.randint(000000, 9999999)
        return f"{prefix}{product_letter}"

    def add_items(self, phone, product_letter, price):
        import firebase_admin
        firebase_admin._apps.clear()
        from firebase_admin import credentials, initialize_app, db
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
                initialize_app(cred, {'databaseURL': 'https://farmzon-abdcb.firebaseio.com/'})
                item_id = self.generate_item_id(product_letter)
                store = db.reference("Gerente").child("Company").child(phone).child('Products').child(
                    product_letter).child("items").child(item_id)
                store.set(
                    {
                        "item_id": item_id,
                        "price": price
                    }
                )
                product_ref = db.reference("Gerente").child("Company").child(phone).child('Products').child(
                    product_letter)
                product_info = product_ref.get()

                if product_info:
                    new_products_count = product_info.get('products_count', 0) + 1
                    product_ref.update({
                        "products_count": new_products_count
                    })

            except:
                return "No Internet!"

# FireBase.Register_user(FireBase(), '0715700411', "Beast", "9060")

# FireBase.add_products(FireBase(), 'Skirts', '0715700411')

# FireBase.add_products(FireBase(), "Skirts", '0715700411', 'B')

# FireBase.add_items(FireBase(), '0715700411', 'A', "9000")
