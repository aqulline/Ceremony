from kivy.clock import mainthread
from kivy.properties import StringProperty
from plyer import gps
from kivy.utils import platform


class Gps:
    gps_location = ""
    gps_status = "Click Start to get GPS location updates"

    def request_android_permissions(self):
        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION], callback)

    def gps_init(self):
        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)

        except NotImplementedError:
            import traceback
            traceback.print_exc()
            gps_status = 'GPS is not implemented for your platform'

            return gps_status

        if platform == "android":
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()

    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)
        self.get_lat_lon()
    def stop(self):
        gps.stop()

    @mainthread
    def on_location(self, **kwargs):
        Gps.gps_location = '\n'.join([
            '{}={}'.format(k, v) for k, v in kwargs.items()])

        print(f'this "{kwargs}" data')



    @mainthread
    def on_status(self, stype, status):
        Gps.gps_status = 'type={}\n{}'.format(stype, status)

        print(Gps.gps_status)

    def get_lat_lon(self):

        return Gps.gps_location


