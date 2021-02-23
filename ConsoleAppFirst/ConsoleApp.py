# import everything that will need
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import mysql.connector
from mysql.connector import Error
import datetime


def my_app1():
    """
    First function called from the console by the command "myApp 1".
    Creating `ptmk` database and then `users` table with fields representing name, date of birth, gender.
    """

    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password=''
    )
    mycurs = mydb.cursor()

    try:
        mycurs.execute("CREATE DATABASE ptmk DEFAULT CHARACTER SET 'utf8'")
        print('\nDatabase `ptmk` was created')
    except Error:
        print('\nDatabase `ptmk` was already created')
        pass
    mycurs.close()

    mydb = mysql.connector.connect(
        host='localhost',
        database='ptmk',
        user='root',
        password=''
    )
    mycurs = mydb.cursor()

    try:
        mycurs.execute('''CREATE TABLE users (
                        `Full name` VARCHAR(250), 
                        `Date of birth` DATE, 
                        `Sex` VARCHAR(15))''')
        print('Table `users` with fields (`Full name`, `Date of birth`, `Sex`) was created\n')
    except Error:
        print('Table `users` with fields (`Full name`, `Date of birth`, `Sex`) was already created\n')
        pass
    mycurs.close()


def my_app2(fullname, dob, sex):
    """
    Second function called from the console by the command "myApp 2 Fullname Date_of_birth Gender".
    Creating a record in the table using the following format: FIO, YYYY-MM-DD, Male/Female.

    :input myApp 2 LRB 1984-07-25 Male
    :param fullname: LRB
    :param dob: 1984-07-25
    :param sex: Male
    :return:
    _________________________________
    | Full name| Date of birth|  Sex|
    |       LRB|    1984-07-25| Male|
    """

    mydb = mysql.connector.connect(
        host='localhost',
        database='ptmk',
        user='root',
        password=''
    )
    mycurs = mydb.cursor()

    query = "INSERT INTO `users`(`Full name`, `Date of birth`, `Sex`) VALUES (%s,%s,%s)"
    args = (fullname, dob, sex)

    try:
        mycurs.execute(query, args)
        print('Table `user` was updated')
    except Error as e:
        print('Invalid input! Try again.')
        print(e)
        pass
    mydb.commit()
    mycurs.close()


def my_app3():
    """
    Third function called from the console by the command "myApp 3".
    Display all rows with a unique value FIO + date_of_birth, sorted by FIO.
    Output contains fullname, date of birth, gender, number of full years.
    """

    mydb = mysql.connector.connect(
        host='localhost',
        database='ptmk',
        user='root',
        password=''
    )
    mycurs = mydb.cursor()

    query = """SELECT DISTINCT(`Full name`), 
    `Date of birth`, 
    `Sex`, 
    YEAR(FROM_DAYS(DATEDIFF(CURRENT_DATE(), `Date of birth`))) as Age FROM `users` ORDER BY `Full name`"""
    mycurs.execute(query)

    row = mycurs.fetchone()

    print()
    while row is not None:
        print(tuple([x.strftime('%d-%m-%Y') if isinstance(x, datetime.date) else x for x in row]))
        row = mycurs.fetchone()
    print()
    mycurs.close()


def my_app4():
    """
    Fourth function called from the console by the command "myApp 4".
    Filling automatically 1,000,000 rows.
    Also filling in automatically 100 rows in which gender is 'Male' and fullname starts with "F"
    """

    mydb = mysql.connector.connect(
        host='localhost',
        database='ptmk',
        user='root',
        password=''
    )
    mycurs = mydb.cursor()

    query = """INSERT INTO `users` VALUES""" + ("""(
            CONCAT(CHAR(FLOOR(65 + (RAND() * 25))), CHAR(FLOOR(65 + (RAND() * 25))), CHAR(FLOOR(65 + (RAND() * 25)))),
            FROM_UNIXTIME(UNIX_TIMESTAMP('1970-04-30') + FLOOR(0 + (RAND() * 999999999))),
            ELT(0.5 + RAND() * 2, 'Male', 'Female')),""" * 999) + """(CONCAT(CHAR(FLOOR(65 + (RAND() * 25))),
            CHAR(FLOOR(65 + (RAND() * 25))), CHAR(FLOOR(65 + (RAND() * 25)))),
            FROM_UNIXTIME(UNIX_TIMESTAMP('1970-04-30') + FLOOR(0 + (RAND() * 999999999))),
            ELT(0.5 + RAND() * 2, 'Male', 'Female'));"""
    for _ in range(1000):
        mycurs.execute(query)
        mydb.commit()
    print('Загружено 1,000,000 случайных записей')

    query2 = """INSERT INTO `users` VALUES""" + ("""(
            CONCAT('F', CHAR(FLOOR(65 + (RAND() * 25))), CHAR(FLOOR(65 + (RAND() * 25)))),
            FROM_UNIXTIME(UNIX_TIMESTAMP('1970-04-30') + FLOOR(0 + (RAND() * 999999999))),
            'Male'),""" * 99) + """(CONCAT('F',
            CHAR(FLOOR(65 + (RAND() * 25))), CHAR(FLOOR(65 + (RAND() * 25)))),
            FROM_UNIXTIME(UNIX_TIMESTAMP('1970-04-30') + FLOOR(0 + (RAND() * 999999999))),
            'Male');"""
    mycurs.execute(query2)
    mydb.commit()
    print('Загружено 100 случайных записей (пол мужской, ФИО начинается с "F)')
    mycurs.close()


def my_app5():
    """
    Fifth function called from the console by the command "myApp 5".
    The result of sampling from the table according to the criterion:
        - gender is 'Male',
        - fullname begins with "F".
    The execution time is also measured.
    """

    import timeit
    mydb = mysql.connector.connect(
        host='localhost',
        database='ptmk',
        user='root',
        password=''
    )

    global mycurs, query
    mycurs = mydb.cursor()
    time = timeit.timeit('mycurs.execute("SELECT * FROM `users` WHERE `Sex` = \'Male\' AND `Full name` LIKE \'F__\';")',
                         setup="from __main__ import mycurs", number=1)
    mycurs.fetchall()
    print(f"Запрос выполнен за {round(time, 4)} сек.")
    mycurs.close()


# that's the dictionary of available commands in the console
comm = {
    'myApp 1': 'my_app1()',
    'myApp 2': 'my_app2(*command[2:])',
    'myApp 3': 'my_app3()',
    'myApp 4': 'my_app4()',
    'myApp 5': 'my_app5()'
}


# main engine of script
if __name__ == '__main__':
    while 1:
        user_input = prompt('>',
                        history=FileHistory('history.txt'),
                        auto_suggest=AutoSuggestFromHistory(),
                       )
        command = user_input.split()
        func = ' '.join(command[:2])
        if func not in comm:
            print('Wrong command! Try again.')
            continue
        try:
            eval(comm[func])
        except BaseException:
            print('Something went wrong! Try again.')
            pass
