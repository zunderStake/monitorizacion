from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import os, sys
import subprocess

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

@app.route('/autodiscovery')
def AutoDiscovery():
    return render_template('autodiscovery.html')

@app.route('/search_autodiscovery',methods=['POST'])
def Search_AutoDiscovery():
    if request.method=='POST':
        def ping(ip_ping):
            p = subprocess.Popen(['ping', '-n', '1', '-w', '2', ip_ping])
            p.wait()
            return '1' if p.poll() == 0 else '0'
        ip_initial = request.form['ip_initial']
        ip_finished = request.form['ip_finished']
        first_ip_octates = ip_initial.split(".")
        finished_ip_octates = ip_finished.split(".")
        ip_incrementa = int(first_ip_octates[3])
        ip_final_incrementa = int(finished_ip_octates[3])
        numero_server = 0
        if first_ip_octates[0]==finished_ip_octates[0]:
            if first_ip_octates[1] == finished_ip_octates[1]:
                if first_ip_octates[2] == finished_ip_octates[2]:
                    while ip_incrementa <= ip_final_incrementa:
                        ip_incrementa_string = str(ip_incrementa)
                        ip_ping =first_ip_octates[0] + "." + first_ip_octates[1] + "." + first_ip_octates[2] + "." + ip_incrementa_string
                        response = int(ping(ip_ping))
                        if response == 1:
                            cur_mysql = mysql.connection.cursor()
                            cur_mysql.execute('INSERT INTO inventory_ip (IP, NOMBRE, ACTIVE) VALUES (%s, %s, %s)',(ip_ping, ip_ping, 1))
                            mysql.connection.commit()
                            numero_server += 1
                        else:
                            pingstatus = "Network Error"
                        ip_incrementa += 1
        flash('Autodiscovery terminado, se han agregado %s IP.',(numero_server))
        return render_template('inventory.html')

@app.route('/inventory')
def Inventory():
    return render_template('inventory.html')

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