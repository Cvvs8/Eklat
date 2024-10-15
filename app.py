from flask import Flask, request, render_template, redirect, url_for, session
import bcrypt
import json
import os
from flask_mysqldb import MySQL
from datetime import date
from datetime import datetime


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_default_secret_key')

# Configuración de conexión a MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Carlosv.Usa8132'  # Cambia esto si tienes una contraseña
app.config['MYSQL_DB'] = 'eklatClientes'

# Inicializar la conexión con MySQL
mysql = MySQL(app)

# Función para cargar los usuarios
def load_users():
    with open('users.json', 'r') as file:
        return json.load(file)
    
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return 'Por favor ingresa tanto el nombre de usuario como la contraseña.', 400

        password_bytes = password.encode('utf-8')
        users = load_users()

        if username in users:
            stored_hash = users[username].encode('utf-8')
            if bcrypt.checkpw(password_bytes, stored_hash):
                session['username'] = username
                return redirect(url_for('menu'))
            else:
                return 'Inicio de sesión fallido. Verifica tus credenciales.', 401
        else:
            return 'Inicio de sesión fallido. Verifica tus credenciales.', 401

    return render_template('login.html')

@app.route('/menu')
def menu():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('Menu.html')  # Asegúrate de que exista la plantilla Menu.html

@app.route('/nueva_orden')
def nueva_orden():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Obtener el último número de orden
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT MAX(pedido_id) FROM pedidos')
    max_pedido_id = cursor.fetchone()[0]
    
    if max_pedido_id is None:
        nuevo_numero_orden = 6467  # Si no hay órdenes, iniciar en 1
    else:
        nuevo_numero_orden = max_pedido_id + 1  # Incrementar en 1

    # Pasar el número de orden a la plantilla index.html
    return render_template('index.html', numero_orden=nuevo_numero_orden)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/submit', methods=['POST'])
