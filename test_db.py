from app import app
from models import db, Usuario, Pago

with app.app_context():
    db.create_all()

    # Verificar si el usuario ya existe
    usuario = Usuario.query.filter_by(username="eleazar").first()
    if not usuario:
        usuario = Usuario(username="eleazar", password="1234")
        db.session.add(usuario)
        db.session.commit()
        print("Usuario creado")
    else:
        print("El usuario ya existe")

    # Crear pago de prueba
    pago = Pago(destino="Platzi", monto=50.0, usuario_id=usuario.id)
    db.session.add(pago)
    db.session.commit()
    print("Pago registrado")