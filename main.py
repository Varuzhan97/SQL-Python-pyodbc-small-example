import pyodbc
import os
from texttable import Texttable
import yaml

details = {
 'server' : '',
 'database' : '',
 'username' : '',
 'password' : ''
 }

def yamlInputDataRead():
    fileName = str(input('---| Enter YAML File Name (File Must Be In "Data" Folder) -> '))
    path = os.path.dirname(os.path.abspath(__file__)) + '/Data/' + fileName
    if os.path.isfile(path):
        with open(path, "r") as f:
            return yaml.load(f)
    else:
        print('---| File Not Exist |---', flush=True)

def yamlCheckerQueryRead(queryName):
    path = os.path.dirname(os.path.abspath(__file__)) + '/' + 'checker_query.yaml'
    if os.path.isfile(path):
        with open(path, "r") as f:
            query = yaml.load(f)
            result = query.get(queryName)
            return result
    else:
        print('---| File "checker_query.yaml" Not Exist |---', flush=True)

def runScript(folderName, fileName):
    connection = pyodbc.connect('Driver=ODBC Driver 17 for SQL Server;server={server};port=1443;database={database};UID={username};PWD={password};'.format(**details))
    cursor = connection.cursor()
    dir = os.path.dirname(os.path.abspath(__file__)) + '/' + folderName + '/' + fileName
    file = open(dir,'r')
    sqlQuerry = file.read()
    cursor.execute(sqlQuerry)
    connection.commit()
    connection.close()

def checkAndCreate(queryCheckName, queryCreateName, elementName, typeName):
    connection = pyodbc.connect('Driver=ODBC Driver 17 for SQL Server;server={server};port=1443;database={database};UID={username};PWD={password};'.format(**details))
    cursor = connection.cursor()
    query = yamlCheckerQueryRead(queryCheckName)
    print('---| Checking %s "%s" |---' %(typeName, elementName), flush=True)
    cursor.execute(query, elementName)
    row = cursor.fetchall()
    if row:
        print('---| %s "%s" Exist |---' %(typeName, elementName), flush=True)
    else:
        print('---| Creating %s "%s" |---' %(typeName, elementName), flush=True)
        runScript(typeName, queryCreateName)
    connection.close()

def checkTables():
    print('---| Checking Tables |---', flush=True)
    checkAndCreate('check_table', 'create_users.sql', 'users', 'Table')
    checkAndCreate('check_table', 'create_user_info.sql', 'user_info', 'Table')
    checkAndCreate('check_table', 'create_employee_info.sql', 'employee_info', 'Table')
    checkAndCreate('check_table', 'create_epochs.sql', 'epochs', 'Table')
    checkAndCreate('check_table', 'create_data.sql', 'data', 'Table')
    checkAndCreate('check_table', 'create_data_info.sql', 'data_info', 'Table')

def checkFunctions():
    print('---| Checking Functions |--- ', flush=True)
    checkAndCreate('check_function', 'getTrainItemsNumber.sql', 'getTrainItemsNumber', 'Function')
    checkAndCreate('check_function', 'getTestItemsNumber.sql', 'getTestItemsNumber', 'Function')
    checkAndCreate('check_function', 'validateEmail.sql', 'validateEmail', 'Function')

def checkAdmin():
    checker = False
    adminPass = str(input('---| Enter Admin Pass -> '))
    if adminPass == '12345$':
        checker = True
    return checker

def loginUser():
    userPIN = inputNumber('---| Enter User PIN -> ', '---| Enter Valid PIN (Only Digits And Minimum 4 Digits) |---')
    connection = pyodbc.connect('Driver=ODBC Driver 17 for SQL Server;server={server};port=1443;database={database};UID={username};PWD={password};'.format(**details))
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, first_name, last_name, pin, is_active FROM dbo.users WHERE pin=?", userPIN)
    row = cursor.fetchall()
    if not row:
        print ('---| User Not Found |---', flush=True)
    elif row[0][4]==0:
        print ('---| User %s %s Deactivated |---' %(row[0][1], row[0][2]), flush=True)
    else:
        print ('---| %s %s Logged In |---' %(row[0][1], row[0][2]), flush=True)
        startSession(row[0][1], row[0][2], row[0][0], row[0][3])
    connection.close()

