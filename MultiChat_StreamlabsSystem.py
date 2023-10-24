import codecs
import json
import os.path
import sys
import time
import webbrowser
import clr
import System
from System.Reflection import *

clr.AddReference([asbly for asbly in System.AppDomain.CurrentDomain.GetAssemblies() if "AnkhBotR2" in str(asbly)][0])
import AnkhBotR2

sys.platform = "win32"
sys.path.append(os.path.dirname(__file__))
from multichat_daemon import common_types
import subprocess

ScriptName = "MultiChat"
Description = "Read Twitch chat in your bot!"
Creator = "TMHK"
Version = "0.1a"
Website = None

Parent = None


class Settings(object):
    __slots__ = ("refresh_interval", "python", "token", "refresh_token")

    def __init__(self):
        self.refresh_interval = 1000
        self.python = "%LOCALAPPDATA%\Programs\Python\Python310\pythonw.exe"
        self.token = ""
        self.refresh_token = ""

    def load_data(self, data):
        for k, v in data.items():
            if k in self.__slots__:
                setattr(self, k, v)

    def load(self):
        fp = os.path.join(os.path.dirname(__file__), "settings.json")
        if not os.path.exists(fp):
            return

        with codecs.open(fp, encoding="utf-8-sig") as f:
            data = json.load(f)

        self.load_data(data)

    def save(self):
        fp = os.path.join(os.path.dirname(__file__), "settings.json")
        with codecs.open(fp, mode="w", encoding="utf-8-sig") as f:
            json.dump({k: getattr(self, k) for k in self.__slots__}, f)


settings = Settings()
proc = None
BASE_URL = "http://127.0.0.1:4835/"
last_check = time.time()


def Init():
    global proc
    settings.load()
    path = settings.python.replace("%LOCALAPPDATA%", os.environ["LOCALAPPDATA"]).replace(
        "%USERPROFILE%", os.environ["USERPROFILE"]
    )
    proc = subprocess.Popen(args=[path, "-m", "multichat_daemon"], cwd=os.path.abspath(os.path.dirname(__file__)))

    if settings.token and settings.refresh_token:
        time.sleep(0.1)  # give it a hot sec to start
        Parent.GetRequest(BASE_URL + "token?token={}&refresh={}".format(settings.token, settings.refresh_token), {})


def Execute():
    pass


def Tick():
    global last_check
    now = time.time()

    if now - last_check > (settings.refresh_interval / 1000):
        last_check = now
        data = json.loads(Parent.GetRequest(BASE_URL + "updates", {}))

        if "response" in data:
            unwrapped = json.loads(data["response"])
            for event in unwrapped:
                if event["type"] == common_types.EventTypes.MESSAGE:
                    handle_message(event)

                elif event["type"] == common_types.EventTypes.TOKEN_UPDATE:
                    handle_token_update(event)

                else:
                    Parent.Log(ScriptName, "Received unknown event {} from the daemon.".format(event["type"]))


def Unload():
    Parent.PostRequest(BASE_URL + "shutdown", {}, {}, True)


def ReloadSettings(data):
    data = json.loads(data)
    settings.load_data(data)

    Unload()
    time.sleep(0.3)
    Init()


def ScriptToggled(state):
    if state is False:
        Unload()

    elif state is True and last_check + 0.1 < time.time():
        Init()


def handle_message(message):
    fmt = "[TWITCH] {author_name}: {content}".format(**message)
    print_server_message(fmt)


def handle_token_update(message):
    settings.token = message["token"]
    settings.refresh_token = message["refresh_token"]

    settings.save()


def print_server_message(msg):
    handler = AnkhBotR2.Managers.GlobalManager.Instance.SystemHandler.StreamerClient
    handler.PrintServerMessage(msg)
    handler.WriteTextToUI()


def button_generate_token():
    webbrowser.open(BASE_URL + "token")

def button_open_readme():
    webbrowser.open("https://github.com/IAmTomahawkx/slcb-multichat/blob/master/README.md")
