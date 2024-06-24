import re
import threading

from kivy.base import EventLoop
from kivy.properties import NumericProperty, StringProperty, DictProperty, ListProperty, BooleanProperty
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy import utils
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.list import IRightBodyTouch, TwoLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField

from database import FireBase as FB

Window.keyboard_anim_args = {"d": .2, "t": "linear"}
Window.softinput_mode = "below_target"
Clock.max_iteration = 250

if utils.platform != 'android':
    Window.size = (412, 732)
else:
    from kvdroid.tools.contact import get_contact_details


class Spin(MDBoxLayout):
    pass


class Buyer(MDCard):
    name = StringProperty("")
    icon = StringProperty("")


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

    print("===========", size_x, size_y, "============")
    code = "3468546"
    sms_sent = StringProperty(
        "Aqulline mteja wa Byney_Fashion tunakusalimu, wewe kama mteja wetu pendwa ulionunua kwetu zaidi ya mara 5 Byner_Fashion inapenda kukufahamisha kuhusu mzigo mpya ulioningia leo jioni tembelea ukurasa wetu wa instagram @byner_fashion")

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
    total_earnings = StringProperty("0")
    total_sms = StringProperty("0")
    total_buyers = StringProperty("0")
    today_transactions = StringProperty("0")
    net_earnings = StringProperty("0")

    # USER INFO
    user_name = StringProperty("")
    user_phone = StringProperty("")
    user_info = DictProperty({})

    # screen
    screens = ['home']
    screens_size = NumericProperty(len(screens) - 1)
    current = StringProperty(screens[len(screens) - 1])

    # Buyers
    USer_Buyers = DictProperty({})

    def on_start(self):
        # self.add_contacts()
        # Clock.schedule_once(self.get_user, 1)
        self.keyboard_hooker()
        self.add_contacts()
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

    def go_premium(self, email, phone):
        from payment import pesapal as PS

        PS.pay_premium(email=email, phone=phone)

    """

                BUYERS END

    """

    """
               CONTACTS FETCHING
   """

    def contacts(self):
        self.screen_capture("contacts")
        name = get_contact_details("phone_book")
        det = get_contact_details("names")
        get_contact_details("mobile_no")

        self.contacts_dic = name
        self.add_contacts()

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

    def search_contacts(self, text):
        self.root.ids.contact.data = {}
        print(text)
        index = 0
        for x, y in self.contacts_dic.items():

            if text.lower() in x.lower():
                self.root.ids.contact.data.append(
                    {
                        "viewclass": "Contacts",
                        "name": x,
                        "phone": y[0],
                        "icon": "checkbox-blank-outline",
                        "image": f"https://storage.googleapis.com/farmzon-abdcb.appspot.com/Letters/{x[0].upper()}",
                        "id": str(x.strip()),
                        "selected": False,
                    }
                )
            index += 1

    def add_contacts(self):
        # self.screen_capture("contacts")
        self.root.ids.contact.data = {}
        index = 0
        for x, y in self.contacts_dic.items():
            self.root.ids.contact.data.append(
                {
                    "viewclass": "Contacts",
                    "name": x,
                    "phone": y[0],
                    "icon": "check",
                    "image": f"https://storage.googleapis.com/farmzon-abdcb.appspot.com/Letters/{x[0].upper()}",
                    "id": str(x.strip()),
                    "selected": False,
                    "data_index": index
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

    def build(self):
        self.theme_cls.material_style = "M3"


MainApp().run()
