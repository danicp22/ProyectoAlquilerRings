from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "clave_secreta_boxeo"

def conectar():
    return mysql.connector.connect(
        host="sql310.infinityfree.com",
        user="if0_41196647",
        password="Dani220055",
        database="if0_41196647_alquilerboxeo",
        port=3306
    )

@app.route("/")
def index():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rings")
    rings = cursor.fetchall()
    conexion.close()
    return render_template("index.html", rings=rings)

@app.route("/registro")
def registro():
    return render_template("registro.html")

@app.route("/guardar_usuario", methods=["POST"])
def guardar_usuario():
    nombre = request.form["nombre"]
    email = request.form["email"]
    password = generate_password_hash(request.form["password"])
    
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s,%s,%s)", (nombre, email, password))
        conexion.commit()
    except:
        return "El email ya está registrado."
    finally:
        conexion.close()
    return redirect(url_for("login"))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login_usuario", methods=["POST"])
def login_usuario():
    email = request.form["email"]
    password = request.form["password"]
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
    usuario = cursor.fetchone()
    conexion.close()

    if usuario and check_password_hash(usuario["password"], password):
        session["usuario_id"] = usuario["id"]
        session["usuario_nombre"] = usuario["nombre"]
        return redirect("/")
    return "Login incorrecto. <a href='/login'>Reintentar</a>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/reservar/<int:id_ring>")
def reservar(id_ring):
    if "usuario_id" not in session: return redirect("/login")
    
    fecha = request.args.get('fecha')
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rings WHERE id=%s", (id_ring,))
    ring = cursor.fetchone()
    
    horas_ocupadas = []
    if fecha:
        cursor.execute("SELECT hora FROM reservas WHERE id_ring=%s AND fecha=%s", (id_ring, fecha))
        horas_ocupadas = [r['hora'] for r in cursor.fetchall()]
    
    conexion.close()
    return render_template("reservar.html", ring=ring, fecha=fecha, horario=range(9, 21), ocupadas=horas_ocupadas)

@app.route("/guardar_reserva", methods=["POST"])
def guardar_reserva():
    if "usuario_id" not in session: return redirect("/login")
    
    id_usuario = session["usuario_id"]
    id_ring = request.form["id_ring"]
    fecha = request.form["fecha"]
    hora = request.form["hora"]

    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("INSERT INTO reservas (id_usuario, id_ring, fecha, hora) VALUES (%s,%s,%s,%s)", (id_usuario, id_ring, fecha, hora))
        conexion.commit()
        return redirect("/mis_reservas")
    except:
        return "Error: Hora ya reservada."
    finally:
        conexion.close()

@app.route("/mis_reservas")
def mis_reservas():
    if "usuario_id" not in session: return redirect("/login")
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.fecha, r.hora, rings.nombre, rings.precio 
        FROM reservas r JOIN rings ON r.id_ring = rings.id 
        WHERE r.id_usuario = %s ORDER BY r.fecha DESC
    """, (session["usuario_id"],))
    reservas = cursor.fetchall()
    conexion.close()
    return render_template("mis_reservas.html", reservas=reservas)

if __name__ == "__main__":
    app.run(debug=True)