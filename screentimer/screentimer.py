import datetime
import subprocess
import time
import sys
import os
import sqlite3
import threading
acur_bug=60*3
sess_gap=60*10
conn=sqlite3.connect(r"C:\Users\user\AppData\Local\Programs\Python\Python312\myScripts\screentimer\screentime.db")
cur=conn.cursor()
#cur.execute("delete from screentime where date='2024-04-30' ")
#conn.commit()
#now = datetime.datetime(2024, 5, 2, 00, 32, 12)
#now_date=datetime.datetime(2024, 5, 2)
def screen_time_update():
    now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    now_date=datetime.datetime.now().strftime('%Y-%m-%d')
    fetch=cur.execute("select * from screentime where date=?",(now_date,)).fetchall()
    if len(fetch)==0:
        cur.execute("INSERT INTO screentime (date, start, end) VALUES (?, ?, ?)", (now_date, now, now))
        conn.commit()
        print("new dated")
    else:
        now_=datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
        end_=datetime.datetime.strptime(fetch[-1][2], "%Y-%m-%d %H:%M:%S")
        start_=datetime.datetime.strptime(fetch[-1][1], "%Y-%m-%d %H:%M:%S")
        if (now_-end_).total_seconds()<sess_gap:
            cur.execute(f"UPDATE screentime set end= ? WHERE start= ? AND date= ?",(now_,start_,now_date))
            conn.commit()
            print("time updated "+str(cur.rowcount))
        else:
            cur.execute(f"insert into screentime(date,start,end) values('{now_date}','{now}','{now}')")  
            conn.commit()
            print("session created "+str(cur.rowcount))
def draw_timeline(date):
    dash=1440 # 24 hr * 60  min = one day
    last=0
    timeline=""
    day_splitted=""
    hour=True
    n=0
    hours=(" 1"," 2"," 3"," 4"," 5"," 6"," 7"," 8"," 9","10","11","12"," 1"," 2"," 3"," 4"," 5"," 6"," 7"," 8"," 9","10","11","12")
    def string(start,end):
        value=""
        for i in range(end-start):
            value+="O"
        return value
    for i in range(dash):
        timeline+=":"
    for start,end in cur.execute(f"select start, end from screentime where date='{date}'").fetchall():
        start=datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        end=datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        start = round((start.hour * 60 + start.minute))
        end = round((end.hour * 60 + end.minute))
        timeline = timeline[:start] + string(start,end) + timeline[end:]
    day_splitted+=" 12 "
    for i in range(1,len(timeline)+1):
        day_splitted += timeline[i-1]
        if i%60 == 0:
            day_splitted+=f" {hours[n]} "
            if hour:
                day_splitted += " "
                hour=False
            else:
                day_splitted += " & echo "+f" {hours[n]} "
                hour=True
            n+=1
    return day_splitted[:-12]
def screen_time_report(date):
    line="---------------------------------------------------"
    report = f"echo {line}&echo ScreenTime Report for {date} &echo {line} &"
    report+=f"title ScreenTime Report for {date} &"
    if date == "today":
        date=datetime.date.today()
        report = f" echo {line}&echo   ScreenTime Report for Today ({date}) & echo {line} &"
        report+=f"title ScreenTime Report for Today ({date}) &"
    elif date == "yesterday":
        date=datetime.date.today()-datetime.timedelta(days=1)
        report = f"echo {line}&echo ScreenTime Report for Yesterday ({date}) & echo {line} &"
        report+=f"title ScreenTime Report for Yesterday ({date}) &"
    data=cur.execute(f"select * from screentime where date='{date}'").fetchall()
    n=0
    total=datetime.timedelta(seconds=0)
    for session in data:
        n=n+1
        start=datetime.datetime.strptime(session[1], "%Y-%m-%d %H:%M:%S")
        end=datetime.datetime.strptime(session[2], "%Y-%m-%d %H:%M:%S")
        if n==1:
            open_time=start
        diff=end-start
        report += f" echo Session {n}:      [ {start.strftime('%H:%M:%S')} - {end.strftime('%H:%M:%S')} ]    {diff} & "
        total+=diff
    if n==0:
        report+="echo;&echo                 no sessions found  &echo;& "
        report+=f" echo {line} & echo Total spent :   [ 00:00:00 - 00:00:00 ]    00:00:00 "
    else:
        report+=f" echo {line} & echo Total spent :   [ {open_time.strftime('%H:%M:%S')} - {end.strftime('%H:%M:%S')} ]    {total} "
    cur.execute("SELECT date('now', '-20 days')")
    startDate=cur.fetchone()[0]
    cur.execute("SELECT date('now')")
    curDate=cur.fetchone()[0]
    report+=f"&echo {line}&echo (Note: acuracy error {acur_bug} seconds) &echo (Note: Session is seperated with atleast {sess_gap} seconds) &"
    report+=f"echo                                                                   .  & echo {draw_timeline(date)} &"
    report+=f"echo                                                                   .  & echo O - when screen is on & echo : - when screen is off &"
    report+=f"echo                                                                   .   {fetch_short_screen_time_report(startDate,curDate)} &"

    
    report+="set /p in= "
    return report
def fetch_short_screen_time_report(date_from,date_to):
    line="-----------------------------------------------------------------------------------------"
    date_from=datetime.datetime.strptime(date_from, "%Y-%m-%d")
    date_to=datetime.datetime.strptime(date_to, "%Y-%m-%d")
    space=""
    report=""
    short_screen_times=[]
    spacing_dic={"Sunday":2,"Monday":15,"Tuesday":28,"Wednesday":41,"Thursday":54,"Friday":67,"Saturday":80}
    first_entry=True
    while(not str(date_to-date_from)[:str(date_to-date_from).find(",")].replace(" days","") == "-1 day"):
        data=cur.execute(f"select * from screentime where date='{str(date_from)[:10]}'").fetchall()
        n=0
        total=datetime.timedelta(seconds=0)
        for session in data:
            n=n+1
            start=datetime.datetime.strptime(session[1], "%Y-%m-%d %H:%M:%S")
            end=datetime.datetime.strptime(session[2], "%Y-%m-%d %H:%M:%S")
            if n==1:
                open_time=start
            diff=end-start
            total+=diff
        if n==0:
            hour="  -  "
        else:
            if len(str(total))==7:
                hour=f"0{str(total)[:-3]}"
            else:
                hour=f"{str(total)[:-3]}"
        if int(date_from.day)==1 or first_entry:
            report+=f" & echo {line} {date_from.year} {date_from.strftime('%B')}& echo     Sun          Mon          \
Tue          Wed          Thu          Fri          Sat & echo {line} & echo"
            for i in range(spacing_dic[date_from.strftime('%A')]):
                space+=" "
        elif date_from.strftime('%A')=="Sunday":
            report+="& echo  "    
        if date_from.day<10:
            report+=f"{space} {date_from.day}) {hour}    "
        else:
            report+=f"{space}{date_from.day}) {hour}    "
        space=""      
        first_entry=False
        date_from+=datetime.timedelta(days=1)
    report+=f"& echo {line}"
    return report
def show_report(date):
    threading.Thread(target=os.system,args=(screen_time_report(date),)).start()
def start_monitoring():
    while True:
        screen_time_update()
        time.sleep(acur_bug)
if __name__=="__main__":
    show_report("today")
