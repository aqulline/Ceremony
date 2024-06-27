import json
# from firebase_db import FireBase as FB
from beem import sms as SM


class Database:
    data_file_name = ""
    bus_name = ""
    bus_id = ""

    def write(self, data):
        with open(self.data_file_name, "w") as file:
            initial_data = json.dumps(data, indent=4)
            file.write(initial_data)

    def load(self):
        with open(self.data_file_name, "r") as file:
            initial_data = json.load(file)
        return initial_data

    def update_data(self, data):
        initial_data = self.load()
        final_data = data
        initial_data.update(final_data)
        self.write(initial_data)

    def write_sms(self, sms_type, data):
        self.data_file_name = "database/message.json"
        data = {sms_type: data}
        self.update_data(data)

    def load_sms(self):
        self.data_file_name = "database/message.json"

        return self.load()