def insertData(userFirstName, userLastName, userID):
    connection = pyodbc.connect('Driver=ODBC Driver 17 for SQL Server;server={server};port=1443;database={database};UID={username};PWD={password};'.format(**details))
    cursor = connection.cursor()
    sources = yamlInputDataRead()
    if sources == 0:
        return
    trainItems = list((sources.get("train_data")).items())
    testItems = list((sources.get("test_data")).items())
    epochItems = list((sources.get("epoch")).values())
    print('---| Inserting Epochs By User %s %s |---' %(userFirstName, userLastName), flush=True)
    cursor.execute("INSERT INTO dbo.epochs(epoch_loss, epoch_accuracy) VALUES (?, ?);", float(epochItems[0]), float(epochItems[1]))
    connection.commit()
    print('---| Inserting Train Data By User %s %s |---' %(userFirstName, userLastName), flush=True)
    for x, y in trainItems:
        cursor.execute("INSERT INTO dbo.data(data_key, data_value) VALUES (?, ?);", str(x), int(y))
        connection.commit()
        print('---| Updating Data Info For Inserted Train Data |---', flush=True)
        cursor.execute("SELECT MAX(data_id) FROM dbo.data")
        maxData = cursor.fetchall()
        cursor.execute("SELECT MAX(epoch_id) FROM dbo.epochs")
        maxEpochs = cursor.fetchall()
        cursor.execute("INSERT INTO dbo.data_info(data_id, data_type, data_adder_id, epoch_id, add_time) VALUES (?, 'Train', ?, ?, GETDATE());", maxData[0][0], userID, maxEpochs[0][0])
        connection.commit()
    print('---| Inserting Test Data By User|---', flush=True)
    for x, y in testItems:
        cursor.execute("INSERT INTO dbo.data(data_key, data_value) VALUES (?, ?);", str(x), int(y))
        connection.commit()
        print("---| Updating Data Info For Inserted Test Data |---", flush=True)
        cursor.execute("SELECT MAX(data_id) FROM dbo.data")
        maxData = cursor.fetchall()
        cursor.execute("SELECT MAX(epoch_id) FROM dbo.epochs")
        maxEpochs = cursor.fetchall()
        cursor.execute("INSERT INTO dbo.data_info(data_id, data_type, data_adder_id, epoch_id, add_time) VALUES (?, 'Test', ?, ?, GETDATE());", maxData[0][0], userID, maxEpochs[0][0])
        connection.commit()
    connection.close()

def searchHistory(userPIN):
    connection = pyodbc.connect('Driver=ODBC Driver 17 for SQL Server;server={server};port=1443;database={database};UID={username};PWD={password};'.format(**details))
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT users.user_id, users.first_name, users.last_name, data_info.epoch_id FROM dbo.users \
    INNER JOIN dbo.data_info ON users.user_id = data_info.data_adder_id \
    WHERE pin=? ORDER BY data_info.epoch_id", userPIN)
    rowEpoch = cursor.fetchall()
    if not rowEpoch:
        print ("---| User Not Found |---", flush=True)
    else:
        tableEpoch = Texttable()
        tableEpoch.set_cols_align(["c", "c", "c"])
        tableEpoch.set_cols_valign(["m", "m", "m"])
        tableEpoch.set_cols_dtype(['a', 'a', 'a'])
        tableEpoch.add_row(['Epoch ID', 'Train Set Size', 'Test Set Size'])
        for x in rowEpoch:
            cursor.execute("SELECT dbo.getTrainItemsNumber(?)", x[3])
            rowTrain = cursor.fetchall()
            cursor.execute("SELECT dbo.getTestItemsNumber(?)", x[3])
            rowTest = cursor.fetchall()
            tableEpoch.add_row([x[3], rowTrain[0][0], rowTest[0][0]])
        print('---| History Of User %s %s |---' %(rowEpoch[0][1], rowEpoch[0][2]), flush=True)
        print(tableEpoch.draw(), flush=True)
        cursor.execute("SELECT data_info.epoch_id, data.data_key, data.data_value, data_info.data_type, data_info.add_time FROM dbo.data \
        INNER JOIN dbo.data_info ON data.data_id = data_info.data_id AND data_info.data_adder_id = ? \
        ORDER BY data_info.epoch_id", rowEpoch[0][0])
        rowData = cursor.fetchall()
        tableData = Texttable()
        tableData.set_cols_align(["c", "c", "c", "c", "c"])
        tableData.set_cols_valign(["m", "m", "m", "m", "m"])
        tableData.set_cols_dtype(['a', 'a', 't', 'a', 'a'])
        tableData.add_row(['Epoch ID', 'Data Key', 'Data Value', 'Data Type', 'Add Time'])
        for x in rowData:
            tableData.add_row([x[0], x[1], bool(x[2]), x[3], x[4]])
        print('---| Data Added By User %s %s |---' %(rowEpoch[0][1], rowEpoch[0][2]), flush=True)
        print(tableData.draw(), flush=True)
    connection.close()

