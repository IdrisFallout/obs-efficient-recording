import time
from obswebsocket import obsws, requests
from dotenv import dotenv_values
from ctypes import Structure, windll, c_uint, sizeof, byref
import asyncio
import winrt.windows.media.control as wmc
import atexit

# import project variables
config = dotenv_values(".env")

# ******************************check inactivity************************************
def print_it():
    # threading.Timer(0.5, print_it).start()
    time.sleep(0.5)
    time_inactive = get_idle_duration()
    if time_inactive > 0.5 and not mediaIs("PLAYING"):
        client.call(requests.PauseRecording())
        # print("pausing")
    else:
        client.call(requests.ResumeRecording())
        # print("recording")
    print_it()


class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]


def get_idle_duration():
    last_input_info = LASTINPUTINFO()
    last_input_info.cbSize = sizeof(last_input_info)
    windll.user32.GetLastInputInfo(byref(last_input_info))
    millis = windll.kernel32.GetTickCount() - last_input_info.dwTime
    return millis / 1000.0

# ******************************end************************************

# *****************************check if music is playing****************
async def getMediaSession():
    sessions = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
    session = sessions.get_current_session()
    return session


def mediaIs(state):
    session = asyncio.run(getMediaSession())
    if session == None:
        return False
    return int(wmc.GlobalSystemMediaTransportControlsSessionPlaybackStatus[
                   state]) == session.get_playback_info().playback_status  # get media state enum and compare to current main media session state

# ******************************end**********************************

# on quit function to stop the recording and close the session
def quit():
    client.call(requests.StopRecording())
    client.disconnect()


print_it.count = 0
client = obsws(config["HOST"], config["PORT"], config["PASSWORD"])
client.connect()
if client.call(requests.GetRecordingStatus()).datain.get("isRecording"):
    print_it()

atexit.register(print, quit())
