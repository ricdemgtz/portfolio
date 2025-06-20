from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields, reqparse # Nuevas importaciones para Flask-RESTX
from database import get_db_connection
from datetime import date, datetime # Para validación de fechas y serialización de fechas

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Configuración de Flask-RESTX
api = Api(app,
          version='1.0',
          title='Venix Manga API',
          description='API para gestionar una colección de mangas, autores y géneros. Accede a /docs/ para la documentación interactiva.',
          doc='/docs/') # La interfaz Swagger UI estará en /docs/

# --- MANEJADORES DE ERRORES GLOBALES (para API) ---
# Flask-RESTX tiene su propio manejo de errores, pero estos pueden seguir siendo útiles
# para errores que ocurren fuera de los recursos de Flask-RESTX o para personalizar respuestas.
@app.errorhandler(400)
def bad_request_error(error):
    # Flask-RESTX a veces puede lanzar sus propios errores 400.
    # Este es un manejador general, puedes refinarlo si Flask-RESTX maneja algunos 400.
    if hasattr(error, 'data') and 'message' in error.data:
        return jsonify({"message": error.data['message'], "errors": error.data.get('errors')}), 400
    return jsonify({"message": "Solicitud incorrecta. Verifique los datos enviados."}), 400

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"message": "Recurso no encontrado."}), 404

@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"message": "Método HTTP no permitido para esta ruta."}), 405

@app.errorhandler(500)
def internal_error(error):
    # En un entorno de producción, aquí no deberías exponer 'error' directamente.
    # Podrías loggear el error.
    return jsonify({"message": f"Error interno del servidor. {error}"}), 500

# --- Endpoint de prueba raíz ---
@app.route('/')
def home():
    return "¡Bienvenido a la API de Venix! Accede a /docs/ para la documentación interactiva."


# --- FUNCIONES AUXILIARES ---

# Función para validar datos del manga (la que ya tenías)
def validate_manga_data(data, is_update=False):
    errors = {}
    
    if not is_update or 'titulo' in data:
        if not data.get('titulo') or not isinstance(data.get('titulo'), str):
            errors['titulo'] = "El título es requerido y debe ser una cadena de texto."
        elif len(data['titulo']) > 255:
            errors['titulo'] = "El título no puede exceder los 255 caracteres."

    if 'estado' in data:
        allowed_states = ['En curso', 'Finalizado', 'Pausado', 'Cancelado']
        if data['estado'] not in allowed_states:
            errors['estado'] = f"El estado debe ser uno de: {', '.join(allowed_states)}."

    if 'fecha_publicacion' in data and data['fecha_publicacion'] is not None:
        try:
            date.fromisoformat(data['fecha_publicacion'])
        except ValueError:
            errors['fecha_publicacion'] = "El formato de la fecha de publicación debe ser YYYY-MM-DD."

    if 'calificacion' in data and data['calificacion'] is not None:
        try:
            calificacion_val = float(data['calificacion'])
            if not (0.00 <= calificacion_val <= 10.00):
                errors['calificacion'] = "La calificación debe ser un número entre 0.00 y 10.00."
        except (ValueError, TypeError):
            errors['calificacion'] = "La calificación debe ser un número válido."

    if 'autor_id' in data and data['autor_id'] is not None:
        try:
            int(data['autor_id'])
        except (ValueError, TypeError):
            errors['autor_id'] = "El ID del autor debe ser un número entero."
    
    if 'generos' in data and not isinstance(data['generos'], list):
        errors['generos'] = "Los géneros deben ser una lista de cadenas de texto."
    elif 'generos' in data and isinstance(data['generos'], list):
        for g in data['generos']:
            if not isinstance(g, str):
                errors['generos'] = "Todos los géneros en la lista deben ser cadenas de texto."
                break
    return errors

# Función para serializar fechas a formato ISO (útil para campos no manejados por marshal_with)
def serialize_dates(item):
    """
    Convierte objetos date/datetime dentro de un diccionario o lista de diccionarios
    a cadenas de formato ISO (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS).
    Modifica el diccionario/lista in-place.
    """
    if isinstance(item, list):
        for i in item:
            serialize_dates(i) # Recursivamente para cada elemento en la lista
    elif isinstance(item, dict):
        for key, value in item.items():
            if isinstance(value, (date, datetime)):
                item[key] = value.isoformat()
            # Si hay objetos anidados que también pueden contener fechas, se puede agregar recursión aquí
            # elif isinstance(value, (dict, list)):
            #     serialize_dates(value)
    return item # Retorna el mismo objeto modificado

