# db.py
import mysql.connector

def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="8106516455",
        database="vote"
    )

def register_user(connection, username, password):
    cursor = connection.cursor()
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    cursor.execute(query, (username, password))
    connection.commit()

def authenticate_user(connection, username, password):
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    return cursor.fetchone()

def is_admin(connection, user_id):
    cursor = connection.cursor(dictionary=True)
    query = "SELECT is_admin FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    return user['is_admin']

def get_ongoing_elections(connection):
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM elections WHERE start_date <= NOW() AND end_date >= NOW()"
    cursor.execute(query)
    return cursor.fetchall()

def has_user_voted(connection, user_id, election_id):
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM votes WHERE user_id = %s AND election_id = %s"
    cursor.execute(query, (user_id, election_id))
    return cursor.fetchone() is not None

def record_vote(connection, user_id, election_id, candidate):
    cursor = connection.cursor()
    query = "INSERT INTO votes (user_id, election_id, candidate) VALUES (%s, %s, %s)"
    cursor.execute(query, (user_id, election_id, candidate))
    connection.commit()

def get_all_users(connection):
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM users"
    cursor.execute(query)
    return cursor.fetchall()

def get_all_votes(connection):
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM votes"
    cursor.execute(query)
    return cursor.fetchall()


def get_all_elections(db_connection):
    cursor = db_connection.cursor(dictionary=True)
    query = "SELECT id, name, start_date, end_date, candidate1_name, candidate2_name, candidate1_image, candidate2_image FROM elections"
    cursor.execute(query)
    elections = cursor.fetchall()
    cursor.close()
    return elections

    

def create_election(connection, name, start_date, end_date,candidate1_name,candidate2_name,candidate1_image, candidate2_image):
    cursor = connection.cursor()
    query = """
        INSERT INTO elections (name, start_date, end_date,candidate1_name,candidate2_name,candidate1_image, candidate2_image)
        VALUES (%s, %s, %s,%s,%s,%s,%s );

    """
    cursor.execute(query, (name, start_date, end_date,candidate1_name,candidate2_name,candidate1_image, candidate2_image))
    connection.commit()

def authenticate_admin(connection, username, password):
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE username = %s AND password = %s AND is_admin = TRUE"
    cursor.execute(query, (username, password))
    return cursor.fetchone()

def delete_election(connection, election_id):
    cursor = connection.cursor()
    # First, delete votes associated with this election
    query_delete_votes = "DELETE FROM votes WHERE election_id = %s"
    cursor.execute(query_delete_votes, (election_id,))
    # Now, delete the election
    query_delete_election = "DELETE FROM elections WHERE id = %s"
    cursor.execute(query_delete_election, (election_id,))
    connection.commit()
    cursor.close()


def get_vote_count(connection, election_id):
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM votes WHERE election_id = %s"
    cursor.execute(query, (election_id,))
    return cursor.fetchone()[0]

def get_winner(connection, election_id):
    cursor = connection.cursor()
    query = "SELECT candidate, COUNT(*) as votes FROM votes WHERE election_id = %s GROUP BY candidate ORDER BY votes DESC LIMIT 1"
    cursor.execute(query, (election_id,))
    result = cursor.fetchone()
    return result[0] if result else "No votes yet"

def record_vote(connection, user_id, election_id, candidate):
    cursor = connection.cursor()
    query = "INSERT INTO votes (user_id, election_id, candidate) VALUES (%s, %s, %s)"
    cursor.execute(query, (user_id, election_id, candidate))
    connection.commit()