def submit():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        # Obtener el último número de orden (pedido_id) más alto de la tabla pedidos
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT MAX(pedido_id) FROM pedidos')
        max_pedido_id = cursor.fetchone()[0]  # Obtener el número de orden más alto
        if max_pedido_id is None:
            nuevo_numero_orden = 6467  # Si no hay órdenes, iniciar con 6467
        else:
            nuevo_numero_orden = max_pedido_id + 1  # Incrementar en 1
        # Recibir los datos del pedido del formulario
        datos_pedido = {
            'fecha': request.form.get('fecha', '00-00-0000'),
            'nombre_laboratorio': request.form.get('nombre_laboratorio', ''),
            'vendedor': request.form.get('vendedor', ''),
            'nombre_cliente': request.form.get('nombre_cliente', ''),
            'tipo_identificacion': request.form.get('tipo_identificacion', ''),
            'numero_identificacion': request.form.get('numero_identificacion', ''),
            'direccion_entrega': request.form.get('direccion_entrega', ''),
            'departamento': request.form.get('departamento', ''),
            'ciudad': request.form.get('ciudad', ''),
            'barrio': request.form.get('barrio', ''),
            'telefonos': request.form.get('telefonos', ''),
            'email': request.form.get('email', ''),
            'tipo_regimen_iva': request.form.get('tipo_regimen_iva', ''),
            'codigo_montura': request.form.get('codigo_montura', ''),
            'valor_montura': request.form.get('valor_montura', '0'),  # Valor predeterminado
            'codigo_lente': request.form.get('codigo_lente', ''),
            'valor_lente': request.form.get('valor_lente', '0'),  # Valor predeterminado
            'otros': request.form.get('otros', ''),
            'valor_otros': request.form.get('valor_otros', '0'),  # Valor predeterminado
            'total_venta': request.form.get('total_venta', '0'),  # Valor predeterminado
            'guia_despacho': request.form.get('guia_despacho', ''),
            'fecha_entrega': request.form.get('fecha_entrega', None),
            'fecha_lab': request.form.get('fecha_lab', '00-00-0000'),
            'observaciones': request.form.get('observaciones', ''),
            'ordenado_a': request.form.get('ordenado_a', ''),
            'ordenado_por': request.form.get('ordenado_por', '')
        }

        def convertir_fecha(fecha):
            if fecha and fecha != '00/00/0000':  # Si la fecha no está vacía
                try:
                    return datetime.strptime(fecha, '%d/%m/%Y').strftime('%Y-%m-%d')
                except ValueError:
                    return None  # Si hay algún problema con la conversión, usar None (NULL en SQL)
            return None  # Fecha vacía o inválida


        datos_pedido['fecha'] = convertir_fecha(datos_pedido['fecha'])
        datos_pedido['fecha_entrega'] = convertir_fecha(datos_pedido['fecha_entrega'])
        datos_pedido['fecha_lab'] = convertir_fecha(datos_pedido['fecha_lab']) 
        # Convertir valores numéricos a float
        try:
            datos_pedido['valor_montura'] = float(datos_pedido['valor_montura'] or 0.0)
            datos_pedido['valor_lente'] = float(datos_pedido['valor_lente'] or 0.0)
            datos_pedido['valor_otros'] = float(datos_pedido['valor_otros'] or 0.0)
            datos_pedido['total_venta'] = float(datos_pedido['total_venta'] or 0.0)
        except ValueError as e:
            return f"Error en la conversión de valores numéricos: {str(e)}"


        # Insertar datos en la tabla clientes
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO clientes (nombre_cliente, tipo_identificacion, numero_identificacion, direccion_entrega, departamento, ciudad, barrio, telefonos, email, regimen_iva, ordenado_a, ordenado_por)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        ''', (datos_pedido['nombre_cliente'], 
              datos_pedido['tipo_identificacion'], 
              datos_pedido['numero_identificacion'], 
              datos_pedido['direccion_entrega'],
              datos_pedido['departamento'],  
              datos_pedido['ciudad'], 
              datos_pedido['barrio'], 
              datos_pedido['telefonos'], 
              datos_pedido['email'], 
              datos_pedido['tipo_regimen_iva'],
              datos_pedido['ordenado_a'],
              datos_pedido['ordenado_por']
              ))
        mysql.connection.commit()
        cliente_id = cursor.lastrowid  # Obtener el ID del último cliente insertado

        if datos_pedido['fecha_entrega'] == '':
            datos_pedido['fecha_entrega'] = None


        # Insertar el nuevo pedido con el número de orden nuevo
        cursor.execute('''
            INSERT INTO pedidos (pedido_id, cliente_id, nombre_laboratorio, vendedor, codigo_montura, valor_montura, codigo_lente, valor_lente, otros, valor_otros, total_venta, fecha_entrega, guia_despacho, observaciones, fecha)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (nuevo_numero_orden,
              cliente_id, 
              datos_pedido['nombre_laboratorio'], 
              datos_pedido['vendedor'], 
              datos_pedido['codigo_montura'], 
              datos_pedido['valor_montura'], 
              datos_pedido['codigo_lente'], 
              datos_pedido['valor_lente'], 
              datos_pedido['otros'], 
              datos_pedido['valor_otros'], 
              datos_pedido['total_venta'], 
              datos_pedido['fecha_entrega'], 
              datos_pedido['guia_despacho'],
              datos_pedido['observaciones'],
              datos_pedido['fecha']))
        mysql.connection.commit()
        pedido_id = cursor.lastrowid  # Obtener el ID del último pedido insertado

        # Insertar detalles de lentes en la tabla detalles_lentes
        datos_lentes = {
            'esfera_od': request.form.get('esfera_od', ''),
            'cilindro_od': request.form.get('cilindro_od', ''),
            'eje_od': request.form.get('eje_od', ''),
            'adicion_od': request.form.get('adicion_od', ''),
            'dp_od': request.form.get('dp_od', ''),
            'esfera_oi': request.form.get('esfera_oi', ''),
            'cilindro_oi': request.form.get('cilindro_oi', ''),
            'eje_oi': request.form.get('eje_oi', ''),
            'adicion_oi': request.form.get('adicion_oi', ''),
            'dp_oi': request.form.get('dp_oi', '')
        }

        cursor.execute('''
            INSERT INTO detalles_lentes (pedido_id, esfera_od, cilindro_od, eje_od, adicion_od, dp_od, esfera_oi, cilindro_oi, eje_oi, adicion_oi, dp_oi)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (pedido_id, 
              datos_lentes['esfera_od'], 
              datos_lentes['cilindro_od'], 
              datos_lentes['eje_od'], 
              datos_lentes['adicion_od'], 
              datos_lentes['dp_od'], 
              datos_lentes['esfera_oi'], 
              datos_lentes['cilindro_oi'], 
              datos_lentes['eje_oi'], 
              datos_lentes['adicion_oi'], 
              datos_lentes['dp_oi']))
        mysql.connection.commit()

        # Insertar datos del laboratorio en la tabla orden_laboratorio
        # Obtener valores del formulario, asegurándose de que los nombres coincidan con el HTML
        datos_laboratorio = {
            'montura': request.form.get('montura', ''),
            'color': request.form.get('color', ''),
            'material_lentes': request.form.get('material_lentes', ''),
            'ar': request.form.get('ar', ''),
            'ar_otro': request.form.get('ar_otro', '') if request.form.get('ar') == 'Otro' else '',  # Solo si el AR es "Otro"
            'progresivo': request.form.get('progresivo', ''),
            'progresivo_gama': request.form.get('progresivo_gama', '') if request.form.get('progresivo') == 'SI' else '',  # Solo si el progresivo es "SI"
            'monofocal': request.form.get('monofocal', ''),
            'monofocal_option': request.form.get('monofocal_option', '') if request.form.get('monofocal') == 'SI' else '',  # Solo si el monofocal es "SI"
            'fotocromatico': request.form.get('fotocrom', ''),
            'fotocromatico_cual': request.form.get('fotocromatico_cual', '') if request.form.get('fotocromatico') == 'SI' else '',  # Solo si el fotocromático es "SI"
            'bifocal': request.form.get('bifocal', ''),
            'af': request.form.get('af', ''),
            'corredor': request.form.get('corredor', ''),
            'adicional': request.form.get('adicional', '')
        }
        

        # Ajustar los valores de AR
        ar = datos_laboratorio['ar']
        if ar == 'Otro':
            ar = datos_laboratorio.get('ar_otro', '')

        # Los valores de progresivo y monofocal se mantienen como están
        progresivo = datos_laboratorio['progresivo']
        gama_progresivo = datos_laboratorio.get('progresivo_gama', '') if progresivo == 'SI' else ''  # Obtener 'gama_progresivo'

        monofocal = datos_laboratorio['monofocal']
        opcion_monofocal = datos_laboratorio.get('monofocal_option', '') if monofocal == 'SI' else ''  # Obtener 'opcion_monofocal'

        fotocromatico = request.form.get('fotocrom', '')
        fotocromatico_cual = request.form.get('fotocromatico_cual', '') if fotocromatico == 'SI' else ''

        # Ejecutar la inserción en la base de datos con los valores corregidos
        cursor.execute('''
            INSERT INTO orden_laboratorio (pedido_id, montura, color, material_lentes, ar, progresivo, gama_progresivo, monofocal, opcion_monofocal, fotocromatico, bifocal, af, corredor, adicional, fecha_lab, gama_fotocromatico)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (nuevo_numero_orden,
            datos_laboratorio['montura'],
            datos_laboratorio['color'],
            datos_laboratorio['material_lentes'],
            ar,  # Valor de AR, que puede ser 'Otro'
            progresivo,  # Valor de progresivo (SI/NO)
            gama_progresivo,  # Valor de gama progresivo si 'SI'
            monofocal,  # Valor de monofocal (SI/NO)
            opcion_monofocal,  # Valor de opción monofocal si 'SI'
            fotocromatico,  # Valor de fotocromático
            datos_laboratorio['bifocal'],  # Valor de bifocal
            datos_laboratorio['af'],  # Valor de AF
            datos_laboratorio['corredor'],  # Valor de corredor
            datos_laboratorio['adicional'],  # Valor adicional
            datos_pedido['fecha'],
            fotocromatico_cual
        ))

        # Hacer commit para guardar los cambios en la base de datos
        mysql.connection.commit()

        # Insertar datos de pagos en la tabla pagos
        pagos = {
            'pago_efectivo': int(request.form.get('pago_efectivo', '0') or 0),
            'pago_bancolombia': int(request.form.get('pago_bancolombia', '0') or 0),
            'pago_davivienda': int(request.form.get('pago_davivienda', '0') or 0),
            'pasa_pagos': int(request.form.get('pasa_pagos', '0') or 0),
            'pago_bold': int(request.form.get('pago_bold', '0') or 0),
            'pago_mercadopago': int(request.form.get('pago_mercadopago', '0') or 0),
            'pago_sistecredito': int(request.form.get('pago_sistecredito', '0') or 0),
            'pago_addi': int(request.form.get('pago_addi', '0') or 0),
            'pago_envia': int(request.form.get('pago_envia', '0') or 0),
            'pago_interapidismo': int(request.form.get('pago_interapidismo', '0') or 0),
            'pago_servientrega': int(request.form.get('pago_servientrega', '0') or 0),
            'pago_otro': int(request.form.get('pago_otro', '0') or 0),
            'pago_mensajeria_eklat':int(request.form.get('pago_mensajeria_eklat', '0') or 0)
        }


        cursor.execute('''
            INSERT INTO pagos (pedido_id, pago_efectivo, pago_bancolombia, pago_davivienda, pasa_pagos, pago_bold, pago_mensajeria_eklat, pago_mercadopago, pago_sistecredito, pago_addi, pago_envia, pago_interapidismo, pago_servientrega, pago_otro)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (pedido_id, 
              pagos['pago_efectivo'], 
              pagos['pago_bancolombia'], 
              pagos['pago_davivienda'], 
              pagos['pasa_pagos'], 
              pagos['pago_bold'], 
              pagos['pago_mensajeria_eklat'],
              pagos['pago_mercadopago'],  
              pagos['pago_sistecredito'], 
              pagos['pago_addi'], 
              pagos['pago_envia'], 
              pagos['pago_interapidismo'], 
              pagos['pago_servientrega'], 
              pagos['pago_otro']))
        mysql.connection.commit()

        return render_template('Confirmacion_Orden.html')

    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Ocurrió un error: {str(e)}"


@app.route('/consulta/<int:pedido_id>', methods=['GET','POST'])
def ver_orden(pedido_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # Consulta los detalles del pedido
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT clientes.nombre_cliente, clientes.tipo_identificacion, clientes.numero_identificacion, 
               clientes.direccion_entrega, clientes.departamento, clientes.ciudad, clientes.barrio, 
               clientes.telefonos, clientes.email, clientes.regimen_iva, clientes.ordenado_a, clientes.ordenado_por,
               pedidos.pedido_id, pedidos.nombre_laboratorio, pedidos.vendedor, pedidos.codigo_montura, 
               pedidos.valor_montura, pedidos.codigo_lente, pedidos.valor_lente, pedidos.otros, 
               pedidos.valor_otros, pedidos.total_venta, pedidos.guia_despacho, pedidos.fecha_entrega, 
               pedidos.observaciones, pedidos.fecha
        FROM pedidos
        JOIN clientes ON pedidos.cliente_id = clientes.cliente_id
        WHERE pedidos.pedido_id = %s
    ''', (pedido_id,))
    pedido = cursor.fetchone()

    if not pedido:
        return "No se encontró el pedido."
    
    fecha_entrega=pedido[23]
    puede_modificar = not fecha_entrega or fecha_entrega == '0000-00-00' or fecha_entrega == '00/00/0000'

    # Consultar la información adicional del laboratorio
    cursor.execute('''
        SELECT montura, color, material_lentes, ar, progresivo, gama_progresivo, monofocal, 
               opcion_monofocal, fotocromatico, bifocal, af, corredor, adicional, fecha_lab, gama_fotocromatico
        FROM orden_laboratorio
        WHERE pedido_id = %s
    ''', (pedido_id,))
    orden_laboratorio = cursor.fetchone()

    # Consultar los detalles de los lentes
    cursor.execute('''
        SELECT esfera_od, cilindro_od, eje_od, adicion_od, dp_od, esfera_oi, cilindro_oi, eje_oi, adicion_oi, dp_oi
        FROM detalles_lentes
        WHERE pedido_id = %s
    ''', (pedido_id,))
    detalles_lentes = cursor.fetchone()

    # Consultar los detalles de los pagos
    cursor.execute('''
        SELECT pago_efectivo, pago_bancolombia, pago_davivienda, pasa_pagos, pago_bold, pago_mensajeria_eklat, 
               pago_mercadopago, pago_sistecredito, pago_addi, pago_envia, pago_interapidismo, pago_servientrega, pago_otro
        FROM pagos
        WHERE pedido_id = %s
    ''', (pedido_id,))
    pagos = cursor.fetchone()

    # Comprobar si las consultas devolvieron valores
    if not orden_laboratorio:
        orden_laboratorio = ('', '', '', '', '', '', '', '', '', '', '', '', '', '', '')

    if not detalles_lentes:
        detalles_lentes = ('', '', '', '', '', '', '', '', '', '')

    if not pagos:
        pagos = ('', '', '', '', '', '', '', '', '', '', '', '', '')

    # Renderizar la plantilla con todos los datos
    return render_template(
            'Res_Consulta.html',
            cliente_id=pedido[12],
            dia=pedido[25].day if pedido[25] else '00',
            mes=pedido[25].month if pedido[25] else '00',
            año=pedido[25].year if pedido[25] else '0000',
            nombre_laboratorio=pedido[13],
            vendedor=pedido[14],
            nombre_cliente=pedido[0],
            tipo_identificacion=pedido[1],
            numero_identificacion=pedido[2],
            departamento=pedido[4],
            ciudad=pedido[5],
            barrio=pedido[6],
            direccion_entrega=pedido[3],
            telefonos=pedido[7],
            email=pedido[8],
            regimen_iva=pedido[9],
            codigo_montura=pedido[15],
            valor_montura=pedido[16],
            codigo_lente=pedido[17],
            valor_lente=pedido[18],
            otros=pedido[19],
            valor_otros=pedido[20],
            total_venta=pedido[21],
            guia_despacho=pedido[22],
            dia_ent=pedido[23].day if pedido[23] else '00',
            mes_ent=pedido[23].month if pedido[23] else '00',
            año_ent=pedido[23].year if pedido[23] else '0000',
            observaciones=pedido[24],
            esfera_od=detalles_lentes[0],
            cilindro_od=detalles_lentes[1],
            eje_od=detalles_lentes[2],
            adicion_od=detalles_lentes[3],
            dp_od=detalles_lentes[4],
            esfera_oi=detalles_lentes[5],
            cilindro_oi=detalles_lentes[6],
            eje_oi=detalles_lentes[7],
            adicion_oi=detalles_lentes[8],
            dp_oi=detalles_lentes[9],
            montura=orden_laboratorio[0],
            color=orden_laboratorio[1],
            material_lentes=orden_laboratorio[2],
            ar=orden_laboratorio[3],
            progresivo=orden_laboratorio[4],
            gama_progresivo=orden_laboratorio[5],
            monofocal=orden_laboratorio[6],
            opcion_monofocal=orden_laboratorio[7],
            fotocrom=orden_laboratorio[8],
            fotocromatico_cual=orden_laboratorio[14],
            bifocal=orden_laboratorio[9],
            af=orden_laboratorio[10],
            corredor=orden_laboratorio[11],
            adicional=orden_laboratorio[12],
            ordenado_a=pedido[10],
            ordenado_por=pedido[11],
            pago_efectivo=pagos[0],
            pago_bancolombia=pagos[1],
            pago_davivienda=pagos[2],
            pasa_pagos=pagos[3],
            pago_bold=pagos[4],
            pago_mensajeria_eklat=pagos[5],
            pago_mercadopago=pagos[6],
            pago_sistecredito=pagos[7],
            pago_addi=pagos[8],
            pago_envia=pagos[9],
            pago_interapidismo=pagos[10],
            pago_servientrega=pagos[11],
            pago_otro=pagos[12],
            puede_modificar=puede_modificar  # Según lógica
        )



