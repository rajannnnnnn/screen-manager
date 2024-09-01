import psutil
import os
import time

def terminate_chrome():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if "chrome.exe" in str(proc.name):
                if "--profile-directory" in str(proc.cmdline()):
                    os.system(f"taskkill /f /pid {proc.pid}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
def stop_incognito():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if "chrome.exe" in str(proc.name):
                if "--disable-databases" in str(proc.cmdline()):  # indicates "incognito"
                    os.system(f"taskkill /f /pid {proc.pid}")     # stop incognito
                    #terminate_chrome()                           # terminate entire chrome
                    #os.system('shutdown /s /t 40 /c " " ')       # shutdown
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass












if __name__ == "__main__":
    while True:
        stop_incognito()
        time.sleep(60)
