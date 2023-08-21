import pymysql
from config import *
import datetime
import serial

try:
    serial_com = serial.Serial('COM5', 9600)
except serial.serialutil.SerialException:
    print("Датчик міток не підключено")
except NameError:
    print("wrong serial")


def onRead():
    try:
        rx = serial_com.readline()
        date = str(rx, 'utf-8').strip()
        return date
    except NameError:
        pass


def createTable():
    try:
        connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )

        try:
            with connection.cursor() as cursor:
                create_schema_query = "CREATE SCHEMA IF NOT EXISTS `time_working`"
                cursor.execute(create_schema_query)
            with connection.cursor() as cursor:
                cursor.execute("CREATE TABLE IF NOT EXISTS `employee` (user_id int AUTO_INCREMENT," 
                               " person varchar (50)," 
                               " rfid_1 varchar (50)," 
                               " rfid_2 varchar (50), PRIMARY KEY (user_id));")

            with connection.cursor() as cursor:
                cursor.execute("CREATE TABLE IF NOT EXISTS `time` (id int AUTO_INCREMENT,"
                               " user_id int,"
                               " time_ON DATETIME DEFAULT CURRENT_TIMESTAMP,"
                               " time_OFF DATETIME DEFAULT 0 ON UPDATE CURRENT_TIMESTAMP,"
                               " time_work VARCHAR(50),"
                               " on_work BOOL DEFAULT 1,"
                               " PRIMARY KEY (id));")
            # Перевірка чи таблиця відповідає словнику (видалення, перезапис)
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM time_working.employee;")
                rows = cursor.fetchall()
                if not len(rows):
                    for person in workers:
                        cursor.execute("INSERT INTO `employee` VALUES (" + person + ", '" + workers[person][0] + "', '"
                                       + workers[person][1] + "', '" + workers[person][2] + "');")
                        connection.commit()

                for row in rows:
                    print(row)
                    global drop_flag
                    drop_flag = True
                    for person in workers:
                        if str(row['user_id']) in person and workers[person][0] in row['person'] \
                                and workers[person][1] in row['rfid_1'] and workers[person][2] in row['rfid_2']:
                            drop_flag = False

                    if drop_flag:
                        cursor.execute("DROP TABLE employee")
                        connection.commit()
                        print("Таблицю видалено")
                        createTable()
                        break

        finally:
            connection.close()
        print("Successfully connected ...")
    except Exception as ex:
        print("connection refused ...")
        print(ex)


def select_date(id_dic):
    user_id = str(id_dic)
    try:
        connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT on_work FROM time WHERE user_id = " + user_id + " ORDER BY on_work DESC")
                row = cursor.fetchone()
                if row is not None:
                    if row['on_work']:
                        print('Finish')
                        cursor.execute("SELECT time_ON FROM time WHERE user_id = " + user_id + " ORDER BY on_work DESC")
                        time_ON = cursor.fetchone()
                        def_time = datetime.datetime.now() - time_ON['time_ON']
                        print(def_time)

                        cursor.execute("UPDATE time SET on_work = 0, time_work = '" + str(
                            def_time) + "' WHERE user_id = " + user_id + " AND on_work = 1")
                        connection.commit()
                    else:
                        print('Start')
                        cursor.execute("INSERT INTO `time` (user_id) VALUES (" + user_id + ");")
                        connection.commit()
                else:
                    cursor.execute("INSERT INTO `time` (user_id) VALUES (" + user_id + ");")
                    connection.commit()

        finally:
            connection.close()
            print("Successfully connected ...")

    except Exception as ex:
        print("connection refused ...")
        print(ex)


if __name__ == "__main__":
    createTable()
    while True:
        rfid = onRead()
        for n in workers:
            if rfid in workers[n]:
                select_date(n)
                print(workers[n][0])