def startSession(userFirstName, userLastName, userID, userPIN):
    while True:
        print('---| 0 -> Log Out |---', flush=True)
        print('---| 1 -> Insert Data |---', flush=True)
        print("---| 2 -> Search User History |---", flush=True)
        x = int(input())
        if x == 0:
            print('---| %s %s Logged Out |---' %(userFirstName, userLastName), flush=True)
            return
        if x == 1:
            insertData(userFirstName, userLastName, userID)
        if x == 2:
            searchHistory(userPIN)

def inputName(header, exception):
    while True:
        userName = str(input(header))
        if userName.isalpha():
            userName = userName.capitalize()
            break
        else:
            print(exception, flush=True)
    return userName

def inputNumber(header, exception, minLength = 4):
    while True:
        number = (input(header))
        if any([len(number) < minLength, number.isnumeric() != True]):
            print(exception)
        else:
            break
    return number

def inputGender(header, exception):
    while True:
        userGender = str(input(header)).lower()
        if all([userGender != 'male', userGender != 'female']):
            print(exception)
        else:
            userGender = userGender.capitalize()
            break
    return userGender

def inputEmail(header, exception):
    connection = pyodbc.connect('Driver=ODBC Driver 17 for SQL Server;server={server};port=1443;database={database};UID={username};PWD={password};'.format(**details))
    cursor = connection.cursor()
    while True:
        userEmail = str(input(header)).lower()
        cursor.execute("SELECT dbo.validateEmail(?)", userEmail)
        row = cursor.fetchall()
        if row[0][0] == False:
            print(exception, flush=True)
        else:
            break
    connection.close()
    return userEmail

def inputProfessionalLevel(header, exception):
    while True:
        eployeeLevel = str(input(header)).lower()
        if all([eployeeLevel != 'junior', eployeeLevel != 'middle', eployeeLevel != 'senior']):
            print('---| Enter Valid Level (Junior / Middle / Senior) |---', flush=True)
        else:
            eployeeLevel = eployeeLevel.capitalize()
            break
    return eployeeLevel

