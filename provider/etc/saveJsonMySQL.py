import json
import mysql.connector

mydb = mysql.connector.connect(host = "localhost", user = "root", password = "0000", database = "metaports")
mycursor = mydb.cursor()

json_data = []

with open('data.json') as json_file:
    json_data = json.load(json_file)

for x in json_data:
    val = []
    for y in x:
        val.append(y)
    
    sql = "INSERT INTO coordinates (keypoint_id, x_coordinate, y_coordinate) VALUES (%s, %s, %s)"
    mycursor.execute(sql, val)
    mydb.commit()