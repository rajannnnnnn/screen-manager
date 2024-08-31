import sqlite3
conn=sqlite3.connect(r"C:\Users\user\AppData\Local\Programs\Python\Python312\myScripts\screentimer\screentime.db")
cur=conn.cursor()
with open("screentime.csv","w") as file:
    for date,start,end in cur.execute("select * from screentime").fetchall():
        file.write(f"{date},{start},{end}\n")
    file.close()
