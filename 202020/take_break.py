import datetime
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import requests
from bs4 import BeautifulSoup as bs4
import pandas as pd
import random
import pyttsx3
import re
import csv
import pyaudio
import pyautogui
import threading
import win32gui
import winsound
import screen_brightness_control as sbc
content=[]
alpha_list=[]
topics=[]
url="https://medlineplus.gov/encyclopedia.html"
def make_list():
    print("makelist report: started")
    try:
        response=requests.get(url)
    except:
        return False
    html=bs4(response.text,"html.parser")
    for alp in html.find_all("ul")[3].find_all("li"):
        alpha_list.append(alp.a['href'])
    print("makelist report: list made")
def refill_content(num=5):
    print("refill report: refill started")
    if not alpha_list:
        if make_list() is False:
            print("refill report: make list failed")
            return False
    print("refill report: list made")
    for i in range(num):
        url="https://medlineplus.gov/"+str(random.choice(alpha_list))
        try:
            response=requests.get(url)
        except:
            return False
        print("refill report: response received "+str(i+1))
        html=bs4(response.text,"html.parser")
        for topic in html.find_all('ul')[4]:
            topics.append(topic.a['href'])
        url="https://medlineplus.gov/ency/"+str(random.choice(topics))
        response=requests.get(url)
        html=bs4(response.text,"html.parser")
        content.append([re.sub(r'\s+', ' ', html.find('div',class_="page-title").text)  ,
                        re.sub(r'\s+', ' ', html.find('div',id="ency_summary"  ).text)  ])
    with open(r"C:\Users\user\AppData\Local\Programs\Python\Python312\myScripts\202020\database.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(content)
    print("refill report: refill made") 
def speak_two(content):
    text = pyttsx3.init()
    voices=text.getProperty('voices')
    text.setProperty('voice',voices[0].id)
    text.setProperty('rate',150)
    text.say(content[0])
    text.runAndWait()
    text.setProperty('voice',voices[1].id)
    text.setProperty('rate',170)
    print(content[1])
    print(f"len: {str(len(content[1]))}")
    text.say(content[1])
    text.runAndWait()
def speak_null():
    time.sleep(3)
    text = pyttsx3.init()
    voices=text.getProperty('voices')
    text.setProperty('voice',voices[0].id)
    text.setProperty('rate',150)
    text.say("failed to fetch information")
    text.runAndWait()
def get_system_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_object = cast(interface, POINTER(IAudioEndpointVolume))
    return volume_object.GetMasterVolumeLevelScalar()
def set_system_volume(volume):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_object = cast(interface, POINTER(IAudioEndpointVolume))
    volume_object.SetMasterVolumeLevelScalar(volume, None)
def get_content():
    limit=300
    data=[]
    with open(r"C:\Users\user\AppData\Local\Programs\Python\Python312\myScripts\202020\database.csv", 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(tuple(row))
    try:
        content = data.pop()
    except IndexError:
        #speak_null()
        try:
            #refill_content()
            pass
        except Exception as e:
            print(e)
        return None
    with open(r"C:\Users\user\AppData\Local\Programs\Python\Python312\myScripts\202020\database.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
    if len(content[1])>limit:
        new_content=content[1][0:limit]
        new_content = new_content[:limit-new_content[::-1].find('.')]
    else:
        new_content=content[1]
    return content[0],new_content
def is_system_audio_set():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    if info.get('deviceCount') == 4:
        return True
##    for i in range(num_devices):
##        device_info = p.get_device_info_by_host_api_device_index(0, i)
##        print(f"{device_info.get('name')}")
    p.terminate()
def interval():
    winsound.Beep(1000,200)
    winsound.Beep(1000,200)
    current_brightness = sbc.get_brightness()
    sbc.set_brightness(0, display=0)
    volume=False
    #if is_system_audio_set():                              #-----------UNDER DEVELOPMENT-------#
    #    volume=get_system_volume()                         #uncomment if volume hightligh needed
    #    set_system_volume(1)                               #uncomment if volume hightligh needed
##    content = get_content()
##    if content is not None:
##        time.sleep(3)
##        threading.Thread(target=speak_two,args=(content,)).start()
    return current_brightness[0],volume                    #uncomment if volume hightligh needed
def interval_off(screen_audio_level):
    sbc.set_brightness(100, display=0)
    if screen_audio_level[1]:
        set_system_volume(screen_audio_level[1])           #uncomment if volume hightligh needed
    winsound.Beep(2000,500)
    sbc.set_brightness(screen_audio_level[0], display=0)
def check_known_titles(foreground):
    if foreground ==  "Course: The Data Science Course: Complete Data Science Bootcamp 2024 | Udemy - Google Chrome":
        return True
    if foreground[-23:] ==  "YouTube - Google Chrome":
        return True
    if foreground[-25:] == "JioCinema - Google Chrome":
        return True
    if foreground[-29:] == "Skilling Pack - Google Chrome":
        return True
    if foreground[-20:] == "Tubi - Google Chrome":
        return True    
    return False
def stop_current_runnings(custom=False):
    foreground=win32gui.GetWindowText(win32gui.GetForegroundWindow())
    print(foreground)
    if foreground[-16:]=="VLC media player"  :
        pyautogui.hotkey("alt","tab")
        pyautogui.hotkey("alt","tab")
        pyautogui.hotkey("space")
        pyautogui.hotkey("left")
        custom=False
    elif check_known_titles(foreground):
        print("got it")
        pyautogui.hotkey("alt","tab")
        pyautogui.hotkey("alt","tab")
        pyautogui.click(691,398)
        pyautogui.hotkey("left")
        pyautogui.hotkey("left")
        custom=False
    if custom:
        pyautogui.hotkey("alt","tab")
        pyautogui.hotkey("alt","tab")
        pyautogui.hotkey("space")
        pyautogui.hotkey("left")
def start_monitoring():
    while True :
        if int(datetime.datetime.now().minute)%20==0:
            stop_current_runnings()
            screen_audio_level=interval()
            time.sleep(60)
            interval_off(screen_audio_level)
        time.sleep(3)                                      # the most important line of the program unlike it seems usuall
def testing():
        time.sleep(6)
        stop_current_runnings()
        screen_audio_level=interval()
        time.sleep(6)
        interval_off(screen_audio_level)
if __name__=="__main__":
    testing()