def addUser():
    validAdmin = checkAdmin()
    if validAdmin:
        connection = pyodbc.connect('Driver=ODBC Driver 17 for SQL Server;server={server};port=1443;database={database};UID={username};PWD={password};'.format(**details))
        cursor = connection.cursor()
        firstName = inputName('---| Enter First Name -> ', '---| Enter Valid First Name (Only Letters) |---')
        lastName = inputName('---| Enter Last Name -> ', '---| Enter Valid Last Name (Only Letters) |---')
        userPIN = inputNumber('---| Enter User PIN -> ', '---| Enter Valid PIN (Only Digits And Minimum 4 Digits) |---')
        userGender = inputGender('---| Enter Gender (Male / Female) -> ', '---| Enter Valid Gender (Male / Female) |---')
        while True:
            userEmail = inputEmail('---| Enter Email -> ', '---| Enter Valid Email |---')
            cursor.execute("SELECT * FROM dbo.user_info WHERE email=?;", userEmail)
            row = cursor.fetchall()
            if row:
                print ('---| Email Already In Use. Enter Another Email) |---', flush=True)
            else:
                break
        userPhone = inputNumber('---| Enter Phone Number -> ', '---| Enter Valid Phone Number (Only Digits And Minimum 9 Digits) |---', 9)
        eployeeLevel = inputProfessionalLevel('---| Enter Professional Level (Junior / Middle / Senior) -> ', '---| Enter Valid Level (Junior / Middle / Senior) |---')
        cursor.execute("INSERT INTO dbo.users(first_name, last_name, pin) VALUES(?, ?, ?);", firstName, lastName, userPIN)
        connection.commit()
        cursor.execute("SELECT MAX(user_id) FROM dbo.users")
        maxID = cursor.fetchall()
        cursor.execute("INSERT INTO dbo.user_info(user_id, gender, email, phone) VALUES(?, ?, ?, ?);", maxID[0][0], userGender, userEmail, userPhone)
        connection.commit()
        cursor.execute("INSERT INTO dbo.employee_info(employee_id, professional_level) VALUES(?, ?);", maxID[0][0], eployeeLevel)
        connection.commit()
        print ('---| User Added Successfully |---', flush=True)
        connection.close()
    else:
        print ('---| Admin Password Is Not Correct |---', flush=True)

def deactivateUser():
    connection = pyodbc.connect('Driver=ODBC Driver 17 for SQL Server;server={server};port=1443;database={database};UID={username};PWD={password};'.format(**details))
    cursor = connection.cursor()
    userEmail = inputEmail('---| Enter Email -> ', '---| Enter Valid Email |---')
    cursor.execute("SELECT users.user_id, users.is_active FROM dbo.users \
    INNER JOIN dbo.user_info ON user_info.user_id = users.user_id AND user_info.email = ?", userEmail)
    row = cursor.fetchall()
    if not row:
        print ('---| User Not Found |---', flush=True)
    else:
        if row[0][1] == 0:
            print('---| User Is Deactive |---', flush=True)
        else:
            print ('---| User Deactivated |---', flush=True)
            cursor.execute("UPDATE dbo.users SET is_active = 0 WHERE user_id=?;", row[0][0])
            connection.commit()
    connection.close()

def activateUser():
    connection = pyodbc.connect('Driver=ODBC Driver 17 for SQL Server;server={server};port=1443;database={database};UID={username};PWD={password};'.format(**details))
    cursor = connection.cursor()
    userEmail = inputEmail('---| Enter Email -> ', '---| Enter Valid Email |---')

    cursor.execute("SELECT users.user_id, users.is_active FROM dbo.users \
    INNER JOIN dbo.user_info ON user_info.user_id = users.user_id AND user_info.email = ?", userEmail)
    row = cursor.fetchall()
    if not row:
        print ('---| User Not Found |---', flush=True)
    else:
        if row[0][1]==1:
            print ('---| User Is Active |---', flush=True)
        else:
            print ('---| User Activated |---', flush=True)
            cursor.execute("UPDATE dbo.users SET is_active = 1 WHERE user_id=?", row[0][0])
            connection.commit()
    connection.close()

def deleteData():
    validAdmin = checkAdmin()
    if validAdmin:
        runScript('Script', 'deleteData.sql')
        print ('---| Database Is Empty |---', flush=True)
    else:
        print ('---| Admin Password Is Not Correct |---', flush=True)

