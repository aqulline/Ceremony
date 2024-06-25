import datetime
import random

import firebase_admin
from firebase_admin import credentials, initialize_app, db
from firebase_admin.exceptions import FirebaseError


class FirebaseManager:
    def __init__(self):
        self.cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
        self.app_initialized = False
        self.database_url = 'https://farmzon-abdcb.firebaseio.com/'

    def initialize_firebase(self):
        firebase_admin._apps.clear()
        if not self.app_initialized:
            try:
                initialize_app(self.cred, {'databaseURL': self.database_url})
                self.app_initialized = True
            except FirebaseError as e:
                print(f"Failed to initialize Firebase: {e}")
                return "No Internet!"

    def user_login(self, phone, password):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                user_ref = db.reference("Gerente").child("Company").child(phone).child('User_Info')
                user_data = user_ref.get()
                if user_data and user_data['user_password'] == password:
                    return {
                        "message": "Login successful!",
                        "status": "200",
                        "user_name": user_data.get('user_name'),
                        "premium": user_data.get('premium'),
                        "payment_token": user_data.get('payment_token'),
                        "direct_url": user_data.get('direct_url'),
                        "subscription_date": user_data.get('subscription_date'),
                        "end_of_subscription": user_data.get('end_of_subscription')
                    }
                else:
                    return {"message": "Invalid phone number or password!", "status": "404"}
            except FirebaseError as e:
                print(f"Failed to login user: {e}")
                return {"message": "Login failed due to a server error!", "status": "500"}
        else:
            return {"message": "Firebase initialization failed!", "status": "500"}

    def get_user_company_info(self, phone):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Retrieve company information
                company_ref = db.reference("Gerente").child("Company").child(phone).child('Info_Company')
                company_info = company_ref.get()

                # Retrieve user information
                user_ref = db.reference("Gerente").child("Company").child(phone).child('User_Info')
                user_info = user_ref.get()

                # Retrieve user PRoducts
                products_ref = db.reference("Gerente").child('Company').child(phone).child('Products')
                products_info = products_ref.get()

                if company_info and user_info:
                    return {
                        "user_info": user_info,
                        "company_info": company_info,
                        "product_info": products_info
                    }
                else:
                    return {"message": "User or company information not found!"}
            except FirebaseError as e:
                print(f"Failed to retrieve user company info: {e}")
                return {"message": "Failed to retrieve data due to a server error!"}
        else:
            return {"message": "Firebase initialization failed!"}

    def add_buyer(self, user_phone, buyer_phone, buyer_name, item_id, quantity):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Fetch the price of the product using product_id
                # Reference to the entire database
                ref = db.reference("Gerente").child("Company").child(user_phone)

                # Fetch all products to find the item
                products_ref = ref.child("Products")
                products = products_ref.get()

                if products:
                    for product_id, product_data in products.items():
                        items_ref = products_ref.child(product_id).child("items")
                        item_ref = items_ref.child(item_id)
                        item_data = item_ref.get()
                        if item_data:
                            # Increment total_amount and item_count for the buyer
                            price = item_data.get("price", 0)

                            # Remove the item from the product
                            item_ref.delete()

                            # Retrieve buyer data
                            buyer_ref = db.reference("Gerente").child("Company").child(user_phone).child(
                                'Buyers').child(
                                buyer_phone)
                            buyer_data = buyer_ref.get()

                            if buyer_data:
                                # Buyer already exists, update item_count and total_amount
                                new_item_count = int(buyer_data.get("item_count", 0)) + int(quantity)
                                new_total_amount = int(buyer_data.get("total_amount", 0)) + int(
                                    (int(price) * int(quantity)))
                            else:
                                # New buyer, initialize item_count and total_amount
                                new_item_count = quantity
                                new_total_amount = int(price) * int(quantity)

                            # Set or update buyer data
                            buyer_ref.set({
                                "buyer_name": buyer_name,
                                "product_id": product_id,
                                "item_count": new_item_count,
                                "total_amount": new_total_amount
                            })

                            # Update product_count for the product
                            new_product_count = product_data.get("products_count", 0) - 1
                            products_ref.child(product_id).update({
                                "products_count": new_product_count
                            })

                            # Increment the total number of buyers in Info_Company
                            company_info_ref = db.reference("Gerente").child("Company").child(user_phone).child(
                                'Info_Company')
                            company_info = company_info_ref.get()

                            if company_info:
                                total_buyers = company_info.get("Total_buyers", 0)
                                if not buyer_data:
                                    total_buyers += 1  # Only increment total buyers if it's a new buyer
                                company_info_ref.update({"Total_buyers": total_buyers})

                            return "Buyer added and item removed successfully!"


            except FirebaseError as e:
                print(f"Failed to add buyer: {e}")
                return "Failed to add buyer!"
        else:
            return "Firebase initialization failed!"

    def get_buyers(self, user_phone):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Reference to the entire database
                ref = db.reference("Gerente").child("Company").child(user_phone).child('Buyers')

                # Fetch all buyers
                buyers_data = ref.get()

                if buyers_data:
                    buyers_list = []
                    for buyer_phone, buyer_info in buyers_data.items():
                        buyers_list.append({
                            "buyer_phone": buyer_phone,
                            "buyer_name": buyer_info.get("buyer_name", ""),
                            "product_id": buyer_info.get("product_id", ""),
                            "item_count": buyer_info.get("item_count", 0),
                            "total_amount": buyer_info.get("total_amount", 0)
                        })

                    return buyers_list
                else:
                    return []

            except FirebaseError as e:
                print(f"Failed to fetch buyers: {e}")
                return []

        else:
            return "Firebase initialization failed!"

    def initialize_delivery_order(self, user_phone, item_id, buyer_phone, buyer_name, bussines_name):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Reference to the user's products
                ref = db.reference("Gerente").child("Company").child(user_phone)

                # Fetch all products to find the item
                products_ref = ref.child("Products")
                products = products_ref.get()

                if products:
                    for product_id, product_data in products.items():
                        items_ref = products_ref.child(product_id).child("items")
                        item_ref = items_ref.child(item_id)
                        item_data = item_ref.get()
                        if item_data:
                            price = item_data.get("price", 0)
                            product_name = product_data.get("product_name", "")
                            # Generate a unique order ID
                            order_id = f"order_{random.randint(1000000, 9999999)}"
                            current_date = datetime.datetime.now().strftime("%Y-%m-%d")

                            # Reference to the delivery orders
                            delivery_orders_ref = db.reference("Gerente").child("DeliveryOrders").child(
                                user_phone).child(current_date).child(order_id)

                            # Set order details
                            delivery_orders_ref.set({
                                "item_id": item_id,
                                "buyer_phone": buyer_phone,
                                "buyer_name": buyer_name,
                                "product_id": product_id,
                                "product_name": product_name,
                                "price": price,
                                "order_date": current_date,
                                "status": "pending"
                            })

                            # Increment the total number of orders for today in Info_Company
                            company_info_ref = db.reference("Gerente").child("Company").child(user_phone).child(
                                'Info_Company')
                            company_info = company_info_ref.get()

                            if company_info:
                                # Fetch all today's orders and count them
                                today_orders_ref = db.reference("Gerente").child("DeliveryOrders").child(
                                    user_phone).child(current_date)
                                today_orders = today_orders_ref.get()
                                today_orders_count = len(today_orders) if today_orders else 0

                                company_info_ref.update({"Today_orders": today_orders_count})

                            from beem import sms

                            sms.send_sms(buyer_phone,
                                         f"Dear {buyer_name} asante kwa kununua bidha kwa {bussines_name}, Mzigo wako umefika utaletewa hivi karibuni, Migo No:{order_id}, KARIBU PORTAL!")

                            return {'message': f"Delivery order {order_id} initialized successfully!", 'status': '200',
                                    'order_id': f'{order_id}'}

                return {"message": "Item not found!"}

            except FirebaseError as e:
                print(f"Failed to initialize delivery order: {e}")
                return {'message': "Failed to initialize delivery order!"}

        else:
            return {'message': "Firebase initialization failed!"}


# print(FirebaseManager.user_login(FirebaseManager(), '0715700411', '9060'))
# print(FirebaseManager.get_user_company_info(FirebaseManager(), '0715700411'))
# FirebaseManager.add_buyer(FirebaseManager(), '0715700411', '0788204328', 'Aqulline Mbuya', '7330341A', '1')
# print(FirebaseManager.get_buyers(FirebaseManager(), '0715700411'))

# print(FirebaseManager.initialize_delivery_order(FirebaseManager(), '0715700411', '2777963A', '0789934496', 'RayMundi',
                                                # 'SomeHoes'))
