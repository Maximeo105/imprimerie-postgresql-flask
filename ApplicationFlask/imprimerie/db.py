import psycopg2
from psycopg2.extras import RealDictCursor
from flask import current_app, g

class DatabaseError(Exception):
    """Exception personnalisée pour les erreurs de base de données."""
    pass

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=current_app.config['POSTGRES_HOST'],
            port=current_app.config['POSTGRES_PORT'],
            database=current_app.config['POSTGRES_DB'],
            user=current_app.config['POSTGRES_USER'],
            password=current_app.config['POSTGRES_PASSWORD']
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def handle_db_error(e):
    """Convertit les erreurs PostgreSQL en messages lisibles."""
    error_msg = str(e)
    
    if 'chk_impression_coherent' in error_msg:
        raise DatabaseError("Erreur: Pour une impression, vous devez spécifier le type d'encre recto. Pour recto/verso, l'encre verso est aussi requise.")
    elif 'chk_numerotage_coherent' in error_msg:
        raise DatabaseError("Erreur: La numérotation de fin doit être supérieure ou égale à la numérotation de début.")
    elif 'chk_dates_coherentes' in error_msg:
        raise DatabaseError("Erreur: La date limite doit être postérieure à la date de commande.")
    elif 'chk_sous_traitant_coherent' in error_msg:
        raise DatabaseError("Erreur: Un coût sous-traitant nécessite de sélectionner un sous-traitant.")
    elif 'fk_commande_no_sous_traitant' in error_msg.lower():
        raise DatabaseError("Impossible de supprimer ce sous-traitant: il est utilisé par une ou plusieurs commandes.")
    elif 'fk_commande_no_client' in error_msg.lower():
        raise DatabaseError("Impossible de supprimer ce client: il a des commandes associées.")
    elif 'fk_commande_no_dossier' in error_msg.lower():
        raise DatabaseError("Impossible de supprimer ce type de travail: il est utilisé par une ou plusieurs commandes.")
    elif 'foreignkeyviolation' in error_msg.lower() or 'foreign key' in error_msg.lower():
        raise DatabaseError("Impossible de supprimer cet élément: il est référencé ailleurs.")
    elif 'unique' in error_msg.lower() or 'duplicate' in error_msg.lower():
        raise DatabaseError("Cet enregistrement existe déjà.")
    else:
        raise DatabaseError(f"Erreur base de données: {error_msg[:200]}")

def execute_query(sql, params=None):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        return results
    except psycopg2.Error as e:
        cursor.close()
        conn.rollback()
        handle_db_error(e)

def execute_query_one(sql, params=None):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        return result
    except psycopg2.Error as e:
        cursor.close()
        conn.rollback()
        handle_db_error(e)

def execute_insert(sql, params=None):
    conn = get_db()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        result = None
        if 'RETURNING' in sql.upper():
            result = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        return result
    except psycopg2.Error as e:
        cursor.close()
        conn.rollback()
        handle_db_error(e)

def execute_update(sql, params=None):
    conn = get_db()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        conn.commit()
        cursor.close()
    except psycopg2.Error as e:
        cursor.close()
        conn.rollback()
        handle_db_error(e)