# --- MODELOS DE DATOS PARA LA DOCUMENTACIÓN (Flask-RESTX) ---
# Estos modelos definen la estructura esperada para las entradas y salidas JSON
# y se usan con @api.expect y @api.marshal_with
manga_model = api.model('Manga', {
    'id': fields.Integer(readOnly=True, description='El identificador único del manga'),
    'titulo': fields.String(required=True, description='El título principal del manga', max_length=255),
    'titulo_alternativo': fields.String(description='Título alternativo o en japonés', max_length=255),
    'sinopsis': fields.String(description='Breve descripción de la trama'),
    'estado': fields.String(enum=['En curso', 'Finalizado', 'Pausado', 'Cancelado'], description='Estado de publicación'),
    'fecha_publicacion': fields.Date(description='Fecha de la primera publicación (YYYY-MM-DD)'),
    'editorial': fields.String(description='Editorial del manga', max_length=255),
    'calificacion': fields.Float(min=0.0, max=10.0, description='Calificación del manga (0.00 a 10.00)'),
    'portada_url': fields.String(description='URL de la imagen de portada', max_length=2048),
    'autor_id': fields.Integer(description='ID del autor principal'),
    'autor_nombre': fields.String(readOnly=True, description='Nombre del autor (solo lectura, se obtiene por JOIN)'),
    'generos': fields.List(fields.String, description='Lista de nombres de géneros asociados al manga')
})

autor_model = api.model('Autor', {
    'id': fields.Integer(readOnly=True, description='El identificador único del autor'),
    'nombre': fields.String(required=True, description='Nombre completo del autor', max_length=255),
    'biografia': fields.String(description='Breve biografía del autor'),
    'fecha_nacimiento': fields.Date(description='Fecha de nacimiento del autor (YYYY-MM-DD)'),
    'pais': fields.String(description='País de origen del autor', max_length=100)
})

genero_model = api.model('Genero', {
    'id': fields.Integer(readOnly=True, description='El identificador único del género'),
    'nombre': fields.String(required=True, description='Nombre del género', max_length=100)
})

# Definición de parsers para parámetros de URL (GET requests)
# Manga GET list parameters
manga_list_parser = reqparse.RequestParser()
manga_list_parser.add_argument('page', type=int, help='Número de página para paginación', default=1, location='args')
manga_list_parser.add_argument('limit', type=int, help='Número de elementos por página', default=10, location='args')
manga_list_parser.add_argument('estado', type=str, help='Filtrar por estado del manga (ej. "En curso", "Finalizado")', location='args')
manga_list_parser.add_argument('genero', type=str, help='Filtrar por nombre de género', location='args')
manga_list_parser.add_argument('autor_id', type=int, help='Filtrar por ID de autor', location='args')
manga_search_parser = reqparse.RequestParser()
manga_search_parser.add_argument('q', type=str, required=True, help='Término de búsqueda por título, sinopsis o autor', location='args')


# --- NAMESPACES (Grupos de Endpoints) ---
ns_mangas = api.namespace('api/v1/mangas', description='Operaciones relacionadas con los mangas')
ns_autores = api.namespace('api/v1/autores', description='Operaciones relacionadas con los autores')
ns_generos = api.namespace('api/v1/generos', description='Operaciones relacionadas con los géneros')


# --- RECURSOS (Clases para los Endpoints) ---

