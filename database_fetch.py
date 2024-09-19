import datetime
import random

import firebase_admin
from firebase_admin import credentials, initialize_app, db, auth
from firebase_admin.exceptions import FirebaseError
from beem import sms




class FirebaseManager:
    def __init__(self):
        self.cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
        self.app_initialized = False
        self.database_url = 'https://farmzon-abdcb.firebaseio.com/'

    def initialize_firebase(self):
        firebase_admin._apps.clear()
        if not self.app_initialized:
            print('buyer')
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

    def get_orders(self, user_phone):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Get the current date
                current_date = datetime.datetime.now().strftime("%Y-%m-%d")

                # Reference to the delivery orders for the user
                delivery_orders_ref = db.reference("Gerente").child("DeliveryOrders").child(user_phone).child(
                    current_date)

                # Fetch all orders for the current date
                orders = delivery_orders_ref.get()

                if orders:
                    return {'message': "Orders retrieved successfully!", 'status': '200', 'orders': orders}
                else:
                    return {'message': "No orders found for today!", 'status': '200', 'orders': {}}

            except FirebaseError as e:
                print(f"Failed to retrieve orders: {e}")
                return {'message': "Failed to retrieve orders!"}
            except Exception as e:
                print(f"Unexpected error: {e}")
                return {'message': "Unexpected error occurred!"}
        else:
            return {'message': "Firebase initialization failed!"}

    def get_orders_custom(self, user_phone, custom_date):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Reference to the user's delivery orders on the custom date
                delivery_orders_ref = db.reference("Gerente").child("DeliveryOrders").child(user_phone).child(
                    custom_date)
                delivery_orders_data = delivery_orders_ref.get()

                if delivery_orders_data:
                    orders = []
                    for order_id, order_info in delivery_orders_data.items():
                        orders.append({
                            "order_id": order_id,
                            "item_id": order_info.get("item_id", ""),
                            "buyer_phone": order_info.get("buyer_phone", ""),
                            "buyer_name": order_info.get("buyer_name", ""),
                            "product_id": order_info.get("product_id", ""),
                            "product_name": order_info.get("product_name", ""),
                            "price": order_info.get("price", 0),
                            "order_date": order_info.get("order_date", ""),
                            "status": order_info.get("status", "pending")
                        })

                    return {
                        'message': "Orders retrieved successfully",
                        'status': '200',
                        'orders': orders
                    }
                else:
                    return {
                        'message': "No orders found for the specified date",
                        'status': '404',
                        'orders': []
                    }

            except FirebaseError as e:
                print(f"Failed to retrieve orders: {e}")
                return {'message': "Failed to retrieve orders!"}
            except Exception as e:
                print(f"Unexpected error: {e}")
                return {'message': "Unexpected error occurred!"}
        else:
            return {'message': "Firebase initialization failed!"}

    def get_orders_Interval(self, user_phone, custom_range):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Reference to the user's delivery orders
                delivery_orders_ref = db.reference("Gerente").child("DeliveryOrders").child(user_phone)
                delivery_orders_data = delivery_orders_ref.get()

                if not delivery_orders_data:
                    return {
                        'message': "No orders found",
                        'status': '404',
                        'orders': []
                    }

                # Get current date
                today = datetime.datetime.now()

                # Define date range based on custom_range
                if custom_range == 'Today':
                    start_date = today.date()
                    end_date = today.date()
                elif custom_range == 'Week':
                    start_date = (today - datetime.timedelta(days=today.weekday())).date()  # Monday of the current week
                    end_date = today.date()  # Today
                elif custom_range == 'Month':
                    start_date = today.replace(day=1).date()  # First day of the current month
                    end_date = today.date()  # Today
                else:
                    return {
                        'message': "Invalid range",
                        'status': '400',
                        'orders': []
                    }

                filtered_orders = []

                # Filter orders within the date range
                for date_str, orders in delivery_orders_data.items():
                    order_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    if start_date <= order_date <= end_date:
                        for order_id, order_info in orders.items():
                            filtered_orders.append({
                                'order_id': order_id,
                                'order_date': date_str,
                                'order_info': order_info
                            })

                if not filtered_orders:
                    return {
                        'message': "No orders found in the specified range",
                        'status': '404',
                        'orders': []
                    }

                return {
                    'message': "Orders retrieved successfully",
                    'status': '200',
                    'orders': filtered_orders
                }

            except FirebaseError as e:
                print(f"Failed to retrieve orders: {e}")
                return {'message': "Failed to retrieve orders!"}
            except Exception as e:
                print(f"Unexpected error: {e}")
                return {'message': "Unexpected error occurred!"}
        else:
            return {'message': "Firebase initialization failed!"}

    def get_order_info(self, user_phone, order_id):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Reference to the user's delivery orders
                delivery_orders_ref = db.reference("Gerente").child("DeliveryOrders").child(user_phone)
                delivery_orders_data = delivery_orders_ref.get()

                if delivery_orders_data:
                    for date, orders in delivery_orders_data.items():
                        if order_id in orders:
                            order_info = orders[order_id]
                            return {
                                'message': "Order information retrieved successfully",
                                'status': '200',
                                'order_info': {
                                    "order_id": order_id,
                                    "bill_payment": order_info.get("bill_payment", ""),
                                    "item_id": order_info.get("item_id", ""),
                                    "buyer_phone": order_info.get("buyer_phone", ""),
                                    "buyer_name": order_info.get("buyer_name", ""),
                                    "product_id": order_info.get("product_id", ""),
                                    "product_name": order_info.get("product_name", ""),
                                    "price": order_info.get("price", 0),
                                    "order_date": order_info.get("order_date", ""),
                                    "status": order_info.get("status", "pending")
                                }
                            }

                    return {
                        'message': "Order not found",
                        'status': '404',
                        'order_info': {}
                    }

            except FirebaseError as e:
                print(f"Failed to retrieve order information: {e}")
                return {'message': "Failed to retrieve order information!"}
            except Exception as e:
                print(f"Unexpected error: {e}")
                return {'message': "Unexpected error occurred!"}
        else:
            return {'message': "Firebase initialization failed!"}

    def initialize_delivery_order(self, user_phone, item_id, buyer_phone, buyer_name, business_name):
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

                            # Add the buyer information
                            self.app_initialized = False
                            self.add_buyer(user_phone, buyer_phone, buyer_name, item_id, 1)

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

                                # Calculate the new total income
                                current_total_income = company_info.get("Total_income", 0)
                                new_total_income = current_total_income + int(price)

                                # Update the Info_Company with new order count and total income
                                company_info_ref.update({
                                    "Today_orders": today_orders_count,
                                    "Total_income": new_total_income
                                })

                            from beem import sms

                            sms.send_sms(buyer_phone,
                                         f"Dear {buyer_name}, thank you for purchasing from {business_name}. Your order has been received and will be delivered shortly. Order No: {order_id}. Welcome to PORTAL!")

                            return {'message': f"Delivery order {order_id} initialized successfully!", 'status': '200',
                                    'order_id': f'{order_id}'}

                return {"message": "Item not found!"}

            except FirebaseError as e:
                print(f"Failed to initialize delivery order: {e}")
                return {'message': "Failed to initialize delivery order!"}

        else:
            return {'message': "Firebase initialization failed!"}

    def set_payment(self, payment_token, direct_url, user_phone):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Reference to the user's info
                user_info_ref = db.reference("Gerente").child("Company").child(user_phone).child('User_Info')

                # Update the direct_url and payment_token
                user_info_ref.update({
                    "payment_token": payment_token,
                    "direct_url": direct_url
                })

                return {'message': "Payment information updated successfully!", 'status': '200'}

            except FirebaseError as e:
                print(f"Failed to update payment information: {e}")
                return {'message': "Failed to update payment information!"}
            except Exception as e:
                print(f"Unexpected error: {e}")
                return {'message': "Unexpected error occurred!"}
        else:
            return {'message': "Firebase initialization failed!"}

    def check_payment(self, payment_token, user_phone, user_name, pay_phone):
        from payment import pesapal as PP

        if PP.get_payment_status(payment_token)['status_code'] == 1:
            premium = True
            subscription_date = datetime.datetime.now().strftime("%Y-%m-%d")
            expiring_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            self.initialize_firebase()
            if self.app_initialized:
                try:
                    # Reference to the user's info
                    user_info_ref = db.reference("Gerente").child("Company").child(pay_phone).child('User_Info')

                    # Update the direct_url and payment_token
                    user_info_ref.update({
                        "premium": premium,
                        "subscription_date": subscription_date,
                        "end_of_subscription": expiring_date
                    })
                    from beem import sms

                    sms.send_sms(user_phone,
                                 f"Dear {user_name} your subscription fee of 5,000 TZS was paid on {subscription_date} until {expiring_date} , KARIBU PORTAL!")
                    return {'message': "Premium user", 'status': '200'}

                except FirebaseError as e:
                    print(f"Failed to update payment information: {e}")
                    return {'message': "Failed to update payment information!", 'status': '100'}
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    return {'message': "Unexpected error occurred!", 'status': '100'}
            else:
                return {'message': "Firebase initialization failed!", 'status': '100'}
        else:
            return {'message': "Firebase initialization failed!", "status": '500'}

    def special_buyer(self, user_phone, buyer_phone):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Reference to the buyer's data
                buyer_ref = db.reference("Gerente").child("Company").child(user_phone).child('Buyers').child(
                    buyer_phone)
                buyer_data = buyer_ref.get()

                if buyer_data:
                    item_count = buyer_data.get("item_count", 0)
                    if item_count > 5:
                        # Update the special buyer status
                        buyer_ref.update({"special_buyer": True})

                        # Increment the total number of special buyers in Info_Company
                        company_info_ref = db.reference("Gerente").child("Company").child(user_phone).child(
                            'Info_Company')
                        company_info = company_info_ref.get()

                        if company_info:
                            special_buyers = company_info.get("Special_buyers", 0) + 1
                            company_info_ref.update({"Special_buyers": special_buyers})

                        return {'message': "Buyer updated to special status", 'status': '200'}
                    else:
                        return {'message': "Buyer does not meet the criteria for special status", 'status': '200'}
                else:
                    return {'message': "Buyer not found", 'status': '404'}

            except FirebaseError as e:
                print(f"Failed to update special buyer: {e}")
                return {'message': "Failed to update special buyer!"}
            except Exception as e:
                print(f"Unexpected error: {e}")
                return {'message': "Unexpected error occurred!"}
        else:
            return {'message': "Firebase initialization failed!"}

    def get_special_buyers(self, user_phone):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Reference to the buyers data
                buyers_ref = db.reference("Gerente").child("Company").child(user_phone).child('Buyers')
                buyers_data = buyers_ref.get()

                if buyers_data:
                    special_buyers = {phone: info for phone, info in buyers_data.items() if
                                      info.get("special_buyer", False)}

                    return {
                        'message': "Special buyers retrieved successfully",
                        'status': '200',
                        'special_buyers': special_buyers
                    }
                else:
                    return {
                        'message': "No buyers found",
                        'status': '404',
                        'special_buyers': {}
                    }

            except FirebaseError as e:
                print(f"Failed to retrieve special buyers: {e}")
                return {'message': "Failed to retrieve special buyers!"}
            except Exception as e:
                print(f"Unexpected error: {e}")
                return {'message': "Unexpected error occurred!"}
        else:
            return {'message': "Firebase initialization failed!"}

    def get_normal_buyers(self, user_phone):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Reference to the buyers data
                buyers_ref = db.reference("Gerente").child("Company").child(user_phone).child('Buyers')
                buyers_data = buyers_ref.get()

                if buyers_data:
                    normal_buyers = {phone: info for phone, info in buyers_data.items() if
                                     not info.get("special_buyer", False)}

                    return {
                        'message': "Normal buyers retrieved successfully",
                        'status': '200',
                        'normal_buyers': normal_buyers
                    }
                else:
                    return {
                        'message': "No buyers found",
                        'status': '404',
                        'normal_buyers': {}
                    }

            except FirebaseError as e:
                print(f"Failed to retrieve normal buyers: {e}")
                return {'message': "Failed to retrieve normal buyers!"}
            except Exception as e:
                print(f"Unexpected error: {e}")
                return {'message': "Unexpected error occurred!"}
        else:
            return {'message': "Firebase initialization failed!"}

    def get_products_counts(self, user_phone):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Reference to the user's products
                products_ref = db.reference("Gerente").child("Company").child(user_phone).child('Products')
                products_data = products_ref.get()

                if products_data:
                    product_counts = {product_id: product_info.get("products_count", 0) for product_id, product_info in
                                      products_data.items()}

                    return {
                        'message': "Product counts retrieved successfully",
                        'status': '200',
                        'product_counts': product_counts
                    }
                else:
                    return {
                        'message': "No products found",
                        'status': '404',
                        'product_counts': {}
                    }

            except FirebaseError as e:
                print(f"Failed to retrieve product counts: {e}")
                return {'message': "Failed to retrieve product counts!"}
            except Exception as e:
                print(f"Unexpected error: {e}")
                return {'message': "Unexpected error occurred!"}
        else:
            return {'message': "Firebase initialization failed!"}

    def get_products_count(self, user_phone):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Reference to the user's products
                products_ref = db.reference("Gerente").child("Company").child(user_phone).child('Products')
                products_data = products_ref.get()

                if products_data:
                    product_details = {}
                    for product_id, product_info in products_data.items():
                        product_details[product_id] = {
                            "product_name": product_info.get("product_name", ""),
                            "product_price": product_info.get("product_price", 0),
                            "products_count": product_info.get("products_count", 0)
                        }

                    return {
                        'message': "Product details retrieved successfully",
                        'status': '200',
                        'product_details': product_details
                    }
                else:
                    return {
                        'message': "No products found",
                        'status': '404',
                        'product_details': {}
                    }

            except FirebaseError as e:
                print(f"Failed to retrieve product details: {e}")
                return {'message': "Failed to retrieve product details!"}
            except Exception as e:
                print(f"Unexpected error: {e}")
                return {'message': "Unexpected error occurred!"}
        else:
            return {'message': "Firebase initialization failed!"}

    def deliver_order(self, user_phone, order_id, distance_price):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Reference to the user's delivery orders
                delivery_orders_ref = db.reference("Gerente").child("DeliveryOrders").child(user_phone)
                delivery_orders_data = delivery_orders_ref.get()

                if delivery_orders_data:
                    for date, orders in delivery_orders_data.items():
                        if order_id in orders:
                            order_info = orders[order_id]

                            if order_info.get("status") == "delivered":
                                return {
                                    'message': f"Order {order_id} is already delivered",
                                    'status': '200',
                                    'order_id': order_id
                                }

                            # Calculate the bill payment
                            item_price = order_info.get("price", 0)
                            bill_payment = (int(item_price) + distance_price) * 0.10

                            # Update the order status to deliver
                            delivery_orders_ref.child(date).child(order_id).update({
                                "status": "delivered",
                                "bill_payment": bill_payment
                            })
                            # Update the user's bill payment
                            user_info_ref = db.reference("Gerente").child("Company").child(user_phone).child(
                                'Info_Company')
                            user_info = user_info_ref.get()

                            if user_info:
                                current_bill_payment = user_info.get("bill_payment", 0)
                                new_bill_payment = int(current_bill_payment) + int(bill_payment)
                                user_info_ref.update({
                                    "bill_payment": new_bill_payment
                                })

                            return {
                                'message': f"Order {order_id} marked as delivered and bill payment updated",
                                'status': '200',
                                'order_id': order_id,
                                'new_bill_payment': new_bill_payment
                            }

                    return {
                        'message': "Order not found",
                        'status': '404',
                        'order_id': order_id
                    }

            except FirebaseError as e:
                print(f"Failed to update order status: {e}")
                return {'message': "Failed to update order status!"}
            except Exception as e:
                print(f"Unexpected error: {e}")
                return {'message': "Unexpected error occurred!"}
        else:
            return {'message': "Firebase initialization failed!"}

    def add_products(self, product_name, phone, product_letter, price):
        self.initialize_firebase()
        if self.app_initialized:
            try:
                # Reference to the user's products
                products_ref = db.reference("Gerente").child("Company").child(phone).child('Products').child(
                    product_letter)

                # Set the product details
                products_ref.set({
                    "products_count": 0,
                    "product_letter": product_letter,
                    "product_price": price,
                    "product_name": product_name
                })

                # Update the total number of products in the company info
                company_info_ref = db.reference("Gerente").child("Company").child(phone).child('Info_Company')
                company_info = company_info_ref.get()

                if company_info:
                    total_products = company_info.get('Total_products', 0) + 1
                    company_info_ref.update({
                        "Total_products": total_products
                    })

                return {'message': "Product added successfully!", 'status': '200'}

            except FirebaseError as e:
                print(f"Failed to add product: {e}")
                return {'message': "Failed to add product!", 'status': '500'}
            except Exception as e:
                print(f"Unexpected error: {e}")
                return {'message': "Unexpected error occurred!", 'status': '500'}
        else:
            return {'message': "Firebase initialization failed!", 'status': '500'}

    def generate_item_id(self, product_letter):
        prefix = random.randint(0000, 9999)
        return f"{prefix}{product_letter}"

    def add_items(self, phone, product_letter, price, count):
        import firebase_admin
        firebase_admin._apps.clear()
        from firebase_admin import credentials, initialize_app, db
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
                initialize_app(cred, {'databaseURL': 'https://farmzon-abdcb.firebaseio.com/'})
                for i in range(count):
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

