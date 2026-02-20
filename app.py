from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "clave_secreta_boxeo"

# -----------------------------
# Conexión SQLite
# -----------------------------
def conectar():
    conexion = sqlite3.connect("database.db")
    conexion.row_factory = sqlite3.Row
    return conexion

# ------------------------------
# Crear tablas y datos iniciales
# ------------------------------
def crear_tablas():
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Tabla usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    # Tabla rings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio INTEGER,
            imagen TEXT
        )
    """)
    
    # Tabla reservas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            id_ring INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora INTEGER NOT NULL,
            UNIQUE(id_ring, fecha, hora),
            FOREIGN KEY(id_usuario) REFERENCES usuarios(id),
            FOREIGN KEY(id_ring) REFERENCES rings(id)
        )
    """)
    
    # Insertar datos de ejemplo en rings si no existen
    cursor.execute("SELECT COUNT(*) as c FROM rings")
    if cursor.fetchone()["c"] == 0:
        cursor.execute("""
            INSERT INTO rings (nombre, descripcion, precio, imagen) VALUES
            ('Ring Profesional', 'Ring oficial para competiciones', 25, 'ring1.jpg'),
            ('Ring Entrenamiento', 'Ring para entrenamientos', 15, 'ring2.jpg')
        """)
    
    conexion.commit()
    conexion.close()

crear_tablas()

# ------------------------------
# Rutas
# ------------------------------
@app.route("/")
def index():
    conexion = conectar()
    cursor = conexion.cursor()
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
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)",
            (nombre, email, password)
        )
        conexion.commit()
    except sqlite3.IntegrityError:
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
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email=?", (email,))
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
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM rings WHERE id=?", (id_ring,))
    ring = cursor.fetchone()
    
    horas_ocupadas = []
    if fecha:
        cursor.execute("SELECT hora FROM reservas WHERE id_ring=? AND fecha=?", (id_ring, fecha))
        horas_ocupadas = [r["hora"] for r in cursor.fetchall()]
    
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
        cursor.execute(
            "INSERT INTO reservas (id_usuario, id_ring, fecha, hora) VALUES (?, ?, ?, ?)",
            (id_usuario, id_ring, fecha, hora)
        )
        conexion.commit()
        return redirect("/mis_reservas")
    except sqlite3.IntegrityError:
        return "Error: Hora ya reservada."
    finally:
        conexion.close()

@app.route("/mis_reservas")
def mis_reservas():
    if "usuario_id" not in session: return redirect("/login")
    
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT r.fecha, r.hora, rings.nombre, rings.precio 
        FROM reservas r JOIN rings ON r.id_ring = rings.id 
        WHERE r.id_usuario = ? ORDER BY r.fecha DESC
    """, (session["usuario_id"],))
    
    reservas = cursor.fetchall()
    conexion.close()
    return render_template("mis_reservas.html", reservas=reservas)

# ------------------------------
# Run
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)