# --- Mangas ---
@ns_mangas.route('/')
class MangaList(Resource):
    @api.doc('list_mangas', description='Obtiene una lista paginada y filtrada de mangas.')
    @api.expect(manga_list_parser)
    @api.marshal_with(api.model('MangaPaginatedList', {
        'total_items': fields.Integer(),
        'page': fields.Integer(),
        'limit': fields.Integer(),
        'data': fields.List(fields.Nested(manga_model)) # CORRECCIÓN PREVIA
    }), code=200, description='Lista de mangas con información de paginación.')
    def get(self):
        args = manga_list_parser.parse_args()
        page = args['page']
        limit = args['limit']
        offset = (page - 1) * limit

        estado_filter = args['estado']
        genero_filter = args['genero']
        autor_filter_id = args['autor_id']

        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")

        try:
            with conn.cursor() as cursor:
                where_clauses = []
                sql_params = []

                if estado_filter:
                    where_clauses.append("m.estado = %s")
                    sql_params.append(estado_filter)
                
                if autor_filter_id:
                    where_clauses.append("m.autor_id = %s")
                    sql_params.append(autor_filter_id)

                if genero_filter:
                    cursor.execute("SELECT id FROM generos WHERE nombre = %s", (genero_filter,))
                    g_id_row = cursor.fetchone()
                    if g_id_row:
                        genero_id_for_filter = g_id_row['id']
                        where_clauses.append("EXISTS (SELECT 1 FROM manga_genero mg2 WHERE mg2.manga_id = m.id AND mg2.genero_id = %s)")
                        sql_params.append(genero_id_for_filter)
                    else:
                        return {
                            "total_items": 0,
                            "page": page,
                            "limit": limit,
                            "data": []
                        }, 200

                sql_where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

                count_sql = f"SELECT COUNT(DISTINCT m.id) AS total_mangas FROM mangas m LEFT JOIN manga_genero mg ON m.id = mg.manga_id LEFT JOIN generos g ON mg.genero_id = g.id {sql_where};"
                cursor.execute(count_sql, tuple(sql_params))
                total_mangas = cursor.fetchone()['total_mangas']

                sql = f"""
                SELECT
                    m.id, m.titulo, m.titulo_alternativo, m.sinopsis, m.estado,
                    m.fecha_publicacion, m.editorial, m.calificacion, m.portada_url,
                    a.nombre AS autor_nombre,
                    GROUP_CONCAT(DISTINCT g.nombre SEPARATOR ', ') AS generos
                FROM mangas m
                LEFT JOIN autores a ON m.autor_id = a.id
                LEFT JOIN manga_genero mg ON m.id = mg.manga_id
                LEFT JOIN generos g ON mg.genero_id = g.id
                {sql_where}
                GROUP BY m.id
                ORDER BY m.id DESC
                LIMIT %s OFFSET %s;
                """
                cursor.execute(sql, tuple(sql_params + [limit, offset]))
                mangas = cursor.fetchall()

                for manga in mangas:
                    if manga['generos']:
                        manga['generos'] = manga['generos'].split(', ')
                    else:
                        manga['generos'] = []
                    serialize_dates(manga)

                return {
                    "total_items": total_mangas,
                    "page": page,
                    "limit": limit,
                    "data": mangas
                }, 200
        except pymysql.Error as e:
            api.abort(500, f"Error al obtener mangas: {e}")
        finally:
            conn.close()

    @api.doc('create_manga', description='Crea un nuevo registro de manga.')
    @api.expect(manga_model, validate=True) # Validamos contra el modelo definido
    @api.marshal_with(manga_model, code=201, description='Manga creado exitosamente.')
    @api.response(400, 'Errores de validación o autor no existe')
    @api.response(409, 'Conflicto: Manga con título similar ya existe')
    def post(self):
        new_manga_data = api.payload

        validation_errors = validate_manga_data(new_manga_data)
        if validation_errors:
            api.abort(400, "Errores de validación", errors=validation_errors)

        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")

        try:
            with conn.cursor() as cursor: # Abrimos el cursor
                # Verificar si el autor existe
                if new_manga_data.get('autor_id'):
                    cursor.execute("SELECT id FROM autores WHERE id = %s", (new_manga_data['autor_id'],))
                    if not cursor.fetchone():
                        api.abort(400, "El autor_id proporcionado no existe.")

                sql_manga = """
                INSERT INTO mangas (titulo, titulo_alternativo, sinopsis, estado, fecha_publicacion, editorial, portada_url, autor_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(sql_manga, (
                    new_manga_data.get('titulo'),
                    new_manga_data.get('titulo_alternativo'),
                    new_manga_data.get('sinopsis'),
                    new_manga_data.get('estado', 'En curso'),
                    new_manga_data.get('fecha_publicacion'),
                    new_manga_data.get('editorial'),
                    new_manga_data.get('portada_url'),
                    new_manga_data.get('autor_id')
                ))
                manga_id = cursor.lastrowid
                
                if 'generos' in new_manga_data and isinstance(new_manga_data['generos'], list):
                    for genero_nombre in new_manga_data['generos']:
                        cursor.execute("SELECT id FROM generos WHERE nombre = %s", (genero_nombre,))
                        genero_row = cursor.fetchone()
                        genero_id = None
                        if genero_row:
                            genero_id = genero_row['id']
                        else:
                            cursor.execute("INSERT INTO generos (nombre) VALUES (%s)", (genero_nombre,))
                            genero_id = cursor.lastrowid

                        if genero_id:
                            cursor.execute("INSERT INTO manga_genero (manga_id, genero_id) VALUES (%s, %s)", (manga_id, genero_id))
                
                conn.commit() # Confirmamos los cambios AQUI, dentro del bloque with

                # Después de insertar y confirmar, recuperamos el objeto completo DENTRO del mismo cursor
                cursor.execute("""
                    SELECT
                        m.id, m.titulo, m.titulo_alternativo, m.sinopsis, m.estado,
                        m.fecha_publicacion, m.editorial, m.calificacion, m.portada_url,
                        a.nombre AS autor_nombre,
                        GROUP_CONCAT(g.nombre SEPARATOR ', ') AS generos
                    FROM mangas m
                    LEFT JOIN autores a ON m.autor_id = a.id
                    LEFT JOIN manga_genero mg ON m.id = mg.manga_id
                    LEFT JOIN generos g ON mg.genero_id = g.id
                    WHERE m.id = %s
                    GROUP BY m.id;
                """, (manga_id,))
                created_manga = cursor.fetchone()
                if created_manga:
                    if created_manga['generos']:
                        created_manga['generos'] = created_manga['generos'].split(', ')
                    else:
                        created_manga['generos'] = []
                    serialize_dates(created_manga)
                    return created_manga, 201
                api.abort(500, "Error: No se pudo recuperar el manga recién creado.")
        except pymysql.Error as e:
            conn.rollback()
            if e.args[0] == 1062:
                 api.abort(409, "Error: Ya existe un manga con este título o similar.")
            elif e.args[0] == 1452:
                 api.abort(400, "Error: El autor_id proporcionado no existe.")
            api.abort(500, f"Error al añadir manga: {e}")
        finally:
            conn.close()

@ns_mangas.route('/<int:manga_id>')
@api.response(404, 'Manga no encontrado')
@api.param('manga_id', 'El identificador único del manga')
class Manga(Resource):
    @api.doc('get_manga_by_id', description='Obtiene los detalles de un manga específico por su ID.')
    @api.marshal_with(manga_model, code=200, description='Detalles del manga.')
    def get(self, manga_id):
        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")

        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT
                    m.id, m.titulo, m.titulo_alternativo, m.sinopsis, m.estado,
                    m.fecha_publicacion, m.editorial, m.calificacion, m.portada_url,
                    a.nombre AS autor_nombre,
                    GROUP_CONCAT(g.nombre SEPARATOR ', ') AS generos
                FROM mangas m
                LEFT JOIN autores a ON m.autor_id = a.id
                LEFT JOIN manga_genero mg ON m.id = mg.manga_id
                LEFT JOIN generos g ON mg.genero_id = g.id
                WHERE m.id = %s
                GROUP BY m.id;
                """
                cursor.execute(sql, (manga_id,))
                manga = cursor.fetchone()

                if manga:
                    if manga['generos']:
                        manga['generos'] = manga['generos'].split(', ')
                    else:
                        manga['generos'] = []
                    serialize_dates(manga)
                    return manga, 200
                api.abort(404, "Manga no encontrado")
        except pymysql.Error as e:
            api.abort(500, f"Error al obtener manga: {e}")
        finally:
            conn.close()

    @api.doc('update_manga', description='Actualiza los datos de un manga existente.')
    @api.expect(manga_model, validate=True)
    @api.marshal_with(manga_model, code=200, description='Manga actualizado exitosamente.')
    @api.response(400, 'Errores de validación o autor no existe')
    @api.response(409, 'Conflicto: Manga con título similar ya existe')
    def put(self, manga_id):
        updated_data = api.payload
        if not updated_data:
            api.abort(400, "No se proporcionaron datos para actualizar")

        validation_errors = validate_manga_data(updated_data, is_update=True)
        if validation_errors:
            api.abort(400, "Errores de validación", errors=validation_errors)

        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")

        try:
            with conn.cursor() as cursor: # Abrimos el cursor
                set_clauses = []
                params = []
                allowed_fields = [
                    'titulo', 'titulo_alternativo', 'sinopsis', 'estado',
                    'fecha_publicacion', 'editorial', 'calificacion', 'portada_url',
                    'autor_id'
                ]

                for field in allowed_fields:
                    if field in updated_data:
                        set_clauses.append(f"{field} = %s")
                        params.append(updated_data[field])
                
                if 'autor_id' in updated_data and updated_data['autor_id'] is not None:
                    cursor.execute("SELECT id FROM autores WHERE id = %s", (updated_data['autor_id'],))
                    if not cursor.fetchone():
                        api.abort(400, "El autor_id proporcionado no existe.")

                if not set_clauses and 'generos' not in updated_data:
                    api.abort(400, "No se proporcionaron campos válidos o géneros para actualizar")

                sql_update_manga = f"UPDATE mangas SET {', '.join(set_clauses)} WHERE id = %s;"
                params.append(manga_id)
                cursor.execute(sql_update_manga, tuple(params))

                if 'generos' in updated_data and isinstance(updated_data['generos'], list):
                    cursor.execute("DELETE FROM manga_genero WHERE manga_id = %s", (manga_id,))
                    for genero_nombre in updated_data['generos']:
                        cursor.execute("SELECT id FROM generos WHERE nombre = %s", (genero_nombre,))
                        genero_row = cursor.fetchone()
                        genero_id = None
                        if genero_row:
                            genero_id = genero_row['id']
                        else:
                            cursor.execute("INSERT INTO generos (nombre) VALUES (%s)", (genero_nombre,))
                            genero_id = cursor.lastrowid

                        if genero_id:
                            cursor.execute("INSERT INTO manga_genero (manga_id, genero_id) VALUES (%s, %s)", (manga_id, genero_id))
                
                # Verificamos si la actualización del manga principal o de los géneros afectó alguna fila.
                # Es importante que el cursor.rowcount se lea *después* de la ejecución de la consulta
                # y antes de que el cursor sea potencialmente cerrado por un nuevo uso.
                # Aquí, la lógica ya tiene el cursor vivo.
                if cursor.rowcount == 0 and not ('generos' in updated_data and isinstance(updated_data['generos'], list) and len(updated_data['generos']) > 0):
                    conn.rollback()
                    api.abort(404, "Manga no encontrado o no hay cambios que aplicar")

                conn.commit() # Confirmamos los cambios AQUI

                # Después de actualizar y confirmar, recuperamos el objeto completo DENTRO del mismo cursor
                cursor.execute("""
                    SELECT
                        m.id, m.titulo, m.titulo_alternativo, m.sinopsis, m.estado,
                        m.fecha_publicacion, m.editorial, m.calificacion, m.portada_url,
                        a.nombre AS autor_nombre,
                        GROUP_CONCAT(g.nombre SEPARATOR ', ') AS generos
                    FROM mangas m
                    LEFT JOIN autores a ON m.autor_id = a.id
                    LEFT JOIN manga_genero mg ON m.id = mg.manga_id
                    LEFT JOIN generos g ON mg.genero_id = g.id
                    WHERE m.id = %s
                    GROUP BY m.id;
                """, (manga_id,))
                updated_manga = cursor.fetchone()
                if updated_manga:
                    if updated_manga['generos']:
                        updated_manga['generos'] = updated_manga['generos'].split(', ')
                    else:
                        updated_manga['generos'] = []
                    serialize_dates(updated_manga)
                    return updated_manga, 200
                api.abort(404, "Manga no encontrado después de la actualización (esto no debería ocurrir)")
        except pymysql.Error as e:
            conn.rollback()
            if e.args[0] == 1062:
                 api.abort(409, "Error: Ya existe un manga con este título o similar.")
            api.abort(500, f"Error al actualizar manga: {e}")
        finally:
            conn.close()

    @api.doc('delete_manga', description='Elimina un manga por su ID.')
    @api.response(204, 'Manga eliminado exitosamente (No Content)')
    def delete(self, manga_id):
        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")

        try:
            with conn.cursor() as cursor:
                sql = "DELETE FROM mangas WHERE id = %s;"
                cursor.execute(sql, (manga_id,))
                if cursor.rowcount == 0:
                    conn.rollback()
                    api.abort(404, "Manga no encontrado")
            conn.commit()
            return '', 204 # Retornar 204 No Content para DELETE exitoso
        except pymysql.Error as e:
            conn.rollback()
            api.abort(500, f"Error al eliminar manga: {e}")
        finally:
            conn.close()

