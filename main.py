# Import Watcher class
from live_reloader import Watcher

# Create reloader
reloader = Watcher()

# Start watcher thread
reloader.start_watcher_thread()

from kivy.app import App
from kivy.core.window import Window
Window.left = Window.size[0] * 2.7
from kivy.uix.button import Button

class MainApp(App):
    title = "Live Reloader"
    def build(self):
        return Button(text = "Hello World 2")

MainApp().run()