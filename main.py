import re
import threading
import webbrowser
from datetime import datetime

from kivy.animation import Animation
from kivy.base import EventLoop
from kivy.properties import NumericProperty, StringProperty, DictProperty, ListProperty, BooleanProperty
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy import utils
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.chip import MDChip
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import IRightBodyTouch, TwoLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField

from database_local import Database as DB
from database import FireBase as FB
from database_fetch import FirebaseManager as FM
from payment import pesapal as PP
from beem import sms as SMS

from kivyauth.google_auth import initialize_google, login_google, logout_google

Window.keyboard_anim_args = {"d": .2, "t": "linear"}
Window.softinput_mode = "below_target"
Clock.max_iteration = 250

if utils.platform != 'android':
    Window.size = (412, 732)
else:
    from kvdroid.tools.contact import get_contact_details


class OrderInfo(MDBoxLayout):
    order_id = StringProperty("")
    deliver = StringProperty("")
    order_date = StringProperty("")


class Spin(MDBoxLayout):
    pass


class ProductInfo(MDBoxLayout):
    name = StringProperty("")
    price = StringProperty("")
    letter = StringProperty("")
    count = StringProperty("")


class ItemInfo(MDBoxLayout):
    pass


class Buyer(MDCard):
    name = StringProperty("")
    icon = StringProperty("")


class MyChip(MDChip):
    icon_check_color = (0, 0, 0, 1)
    text_color = (0, 0, 0, 0.5)
    _no_ripple_effect = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(active=self.set_chip_bg_color)
        self.bind(active=self.set_chip_text_color)

    def set_chip_bg_color(self, instance_chip, active_value: int):
        '''
        Will be called every time the chip is activated/deactivated.
        Sets the background color of the chip.
        '''

        self.md_bg_color = (
            "#2e4052"
            if active_value
            else (
                self.theme_cls.bg_darkest
                if self.theme_cls.theme_style == "Light"
                else (
                    self.theme_cls.bg_light
                    if not self.disabled
                    else self.theme_cls.disabled_hint_text_color
                )
            )
        )

    def set_chip_text_color(self, instance_chip, active_value: int):
        Animation(
            color=(1, 1, 1, 1) if active_value else (0, 0, 0, 0.5), d=0.2
        ).start(self.ids.label)


class Contacts(TwoLineAvatarIconListItem):
    name = StringProperty("")
    phone = StringProperty("")
    image = StringProperty("")
    check = StringProperty("normal")
    icon = StringProperty("checkbox-blank-outline")

    selected = BooleanProperty(False)  # is this checkbox down
    data_index = NumericProperty(-1)  # index into the RV data

    def state_changed(self):
        self.selected = self.ids.lcb.state == 'down'  # set the selected property

        print(self.data_index)
        # save the change to the data
        rv = MDApp.get_running_app().root.ids.contact
        rv.data[self.data_index]['selected'] = self.selected

class ProductLetter(MDTextField):
    # Restrict input to one uppercase letter
    text = StringProperty()

    def insert_text(self, substring, from_undo=False):
        # Only allow letters and limit to one character
        substring = re.sub('[^a-zA-Z]', '', substring)
        if len(substring) > 0:
            substring = substring.upper()  # Convert to uppercase
        if len(self.text) + len(substring) > 1:
            substring = ''  # Prevent inserting more than one letter
        super().insert_text(substring, from_undo=from_undo)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        # Handle backspace to allow deletion of the character
        if keycode[1] == 'backspace':
            self.text = ""
        return super().keyboard_on_key_down(window, keycode, text, modifiers)

class NumberOnlyField(MDTextField):
    pat = re.compile('[^0-9]')

    input_type = "number"

    def insert_text(self, substring, from_undo=False):

        pat = self.pat

        if "." in self.text:
            s = re.sub(pat, "", substring)

        else:
            s = ".".join([re.sub(pat, "", s) for s in substring.split(".", 1)])

        return super(NumberOnlyField, self).insert_text(s, from_undo=from_undo)