# Endpoint de búsqueda (separado como antes, para fines de demostración)
@ns_mangas.route('/search')
class MangaSearch(Resource):
    @api.doc('search_mangas', description='Busca mangas por palabra clave en título, sinopsis o nombre de autor.')
    @api.expect(manga_search_parser)
    @api.marshal_with(manga_model, as_list=True, code=200, description='Lista de mangas encontrados.')
    def get(self):
        args = manga_search_parser.parse_args()
        query = args['q']
        if not query:
            api.abort(400, "El parámetro 'q' es requerido para la búsqueda")

        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")

        try:
            with conn.cursor() as cursor:
                search_term = f"%{query}%"
                sql = """
                SELECT
                    m.id, m.titulo, m.titulo_alternativo, m.sinopsis, m.estado,
                    m.fecha_publicacion, m.editorial, m.calificacion, m.portada_url,
                    a.nombre AS autor_nombre,
                    GROUP_CONCAT(g.nombre SEPARATOR ', ') AS generos
                FROM mangas m
                LEFT JOIN autores a ON m.autor_id = a.id
                LEFT JOIN manga_genero mg ON m.id = mg.manga_id
                LEFT JOIN generos g ON mg.genero_id = g.id
                WHERE m.titulo LIKE %s OR m.sinopsis LIKE %s OR a.nombre LIKE %s
                GROUP BY m.id
                ORDER BY m.id DESC;
                """
                cursor.execute(sql, (search_term, search_term, search_term))
                mangas = cursor.fetchall()

                for manga in mangas:
                    if manga['generos']:
                        manga['generos'] = manga['generos'].split(', ')
                    else:
                        manga['generos'] = []
                    serialize_dates(manga)

                return mangas, 200
        except pymysql.Error as e:
            api.abort(500, f"Error al buscar mangas: {e}")
        finally:
            conn.close()


