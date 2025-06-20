import pymysql
from config import Config

def get_db_connection():
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor # Esto nos da resultados como diccionarios
        )
        return conn
    except pymysql.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None