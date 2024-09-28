from flask import Flask, request, render_template, redirect, url_for, session
from excel_utils import completar_orden_excel
import bcrypt
import json
import os
from flask_mysqldb import MySQL
from datetime import date


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_default_secret_key')

# Configuración de conexión a MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Cv.Usa8132'  # Cambia esto si tienes una contraseña
app.config['MYSQL_DB'] = 'eklat_clientes'

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
    cursor.execute('SELECT MAX(pedido_id) FROM Pedidos')
    max_pedido_id = cursor.fetchone()[0]
    
    if max_pedido_id is None:
        nuevo_numero_orden = 6501  # Si no hay órdenes, iniciar en 1
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
        # Obtener el último número de orden (pedido_id) más alto de la tabla Pedidos
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT MAX(pedido_id) FROM Pedidos')
        max_pedido_id = cursor.fetchone()[0]  # Obtener el número de orden más alto
        if max_pedido_id is None:
            nuevo_numero_orden = 6501  # Si no hay órdenes, iniciar con 6501
        else:
            nuevo_numero_orden = max_pedido_id + 1  # Incrementar en 1
        # Recibir los datos del pedido del formulario
        datos_pedido = {
            'dia': request.form.get('dia', ''),
            'mes': request.form.get('mes', ''),
            'año': request.form.get('año', ''),
            'nombre_laboratorio': request.form.get('nombre_laboratorio', ''),
            'vendedor': request.form.get('vendedor', ''),
            'nombre_cliente': request.form.get('nombre_cliente', ''),
            'tipo_identificacion': request.form.get('tipo_identificacion', ''),
            'numero_identificacion': request.form.get('numero_identificacion', ''),
            'direccion_entrega': request.form.get('direccion_entrega', ''),
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
            'dia_ent': request.form.get('dia_ent', ''),
            'mes_ent': request.form.get('mes_ent', ''),
            'año_ent': request.form.get('año_ent', ''),
            'dia_lab': request.form.get('dia_lab', ''),
            'mes_lab': request.form.get('mes_lab', ''),
            'año_lab': request.form.get('año_lab', ''),
            'observaciones': request.form.get('observaciones', ''),
            'ordenado_a': request.form.get('ordenado_a', ''),
            'ordenado_por': request.form.get('ordenado_por', '')
        }

        # Convertir valores numéricos a float
        try:
            datos_pedido['valor_montura'] = float(datos_pedido['valor_montura'] or 0.0)
            datos_pedido['valor_lente'] = float(datos_pedido['valor_lente'] or 0.0)
            datos_pedido['valor_otros'] = float(datos_pedido['valor_otros'] or 0.0)
            datos_pedido['total_venta'] = float(datos_pedido['total_venta'] or 0.0)
        except ValueError as e:
            return f"Error en la conversión de valores numéricos: {str(e)}"

        # Formatear la fecha de entrega en formato 'YYYY-MM-DD'
        dia = datos_pedido['dia'].zfill(2)
        mes = datos_pedido['mes'].zfill(2)
        año = datos_pedido['año'] if datos_pedido['año'] else '0000'
        fecha = f"{año}-{mes}-{dia}" if dia and mes and año else '0000-00-00'

        # Insertar datos en la tabla Clientes
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO Clientes (nombre_cliente, tipo_identificacion, numero_identificacion, direccion_entrega, ciudad, barrio, telefonos, email, regimen_iva, ordenado_a, ordenado_por)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (datos_pedido['nombre_cliente'], 
              datos_pedido['tipo_identificacion'], 
              datos_pedido['numero_identificacion'], 
              datos_pedido['direccion_entrega'], 
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

        # Formatear la fecha de entrega en formato 'YYYY-MM-DD'
        dia_ent = datos_pedido['dia_ent'].zfill(2)
        mes_ent = datos_pedido['mes_ent'].zfill(2)
        año_ent = datos_pedido['año_ent'] if datos_pedido['año'] else '0000'
        dia_entrega = f"{año_ent}-{mes_ent}-{dia_ent}" if dia and mes and año else '0000-00-00'

        # Insertar el nuevo pedido con el número de orden nuevo
        cursor.execute('''
            INSERT INTO Pedidos (pedido_id, cliente_id, nombre_laboratorio, vendedor, codigo_montura, valor_montura, codigo_lente, valor_lente, otros, valor_otros, total_venta, dia_entrega, guia_despacho, observaciones, fecha)
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
              dia_entrega, 
              datos_pedido['guia_despacho'],
              datos_pedido['observaciones'],
              fecha))
        mysql.connection.commit()
        pedido_id = cursor.lastrowid  # Obtener el ID del último pedido insertado

        # Insertar detalles de lentes en la tabla Detalles_Lentes
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
            INSERT INTO Detalles_Lentes (pedido_id, esfera_od, cilindro_od, eje_od, adicion_od, dp_od, esfera_oi, cilindro_oi, eje_oi, adicion_oi, dp_oi)
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

        # Insertar datos del laboratorio en la tabla Orden_Laboratorio
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

        dia_lab = datos_pedido['dia_lab'].zfill(2)
        mes_lab = datos_pedido['mes_lab'].zfill(2)
        año_lab = datos_pedido['año_lab'] if datos_pedido['año'] else '0000'
        fecha_lab = f"{año_lab}-{mes_lab}-{dia_lab}" if dia and mes and año else '0000-00-00'
        

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
            INSERT INTO Orden_Laboratorio (pedido_id, montura, color, material_lentes, ar, progresivo, gama_progresivo, monofocal, opcion_monofocal, fotocromatico, bifocal, af, corredor, adicional, fecha_lab, gama_fotocromatico)
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
            fecha_lab,
            fotocromatico_cual
        ))

        # Hacer commit para guardar los cambios en la base de datos
        mysql.connection.commit()

        # Insertar datos de pagos en la tabla Pagos
        pagos = {
            'pago_efectivo': int(request.form.get('pago_efectivo', '0') or 0),
            'pago_bancolombia': int(request.form.get('pago_bancolombia', '0') or 0),
            'pago_davivienda': int(request.form.get('pago_davivienda', '0') or 0),
            'pago_redeban': int(request.form.get('pago_redeban', '0') or 0),
            'pago_bold': int(request.form.get('pago_bold', '0') or 0),
            'pago_mercadopago': int(request.form.get('pago_mercadopago', '0') or 0),
            'pago_payco': int(request.form.get('pago_payco', '0') or 0),
            'pago_sistecredito': int(request.form.get('pago_sistecredito', '0') or 0),
            'pago_addi': int(request.form.get('pago_addi', '0') or 0),
            'pago_envia': int(request.form.get('pago_envia', '0') or 0),
            'pago_interapidism': int(request.form.get('pago_interapidism', '0') or 0),
            'pago_servientrega': int(request.form.get('pago_servientrega', '0') or 0),
            'pago_otro': int(request.form.get('pago_otro', '0') or 0),
            'pago_mensajeria_eklat':int(request.form.get('pago_mensajeria_eklat', '0') or 0)
        }


        cursor.execute('''
            INSERT INTO Pagos (pedido_id, pago_efectivo, pago_bancolombia, pago_davivienda, pago_redeban, pago_bold, pago_mensajeria_eklat, pago_mercadopago, pago_payco, pago_sistecredito, pago_addi, pago_envia, pago_interapidismo, pago_servientrega, pago_otro)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        ''', (pedido_id, 
              pagos['pago_efectivo'], 
              pagos['pago_bancolombia'], 
              pagos['pago_davivienda'], 
              pagos['pago_redeban'], 
              pagos['pago_bold'], 
              pagos['pago_mensajeria_eklat'],
              pagos['pago_mercadopago'], 
              pagos['pago_payco'], 
              pagos['pago_sistecredito'], 
              pagos['pago_addi'], 
              pagos['pago_envia'], 
              pagos['pago_interapidism'], 
              pagos['pago_servientrega'], 
              pagos['pago_otro']))
        mysql.connection.commit()

        return "Orden guardada exitosamente"

    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Ocurrió un error: {str(e)}"


@app.route('/consulta', methods=['GET', 'POST'])
def consulta():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        numero_identificacion = request.form.get('numero_identificacion')

        # Consulta la información del pedido
        cursor = mysql.connection.cursor()
        cursor.execute('''
            SELECT Clientes.nombre_cliente, Clientes.tipo_identificacion, Clientes.numero_identificacion, Clientes.direccion_entrega, Clientes.ciudad, Clientes.barrio, Clientes.telefonos, Clientes.email, Clientes.regimen_iva, Clientes.ordenado_a, Clientes.ordenado_por,
                   Pedidos.pedido_id, Pedidos.nombre_laboratorio, Pedidos.vendedor, Pedidos.codigo_montura, Pedidos.valor_montura, Pedidos.codigo_lente, Pedidos.valor_lente,
                   Pedidos.otros, Pedidos.valor_otros, Pedidos.total_venta, Pedidos.guia_despacho, Pedidos.dia_entrega, Pedidos.observaciones, Pedidos.fecha
            FROM Pedidos
            JOIN Clientes ON Pedidos.cliente_id = Clientes.cliente_id
            WHERE Clientes.numero_identificacion = %s
            ORDER BY Pedidos.pedido_id DESC
            LIMIT 1
        ''', (numero_identificacion,))

        pedido = cursor.fetchone()

        if not pedido:
            return "No se encontró ninguna orden para este número de identificación."

        # Obtener la fecha del pedido correctamente (última columna de la consulta)
        fecha_pedido = pedido[24]

        # Convertir la fecha a día, mes, y año
        if isinstance(fecha_pedido, date):
            dia, mes, año = fecha_pedido.strftime('%d'), fecha_pedido.strftime('%m'), fecha_pedido.strftime('%Y')
        else:
            dia, mes, año = '00', '00', '0000'

        # Usar la fecha de pedido para la fecha de laboratorio (dia_lab, mes_lab, año_lab)
        dia_lab, mes_lab, año_lab = dia, mes, año

        # Procesar la fecha de entrega correctamente
        fecha_entrega_str = pedido[22]
        if isinstance(fecha_entrega_str, date):
            fecha_entrega = fecha_entrega_str.strftime('%Y-%m-%d').split('-')
        else:
            fecha_entrega = ['0000', '00', '00']

        # Obtener 'pedido_id' correctamente
        pedido_id = pedido[11]

        # Consulta la información adicional del laboratorio
        cursor.execute('''
            SELECT montura, color, material_lentes, ar, progresivo, gama_progresivo, monofocal, opcion_monofocal, fotocromatico, bifocal, af, corredor, adicional, fecha_lab, gama_fotocromatico
            FROM Orden_Laboratorio
            WHERE pedido_id = %s
        ''', (pedido_id,))
        orden_laboratorio = cursor.fetchone()

        # Manejar caso en que orden_laboratorio sea None
        if orden_laboratorio is None:
            orden_laboratorio = ('', '', '', '', '', '', '', '', '', '', '', '', '', '', '')

        # Consulta los detalles de los lentes
        cursor.execute('''
            SELECT esfera_od, cilindro_od, eje_od, adicion_od, dp_od, esfera_oi, cilindro_oi, eje_oi, adicion_oi, dp_oi
            FROM Detalles_Lentes
            WHERE pedido_id = %s
        ''', (pedido_id,))
        detalles_lentes = cursor.fetchone()

        # Manejar caso en que detalles_lentes sea None
        if detalles_lentes is None:
            detalles_lentes = ('', '', '', '', '', '', '', '', '', '')

        # Consulta los detalles de pagos
        cursor.execute('''
            SELECT pago_efectivo, pago_bancolombia, pago_davivienda, pago_redeban, pago_bold, pago_mensajeria_eklat, pago_mercadopago, pago_payco, pago_sistecredito, pago_addi, pago_envia, pago_interapidismo, pago_servientrega, pago_otro
            FROM Pagos
            WHERE pedido_id = %s
        ''', (pedido_id,))
        pagos = cursor.fetchone()

        # Manejar caso en que pagos sea None
        if pagos is None:
            pagos = ('', '', '', '', '', '', '', '', '', '', '', '', '', '')

        observaciones = pedido[23] 

        # Renderiza la información en Res_Consulta.html
        return render_template('Res_Consulta.html',
                       # Información del cliente
                       nombre_cliente=pedido[0],
                       tipo_identificacion=pedido[1],
                       numero_identificacion=pedido[2],
                       direccion_entrega=pedido[3],
                       ciudad=pedido[4],
                       barrio=pedido[5],
                       telefonos=pedido[6],
                       email=pedido[7],
                       regimen_iva=pedido[8],
                       ordenado_a = pedido[9],
                       ordenado_por=pedido[10],
                       # Información del pedido
                       nombre_laboratorio=pedido[12],
                       vendedor=pedido[13],
                       codigo_montura=pedido[14],
                       valor_montura=pedido[15],
                       codigo_lente=pedido[16],
                       valor_lente=pedido[17],
                       otros=pedido[18],
                       valor_otros=pedido[19],
                       total_venta=pedido[20],
                       guia_despacho=pedido[21],
                       # Fecha del pedido
                       dia=dia,
                       mes=mes,
                       año=año,
                       observaciones=observaciones,
                       # Fecha de entrega
                       dia_ent=fecha_entrega[2],
                       mes_ent=fecha_entrega[1],
                       año_ent=fecha_entrega[0],
                       # Fecha de laboratorio (igual a la fecha del pedido)
                       dia_lab=dia_lab,
                       mes_lab=mes_lab,
                       año_lab=año_lab,
                       # Datos de la orden de laboratorio (con valores predeterminados si es None)
                       montura=orden_laboratorio[0],
                       color=orden_laboratorio[1],
                       material_lentes=orden_laboratorio[2],
                       ar=orden_laboratorio[3],
                       progresivo=orden_laboratorio[4],
                       gama_progresivo=orden_laboratorio[5],
                       monofocal=orden_laboratorio[6],
                       opcion_monofocal=orden_laboratorio[7],
                       fotocrom=orden_laboratorio[8],
                       bifocal=orden_laboratorio[9],
                       af=orden_laboratorio[10],
                       corredor=orden_laboratorio[11],
                       adicional=orden_laboratorio[12],
                       fecha_lab=orden_laboratorio[13],
                       fotocromatico_cual=orden_laboratorio[14],
                       # Detalles de los lentes
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
                       # Información de pagos
                       pago_efectivo=pagos[0],
                       pago_bancolombia=pagos[1],
                       pago_davivienda=pagos[2],
                       pago_redeban=pagos[3],
                       pago_bold=pagos[4],
                       pago_mensajeria_eklat=pagos[5],
                       pago_mercadopago=pagos[6],
                       pago_payco=pagos[7],
                       pago_sistecredito=pagos[8],
                       pago_addi=pagos[9],
                       pago_envia=pagos[10],
                       pago_interapidismo=pagos[11],
                       pago_servientrega=pagos[12],
                       pago_otro=pagos[13]
                       )

    # Mostrar la página de consulta (formulario de número de identificación)
    return render_template('Consulta.html')


@app.route('/imprimir_laboratorio/<numero_identificacion>')
def imprimir_laboratorio(numero_identificacion):
    cursor = mysql.connection.cursor()

    # Consulta los datos del pedido más reciente para el cliente con ese numero_identificacion
    cursor.execute('''
        SELECT Clientes.nombre_cliente, Clientes.ordenado_a, Clientes.ordenado_por,
               Pedidos.fecha, Pedidos.pedido_id, Pedidos.codigo_montura,
               Detalles_Lentes.esfera_od, Detalles_Lentes.cilindro_od, Detalles_Lentes.eje_od, Detalles_Lentes.adicion_od, Detalles_Lentes.dp_od,
               Detalles_Lentes.esfera_oi, Detalles_Lentes.cilindro_oi, Detalles_Lentes.eje_oi, Detalles_Lentes.adicion_oi, Detalles_Lentes.dp_oi,
               Orden_Laboratorio.material_lentes, Orden_Laboratorio.ar, Orden_Laboratorio.gama_fotocromatico, Orden_Laboratorio.color, Orden_Laboratorio.gama_progresivo,
               Orden_Laboratorio.opcion_monofocal, Orden_Laboratorio.bifocal, Orden_Laboratorio.adicional
        FROM Pedidos
        JOIN Clientes ON Pedidos.cliente_id = Clientes.cliente_id
        JOIN Detalles_Lentes ON Pedidos.pedido_id = Detalles_Lentes.pedido_id
        JOIN Orden_Laboratorio ON Pedidos.pedido_id = Orden_Laboratorio.pedido_id
        WHERE Clientes.numero_identificacion = %s
        ORDER BY Pedidos.pedido_id DESC
        LIMIT 1
    ''', (numero_identificacion,))

    pedido = cursor.fetchone()

    if not pedido:
        return "No se encontró ningún pedido para este número de identificación."

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
                           adicional=pedido[23])


@app.route('/imprimir_pedido/<numero_identificacion>')
def imprimir_pedido(numero_identificacion):
    cursor = mysql.connection.cursor()

    # Consulta los datos del pedido y cliente usando el número de identificación
    cursor.execute('''
        SELECT Clientes.nombre_cliente, Clientes.numero_identificacion, Clientes.direccion_entrega, Clientes.ciudad, Clientes.barrio, Clientes.telefonos, Clientes.email,
               Pedidos.pedido_id, Pedidos.nombre_laboratorio, Pedidos.vendedor, Pedidos.codigo_montura, Pedidos.valor_montura, Pedidos.codigo_lente, Pedidos.valor_lente,
               Pedidos.otros, Pedidos.valor_otros, Pedidos.total_venta, Pedidos.fecha, Pedidos.observaciones,
               Pagos.pago_efectivo, Pagos.pago_bancolombia, Pagos.pago_davivienda, Pagos.pago_redeban, Pagos.pago_bold, Pagos.pago_mercadopago, Pagos.pago_payco,
               Pagos.pago_sistecredito, Pagos.pago_addi, Pagos.pago_envia, Pagos.pago_interapidismo, Pagos.pago_servientrega, Pagos.pago_mensajeria_eklat, Pagos.pago_otro
        FROM Pedidos
        JOIN Clientes ON Pedidos.cliente_id = Clientes.cliente_id
        JOIN Pagos ON Pedidos.pedido_id = Pagos.pedido_id
        WHERE Clientes.numero_identificacion = %s
        ORDER BY Pedidos.pedido_id DESC
        LIMIT 1
    ''', (numero_identificacion,))
    
    pedido = cursor.fetchone()

    if not pedido:
        return "No se encontró ningún pedido para este número de identificación."

    # Manejo de fecha: si fecha es un string, convertirla en un objeto datetime
    fecha_pedido = pedido[17]  # La columna fecha está en el índice 16
    dia = fecha_pedido.day
    mes = fecha_pedido.month
    año = fecha_pedido.year

    # Renderizar la plantilla pedido.html
    return render_template('pedido.html',
                           dia=dia,
                           mes=mes,
                           año=año,
                           numero_orden=pedido[7],
                           nombre_laboratorio=pedido[8],
                           vendedor=pedido[9],
                           nombre_cliente=pedido[0],
                           identificacion_cliente=pedido[1],
                           direccion_entrega=pedido[2],
                           ciudad=pedido[3],
                           barrio=pedido[4],
                           telefonos=pedido[5],
                           email=pedido[6],
                           codigo_montura=pedido[10],
                           valor_montura=pedido[11],
                           codigo_lente=pedido[12],
                           valor_lente=pedido[13],
                           otros=pedido[14],
                           valor_otros=pedido[15],
                           total_venta=pedido[16],
                           pago_efectivo=pedido[19],
                           pago_bancolombia=pedido[20],
                           pago_davivienda=pedido[21],
                           pago_redeban=pedido[22],
                           pago_bold=pedido[23],
                           pago_mercadopago=pedido[24],
                           pago_payco=pedido[25],
                           pago_sistecredito=pedido[26],
                           pago_addi=pedido[27],
                           pago_envia=pedido[28],
                           pago_interapidismo=pedido[29],
                           pago_servientrega=pedido[30],
                           pago_mensajeria_eklat=pedido[31],
                           pago_otro=pedido[32],
                           observaciones=pedido[18])

if __name__ == '__main__':
    app.run(debug=True)




