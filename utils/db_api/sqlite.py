import sqlite3


class Database:
    def __init__(self, path_to_db="../../data/Main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False,
                fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()
        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE Users (
        id int NOT NULL,
        name varchar(255) NOT NULL,
        email varchar(255),
        PRIMARY KEY (id)
        )
        """
        self.execute(sql, commit=True)

    def add_user(self, user_id: int, name: str, email: str = None):
        sql = "INSERT INTO Users(id, name, email) VALUES(?, ?, ?)"
        parameters = (user_id, name, email)
        self.execute(sql, parameters=parameters, commit=True)

    def select_all_users(self):
        sql = "SELECT * FROM Users"
        return self.execute(sql, fetchall=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) form Users", fetchone=True)

    def update_email(self, email, user_id):
        sql = "UPDATE Users SET email=? WHERE id=?"
        return self.execute(sql, parameters=(email, user_id), commit=True)

    def delete_all_users(self):
        self.execute("DELETE FROM Users WHERE True", commit=True)

    def delete_user(self, user_id):
        sql = "DELETE FROM Users WHERE id=?"
        self.execute(sql, parameters=(user_id,), commit=True)


def logger(statement):
    print(f"""
--------------------------------------------------------
Executing: {statement}
""")
