import mariadb
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
app=Flask(__name__)
app.secret_key = 'ahmed'
@app.route('/login',methods=['POST'])
def login():
 if request.method=='POST':
    emailForLogin=request.json.get('email')
    passForLogin=request.json.get('password')
    conn = mariadb.connect(
        user="root",
        password="ahmed2006",
        host="localhost",
        database="internship",
        port=3306
    )
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email=%s AND password=%s", (emailForLogin, passForLogin))

    logged_in_user_id = cur.fetchone()
    if logged_in_user_id:
        session['id'] = logged_in_user_id[0]

        return jsonify({"message": "Login succesful","email":emailForLogin,"password":passForLogin}),200
    else:
        return jsonify({"message": "invalid email or password"}),401
 #return render_template('login.html')



@app.route('/ContactList')
def contactList():
    conn = mariadb.connect(
        user="root",
        password="ahmed2006",
        host="localhost",
        database="internship",
        port=3306
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM contacts")
    contacts = cur.fetchall()
    #return render_template('ContactList.html')

@app.route('/contactDetails',methods=['GET', 'POST'])
def contactDetails(id):
    conn = mariadb.connect(
        user="root",
        password="ahmed2006",
        host="localhost",
        database="internship",
        port=3306
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM contacts WHERE id=?", (id,))
    if request.method=='POST':
        newEmail=request.form['newEmail']
        newPhone=request.form['newPhone']
        newName=request.form['newName']
        cur.execute("UPDATE contacts SET name=?,phone=?,email=?  WHERE id=?", (newName,newPhone,newEmail, id))
        return redirect(url_for('contactList.html'))
   # return render_template('contactDetails.html')


@app.route('/newContact',methods=['GET', 'POST'])
def addNewContact():
    conn = mariadb.connect(
        user="root",
        password="ahmed2006",
        host="localhost",
        database="internship",
        port=3306
    )
    cur = conn.cursor()
    user_id = session['user_id']
    optionalEmail = request.form['email_optional']
    PhoneNumber = request.form['phone_mandatory']
    name = request.form['name_mandatory']
    if request.method=='POST':
        cur.execute("INSERT INTO contacts(user_id,name,email,phone) VALUES(?,?,?,?),(user_id,name,optionalEmail,phoneNumber)")



if __name__ == '__main__':
    app.run(debug=True)