@app.route('/imprimir_laboratorio/<int:pedido_id>')
def imprimir_laboratorio(pedido_id):
    cursor = mysql.connection.cursor()

    # Consulta los datos del pedido correspondiente al pedido_id proporcionado
    cursor.execute('''
        SELECT clientes.nombre_cliente, clientes.ordenado_a, clientes.ordenado_por,
               pedidos.fecha, pedidos.pedido_id, pedidos.codigo_montura,
               detalles_lentes.esfera_od, detalles_lentes.cilindro_od, detalles_lentes.eje_od, detalles_lentes.adicion_od, detalles_lentes.dp_od,
               detalles_lentes.esfera_oi, detalles_lentes.cilindro_oi, detalles_lentes.eje_oi, detalles_lentes.adicion_oi, detalles_lentes.dp_oi,
               orden_laboratorio.material_lentes, orden_laboratorio.ar, orden_laboratorio.gama_fotocromatico, orden_laboratorio.color, orden_laboratorio.gama_progresivo,
               orden_laboratorio.opcion_monofocal, orden_laboratorio.bifocal, orden_laboratorio.af, orden_laboratorio.corredor, orden_laboratorio.adicional
        FROM pedidos
        JOIN clientes ON pedidos.cliente_id = clientes.cliente_id
        JOIN detalles_lentes ON pedidos.pedido_id = detalles_lentes.pedido_id
        JOIN orden_laboratorio ON pedidos.pedido_id = orden_laboratorio.pedido_id
        WHERE pedidos.pedido_id = %s
    ''', (pedido_id,))

    pedido = cursor.fetchone()

    if not pedido:
        return "No se encontró ningún pedido con ese número de pedido."

    # Dividir la fecha del pedido en día, mes y año para los campos dia_lab, mes_lab, año_lab
    fecha_pedido = pedido[3]
    dia_lab = fecha_pedido.day
    mes_lab = fecha_pedido.month
    año_lab = fecha_pedido.year

    # Renderiza el template laboratorio.html con los datos correspondientes
    return render_template('laboratorio.html',
                           dia_lab=dia_lab,
                           mes_lab=mes_lab,
                           año_lab=año_lab,
                           numero_orden=pedido[4],  # pedido_id
                           ordenado_por=pedido[2],
                           ordenado_a=pedido[1],
                           montura=pedido[5],
                           esfera_od=pedido[6],
                           cilindro_od=pedido[7],
                           eje_od=pedido[8],
                           adicion_od=pedido[9],
                           dp_od=pedido[10],
                           esfera_oi=pedido[11],
                           cilindro_oi=pedido[12],
                           eje_oi=pedido[13],
                           adicion_oi=pedido[14],
                           dp_oi=pedido[15],
                           material_lentes=pedido[16],
                           ar=pedido[17],
                           fotocromatico_cual=pedido[18],
                           color_lente=pedido[19],
                           progresivo=pedido[20],
                           monofocal=pedido[21],
                           bifocal=pedido[22],
                           af = pedido[23],
                           corredor = pedido[24],
                           adicional=pedido[25])