# --- Autores ---
@ns_autores.route('/')
class AutorList(Resource):
    @api.doc('list_autores', description='Obtiene una lista de todos los autores.')
    @api.marshal_with(autor_model, as_list=True, code=200, description='Lista de autores.')
    def get(self):
        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM autores ORDER BY nombre ASC")
                autores = cursor.fetchall()
                serialize_dates(autores)
                return autores, 200
        except pymysql.Error as e:
            api.abort(500, f"Error al obtener autores: {e}")
        finally:
            conn.close()

    @api.doc('create_autor', description='Crea un nuevo autor.')
    @api.expect(autor_model, validate=True)
    @api.marshal_with(autor_model, code=201, description='Autor creado exitosamente.')
    @api.response(409, 'Conflicto: Autor con este nombre ya existe')
    def post(self):
        new_autor_data = api.payload
        if not new_autor_data or 'nombre' not in new_autor_data:
            api.abort(400, "El nombre del autor es requerido.")

        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")
        try:
            with conn.cursor() as cursor: # Abrimos el cursor
                sql = "INSERT INTO autores (nombre, biografia, fecha_nacimiento, pais) VALUES (%s, %s, %s, %s);"
                cursor.execute(sql, (
                    new_autor_data['nombre'],
                    new_autor_data.get('biografia'),
                    new_autor_data.get('fecha_nacimiento'),
                    new_autor_data.get('pais')
                ))
                autor_id = cursor.lastrowid
                conn.commit() # Confirmamos los cambios AQUI
                # Después de insertar y confirmar, recuperamos el objeto completo DENTRO del mismo cursor
                cursor.execute("SELECT * FROM autores WHERE id = %s", (autor_id,))
                new_autor = cursor.fetchone()
                serialize_dates(new_autor)
                return new_autor, 201
        except pymysql.Error as e:
            conn.rollback()
            if e.args[0] == 1062:
                api.abort(409, "Error: Ya existe un autor con este nombre.")
            api.abort(500, f"Error al añadir autor: {e}")
        finally:
            conn.close()

