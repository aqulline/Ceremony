from jnius import autoclass
from jnius import cast
from android.runnable import run_on_ui_thread
from kivy.clock import Clock

# "android.permission.CALL_PHONE"

class Actions:
    url = ""
    webview = None

    def call(self, num):
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        intent = Intent(Intent.ACTION_CALL)
        intent.setData(Uri.parse("tel:" + num))
        currentActivity = cast('android.app.Activity',
                               PythonActivity.mActivity)
        currentActivity.startActivity(intent)


    @run_on_ui_thread
    def create_webview(self, **kwargs):
        WebView = autoclass('android.webkit.WebView')
        WebViewClient = autoclass('android.webkit.WebViewClient')
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        Actions.webview = WebView(activity)
        settings = Actions.webview.getSettings()
        settings.setJavaScriptEnabled(True)
        settings.setUseWideViewPort(True)
        settings.setLoadWithOverviewMode(True)
        settings.setSupportZoom(True)
        settings.setBuiltInZoomControls(True)

        wvc = WebViewClient();
        Actions.webview.setWebViewClient(wvc);
        activity.setContentView(Actions.webview)
        Actions.webview.loadUrl(Actions.url)

    @run_on_ui_thread
    def key_back_handler(self, *args):
        if Actions.webview:
            if Actions.webview.canGoBack():
                Actions.webview.goBack()
            else:
                print("step 2")
                Clock.schedule_once(self.detach_webview, 0)

    @run_on_ui_thread
    def detach_webview(self, *args):
        if Actions.webview:
            print("step 3")
            Actions.webview.loadUrl("about:blank")
            Actions.webview.clearHistory()  # refer to android webview api
            Actions.webview.clearCache(True)
            Actions.webview.clearFormData()
            Actions.webview.freeMemory()
            # self.webview.pauseTimers()


    def quit_screens(self):
        print("step 1")
        if Actions.webview:
            print("step 1.1")
            Actions.key_back_handler()

            return True
        else:

            return False
