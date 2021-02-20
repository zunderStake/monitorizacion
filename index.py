from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import os, sys, subprocess, psutil


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
    return render_template('index.html')

#Autodiscovery
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
                    else:
                        flash('Autodiscovery terminado')
        return render_template('inventory.html')
#Inventario
@app.route('/inventory')
def Inventory():
    cur_mysql = mysql.connection.cursor()
    cur_mysql.execute('SELECT * FROM inventory_ip where ACTIVE=1')
    data = cur_mysql.fetchall()
    return render_template('inventory.html', servers=data)

@app.route('/edit_server/<string:id>')
def get_server(id):
    cur_mysql = mysql.connection.cursor()
    cur_mysql.execute('SELECT * FROM inventory_ip WHERE ID_IP={0}'.format(id))
    data = cur_mysql.fetchall()
    return render_template('edit_server.html', server=data[0])

@app.route('/update_server/<string:id>',methods=['POST'])
def update_contact(id):
    if request.method == 'POST':
        fullname = request.form['fullname']
        ip = request.form['ip']
        cur_mysql = mysql.connection.cursor()
        cur_mysql.execute("""
        UPDATE inventory_ip 
        SET IP = %s,
            NOMBRE = %s
        where ID_IP = %s 
        """, (ip, fullname, id))
        mysql.connection.commit()
        flash('Servidor actualizado correctamente')
        return redirect(url_for('Inventory'))

@app.route('/delete_server/<string:id>')
def del_contact(id):
    cur_mysql = mysql.connection.cursor()
    cur_mysql.execute('DELETE FROM inventory_ip where ID_IP = {0}'.format(id))
    mysql.connection.commit()
    flash('Servidor eliminado correctamente')
    return redirect(url_for('Inventory'))

#Dashboard Servidor
@app.route('/dashboard/<string:id>')
def dashboard_server(id):
    cur_mysql = mysql.connection.cursor()
    cur_mysql.execute('SELECT * FROM thresholds')
    data_thresholds = cur_mysql.fetchall()
    cur_mysql = mysql.connection.cursor()
    cur_mysql.execute('SELECT * FROM inventory_ip WHERE ID_IP={0}'.format(id))
    data = cur_mysql.fetchall()
    #USO_CPU
    cpu=psutil.cpu_percent(interval=1)
    #MEMORIA
    vm_memory=psutil.virtual_memory()
    swap_memory = psutil.swap_memory()
    #RED
    red = psutil.net_io_counters(pernic=True)
    #unidades
    particiones = psutil.disk_partitions()
    count_discos = 0
    discos = []
    for x in range(0, len(particiones)):
        #DISCOS
        disk_usage = psutil.disk_usage(particiones[x][0])
        nombre_particion = particiones[x][0]
        #TOTAL_BRUTO
        disk_total_bruto = str(disk_usage.total / 1024 ** 3)
        #TOTAL_GB
        disk_total_gb = format(disk_total_bruto[:disk_total_bruto.index('.') + 2] + "GB")
        #USADO_BRUTO
        disk_used_gb_bruto = str(disk_usage.used / 1024 ** 3)
        #USADO_GB
        disk_used_gb = format(disk_used_gb_bruto[:disk_used_gb_bruto.index('.') + 2] + "GB")
        #LIBRE_BRUTO
        disk_free_gb_bruto = str(disk_usage.free / 1024 ** 3)
        #LIBRE_GB
        disk_free_gb = format(disk_free_gb_bruto[:disk_free_gb_bruto.index('.') + 2] + "GB")
        info_disco = [nombre_particion, disk_total_gb, disk_used_gb, disk_free_gb]
        discos.append([count_discos, info_disco])
        count_discos = count_discos + 1
    print(red)
    return render_template('dashboard_server.html', thresholds=data_thresholds, server=data[0], numero_particiones=count_discos, discos=discos, cpu=cpu, vm_memory=vm_memory, swap_memory=swap_memory, red=red)

if __name__ == '__main__':
 app.run(port = 5050, debug = True)