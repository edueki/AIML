import mysql.connector

cnx = mysql.connector.connect(user='root', password='Admin123',
                              host='localhost',
                              database='logindb')
# print (cnx)

cursor = cnx.cursor()
response = cursor.execute('SELECT * FROM signup WHERE username="pr"')
rows = cursor.fetchall()

for row in rows:
    id, username, password, email = row
    print (id, username, password, email)