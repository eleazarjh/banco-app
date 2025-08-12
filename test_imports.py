try:
    from flask_sqlalchemy import SQLAlchemy
    from flask_login import UserMixin
    print("✅ Importaciones exitosas")
except ImportError as e:
    print(f"❌ Error de importación: {e}")