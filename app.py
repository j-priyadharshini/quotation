from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import yfinance as yf

import pandas as pd
import json
import plotly
import plotly.express as px

from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime
import cherrypy

import pyttsx3

from dotenv import load_dotenv   #for python-dotenv method
load_dotenv(".env")                    #for python-dotenv method

import os 

from flask_mail import  Mail, Message
from random import * 
import smtplib

app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'poorni123'
app.config['MYSQL_DB'] = 'onlinequotation'


# Intialize MySQL
mysql = MySQL(app)


### FRONT PAGE

@app.route("/")
def front():
    return render_template('front.html')

@app.route('/contact_us' , methods=['GET'])
def contact_us():
    return render_template('contact_us.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = % s AND password = % s', (email, password ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            # return redirect(url_for('home'))
            if account['usertype'] == 'admin':
                return render_template('admin_home.html', msg = msg,name=session['username'])
            else:
                return render_template('user_home.html', msg = msg,name=session['username'])
           

        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

    
@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html',name=session['username'])

### ADMIN

### SUPPLIER MASTER

@app.route('/home/supplier_master', methods=['GET'])
def supplier_master():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM suppliermaster")
    data = cur.fetchall()
    
    return render_template('supplier_master.html', suppliers =data ,name=session['username'])

@app.route('/home/supplier_master/insert', methods = ['POST'])
def insert():

    if request.method == "POST":
        flash("Data Inserted Successfully")
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        city = request.form['city']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO suppliermaster (sm_name, sm_email, sm_mobile, sm_city) VALUES (%s, %s, %s,%s)", (name, email, phone,city))
        mysql.connection.commit()
        return redirect(url_for('supplier_master'))


@app.route('/home/supplier_master/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM suppliermaster WHERE sm_code=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('supplier_master'))


@app.route('/home/supplier_master/update',methods=['POST','GET'])
def update():

    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        city = request.form['city']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE suppliermaster
               SET name=%s, email=%s, phone=%s, city= %s
               WHERE id=%s
            """, (name, email, phone, id_data))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('supplier_master'))



### ITEM MASTER

@app.route('/home/item_master', methods=['GET'])
def item_master():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM itemmaster")
    data = cur.fetchall()
    
    return render_template('item_master.html', items =data ,name=session['username'])


@app.route('/home/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/home/help', methods=['GET'])
def help():
    return render_template('help.html')


### USER

@app.route('/home/quotation_list', methods=['GET'])
def quotation_list():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM suppliermaster")
    data = cur.fetchall()
    
    return render_template('quotation_list.html', suppliers =data ,name=session['username'])


if __name__ == '__main__':
    app.run(debug=True) #Run the Server