class Buyers(TwoLineAvatarIconListItem):
    name = StringProperty("")
    phone = StringProperty("")
    image = StringProperty("")


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    pass


class MainApp(MDApp):
    # app
    size_x, size_y = Window.size
    dialog_spin = None
    is_admin = False
    admin_pos_x = NumericProperty(.5)
    admin_pos_y = NumericProperty(.04)
    selected_time_frame = "Today"

    print("===========", size_x, size_y, "============")
    code = "3468546"
    sms_type = StringProperty('')
    sms_is_special = BooleanProperty(False)
    sms_sent = StringProperty(
        "Aqulline mteja wa Byney_Fashion tunakusalimu, wewe kama mteja wetu pendwa ulionunua kwetu zaidi ya mara 5 "
        "Byner_Fashion inapenda kukufahamisha kuhusu mzigo mpya ulioningia leo jioni tembelea ukurasa wetu wa "
        "instagram @byner_fashion")

    contacts_dic = DictProperty(
        {'Abob': ['+255626240705'], 'Adam': ['0689477825'], 'Ahmed': ['+255674738796'],
         'Aisha': ['+255719744631'], 'Alex': ['+255711311696'], 'Alice Nds': ['+255684449934'],
         'Aln': ['+255743913002'], 'Alp': ['0621491272'], 'Alp Mam': ['+255763548722'],
         'Alphaxad': ['+255699220818', '0714069014'], 'Alyc': ['0657555698'], 'Amani': ['0672700204'],
         'Andrew Mosses': ['0655584336'], 'Angel ❣️': ['0684573258'],
         'Aqulline Mbuya': ['+255656933275', '0715700411', '0786857974']})

    # Contacts
    selected_contacts = ListProperty([])

    # Transactions
    total_bill = StringProperty('0')
    total_deliveries = StringProperty('0')
    total_buyers = StringProperty('0')
    total_orders = StringProperty('0')
    today_orders = StringProperty('0')
    today_deliveries = StringProperty('0')
    total_special = StringProperty('0')
    payment_check_event = None

    # USER INFO
    user_data = DictProperty({})
    user_name = StringProperty("0")
    user_phone = StringProperty("0")
    user_special_sms = StringProperty('0')
    user_sms = StringProperty('0')
    user_info = DictProperty({})
    user_image = StringProperty('0')
    user_products_counts = StringProperty('0')
    premium = False

    # PRODUCT INFO
    input_order = StringProperty("")
    product_id = StringProperty('-----')
    product_price = StringProperty('-----')
    customer_name = StringProperty('-----')
    customer_number = StringProperty('-----')
    delivery_Status = StringProperty('-----')
    status_color = StringProperty('#FFDBBB')#FFFFC5 #90EE90
    bill_payed = StringProperty('-----')

    # screen
    screens = ['home']
    screens_size = NumericProperty(len(screens) - 1)
    current = StringProperty(screens[len(screens) - 1])

    # Buyers
    USer_Buyers = DictProperty({})

    def on_start(self):
        self.keyboard_hooker()
        self.check_admin()
        if utils.platform == 'android':
            self.request_android_permissions()

    def keyboard_hooker(self, *args):
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def hook_keyboard(self, window, key, *largs):
        print(self.screens_size)
        if key == 27 and self.screens_size > 0:
            print(f"your were in {self.current}")
            last_screens = self.current
            self.screens.remove(last_screens)
            print(self.screens)
            self.screens_size = len(self.screens) - 1
            self.current = self.screens[len(self.screens) - 1]
            self.screen_capture(self.current)
            return True
        elif key == 27 and self.screens_size == 0:
            toast('Press Home button!')
            return True

    def spin_dialog(self):
        if not self.dialog_spin:
            self.dialog_spin = MDDialog(
                type="custom",
                auto_dismiss=False,
                size_hint=(.43, None),
                content_cls=Spin(),
            )
        self.dialog_spin.open()

    def add_comma(self, number):
        if number != '':
            number = str(number).replace(',', '')
            number = str(number).replace('.', '')
            number = int(number)
            return f'{number:,}'
        else:
            return ''

    def remove_comma(self, number):

        new_number = str(number).replace(',', '')

        return int(new_number)

    """
    
                ADMIN FUNCTIONS
    
    """

    def check_admin(self):
        if not self.is_admin:
            self.admin_pos_x = 11
            self.admin_pos_y = 11

    def getInfo_opt(self):
        self.spin_dialog()

        thr = threading.Thread(target=self.getInfo)
        thr.start()

    def getInfo(self):
        datas = FM.get_order_info(FM(), self.user_phone, self.input_order)
        print(datas)

        if datas['status'] == '200':
            data = datas['order_info']
            self.product_id = data['item_id']
            self.product_price = self.add_comma(data['price'])
            self.customer_name = data['buyer_name']
            self.customer_number = data['buyer_phone']
            self.bill_payed = self.add_comma(data['bill_payment'])
            self.delivery_Status = data['status']
            Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)
        else:
            Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)
            Clock.schedule_once(lambda dt: toast(datas['message']), 0)



    def calculate_bill(self):
        # Calculate the bill payment
        item_price = self.product_price
        bill_payment = (int(self.remove_comma(item_price)) + self.remove_comma(
            self.root.ids.logistic_price.text)) * 0.10
        print(bill_payment)

    def deliver_opt(self):
        self.spin_dialog()

        thr = threading.Thread(target=self.delivery)
        thr.start()

    def delivery(self):
        deliver = FM.deliver_order(FM(), self.user_phone, self.root.ids.item_id.text,
                                   self.remove_comma(self.root.ids.logistic_price.text))
        Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)
        Clock.schedule_once(lambda dt: toast(deliver['message']), 0)

    def removes_marks_all_chips(self):
        for instance_chip in self.root.ids.chip_box.children:
            if instance_chip.active:
                instance_chip.active = False

    def get_orders_opt(self):
        self.spin_dialog()

        thr = threading.Thread(target=self.get_orders)
        thr.start()

    def get_orders(self):
        if self.selected_time_frame == "Today":
            self.root.ids.select_today.active = True
        if self.selected_time_frame == "Week":
            self.root.ids.select_week.active = True
        if self.selected_time_frame == "Month":
            self.root.ids.select_month.active = True
        data = FM.get_orders_Interval(FM(), self.user_phone, self.selected_time_frame)
        self.order_list(data)
        Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)
        Clock.schedule_once(lambda dt: toast(data['message']), 0)


    """
    
                END ADMIN FUNCTION
    
    """

    """
            USER PREMIUM
    
    """

    def go_premium_opt(self):
        self.spin_dialog()

        thr = threading.Thread(target=self.go_premium)
        thr.start()

    def go_premium(self):

        if self.user_data['user_info']['direct_url'] == '':
            email = self.root.ids.pcustomer_name.text
            phone = self.root.ids.pcustomer_number.text

            from payment import pesapal as PS

            payment_data = PS.pay_premium(email=email, phone=phone)

            FM.set_payment(FM(), payment_data['order_tracking_id'], payment_data['redirect_url'], self.user_phone)

            Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)
            Clock.schedule_once(lambda dt: toast('Waiting for payment'), 0)
            self.payment_check_event = Clock.schedule_interval(
                lambda x: self.check_payment_int(phone, payment_data['order_tracking_id']), 5)
        else:
            webbrowser.open(self.user_data['user_info']['direct_url'])
            Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)

    def check_payment_int(self, phone, tracking_id):
        data = FM.check_payment(FM(), tracking_id, phone, self.user_name, self.user_phone)

        if data['status'] == '200':
            Clock.unschedule(self.payment_check_event)

    def check_premium(self):
        pay_token = self.user_data['user_info']['payment_token']
        print(self.user_data['user_info'])
        if PP.get_payment_status(pay_token)['status_code'] == 1 and self.check_subscription_exp(self.user_data['user_info']['end_of_subscription'], str(datetime.now().date())):
            self.premium = True

    def check_subscription_exp(self, exp_date, current_date):
        # Example date format: 'YYYY-MM-DD'
        exp_date = datetime.strptime(exp_date, '%Y-%m-%d')
        current_date = datetime.strptime(current_date, '%Y-%m-%d')

        if current_date > exp_date:
            return False
        else:
            return True

    def is_premium_screen(self):
        if self.premium:
            self.screen_capture('premium1')
        else:
            self.screen_capture('premium')

    def edit_sms(self, sms):
        DB.write_sms(DB(), self.sms_type, sms)
        self.user_special_sms = DB.load_sms(DB())['special_sms']
        self.user_sms = DB.load_sms(DB())['sms']

        toast('Edited success!')

    def send_sms_opt(self):
        self.spin_dialog()

        thr = threading.Thread(target=self.send_sms)
        thr.start()

    def send_sms(self):
        if self.sms_is_special:
            buyers = FM.get_special_buyers(FM(), self.user_phone)
            types = 'special_buyers'
        else:
            buyers = FM.get_normal_buyers(FM(), self.user_phone)
            types = 'normal_buyers'

        buyer = buyers[types]

        print(buyer)
        for i, j in buyer.items():
            SMS.send_sms(i, self.user_special_sms)

        SMS.send_sms(self.user_phone, self.user_special_sms)

        Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)
        Clock.schedule_once(lambda dt: toast('Message sends successfully'), 0)

    def send_sms_ind_opt(self):
        self.spin_dialog()

        thr = threading.Thread(target=self.send_sms_ind)
        thr.start()

    def send_sms_ind(self):
        for i in self.selected_contacts:
            for y, x in i.items():
                SMS.send_sms(x, self.user_special_sms)
        Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)
        Clock.schedule_once(lambda dt: toast('Message sends successfully'), 0)

    def capture_user(self):
        if len(self.selected_contacts) == 1:
            data = self.selected_contacts[0]
            for i, y in data.items():
                self.root.ids.customer_name.text = i
                self.root.ids.customer_number.text = y
                self.screen_capture("sell")
        else:
            toast("Select only one to send order to!")

    """
    
            END USER PREMIUM
    
    """

    """
                USER INFO
    
    """

    def get_user(self, *args):
        self.user_info = FB.get_user(FB(), "0788204327")
        company_info = self.user_info["Info_Company"]
        user_info = self.user_info["User_Info"]

        # user
        self.user_name = user_info["user_name"]
        self.user_phone = user_info["user_phone"]

        # company
        self.net_earnings = str(company_info["Net_earnings"])
        self.today_transactions = str(company_info["Today_transactions"])
        self.total_earnings = str(company_info["Total_earnings"])
        self.total_sms = str(company_info["Total_sms"])
        self.total_buyers = str(company_info["Total_buyers"])

    def user_login_opt(self):
        self.spin_dialog()

        thr = threading.Thread(target=self.user_login)
        thr.start()

    def user_login(self):

        number = self.root.ids.user_number.text
        password = self.root.ids.password.text

        if number == "":
            Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)
            Clock.schedule_once(lambda dt: toast("Number Empty!"), 0)
        if password == "":
            Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)
            Clock.schedule_once(lambda dt: toast("Password Empty!"), 0)

        data = FM.user_login(FM(), number, password)

        status = data['status']

        if status == '200':
            self.user_phone = number

            Clock.schedule_once(lambda dt: self.screen_capture("home"), 0)

        Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)
        Clock.schedule_once(lambda dt: toast(data['message']), 0)
        Clock.schedule_once(lambda dt: self.refresh_opt(), 0)

    def refresh_opt(self):
        thr = threading.Thread(target=self.refresh_data)
        thr.start()

    def refresh_data(self):
        self.user_data = FM.get_user_company_info(FM(), self.user_phone)
        self.total_bill = self.add_comma(self.user_data['company_info']['Total_income'])
        self.today_orders = self.add_comma(self.user_data['company_info']['Today_orders'])
        self.today_deliveries = self.add_comma(self.user_data['company_info']['Today_delivered'])
        self.user_phone = self.user_data['user_info']['user_phone']
        self.user_name = self.user_data['user_info']['user_name']
        self.user_image = f"https://storage.googleapis.com/farmzon-abdcb.appspot.com/Letters/{self.user_name[0]}"
        self.total_special = self.add_comma(self.user_data['company_info']['Special_buyers'])
        self.total_buyers = self.add_comma(
            self.user_data['company_info']['Total_buyers'] - self.user_data['company_info']['Special_buyers'])
        self.user_special_sms = DB.load_sms(DB())['special_sms']
        self.user_sms = DB.load_sms(DB())['sms']
        self.check_premium()
        self.user_products_counts = str(FM.get_products_counts(FM(), self.user_phone)['product_counts'].__len__())
        Clock.schedule_once(lambda dt: self.add_contacts(), 0)
        Clock.schedule_once(lambda dt: self.add_products(), 0)

    def set_order_opt(self):
        self.spin_dialog()

        thr = threading.Thread(target=self.set_order)
        thr.start()

    def set_order(self):
        customer_number = self.root.ids.customer_number.text
        customer_name = self.root.ids.customer_name.text
        product_id = self.root.ids.product_id.text

        print(customer_number, product_id, self.user_phone, customer_name, self.user_name)
        order_init = FM.initialize_delivery_order(FM(), self.user_phone, product_id, customer_number, customer_name,
                                                  self.user_name)
        self.refresh_data()
        Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)
        Clock.schedule_once(lambda dt: toast(order_init['message']), 0)

    def add_product_opt(self):
        self.spin_dialog()

        thr = threading.Thread(target=self.add_product)
        thr.start()

    def add_product(self):
        product_name = self.root.ids.product_name.text
        product_letter = self.root.ids.product_letter.text
        product_price = self.root.ids.product_price.text
        data = FM.add_products(FM(), product_name, self.user_phone, product_letter, product_price)
        print(data)
        if data['status'] == '200':
            self.refresh_data()
            Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)
            Clock.schedule_once(lambda dt: self.screen_capture("products"), 0)
            Clock.schedule_once(lambda dt: toast(data['message']), 0)
        else:
            Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)
            Clock.schedule_once(lambda dt: toast(data['message']), 0)

    def capp_limit(self, text):
        import string
        if str(text) in string.punctuation:
            return ''
        if str(text).isnumeric():
            return ''
        if len(text) == 0:
            return ''
        if len(text) == 1:
            return str(text).capitalize()
        else:
            return str(text[0]).capitalize()




    """
            END USER iNFO
    
    """
    """
    
            BUYERS FUNCTIONS
    
    """

    contact_count = StringProperty("0")

    def add_from_contact(self):
        self.screen_capture("home")
        for i in self.selected_contacts:
            self.USer_Buyers = {**self.USer_Buyers, **i}
        print(self.USer_Buyers)
        self.display_buyer()
        thread = threading.Thread(self.add_buyers())
        thread.start()

    def check_buyers(self):
        if "Buyers" in self.user_info:
            self.USer_Buyers = self.user_info["Buyers"]
            self.display_buyer()
        else:
            print("No")

    def add_buyers(self):
        print("reaches!!!!!!!!!!!!!!!!!!!!!!!!!")
        FB.add_buyer(FB(), self.USer_Buyers, "0788204327")

    def display_buyer(self):
        self.root.ids.buyer.data = {}
        for x, y in self.USer_Buyers.items():
            self.root.ids.buyer.data.append(
                {
                    "viewclass": "Buyers",
                    "name": x,
                    "phone": y,
                    "icon": "check",
                    "image": f"https://storage.googleapis.com/farmzon-abdcb.appspot.com/Letters/{x[0].upper()}",
                    "id": str(x.strip()),
                }
            )

    """
    
                BUYERS END
    
    """

    """
               CONTACTS FETCHING
   """

    def legalize_number(self, phone):
        if "+255" in phone:
            print(True)
            phone = phone.replace("+255", "0")
            return phone
        else:
            return phone

    def action(self, instance, pdata, name):
        print(instance.state)
        pdata = self.legalize_number(pdata)
        if instance.state == "down":
            data = {name: pdata}
            self.selected_contacts.append(data)
            print(self.selected_contacts)
            self.contact_count = str(int(self.contact_count) + 1)
        else:
            data = {name: pdata}
            self.selected_contacts.remove(data)
            print(self.selected_contacts)
            self.contact_count = str(int(self.contact_count) - 1)

    def add_contacts(self):
        # self.screen_capture("contacts")
        self.root.ids.contact.data = {}
        index = 0
        data = FM.get_buyers(FM(), self.user_phone)
        for x in data:
            self.root.ids.contact.data.append(
                {
                    "viewclass": "Contacts",
                    "name": x['buyer_name'],
                    "phone": x['buyer_phone'],
                    "icon": "check",
                    "image": f"https://storage.googleapis.com/farmzon-abdcb.appspot.com/Letters/{x['buyer_name'][0].upper()}",
                    "id": x['buyer_phone'],
                    "selected": False,
                    "data_index": index
                }
            )
            index += 1

    def order_list(self, data):
        # self.screen_capture("contacts")
        self.root.ids.order_list.data = {}
        orders = data['orders']
        for x in orders:
            self.root.ids.order_list.data.append(
                {
                    "viewclass": "OrderInfo",
                    "order_id": x['order_id'],
                    "order_date": x['order_date'],
                    "deliver": x['order_info']['status'],
                }
            )

    def add_products(self):
        # self.screen_capture("contacts")
        self.root.ids.products.data = {}
        index = 0
        data = FM.get_products_count(FM(), self.user_phone)['product_details']
        for x, j in data.items():
            self.root.ids.products.data.append(
                {
                    "viewclass": "ProductInfo",
                    "name": j['product_name'],
                    'price': self.add_comma(j['product_price']),
                    'letter': x,
                    'count': self.add_comma(j['products_count'])
                }
            )
            index += 1

    def request_android_permissions(self):
        if utils.platform == 'android':
            from android.permissions import request_permissions, Permission

            def callback(permissions, results):
                if all([res for res in results]):
                    print("callback. All permissions granted.")
                else:
                    print("callback. Some permissions refused.")

            request_permissions([Permission.READ_CONTACTS, Permission.WRITE_CONTACTS, ], callback)

    """
            END FETCHING
    """

    def screen_capture(self, screen):
        sm = self.root
        sm.current = screen
        if screen in self.screens:
            pass
        else:
            self.screens.append(screen)
        print(self.screens)
        self.screens_size = len(self.screens) - 1
        self.current = self.screens[len(self.screens) - 1]
        print(f'size {self.screens_size}')
        print(f'current screen {screen}')

    def screen_leave(self):
        print(f"your were in {self.current}")
        last_screens = self.current
        self.screens.remove(last_screens)
        print(self.screens)
        self.screens_size = len(self.screens) - 1
        self.current = self.screens[len(self.screens) - 1]
        self.screen_capture(self.current)

    def after_login(self, *args):
        print("Hurray")
        self.screen_capture("home")
        print(*args)

    def erro_login(self, *args):
        print("Booo!!")

    def login(self):
        login_google()

    def logout(self):
        logout_google(self.erro_login)

#920982026239-k6p67d3k124npliloa0kle2v84lgorln.apps.googleusercontent.com
    def build(self):
        initialize_google(self.after_login, self.erro_login, client_id='240132364342-bpp6asa19iec10cvl67f6vujghin6e44.apps.googleusercontent.com', client_secret="vAoceO8PdEh84fD81YsXs9tq")
        self.theme_cls.material_style = "M3"


MainApp().run()