@ns_autores.route('/<int:autor_id>')
@api.response(404, 'Autor no encontrado')
@api.param('autor_id', 'El identificador único del autor')
class Autor(Resource):
    @api.doc('get_autor_by_id', description='Obtiene los detalles de un autor específico por su ID.')
    @api.marshal_with(autor_model, code=200, description='Detalles del autor.')
    def get(self, autor_id):
        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM autores WHERE id = %s", (autor_id,))
                autor = cursor.fetchone()
                if autor:
                    serialize_dates(autor)
                    return autor, 200
                api.abort(404, "Autor no encontrado")
        except pymysql.Error as e:
            api.abort(500, f"Error al obtener autor: {e}")
        finally:
            conn.close()

    @api.doc('update_autor', description='Actualiza los datos de un autor existente.')
    @api.expect(autor_model, validate=True)
    @api.marshal_with(autor_model, code=200, description='Autor actualizado exitosamente.')
    @api.response(409, 'Conflicto: Autor con este nombre ya existe')
    def put(self, autor_id):
        updated_data = api.payload
        if not updated_data:
            api.abort(400, "No se proporcionaron datos para actualizar")
        if 'nombre' in updated_data and not isinstance(updated_data['nombre'], str):
            api.abort(400, "El nombre del autor debe ser una cadena de texto.")

        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")

        try:
            with conn.cursor() as cursor: # Abrimos el cursor
                set_clauses = []
                params = []
                allowed_fields = ['nombre', 'biografia', 'fecha_nacimiento', 'pais']

                for field in allowed_fields:
                    if field in updated_data:
                        set_clauses.append(f"{field} = %s")
                        params.append(updated_data[field])

                if not set_clauses:
                    api.abort(400, "No se proporcionaron campos válidos para actualizar")

                sql = f"UPDATE autores SET {', '.join(set_clauses)} WHERE id = %s;"
                params.append(autor_id)
                cursor.execute(sql, tuple(params))

                if cursor.rowcount == 0:
                    conn.rollback()
                    api.abort(404, "Autor no encontrado o no hay cambios que aplicar")
            
                conn.commit() # Confirmamos los cambios AQUI
                # Después de actualizar y confirmar, recuperamos el objeto completo DENTRO del mismo cursor
                cursor.execute("SELECT * FROM autores WHERE id = %s", (autor_id,))
                updated_autor = cursor.fetchone()
                serialize_dates(updated_autor)
                return updated_autor, 200
        except pymysql.Error as e:
            conn.rollback()
            if e.args[0] == 1062:
                api.abort(409, "Error: Ya existe un autor con este nombre.")
            api.abort(500, f"Error al actualizar autor: {e}")
        finally:
            conn.close()

    @api.doc('delete_autor', description='Elimina un autor por su ID.')
    @api.response(204, 'Autor eliminado exitosamente (No Content)')
    @api.response(409, 'Conflicto: El autor está asociado a mangas.')
    def delete(self, autor_id):
        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")
        try:
            with conn.cursor() as cursor:
                sql = "DELETE FROM autores WHERE id = %s;"
                cursor.execute(sql, (autor_id,))
                if cursor.rowcount == 0:
                    conn.rollback()
                    api.abort(404, "Autor no encontrado")
                conn.commit() # Confirmamos los cambios AQUI
            return '', 204
        except pymysql.Error as e:
            conn.rollback()
            if e.args[0] == 1451:
                api.abort(409, "Error: No se puede eliminar el autor porque está asociado a uno o más mangas. Considera desvincular los mangas primero.")
            api.abort(500, f"Error al eliminar autor: {e}")
        finally:
            conn.close()