@app.route('/imprimir_pedido/<int:pedido_id>')
def imprimir_pedido(pedido_id):
    cursor = mysql.connection.cursor()

    # Consulta los datos del pedido y cliente usando el pedido_id
    cursor.execute('''
        SELECT clientes.nombre_cliente, clientes.numero_identificacion, clientes.direccion_entrega, clientes.departamento, clientes.ciudad, clientes.barrio, clientes.telefonos, clientes.email,
               pedidos.pedido_id, pedidos.nombre_laboratorio, pedidos.vendedor, pedidos.codigo_montura, pedidos.valor_montura, pedidos.codigo_lente, pedidos.valor_lente,
               pedidos.otros, pedidos.valor_otros, pedidos.total_venta, pedidos.fecha, pedidos.observaciones,
               pagos.pago_efectivo, pagos.pago_bancolombia, pagos.pago_davivienda, pagos.pasa_pagos, pagos.pago_bold, pagos.pago_mercadopago,
               pagos.pago_sistecredito, pagos.pago_addi, pagos.pago_envia, pagos.pago_interapidismo, pagos.pago_servientrega, pagos.pago_mensajeria_eklat, pagos.pago_otro
        FROM pedidos
        JOIN clientes ON pedidos.cliente_id = clientes.cliente_id
        JOIN pagos ON pedidos.pedido_id = pagos.pedido_id
        WHERE pedidos.pedido_id = %s
    ''', (pedido_id,))
    
    pedido = cursor.fetchone()

    if not pedido:
        return "No se encontró ningún pedido con ese número de pedido."

    # Manejo de fecha: la columna fecha está en el índice 18
    fecha_pedido = pedido[18]  
    dia = fecha_pedido.day
    mes = fecha_pedido.month
    año = fecha_pedido.year

    # Renderizar la plantilla pedido.html
    return render_template('pedido.html',
                           dia=dia,
                           mes=mes,
                           año=año,
                           numero_orden=pedido[8],  # pedido_id que está en el índice 8
                           nombre_laboratorio=pedido[9],  # índice 9
                           vendedor=pedido[10],  # índice 10
                           nombre_cliente=pedido[0],  # índice 0
                           identificacion_cliente=pedido[1],  # índice 1
                           direccion_entrega=pedido[2],  # índice 2
                           departamento=pedido[3],  # índice 3
                           ciudad=pedido[4],  # índice 4
                           barrio=pedido[5],  # índice 5
                           telefonos=pedido[6],  # índice 6
                           email=pedido[7],  # índice 7
                           codigo_montura=pedido[11],  # índice 11
                           valor_montura=pedido[12],  # índice 12
                           codigo_lente=pedido[13],  # índice 13
                           valor_lente=pedido[14],  # índice 14
                           otros=pedido[15],  # índice 15
                           valor_otros=pedido[16],  # índice 16
                           total_venta=pedido[17],  # índice 17
                           observaciones=pedido[19],  # observaciones en el índice 19
                           # Información de pagos (correctamente alineada)
                           pago_efectivo=pedido[20],  # índice 20
                           pago_bancolombia=pedido[21],  # índice 21
                           pago_davivienda=pedido[22],  # índice 22
                           pago_pasa_pagos=pedido[23],  # índice 23
                           pago_bold=pedido[24],  # índice 24
                           pago_mercadopago=pedido[25],  # índice 25
                           pago_sistecredito=pedido[26],  # índice 26
                           pago_addi=pedido[27],  # índice 27
                           pago_envia=pedido[28],  # índice 28
                           pago_interapidismo=pedido[29],  # índice 29
                           pago_servientrega=pedido[30],  # índice 30
                           pago_mensajeria_eklat=pedido[31],  # índice 31
                           pago_otro=pedido[32])  # índice 32


