import random, hashlib
from Models.Userdata import userData
import json, collections, datetime


class DBController:
    def __init__(self, cursor, mysql):
        self.cursor = cursor
        self.mysql = mysql

    def getUser(self, username):
        print("username in getuser", username, type(username))
        # self.cursor.execute('SELECT u1.FIRST_NAME, r1.RIDE_ID as Offered, r2.STATUS FROM RIDES_OFFERED r1 INNER JOIN USER u1 ON r1.USERNAME = u1.USERNAME INNER JOIN RIDES_REQUESTED r2 ON r1.USERNAME = r2.USERNAME WHERE r1.USERNAME = "%s"'% (username))
        self.cursor.execute('SELECT * FROM USER WHERE USERNAME = "%s"'% (username))
        user_data = self.cursor.fetchall()
        print("user_data", user_data)
        print()
        for i in user_data:
            print(i)
            self.cursor.execute(
                'SELECT `RIDE_ID`, `USERNAME`, `STATUS` FROM RIDES_REQUESTED WHERE RIDE_ID = "%s"'
                % (i[4])
            )
            offered_data = self.cursor.fetchall()
            print("offered_data", offered_data)

        print("------")
        self.cursor.execute(
            'SELECT `RIDE_ID`, `USERNAME`, `STATUS` FROM RIDES_REQUESTED WHERE USERNAME = "%s"'
            % (username)
        )
        requested_data = self.cursor.fetchall()
        print("requested_data", requested_data)

        user_model = userData(user_data, offered_data, requested_data)
        resp = user_model.getUserData()
        print()
        print(resp)
        return resp

    def saveRequest(self, RideID, eventID, userID, status):
        self.cursor.execute(
            """INSERT INTO RIDES_REQUESTED (RIDE_ID,EVENT_ID,USERNAME,STATUS) VALUES(%s,%s,%s,%s)""",
            (RideID, eventID, userID, status),
        )
        print("Data Saved!")
        # return response

    def getrides_wo_username(
        self, eventId
    ):  # to send offered rides data when eventId is provided
        data = []
        self.cursor.execute(
            """ 
        SELECT U.FIRST_NAME, U.LAST_NAME, RO.EVENT_ID, RO.RIDE_ID, RO.USERNAME, RO.START_TIME   
            FROM RIDES_OFFERED AS RO INNER JOIN USER AS U 
            ON U.USERNAME = RO.USERNAME AND RO.EVENT_ID=%s""",
            [eventId],
        )
        ridesdata = self.cursor.fetchall()
        for ride in ridesdata:
            d = collections.OrderedDict()
            d["FIRST_NAME"] = ride[0]
            d["LAST_NAME"] = ride[1]
            d["EVENT_ID"] = ride[2]
            d["RIDE_ID"] = ride[3]
            d["USERNAME"] = ride[4]
            #            d["CAR_MODEL"] = ride[5]
            #            d["NO_OF_SEATS"] = ride[6]
            d["START_TIME"] = ride[5].strftime("%d-%m-%Y %H:%M:%S")
            #           d["WAIT_TIME"] = datetime.time(ride[8])
            #          d["START_ADDRESS_LINE1"] = ride[9]
            #         d["START_ADDRESS_LINE2"] = ride[10]
            #           d["START_CITY"] = ride[11]
            #          d["START_STATE"] = ride[12]
            #          d["START_ZIP_CODE"] = ride[13]
            data.append(d)
        final_dat = json.dumps(data)
        return final_dat

    def getrides_username(
        self, eventId, userId
    ):  # to send offered rides data when eventId and userId is provided
        userId = "khoston10"
        eventId = 4704993
        data = []
        self.cursor.execute(
            """ 
        SELECT RO.EVENT_ID, RO.RIDE_ID, RO.USERNAME, RO.START_TIME, RR.STATUS
        FROM (SELECT * FROM RIDES_OFFERED WHERE EVENT_ID= %s AND USERNAME NOT IN (%s) ) AS RO 
        LEFT OUTER JOIN RIDES_REQUESTED AS RR ON RR.RIDE_ID = RO.RIDE_ID""",
            [eventId, userId],
        )
        ridesdata = self.cursor.fetchall()
        for ride in ridesdata:
            print(ride)
            d = collections.OrderedDict()
            d["EVENT_ID"] = ride["EVENT_ID"]
            d["RIDE_ID"] = ride["RIDE_ID"]
            d["RIDE_HOST_USERNAME"] = ride["USERNAME"]
            d["START_TIME"] = ride["START_TIME"].strftime("%d-%m-%Y %H:%M:%S")
            d["STATUS"] = ride["STATUS"] or "NULL"
            data.append(d)
        final_dat = json.dumps(data)
        return final_dat

    def enterUser(self, data):
        print()
        print('!!In enterUser!!')
        #Generate username
        userName = data['firstName'][:3] + data['lastName'] + str(random.randint(10, 99))

        #Generate password Hash
        hashed_password = (hashlib.md5(data['password'].encode())).hexdigest()
        print('password hex is', hashed_password)

        try:
            self.cursor.execute(
                'Select * from USER where EMAIL_ID ="%s"' % (data["email"])
            )
            response = self.cursor.fetchall()
            print("Select resp", response)
            if response:
                return "Email already present. Try a new email-id"
            else:
                self.cursor.execute(
                    'INSERT INTO USER (USERNAME, PASSWORD, FIRST_NAME, LAST_NAME, CONTACT_NO, EMAIL_ID ) VALUES ("%s", "%s", "%s", "%s", "%s", "%s")'
                    % (
                        userName,
                        hashed_password,
                        data["firstName"],
                        data["lastName"],
                        data["phoneNumber"],
                        data["email"],
                    )
                )
                self.mysql.connection.commit()
                return "Success"
        except Exception as e:
            return "error:" + str(e)