def searchEpoch():
    connection = pyodbc.connect('Driver=ODBC Driver 17 for SQL Server;server={server};port=1443;database={database};UID={username};PWD={password};'.format(**details))
    cursor = connection.cursor()
    cursor.execute("SELECT Distinct dbo.epochs.epoch_id, dbo.epochs.epoch_loss, dbo.epochs.epoch_accuracy, dbo.users.user_id, dbo.users.first_name, dbo.users.last_name\
    FROM dbo.epochs \
    INNER JOIN dbo.data_info ON epochs.epoch_id = data_info.epoch_id \
    INNER JOIN dbo.users ON data_info.data_adder_id = users.user_id AND users.is_active=1 \
    WHERE epoch_accuracy = (SELECT MAX(epoch_accuracy) FROM  dbo.epochs)")
    row = cursor.fetchall()
    if not row:
        print ("---| There Is No Any Epoch In Database |---", flush=True)
    else:
        print('---| Maximum Accuracy |---', flush=True)
        tableMax = Texttable()
        tableMax.set_cols_align(["c", "c", "c", "c", "c", "c", "c"])
        tableMax.set_cols_valign(["m", "m", "m", "m", "m", "m", "m"])
        tableMax.set_cols_dtype(['a', 'a', 'a', 'a', 'a', 'a', 'a']) # automatic
        tableMax.add_row(['Epoch ID', 'Epoch Loss', 'Epoch Accuracy', 'User ID', 'User Full Name', 'Train Set Size', 'Test Set Size'])
        for x in row:
            cursor.execute("SELECT dbo.getTrainItemsNumber(?)", x[0])
            rowTrain = cursor.fetchall()
            cursor.execute("SELECT dbo.getTestItemsNumber(?)", x[0])
            rowTest = cursor.fetchall()
            tableMax.add_row([x[0], x[1], x[2], x[3], (x[4] + ' ' + x[5]), rowTrain[0][0], rowTest[0][0]])
        print(tableMax.draw(), flush=True)
        print("---| 0 -> Quit |---", flush=True)
        print("---| 1 -> Search By Range |---", flush=True)
        x = int(input())
        if x == 1:
            print('---| Accuracy Range -> [0, 100] |---', flush=True)
            while True:
                accuracyRS = float(input('---| Enter Min Accuracy (Range [0, 100]) ---> '))
                if accuracyRS < 0:
                    print('---| Accuracy Min Range < 0 (Try Again) |---', flush=True)
                    continue
                break
            while True:
                accuracyRE = float(input('---| Enter Max Accuracy (Range [%f, 100]) ---> ' %accuracyRS))
                if accuracyRE > 100:
                    print('---| Accuracy Max Range > 100 (Try Again) |---', flush=True)
                    continue
                if accuracyRE < accuracyRS:
                    print('---| Accuracy Max Range < Min Range (Try Again) |---', flush=True)
                    continue
                break
            cursor.execute("SELECT Distinct epochs.epoch_id, epoch_loss, epoch_accuracy, users.user_id, users.first_name, users.last_name \
            FROM dbo.epochs \
            INNER JOIN dbo.data_info ON epochs.epoch_id = data_info.epoch_id \
            INNER JOIN dbo.users ON data_info.data_adder_id = users.user_id AND users.is_active=1 \
            WHERE epoch_accuracy>=? AND epoch_accuracy<=?", accuracyRS, accuracyRE)
            row = cursor.fetchall()
            if not row:
                print ("---| Nothing Found |---", flush=True)
            else:
                tableRange = Texttable()
                tableRange.set_cols_align(["c", "c", "c", "c", "c", "c", "c"])
                tableRange.set_cols_valign(["m", "m", "m", "m", "m", "m", "m"])
                tableRange.set_cols_dtype(['a', 'a', 'a','a', 'a','a','a']) # automatic
                tableRange.add_row(['Epoch ID', 'Epoch Loss', 'Epoch Accuracy', 'User ID', 'User Full Name', 'Train Set Size', 'Test Set Size'])
                for x in row:
                    cursor.execute("SELECT dbo.getTrainItemsNumber(?)", x[0])
                    rowTrain = cursor.fetchall()
                    cursor.execute("SELECT dbo.getTestItemsNumber(?)", x[0])
                    rowTest = cursor.fetchall()
                    tableRange.add_row([x[0], x[1], x[2], x[3], x[4] + ' ' + x[5], rowTrain[0][0], rowTest[0][0]])
                print(tableRange.draw())
    connection.close()