# x = FirebaseManager.get_products_count(FirebaseManager(), '0715700411')
# print(x)

# print(FirebaseManager.user_login(FirebaseManager(), '0715700411', '9060'))
# print(FirebaseManager.get_user_company_info(FirebaseManager(), '0715700411'))
# FirebaseManager.add_buyer(FirebaseManager(), '0715700411', '0788204328', 'Aqulline Mbuya', '7330341A', '1')


# print(FirebaseManager.initialize_delivery_order(FirebaseManager(), '0715700411', '2777963A', '0789934496', 'RayMundi',
# 'SomeHoes'))

# print(FirebaseManager.get_orders(FirebaseManager(), '0715700411'))
# print(FirebaseManager.get_orders_custom(FirebaseManager(), '0715700411', '2024-06-25'))
# print(FirebaseManager.get_orders_Interval(FirebaseManager(), '0715700411', 'Month'))

# x = FirebaseManager.get_buyers(FirebaseManager(), '0715700411')

# FirebaseManager.special_buyer(FirebaseManager(), '0715700411', '0654327335')
# x = FirebaseManager.get_special_buyers(FirebaseManager(), '0715700411')

# print(x)

# x = FirebaseManager.get_normal_buyers(FirebaseManager(), '0715700411')
# print(x)

# print(FirebaseManager.get_order_info(FirebaseManager(), '0715700411', 'order_1772470'))

# print(FirebaseManager.deliver_order(FirebaseManager(), '0715700411', 'order_1772470', 3000))
