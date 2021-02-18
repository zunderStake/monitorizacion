from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
app = Flask(__name__)
#mysql conexion
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Td220201*'
app.config['MYSQL_DB'] = 'monitor'
mysql = MySQL(app)

#sesion app
app.secret_key = 'mysecretkey'

@app.route('/')
def Index():
    cur_mysql = mysql.connection.cursor()
    cur_mysql.execute('SELECT * FROM contacts')
    data = cur_mysql.fetchall()
    return render_template('add_contact.html', contacts=data)

@app.route('/add_contact',methods=['POST'])
def add_contact():
    if request.method=='POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        cur_mysql = mysql.connection.cursor()
        cur_mysql.execute('INSERT INTO contacts (fullname, phone, email) VALUES (%s, %s, %s)', (fullname, phone, email))
        mysql.connection.commit()
        flash('Contact Added sucessfully')
        return redirect(url_for('Index'))

@app.route('/edit/<string:id>')
def get_contact(id):
    cur_mysql = mysql.connection.cursor()
    cur_mysql.execute('SELECT * FROM contacts WHERE id=%s',(id))
    mysql.connection.commit()
    data = cur_mysql.fetchall()
    return render_template('edit_contact.html', contact=data[0])

@app.route('/update/<string:id>',methods=['POST'])
def update_contact(id):
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        cur_mysql = mysql.connection.cursor()
        cur_mysql.execute("""
        UPDATE contacts 
        SET fullname = %s,
            phone = %s,
            email = %s
        where id = %s 
        """, (fullname, phone, email, id))
        mysql.connection.commit()
        flash('Contact Update sucessfully')
        return redirect(url_for('Index'))

@app.route('/delete/<string:id>')
def del_contact(id):
    cur_mysql = mysql.connection.cursor()
    cur_mysql.execute('DELETE FROM contacts where id = {0}'.format(id))
    mysql.connection.commit()
    flash('Contact Delete sucessfully')
    return redirect(url_for('Index'))

if __name__ == '__main__':
 app.run(port = 5050, debug = True)