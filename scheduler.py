from re import S
import sqlite3
import datetime
from notifypy import Notify
import time
from threading import Thread

# this class handles the functions associated with the scheduler
class Scheduler:
    def __init__(self, name, date, time):
        self.name = name
        self.date = date
        self.time = time

    def __repr__(self):
        return f"[self] = Scheduler({self.name},{self.date},{self.time})"

    @staticmethod
    def get_tasks(task=None):
        c.execute("""SELECT * FROM schedule
        ORDER BY date, time""")
        return (c.fetchall())

    def add_task(self):
        id = len(self.get_tasks())
        c.execute(f"""
        INSERT INTO schedule 
        VALUES (?,?,?,?,?)
        """, (id+1,self.name,self.date,self.time, 0))
        connection.commit()

    @staticmethod
    def clear_tasks():
        c.execute(f"""
        DELETE FROM schedule
        """)
        connection.commit()

    @staticmethod
    def del_task(taskname):
        c.execute(f"""
        DELETE FROM schedule 
        WHERE task = '{taskname}'
        """)
        connection.commit()
    
    @staticmethod
    def notification_mode_input():
        x = input()
        result[0] = x.strip()

# this is the structure of the table in schedule_db.db:
# CREATE TABLE schedule(
#     id INTEGER,
#     task CHAR(255),
#     date DATE,
#     time TIME,
#     notified BOOL)

connection = sqlite3.connect('schedule_db.db')
c = connection.cursor()

# this part loops the input 
while True:
    task_list = Scheduler.get_tasks()
    print('\n|Task Scheduler - Scheduling Mode| ("help" for help)\n|Current tasks|')
    if len(task_list)!=0:
        for i in task_list:
            print(i)
    command = input('\n')
    key = command.strip().split()[0]
    if command.strip() == 'help':
        print("""
Commands and Usage:
    add [task_name] [task_date(yyyy-mm-dd)] [task_time(hh:mm:ss)]: adds a task
    del [task_name]: deletes a task 
    clear CONFIRM: clears all scheduled tasks
    notification mode: enter notification mode (you will be notified
    for your tasks 30 minutes prior)
    quit: quit the program
        """)

    elif command.strip() == 'quit':
        break

    elif key == 'add':
        info = command.strip()[3:].strip().split()
        task = Scheduler(f'{info[0]}',f'{info[1]}',f'{info[2]}')
        Scheduler.add_task(task)

    elif key == 'del':
        task = command.strip().strip().split()[1]
        Scheduler.del_task(task)

    elif command.strip() == 'clear CONFIRM':
        Scheduler.clear_tasks()
        
    elif command.strip() == 'notification mode':

        print('''\n|Task Scheduler - Notification Mode| ("quit" to reenter Scheduling Mode)''')

        #checks if all tasks notified
        c.execute("""SELECT task,date,time,notified FROM schedule
        WHERE notified = 0
        """)
        task_list = c.fetchall()
        if len(task_list)==0:
            print('All tasks notified, "quit" to return...\n')
        else:
            print('|Unnotified tasks|')
            for i in task_list:
                print (i)

        result = [[None]*10]

        thread = Thread(target=Scheduler.notification_mode_input)
        thread.start()

        while True:
            if result[0] == 'quit':
                break
            now = datetime.datetime.now()
            for i in task_list:
                dateinfo = i[1].split('-')
                timeinfo = i[2].split(':')
                d1 = datetime.datetime(int(dateinfo[0]),int(dateinfo[1]),int(dateinfo[2]),int(timeinfo[0]),int(timeinfo[1]),int(timeinfo[2]))-datetime.timedelta(minutes=30)
                if now>=d1:
                    notification = Notify()
                    notification.title = f"Notification for Task: {i[0]}"
                    notification.message = f"Scheduled for {d1}!"
                    notification.audio = '/Users/marcuslai/Desktop/Codes/Python/Scheduler/notification_audio.wav'
                    notification.icon = '/Users/marcuslai/Desktop/Codes/Python/Scheduler/icon.png'
                    notification.send()
                    c.execute(f"""UPDATE schedule
                    SET notified = 1
                    WHERE task="{i[0]}"
                    """)
                    connection.commit()
                    print('''\n|Task Scheduler - Notification Mode| ("quit" to reenter Scheduling Mode)''')
                    c.execute("""SELECT task,date,time,notified FROM schedule
                    WHERE notified = 0
                    """)
                    task_list = c.fetchall()
                    if len(task_list)==0:
                        print('All tasks notified, "quit" to return...\n')
                    else:
                        print('|Unnotified tasks|')
                        for i in task_list:
                            print (i)

    else:
        print('\nCommand not recognized')

connection.close()
