import sqlite3
import datetime
from notifypy import Notify
import time

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
    print('|Task Scheduler ("help" for help)|\nCurrent tasks:')
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
                clear: clears all scheduled tasks
                notification mode: enter notification mode (you won't be able to edit your schedule 
                    but you will be notified of your tasks 30 minutes prior to each)
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

    elif command.strip() == 'clear':
        Scheduler.clear_tasks()
        
    elif command.strip() == 'notification mode':
        print('You are in notification mode, once you are notified of all your tasks this mode will be exited.')
        while True:
            c.execute("""SELECT task,date,time,notified FROM schedule""")
            task_list = c.fetchall()
            now = datetime.datetime.now()

            # this counter checks if all tasks have been notified
            counter = 0
            for i in task_list:
                if i[3]==False:
                    counter+=1

            # this notifies when it's less than 30 min away
            if counter>0:
                for i in task_list:
                    if i[3]==False:
                        dateinfo = i[1].split('-')
                        timeinfo = i[2].split(':')
                        d1 = datetime.datetime(int(dateinfo[0]),int(dateinfo[1]),int(dateinfo[2]),int(timeinfo[0]),int(timeinfo[1]),int(timeinfo[2]))-datetime.timedelta(minutes=30)
                        if now>=d1:
                            notification = Notify()
                            notification.title = f"Notification for Task: {i[0]}"
                            notification.message = f"Scheduled for {d1}!"
                            notification.send()
                            c.execute(f"""UPDATE schedule
                            SET notified = 1
                            WHERE task="{i[0]}"
                            """)
                            connection.commit()
                time.sleep(30)
            else:
                break
    else:
        print('\nCommand not recognized')

connection.close()
