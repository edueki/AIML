import mysql.connector

cnx = mysql.connector.connect(user='root', password='Admin123',
                              host='localhost',
                              database='logindb')

cursor = cnx.cursor()