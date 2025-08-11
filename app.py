

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from models import db, Pago, Usuario
import os

# Cargar variables de entorno
load_dotenv()

# Inicializar la app
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "clave_secreta")

# Configuración de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///pagos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['API_KEY'] = os.getenv('API_KEY')

# Inicializar base de datos
db.init_app(app)

# Configurar Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Crear tablas si no existen
with app.app_context():
    db.create_all()

# Rutas
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/historial')
@login_required
def historial():
    pagos = Pago.query.filter_by(usuario_id=current_user.id).all()
    return render_template('historial.html', pagos=pagos)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        if Usuario.query.filter_by(username=username).first():
            return "El usuario ya existe", 400

        nuevo_usuario = Usuario(username=username, password=password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = Usuario.query.filter_by(username=request.form['username']).first()
        if usuario and check_password_hash(usuario.password, request.form['password']):
            login_user(usuario)
            return redirect(url_for('index'))
        return "Credenciales incorrectas"
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/pagar', methods=['POST'])
@login_required
def pagar():
    data = request.get_json()
    monto = data.get('monto')
    destino = data.get('destino')

    try:
        monto = float(monto)
    except (TypeError, ValueError):
        return jsonify({"status": "error", "mensaje": "Monto inválido"}), 400

    if destino:
        nuevo_pago = Pago(destino=destino, monto=monto, usuario_id=current_user.id)
        db.session.add(nuevo_pago)
        db.session.commit()
        return jsonify({"status": "ok", "mensaje": f"Pago de S/{monto} a {destino} registrado."})
    else:
        return jsonify({"status": "error", "mensaje": "Destino requerido"}), 400

@app.route('/api/yape', methods=['POST'])
def api_yape():
    data = request.get_json()
    monto = data.get('monto')
    destino = data.get('destino')

    if monto and destino:
        return jsonify({"status": "success", "mensaje": f"Transferencia de S/{monto} a {destino} completada."})
    else:
        return jsonify({"status": "error", "mensaje": "Datos inválidos"}), 400

# Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)