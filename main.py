from kivy.base import EventLoop
from kivy.properties import NumericProperty, StringProperty, DictProperty, ListProperty
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy import utils
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.list import TwoLineAvatarListItem, IRightBodyTouch, TwoLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox

from database import FireBase

Window.keyboard_anim_args = {"d": .2, "t": "linear"}
Window.softinput_mode = "below_target"
Clock.max_iteration = 250

if utils.platform != 'android':
    Window.size = (412, 732)
else:
    from kvdroid.tools.contact import get_contact_details


class Contacts(MDCard):
    name = StringProperty("")
    phone = StringProperty("")
    image = StringProperty("")
    check = StringProperty("normal")
    icon = StringProperty("checkbox-blank-outline")


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    pass


class MainApp(MDApp):
    # app
    size_x, size_y = Window.size

    code = "3468546"

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

    def on_start(self):
        # self.add_contacts()
        # Clock.schedule_once(self.get_user, 1)
        pass

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
        self.user_info = FireBase.get_user(FireBase(), "0788204327")
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
               CONTACTS FETCHING
   """

    def contacts(self):
        name = get_contact_details("phone_book")  # gets a dictionary of all contact both contact name and phone mumbers
        get_contact_details("names")  # gets a list of all contact names
        get_contact_details("mobile_no")  # gets a list of all contact phone numbers

        self.contacts_dic = name
        self.add_contacts()

    def selection_contact(self, contact, value):
        print(value.id)
        if value.md_bg_color == [0.9294117647058824, 0.8627450980392157, 0.8235294117647058, 1.0] and contact not in self.selected_contacts:
            value.md_bg_color = "#CB997E"
            self.selected_contacts.append(contact)
            print(self.selected_contacts)
            self.add_contacts()
        else:
            self.selected_contacts.remove(contact)
            print(self.selected_contacts)
            value.md_bg_color = "#EDDCD2"
            self.add_contacts()

    search_count = NumericProperty(0)

    def search_contacts(self, text):
        self.root.ids.contact.data = {}
        self.search_count = 0
        print(text)
        for x, y in self.contacts_dic.items():

            if text.lower() in x.lower():
                self.search_count += 1
                if self.search_count <= 3:
                    self.root.ids.contact.data.append(
                        {
                            "viewclass": "Contacts",
                            "name": x,
                            "phone": y[0],
                            "icon": "checkbox-blank-outline",
                            "image": f"https://storage.googleapis.com/farmzon-abdcb.appspot.com/Letters/{x[0].upper()}",
                            "id": str(x.strip())
                        }
                    )


    def add_contacts(self):
        self.screen_capture("contacts")
        self.root.ids.contact.data = {}
        for x, y in self.contacts_dic.items():
            self.root.ids.contact.data.append(
                {
                    "viewclass": "Contacts",
                    "name": x,
                    "phone": y[0],
                    "icon": "check",
                    "image": f"https://storage.googleapis.com/farmzon-abdcb.appspot.com/Letters/{x[0].upper()}",
                    "id": str(x.strip())
                }
            )

    def request_android_permissions(self):
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