def getUserInfo():
    print("---| 0 -> Quit |---", flush=True)
    print("---| 1 -> Search User By Full Name |---", flush=True)
    print("---| 2 -> Search User By Email |---", flush=True)
    x = int(input())
    if x == 0:
        return
    else:
        connection = pyodbc.connect('Driver=ODBC Driver 17 for SQL Server;server={server};port=1443;database={database};UID={username};PWD={password};'.format(**details))
        cursor = connection.cursor()
        if x == 1:
            firstName = inputName('---| Enter First Name -> ', '---| Enter Valid First Name (Only Letters) |---')
            lastName = inputName('---| Enter Last Name -> ', '---| Enter Valid Last Name (Only Letters) |---')
            cursor.execute("SELECT users.user_id, users.first_name, users.last_name, users.is_active, employee_info.professional_level, user_info.gender, user_info.email, user_info.phone \
            FROM dbo.users \
            INNER JOIN dbo.user_info ON user_info.user_id = users.user_id \
            INNER JOIN dbo.employee_info ON employee_info.employee_id = users.user_id \
            WHERE first_name=? AND last_name=?", firstName, lastName)
            row = cursor.fetchall()
            if not row:
                print ("---| User Not Found |---", flush=True)
            else:
                table = Texttable()
                table.set_cols_align(["c", "c", "c", "c", "c", "c", "c", "c"])
                table.set_cols_valign(["m", "m", "m", "m", "m", "m", "m", "m"])
                table.set_cols_dtype(['a', 'a', 'a', 'a','a', 'a','a','a']) # automatic
                table.add_row(['ID', 'First Name', 'Last Name', 'Activity Status','Professional Level', 'Gender', 'User Email', 'Phone'])
                for x in row:
                    table.add_row([x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7]])
                print(table.draw())
        if x == 2:
            userEmail = inputEmail('---| Enter Email -> ', '---| Enter Valid Email |---')
            cursor.execute("SELECT users.user_id, users.first_name, users.last_name, users.is_active, employee_info.professional_level, user_info.gender, user_info.email, user_info.phone \
            FROM dbo.user_info \
            INNER JOIN dbo.users ON user_info.user_id = users.user_id \
            INNER JOIN dbo.employee_info ON employee_info.employee_id = users.user_id \
            WHERE email=?", userEmail)
            row = cursor.fetchall()
            if not row:
                print ("---| User Not Found |---", flush=True)
            else:
                table = Texttable()
                table.set_cols_align(["c" , "c", "c", "c", "c", "c", "c", "c"])
                table.set_cols_valign(["m", "m", "m", "m", "m", "m", "m", "m"])
                table.set_cols_dtype(['a', 'a', 'a', 'a','a', 'a','a','a']) # automatic
                table.add_row(['ID', 'First Name', 'Last Name', 'Activity Status', 'Professional Level', 'Gender', 'User Email', 'Phone'])
                for x in row:
                    table.add_row([x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7]])
                print(table.draw())
    connection.close()

def changeUserVisisbility():
    validAdmin = checkAdmin()
    if validAdmin:
        while True:
            print('---| 0 -> Quit |---', flush=True)
            print('---| 1 -> Activate User |---', flush=True)
            print("---| 2 -> Deactivate User |---", flush=True)
            x = int(input())
            if x == 0:
                return
            if x == 1:
                activateUser()
            if x == 2:
                deactivateUser()
    else:
        print ('---| Admin Password Is Not Correct |---', flush=True)

checkTables()
checkFunctions()
while True:
    print("---| 0 -> Quit |---", flush=True)
    print("---| 1 -> Log In |---", flush=True)
    print("---| 2 -> Add User |---", flush=True)
    print("---| 3 -> Activate / Deactivate User |---", flush=True)
    print("---| 4 -> Search History By Epoch Accuracy |---", flush=True)
    print("---| 5 -> Get User Information |---", flush=True)
    print("---| 6 -> Delete Data |---", flush=True)
    x = int(input())
    if x == 0:
        break
    if x == 1:
        loginUser()
    if x == 2:
        addUser()
    if x == 3:
        changeUserVisisbility()
    if x == 4:
        searchEpoch()
    if x == 5:
        getUserInfo()
    if x == 6:
        deleteData()