@app.route('/editar/<int:cliente_id>', methods=['GET'])
def editar(cliente_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    departamentosYciudades = {
    "Amazonas": ["Leticia", "Puerto Nariño", "El Encanto", "La Chorrera", "La Pedrera", "La Victoria", "Mirití-Paraná", "Puerto Alegría", "Puerto Arica", "Tarapacá"],
    "Antioquia": ["Abejorral", "Abriaquí", "Alejandría", "Amagá", "Amalfi", "Andes", "Angelópolis", "Angostura", "Anorí", "Santafé de Antioquia", "Anza", "Apartadó", "Arboletes", "Argelia", "Armenia", "Barbosa", "Bello", "Belmira", "Betania", "Betulia", "Briceño", "Buriticá", "Cáceres", "Caicedo", "Caldas", "Campamento", "Cañasgordas", "Caracolí", "Caramanta", "Carepa", "Carolina", "Caucasia", "Chigorodó", "Cisneros", "Cocorná", "Concepción", "Concordia", "Copacabana", "Dabeiba", "Donmatías", "Ebéjico", "El Bagre", "Entrerríos", "Envigado", "Fredonia", "Frontino", "Giraldo", "Girardota", "Gómez Plata", "Granada", "Guadalupe", "Guarne", "Guatapé", "Heliconia", "Hispania", "Itagüí", "Ituango", "Jardín", "Jericó", "La Ceja", "La Estrella", "La Pintada", "La Unión", "Liborina", "Maceo", "Marinilla", "Medellín", "Montebello", "Murindó", "Mutatá", "Nariño", "Nechí", "Necoclí", "Olaya", "Peque", "Pueblorrico", "Puerto Berrío", "Puerto Nare", "Puerto Triunfo", "Remedios", "Retiro", "Rionegro", "Sabanalarga", "Sabaneta", "Salgar", "San Andrés de Cuerquia", "San Carlos", "San Francisco", "San Jerónimo", "San José de la Montaña", "San Juan de Urabá", "San Luis", "San Pedro de los Milagros", "San Pedro de Urabá", "San Rafael", "San Roque", "San Vicente", "Santa Bárbara", "Santa Rosa de Osos", "Santo Domingo", "Segovia", "Sonsón", "Sopetrán", "Támesis", "Tarazá", "Tarso", "Titiribí", "Toledo", "Turbo", "Uramita", "Urrao", "Valdivia", "Valparaíso", "Vegachí", "Venecia", "Vigía del Fuerte", "Yalí", "Yarumal", "Yolombó", "Yondó", "Zaragoza"],
    "Arauca": ["Arauca", "Arauquita", "Cravo Norte", "Fortul", "Puerto Rondón", "Saravena", "Tame"],
    "Atlántico": ["Barranquilla", "Baranoa", "Campo de la Cruz", "Candelaria", "Galapa", "Juan de Acosta", "Luruaco", "Malambo", "Manatí", "Palmar de Varela", "Piojó", "Polonuevo", "Ponedera", "Puerto Colombia", "Repelón", "Sabanagrande", "Sabanalarga", "Santa Lucía", "Santo Tomás", "Soledad", "Suan", "Tubará", "Usiacurí"],
    "Bogotá D.C": ["Bogotá D.C."],
    "Bolívar": ["Cartagena de Indias", "Achí", "Altos del Rosario", "Arenal", "Arjona", "Arroyohondo", "Barranco de Loba", "Calamar", "Cantagallo", "Cicuco", "Clemencia", "Córdoba", "El Carmen de Bolívar", "El Guamo", "El Peñón", "Hatillo de Loba", "Magangué", "Mahates", "Margarita", "María la Baja", "Montecristo", "Morales", "Norosí", "Pinillos", "Regidor", "Río Viejo", "San Cristóbal", "San Estanislao", "San Fernando", "San Jacinto", "San Jacinto del Cauca", "San Juan Nepomuceno", "San Martín de Loba", "Santa Catalina", "Santa Rosa", "Santa Rosa del Sur", "Simití", "Soplaviento", "Talaigua Nuevo", "Tiquisio", "Turbaco", "Turbaná", "Villanueva", "Zambrano"],
    "Boyacá": ["Tunja", "Almeida", "Aquitania", "Arcabuco", "Belén", "Berbeo", "Betéitiva", "Boavita", "Boyacá", "Briceño", "Buena Vista", "Busbanzá", "Caldas", "Campohermoso", "Cerinza", "Chinavita", "Chiquinquirá", "Chíquiza", "Chiscas", "Chita", "Chitaraque", "Chivatá", "Ciénaga", "Cómbita", "Coper", "Corrales", "Covarachía", "Cubará", "Cucaita", "Cuítiva", "Chivor", "Duitama", "El Cocuy", "El Espino", "Firavitoba", "Floresta", "Gachantivá", "Gámeza", "Garagoa", "Guacamayas", "Guateque", "Guayatá", "Güicán", "Iza", "Jenesano", "Jericó", "Labranzagrande", "La Capilla", "La Uvita", "La Victoria", "Macanal", "Maripí", "Miraflores", "Mongua", "Monguí", "Moniquirá", "Motavita", "Muzo", "Nobsa", "Nuevo Colón", "Oicatá", "Otanche", "Pachavita", "Páez", "Paipa", "Pajarito", "Panqueba", "Pauna", "Paya", "Paz de Río", "Pesca", "Pisba", "Puerto Boyacá", "Quípama", "Ramiriquí", "Ráquira", "Rondón", "Saboyá", "Sáchica", "Samacá", "San Eduardo", "San José de Pare", "San Luis de Gaceno", "San Mateo", "San Miguel de Sema", "San Pablo de Borbur", "Santa María", "Santa Rosa de Viterbo", "Santa Sofía", "Santana", "Sativanorte", "Sativasur", "Siachoque", "Soatá", "Socha", "Socotá", "Sogamoso", "Somondoco", "Sora", "Sotaquirá", "Soracá", "Susacón", "Sutamarchán", "Sutatenza", "Tasco", "Tenza", "Tibaná", "Tibasosa", "Tinjacá", "Tipacoque", "Toca", "Togüí", "Tópaga", "Tota", "Tununguá", "Turmequé", "Tuta", "Tutazá", "Úmbita", "Ventaquemada", "Viracachá", "Zetaquira"],
    "Caldas": ["Manizales", "Aguadas", "Anserma", "Aranzazu", "Belalcázar", "Chinchiná", "Filadelfia", "La Dorada", "La Merced", "Manzanares", "Marmato", "Marquetalia", "Marulanda", "Neira", "Norcasia", "Pácora", "Palestina", "Pensilvania", "Riosucio", "Risaralda", "Salamina", "Samaná", "San José", "Supía", "Victoria", "Villamaría", "Viterbo"],
    "Caquetá": ["Florencia", "Albania", "Belén de los Andaquíes", "Cartagena del Chairá", "Curillo", "El Doncello", "El Paujil", "La Montañita", "Milán", "Morelia", "Puerto Rico", "San José del Fragua", "San Vicente del Caguán", "Solano", "Solita", "Valparaíso"],
    "Casanare": ["Yopal", "Aguazul", "Chámeza", "Hato Corozal", "La Salina", "Maní", "Monterrey", "Nunchía", "Orocué", "Paz de Ariporo", "Pore", "Recetor", "Sabanalarga", "Sácama", "San Luis de Palenque", "Támara", "Tauramena", "Trinidad", "Villanueva"],
    "Cauca": ["Popayán", "Almaguer", "Argelia", "Balboa", "Bolívar", "Buenos Aires", "Cajibío", "Caldono", "Caloto", "Corinto", "El Tambo", "Florencia", "Guachené", "Guapí", "Inzá", "Jambaló", "La Sierra", "La Vega", "López de Micay", "Mercaderes", "Miranda", "Morales", "Padilla", "Páez", "Patía", "Piamonte", "Piendamó", "Puerto Tejada", "Puracé", "Rosas", "San Sebastián", "Santa Rosa", "Santander de Quilichao", "Silvia", "Sotará", "Suárez", "Sucre", "Timbío", "Timbiquí", "Toribío", "Totoró", "Villa Rica"],
    "Cesar": ["Valledupar", "Aguachica", "Agustín Codazzi", "Astrea", "Becerril", "Bosconia", "Chimichagua", "Chiriguaná", "Curumaní", "El Copey", "El Paso", "Gamarra", "González", "La Gloria", "La Jagua de Ibirico", "La Paz", "Manaure Balcón del Cesar", "Pailitas", "Pelaya", "Pueblo Bello", "Río de Oro", "San Alberto", "San Diego", "San Martín", "Tamalameque"],
    "Chocó": ["Quibdó", "Acandí", "Alto Baudó", "Atrato", "Bagadó", "Bahía Solano", "Bajo Baudó", "Bojayá", "Cantón de San Pablo", "Cértegui", "Condoto", "El Carmen de Atrato", "El Carmen del Darién", "Istmina", "Juradó", "Litoral del San Juan", "Lloró", "Medio Atrato", "Medio Baudó", "Medio San Juan", "Nóvita", "Nuquí", "Río Iró", "Río Quito", "Riosucio", "San José del Palmar", "Sipí", "Tadó", "Unguía", "Unión Panamericana"],
    "Córdoba": ["Montería", "Ayapel", "Buenavista", "Canalete", "Cereté", "Chimá", "Chinú", "Ciénaga de Oro", "Cotorra", "La Apartada", "Lorica", "Los Córdobas", "Momil", "Montelíbano", "Moñitos", "Planeta Rica", "Pueblo Nuevo", "Puerto Escondido", "Puerto Libertador", "Purísima", "Sahagún", "San Andrés de Sotavento", "San Antero", "San Bernardo del Viento", "San Carlos", "San José de Uré", "San Pelayo", "Tierralta", "Tuchín", "Valencia"],
    "Cundinamarca": ["Agua de Dios", "Albán", "Anapoima", "Anolaima", "Apulo", "Arbeláez", "Beltrán", "Bituima", "Bojacá", "Cabrera", "Cachipay", "Cajicá", "Caparrapí", "Cáqueza", "Carmen de Carupa", "Chaguaní", "Chía", "Chipaque", "Choachí", "Chocontá", "Cogua", "Cota", "Cucunubá", "El Colegio", "El Peñón", "El Rosal", "Facatativá", "Fómeque", "Fosca", "Funza", "Fúquene", "Fusagasugá", "Gachalá", "Gachancipá", "Gachetá", "Gama", "Girardot", "Granada", "Guachetá", "Guaduas", "Guasca", "Guataquí", "Guatavita", "Guayabal de Síquima", "Guayabetal", "Gutiérrez", "Jerusalén", "Junín", "La Calera", "La Mesa", "La Palma", "La Peña", "La Vega", "Lenguazaque", "Machetá", "Madrid", "Manta", "Medina", "Mosquera", "Nariño", "Nemocón", "Nilo", "Nimaima", "Nocaima", "Pacho", "Paime", "Pandi", "Paratebueno", "Pasca", "Puerto Salgar", "Pulí", "Quebradanegra", "Quetame", "Quipile", "Ricaurte", "San Antonio del Tequendama", "San Bernardo", "San Cayetano", "San Francisco", "San Juan de Río Seco", "Sasaima", "Sesquilé", "Sibaté", "Silvania", "Simijaca", "Soacha", "Sopó", "Subachoque", "Suesca", "Supatá", "Susa", "Sutatausa", "Tabio", "Tausa", "Tena", "Tenjo", "Tibacuy", "Tibirita", "Tocaima", "Tocancipá", "Topaipí", "Ubalá", "Ubaque", "Ubaté", "Une", "Útica", "Venecia", "Vergara", "Vianí", "Villagómez", "Villapinzón", "Villeta", "Viotá", "Yacopí", "Zipacón", "Zipaquirá"],
    "Guainía": ["Inírida", "Barrancominas"],
    "Guaviare": ["San José del Guaviare", "Calamar", "El Retorno", "Miraflores"],
    "Huila": ["Neiva", "Acevedo", "Agrado", "Aipe", "Algeciras", "Altamira", "Baraya", "Campoalegre", "Colombia", "Elías", "Garzón", "Gigante", "Guadalupe", "Hobo", "Iquira", "Isnos", "La Argentina", "La Plata", "Nátaga", "Oporapa", "Paicol", "Palermo", "Palestina", "Pital", "Pitalito", "Rivera", "Saladoblanco", "San Agustín", "Santa María", "Suaza", "Tarqui", "Tello", "Teruel", "Tesalia", "Timaná", "Villavieja", "Yaguará"],
    "La Guajira": ["Riohacha", "Albania", "Barrancas", "Dibulla", "Distracción", "El Molino", "Fonseca", "Hatonuevo", "La Jagua del Pilar", "Maicao", "Manaure", "San Juan del Cesar", "Uribia", "Urumita", "Villanueva"],
    "Magdalena": ["Santa Marta", "Algarrobo", "Aracataca", "Ariguaní", "Cerro de San Antonio", "Chibolo", "Ciénaga", "Concordia", "El Banco", "El Piñón", "El Retén", "Fundación", "Guamal", "Nueva Granada", "Pedraza", "Pijiño del Carmen", "Pivijay", "Plato", "Puebloviejo", "Remolino", "Sabanas de San Ángel", "Salamina", "San Sebastián de Buenavista", "San Zenón", "Santa Ana", "Santa Bárbara de Pinto", "Sitionuevo", "Tenerife", "Zapayán", "Zona Bananera"],
    "Meta": ["Villavicencio", "Acacías", "Barranca de Upía", "Cabuyaro", "Castilla La Nueva", "Cubarral", "Cumaral", "El Calvario", "El Castillo", "El Dorado", "Fuente de Oro", "Granada", "Guamal", "Mapiripán", "Mesetas", "La Macarena", "La Uribe", "Lejanías", "Puerto Concordia", "Puerto Gaitán", "Puerto Lleras", "Puerto López", "Puerto Rico", "Restrepo", "San Carlos de Guaroa", "San Juan de Arama", "San Juanito", "San Martín", "Vista Hermosa"],
    "Nariño": ["Pasto", "Albán", "Aldana", "Ancuyá", "Arboleda", "Barbacoas", "Belén", "Buesaco", "Chachagüí", "Colón", "Consacá", "Contadero", "Córdoba", "Cuaspud", "Cumbal", "Cumbitara", "El Charco", "El Peñol", "El Rosario", "El Tablón de Gómez", "El Tambo", "Francisco Pizarro", "Funes", "Guachucal", "Guaitarilla", "Gualmatán", "Iles", "Imués", "Ipiales", "La Cruz", "La Florida", "La Llanada", "La Tola", "La Unión", "Leiva", "Linares", "Los Andes", "Magüí", "Mallama", "Mosquera", "Nariño", "Olaya Herrera", "Ospina", "Policarpa", "Potosí", "Providencia", "Puerres", "Pupiales", "Ricaurte", "Roberto Payán", "Samaniego", "San Bernardo", "San Lorenzo", "San Pablo", "San Pedro de Cartago", "Sandoná", "Santa Bárbara", "Santacruz", "Sapuyes", "Taminango", "Tangua", "Tumaco", "Túquerres", "Yacuanquer"],
    "Norte de Santander": ["Cúcuta", "Abrego", "Arboledas", "Bochalema", "Bucarasica", "Cácota", "Cáchira", "Chinácota", "Chitagá", "Convención", "Cucutilla", "Durania", "El Carmen", "El Tarra", "El Zulia", "Gramalote", "Hacarí", "Herrán", "La Esperanza", "La Playa", "Labateca", "Los Patios", "Lourdes", "Mutiscua", "Ocaña", "Pamplona", "Pamplonita", "Puerto Santander", "Ragonvalia", "Salazar", "San Calixto", "San Cayetano", "Santiago", "Sardinata", "Silos", "Teorama", "Tibú", "Toledo", "Villa Caro", "Villa del Rosario"],
    "Putumayo": ["Mocoa", "Colón", "Orito", "Puerto Asís", "Puerto Caicedo", "Puerto Guzmán", "Leguízamo", "San Francisco", "San Miguel", "Santiago", "Sibundoy", "Valle del Guamuez", "Villagarzón"],
    "Quindío": ["Armenia", "Buenavista", "Calarcá", "Circasia", "Córdoba", "Filandia", "Génova", "La Tebaida", "Montenegro", "Pijao", "Quimbaya", "Salento"],
    "Risaralda": ["Pereira", "Apía", "Balboa", "Belén de Umbría", "Dosquebradas", "Guática", "La Celia", "La Virginia", "Marsella", "Mistrató", "Pueblo Rico", "Quinchía", "Santa Rosa de Cabal", "Santuario"],
    "San Andrés y Providencia": ["San Andrés", "Providencia"],
    "Santander": ["Bucaramanga", "Aguada", "Albania", "Aratoca", "Barbosa", "Barichara", "Barrancabermeja", "Betulia", "Bolívar", "Cabrera", "California", "Capitanejo", "Carcasí", "Cepitá", "Cerrito", "Charalá", "Charta", "Chima", "Chipatá", "Cimitarra", "Concepción", "Confines", "Contratación", "Coromoro", "Curití", "El Carmen de Chucurí", "El Guacamayo", "El Peñón", "El Playón", "Encino", "Enciso", "Florián", "Floridablanca", "Galán", "Gámbita", "Girón", "Guaca", "Guadalupe", "Guapotá", "Guavatá", "Güepsa", "Hato", "Jesús María", "Jordán", "La Belleza", "La Paz", "Landázuri", "Lebrija", "Los Santos", "Macaravita", "Málaga", "Matanza", "Mogotes", "Molagavita", "Ocamonte", "Oiba", "Onzaga", "Palmar", "Palmas del Socorro", "Páramo", "Piedecuesta", "Pinchote", "Puente Nacional", "Puerto Parra", "Puerto Wilches", "Rionegro", "Sabana de Torres", "San Andrés", "San Benito", "San Gil", "San Joaquín", "San José de Miranda", "San Miguel", "San Vicente de Chucurí", "Santa Bárbara", "Santa Helena del Opón", "Simacota", "Socorro", "Suaita", "Sucre", "Suratá", "Tona", "Valle de San José", "Vetas", "Villanueva", "Zapatoca"],
    "Sucre": ["Sincelejo", "Buenavista", "Caimito", "Chalán", "Colosó", "Corozal", "Coveñas", "El Roble", "Galeras", "Guaranda", "La Unión", "Los Palmitos", "Majagual", "Morroa", "Ovejas", "Palmito", "Sampués", "San Benito Abad", "San Juan de Betulia", "San Marcos", "San Onofre", "San Pedro", "Sincé", "Sucre", "Tolú", "Tolú Viejo"],
    "Tolima": ["Ibagué", "Alpujarra", "Alvarado", "Ambalema", "Anzoátegui", "Ataco", "Cajamarca", "Carmen de Apicalá", "Casabianca", "Chaparral", "Coello", "Coyaima", "Cunday", "Dolores", "Espinal", "Falan", "Flandes", "Fresno", "Guamo", "Herveo", "Honda", "Icononzo", "Lérida", "Líbano", "Melgar", "Murillo", "Natagaima", "Ortega", "Palocabildo", "Piedras", "Planadas", "Prado", "Purificación", "Rio Blanco", "Roncesvalles", "Rovira", "Saldaña", "San Antonio", "San Luis", "Santa Isabel", "Suárez", "Valle de San Juan", "Venadillo", "Villahermosa", "Villarrica"],
    "Valle del Cauca": ["Cali", "Alcalá", "Andalucía", "Ansermanuevo", "Argelia", "Bolívar", "Buenaventura", "Buga", "Bugalagrande", "Caicedonia", "Calima", "Candelaria", "Cartago", "Dagua", "El Águila", "El Cairo", "El Cerrito", "El Dovio", "Florida", "Ginebra", "Guacarí", "Jamundí", "La Cumbre", "La Unión", "La Victoria", "Obando", "Palmira", "Pradera", "Restrepo", "Riofrío", "Roldanillo", "San Pedro", "Sevilla", "Toro", "Trujillo", "Tuluá", "Ulloa", "Versalles", "Vijes", "Yotoco", "Yumbo", "Zarzal"],
    "Vaupés": ["Mitú", "Carurú", "Pacoa", "Taraira", "Yavaraté"],
    "Vichada": ["Puerto Carreño", "Cumaribo", "La Primavera", "Santa Rosalía"]
    }

    # Consultar los datos del pedido y cliente
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT 
            clientes.cliente_id, 
            clientes.nombre_cliente, 
            clientes.tipo_identificacion, 
            clientes.numero_identificacion, 
            clientes.direccion_entrega, 
            clientes.departamento, 
            clientes.ciudad, 
            clientes.barrio, 
            clientes.telefonos, 
            clientes.email, 
            clientes.regimen_iva, 
            clientes.ordenado_a, 
            clientes.ordenado_por,
            pedidos.pedido_id, 
            pedidos.nombre_laboratorio, 
            pedidos.vendedor, 
            pedidos.codigo_montura, 
            pedidos.valor_montura, 
            pedidos.codigo_lente, 
            pedidos.valor_lente,
            pedidos.otros, 
            pedidos.valor_otros, 
            pedidos.total_venta, 
            pedidos.guia_despacho, 
            DATE_FORMAT(pedidos.fecha_entrega, '%%d/%%m/%%Y') as fecha_entrega, 
            pedidos.observaciones, 
            DATE_FORMAT(pedidos.fecha, '%%d/%%m/%%Y') as fecha
        FROM pedidos
        JOIN clientes ON pedidos.cliente_id = clientes.cliente_id
        WHERE clientes.cliente_id = %s
    ''', (cliente_id,))
    
    pedido = cursor.fetchone()

    if not pedido:
        return "No se encontró ninguna orden para este cliente_id."

    cliente_id = pedido[0]  # cliente_id ahora está en el índice 0
    pedido_id = pedido[13]  # pedido_id está en el índice 13
    fecha_entrega = pedido[24]

    puede_modificar = not fecha_entrega or fecha_entrega == '00/00/0000' or fecha_entrega.strip() == ''


    # Obtener detalles de los lentes
    cursor.execute('''
        SELECT esfera_od, cilindro_od, eje_od, adicion_od, dp_od, esfera_oi, cilindro_oi, eje_oi, adicion_oi, dp_oi
        FROM detalles_lentes
        WHERE pedido_id = %s
    ''', (pedido_id,))
    detalles_lentes = cursor.fetchone()

    # Obtener detalles de los pagos
    cursor.execute('''
        SELECT pago_efectivo, pago_bancolombia, pago_davivienda, pasa_pagos, pago_bold, pago_mensajeria_eklat, pago_mercadopago, pago_sistecredito, pago_addi, pago_envia, pago_interapidismo, pago_servientrega, pago_otro
        FROM pagos
        WHERE pedido_id = %s
    ''', (pedido_id,))
    pagos = cursor.fetchone()

    # Obtener información adicional del laboratorio
    cursor.execute('''
        SELECT montura, color, material_lentes, ar, progresivo, gama_progresivo, monofocal, opcion_monofocal, fotocromatico, bifocal, af, corredor, adicional, DATE_FORMAT(fecha_lab, '%%d/%%m/%%Y') as fecha_lab, gama_fotocromatico
        FROM orden_laboratorio
        WHERE pedido_id = %s
    ''', (pedido_id,))
    orden_laboratorio = cursor.fetchone()

    if orden_laboratorio is None:
        orden_laboratorio = ('', '', '', '', '', '', '', '', '', '', '', '', '', '', '')

    # Renderizar el template para la edición
    return render_template('Res_Con_Ent.html',
                           cliente_id=cliente_id,
                           pedido=pedido,
                           detalles_lentes=detalles_lentes,
                           pagos=pagos,
                           orden_laboratorio=orden_laboratorio,
                           departamentosYciudades=departamentosYciudades,
                           puede_modificar=puede_modificar)


@app.route('/guardar_cambios/<int:cliente_id>', methods=['POST'])
def guardar_cambios(cliente_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        # Recibir los datos del formulario
        datos_pedido = {
            'fecha': request.form.get('fecha', '00-00-0000'),
            'nombre_laboratorio': request.form.get('nombre_laboratorio', ''),
            'vendedor': request.form.get('vendedor', ''),
            'nombre_cliente': request.form.get('nombre_cliente', ''),
            'tipo_identificacion': request.form.get('tipo_identificacion', ''),
            'numero_identificacion': request.form.get('numero_identificacion', ''),
            'direccion_entrega': request.form.get('direccion_entrega', ''),
            'departamento': request.form.get('departamento', ''),
            'ciudad': request.form.get('ciudad', ''),
            'barrio': request.form.get('barrio', ''),
            'telefonos': request.form.get('telefonos', ''),
            'email': request.form.get('email', ''),
            'tipo_regimen_iva': request.form.get('tipo_regimen_iva', ''),
            'codigo_montura': request.form.get('codigo_montura', ''),
            'valor_montura': request.form.get('valor_montura', '0'),
            'codigo_lente': request.form.get('codigo_lente', ''),
            'valor_lente': request.form.get('valor_lente', '0'),
            'otros': request.form.get('otros', ''),
            'valor_otros': request.form.get('valor_otros', '0'),
            'total_venta': request.form.get('total_venta', '0'),
            'guia_despacho': request.form.get('guia_despacho', ''),
            'fecha_entrega': request.form.get('fecha_entrega', ''),
            'observaciones': request.form.get('observaciones', ''),
            'ordenado_por': request.form.get('ordenado_por', ''),
            'ordenado_a': request.form.get('ordenado_a', '')
        }

        # Función para convertir fechas
        def convertir_fecha(fecha):
            if fecha and fecha != '00/00/0000':  # Si la fecha no está vacía
                try:
                    return datetime.strptime(fecha, '%d/%m/%Y').strftime('%Y-%m-%d')
                except ValueError:
                    return None  # Si hay algún problema con la conversión, usar None (NULL en SQL)
            return None  # Fecha vacía o inválida

        datos_pedido['fecha'] = convertir_fecha(datos_pedido['fecha'])
        datos_pedido['fecha_entrega'] = convertir_fecha(datos_pedido['fecha_entrega'])

        # Convertir valores numéricos a float
        try:
            datos_pedido['valor_montura'] = float(datos_pedido['valor_montura'] or 0.0)
            datos_pedido['valor_lente'] = float(datos_pedido['valor_lente'] or 0.0)
            datos_pedido['valor_otros'] = float(datos_pedido['valor_otros'] or 0.0)
            datos_pedido['total_venta'] = float(datos_pedido['total_venta'] or 0.0)
        except ValueError as e:
            return f"Error en la conversión de valores numéricos: {str(e)}"

        # Actualizar los datos del cliente
        cursor = mysql.connection.cursor()
        cursor.execute('''
            UPDATE clientes
            SET nombre_cliente = %s, tipo_identificacion = %s, numero_identificacion = %s, direccion_entrega = %s, departamento = %s, ciudad = %s, barrio = %s, telefonos = %s, email = %s, regimen_iva = %s, ordenado_por = %s, ordenado_a = %s
            WHERE cliente_id = %s
        ''', (datos_pedido['nombre_cliente'], datos_pedido['tipo_identificacion'], datos_pedido['numero_identificacion'],
              datos_pedido['direccion_entrega'], datos_pedido['departamento'], datos_pedido['ciudad'], datos_pedido['barrio'], datos_pedido['telefonos'],
              datos_pedido['email'], datos_pedido['tipo_regimen_iva'],  datos_pedido['ordenado_por'], datos_pedido['ordenado_a'], cliente_id))

        # Actualizar los datos del pedido
        cursor.execute('''
            UPDATE pedidos
            SET nombre_laboratorio = %s, vendedor = %s, codigo_montura = %s, valor_montura = %s, codigo_lente = %s, valor_lente = %s, otros = %s, valor_otros = %s, total_venta = %s, guia_despacho = %s, observaciones = %s, fecha_entrega = %s
            WHERE cliente_id = %s
        ''', (datos_pedido['nombre_laboratorio'], datos_pedido['vendedor'], datos_pedido['codigo_montura'], datos_pedido['valor_montura'],
              datos_pedido['codigo_lente'], datos_pedido['valor_lente'], datos_pedido['otros'], datos_pedido['valor_otros'],
              datos_pedido['total_venta'], datos_pedido['guia_despacho'], datos_pedido['observaciones'], datos_pedido['fecha_entrega'], cliente_id))

        # Obtener el pedido_id para actualizar las demás tablas
        cursor.execute('SELECT pedido_id FROM pedidos WHERE cliente_id = %s ORDER BY pedido_id DESC LIMIT 1', (cliente_id,))
        pedido_id = cursor.fetchone()[0]

        # Actualizar los detalles de los lentes
        cursor.execute('''
            UPDATE detalles_lentes
            SET esfera_od = %s, cilindro_od = %s, eje_od = %s, adicion_od = %s, dp_od = %s, esfera_oi = %s, cilindro_oi = %s, eje_oi = %s, adicion_oi = %s, dp_oi = %s
            WHERE pedido_id = %s
        ''', (request.form.get('esfera_od', ''), request.form.get('cilindro_od', ''), request.form.get('eje_od', ''), request.form.get('adicion_od', ''),
              request.form.get('dp_od', ''), request.form.get('esfera_oi', ''), request.form.get('cilindro_oi', ''), request.form.get('eje_oi', ''),
              request.form.get('adicion_oi', ''), request.form.get('dp_oi', ''), pedido_id))

        # Obtener el valor de AR y si es "Otro", obtener el valor del campo adicional
        ar = request.form.get('ar', '')
        if ar == 'Otro':
            ar = request.form.get('ar_otro', '')

        # Actualizar la orden del laboratorio
        cursor.execute('''
            UPDATE orden_laboratorio
            SET montura = %s, color = %s, material_lentes = %s, ar = %s, progresivo = %s, gama_progresivo = %s, monofocal = %s, opcion_monofocal = %s, fotocromatico = %s, bifocal = %s, af = %s, corredor = %s, adicional = %s
            WHERE pedido_id = %s
        ''', (request.form.get('montura', ''), request.form.get('color', ''), request.form.get('material_lentes', ''), ar,  # Usar el valor ajustado de AR
              request.form.get('progresivo', ''), request.form.get('progresivo_gama', ''), request.form.get('monofocal', ''), request.form.get('monofocal_option', ''),
              request.form.get('fotocrom', ''), request.form.get('bifocal', ''), request.form.get('af', ''), request.form.get('corredor', ''),
              request.form.get('adicional', ''), pedido_id))

        # Actualizar los pagos
        cursor.execute('''
            UPDATE pagos
            SET pago_efectivo = %s, pago_bancolombia = %s, pago_davivienda = %s, pasa_pagos = %s, pago_bold = %s, pago_mensajeria_eklat = %s, pago_mercadopago = %s, pago_sistecredito = %s, pago_addi = %s, pago_envia = %s, pago_interapidismo = %s, pago_servientrega = %s, pago_otro = %s
            WHERE pedido_id = %s
        ''', (int(request.form.get('pago_efectivo', '0')), int(request.form.get('pago_bancolombia', '0')), int(request.form.get('pago_davivienda', '0')),
              int(request.form.get('pasa_pagos', '0')), int(request.form.get('pago_bold', '0')), int(request.form.get('pago_mensajeria_eklat', '0')),
              int(request.form.get('pago_mercadopago', '0')), int(request.form.get('pago_sistecredito', '0')), int(request.form.get('pago_addi', '0')),
              int(request.form.get('pago_envia', '0')), int(request.form.get('pago_interapidismo', '0')), int(request.form.get('pago_servientrega', '0')),
              int(request.form.get('pago_otro', '0')), pedido_id))

        mysql.connection.commit()

        return render_template('Confirmacion_Modi.html')

    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Ocurrió un error: {str(e)}"

@app.route('/consulta_unificada', methods=['GET', 'POST'])
def consulta_unificada():
    filtro = None
    numero_identificacion = None
    pedidos = []

    if request.method == 'POST':
        filtro = request.form.get('filtro')
        numero_identificacion = request.form.get('numero_identificacion')

        cursor = mysql.connection.cursor()

        if numero_identificacion:
            # Consulta por número de identificación
            cursor.execute('''
                SELECT pedidos.pedido_id, pedidos.fecha, pedidos.total_venta, pedidos.guia_despacho,
                       pedidos.fecha_entrega, clientes.cliente_id
                FROM pedidos
                JOIN clientes ON pedidos.cliente_id = clientes.cliente_id
                WHERE clientes.numero_identificacion = %s
                ORDER BY pedidos.pedido_id DESC
            ''', (numero_identificacion,))
        elif filtro:
            # Consulta por filtro, asegurando siempre el mismo orden de columnas
            if filtro == 'Activos':
                cursor.execute("SELECT pedido_id, fecha, total_venta, guia_despacho, fecha_entrega, cliente_id FROM pedidos WHERE fecha_entrega IS NULL")
            elif filtro == 'Terminados':
                cursor.execute("SELECT pedido_id, fecha, total_venta, guia_despacho, fecha_entrega, cliente_id FROM pedidos WHERE fecha_entrega IS NOT NULL")
            elif filtro == 'En proceso':
                cursor.execute("SELECT pedido_id, fecha, total_venta, guia_despacho, fecha_entrega, cliente_id FROM pedidos WHERE (guia_despacho IS NULL OR guia_despacho = '') AND fecha_entrega IS NULL")
            elif filtro == 'Despachados':
                cursor.execute("SELECT pedido_id, fecha, total_venta, guia_despacho, fecha_entrega, cliente_id FROM pedidos WHERE guia_despacho IS NOT NULL AND guia_despacho != '' AND fecha_entrega IS NULL")
            else:
                cursor.execute("SELECT pedido_id, fecha, total_venta, guia_despacho, fecha_entrega, cliente_id FROM pedidos")
        
        pedidos = cursor.fetchall()
        cursor.close()

        # Imprimir los pedidos para depuración
        print("pedidos recuperados:", pedidos)

    return render_template('lista.html', pedidos=pedidos, filtro=filtro, numero_identificacion=numero_identificacion)






if __name__ == '__main__':
    app.run(debug=True)




