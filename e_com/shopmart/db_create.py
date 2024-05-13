# Creating a Database
import mysql.connector

mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '12345'
)

mycursor = mydb.cursor()

mycursor.execute("create database shopmart")