# --- Géneros ---
@ns_generos.route('/')
class GeneroList(Resource):
    @api.doc('list_generos', description='Obtiene una lista de todos los géneros.')
    @api.marshal_with(genero_model, as_list=True, code=200, description='Lista de géneros.')
    def get(self):
        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM generos ORDER BY nombre ASC")
                generos = cursor.fetchall()
                return generos, 200
        except pymysql.Error as e:
            api.abort(500, f"Error al obtener géneros: {e}")
        finally:
            conn.close()

    @api.doc('create_genero', description='Crea un nuevo género.')
    @api.expect(genero_model, validate=True)
    @api.marshal_with(genero_model, code=201, description='Género creado exitosamente.')
    @api.response(409, 'Conflicto: Género con este nombre ya existe')
    def post(self):
        new_genero_data = api.payload
        if not new_genero_data or 'nombre' not in new_genero_data or not isinstance(new_genero_data['nombre'], str):
            api.abort(400, "El nombre del género es requerido y debe ser una cadena de texto.")
        if len(new_genero_data['nombre']) > 100:
            api.abort(400, "El nombre del género no puede exceder los 100 caracteres.")

        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")
        try:
            with conn.cursor() as cursor: # Abrimos el cursor
                sql = "INSERT INTO generos (nombre) VALUES (%s);"
                cursor.execute(sql, (new_genero_data['nombre'],))
                genero_id = cursor.lastrowid
                conn.commit() # Confirmamos los cambios AQUI
                # Después de insertar y confirmar, recuperamos el objeto completo DENTRO del mismo cursor
                cursor.execute("SELECT * FROM generos WHERE id = %s", (genero_id,))
                new_genero = cursor.fetchone()
                return new_genero, 201
        except pymysql.Error as e:
            conn.rollback()
            if e.args[0] == 1062:
                api.abort(409, "Error: Ya existe un género con este nombre.")
            api.abort(500, f"Error al añadir género: {e}")
        finally:
            conn.close()

@ns_generos.route('/<int:genero_id>')
@api.response(404, 'Género no encontrado')
@api.param('genero_id', 'El identificador único del género')
class Genero(Resource):
    @api.doc('get_genero_by_id', description='Obtiene los detalles de un género específico por su ID.')
    @api.marshal_with(genero_model, code=200, description='Detalles del género.')
    def get(self, genero_id):
        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM generos WHERE id = %s", (genero_id,))
                genero = cursor.fetchone()
                if genero:
                    return genero, 200
                api.abort(404, "Género no encontrado")
        except pymysql.Error as e:
            api.abort(500, f"Error al obtener género: {e}")
        finally:
            conn.close()

    @api.doc('update_genero', description='Actualiza los datos de un género existente.')
    @api.expect(genero_model, validate=True)
    @api.marshal_with(genero_model, code=200, description='Género actualizado exitosamente.')
    @api.response(409, 'Conflicto: Género con este nombre ya existe')
    def put(self, genero_id):
        updated_data = api.payload
        if not updated_data or 'nombre' not in updated_data or not isinstance(updated_data['nombre'], str):
            api.abort(400, "El nombre del género es requerido para actualizar y debe ser una cadena de texto.")
        if len(updated_data['nombre']) > 100:
            api.abort(400, "El nombre del género no puede exceder los 100 caracteres.")

        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")

        try:
            with conn.cursor() as cursor: # Abrimos el cursor
                sql = "UPDATE generos SET nombre = %s WHERE id = %s;"
                cursor.execute(sql, (updated_data['nombre'], genero_id))

                if cursor.rowcount == 0:
                    conn.rollback()
                    api.abort(404, "Género no encontrado o no hay cambios que aplicar")
                
                conn.commit() # Confirmamos los cambios AQUI
                # Después de actualizar y confirmar, recuperamos el objeto completo DENTRO del mismo cursor
                cursor.execute("SELECT * FROM generos WHERE id = %s", (genero_id,))
                updated_genero = cursor.fetchone()
                return updated_genero, 200
        except pymysql.Error as e:
            conn.rollback()
            if e.args[0] == 1062:
                api.abort(409, "Error: Ya existe un género con este nombre.")
            api.abort(500, f"Error al actualizar género: {e}")
        finally:
            conn.close()

    @api.doc('delete_genero', description='Elimina un género por su ID.')
    @api.response(204, 'Género eliminado exitosamente (No Content)')
    @api.response(409, 'Conflicto: El género está asociado a mangas.')
    def delete(self, genero_id):
        conn = get_db_connection()
        if conn is None:
            api.abort(500, "Error de conexión a la base de datos")
        try:
            with conn.cursor() as cursor:
                sql = "DELETE FROM generos WHERE id = %s;"
                cursor.execute(sql, (genero_id,))
                if cursor.rowcount == 0:
                    conn.rollback()
                    api.abort(404, "Género no encontrado")
                conn.commit() # Confirmamos los cambios AQUI
            return '', 204
        except pymysql.Error as e:
            conn.rollback()
            if e.args[0] == 1451:
                api.abort(409, "Error: No se puede eliminar el género porque está asociado a uno o más mangas.")
            api.abort(500, f"Error al eliminar género: {e}")
        finally:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
