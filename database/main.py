"""
Database Module

This module provides a database manager class for interacting with an SQLite database. It includes methods for
connecting to the database, creating tables, inserting data, updating data, and performing various database
operations. The module is designed to support context management for handling database connections and transactions.

Classes:
    - DatabaseManager: A class for managing database interactions.

Example:
    # Initialize a DatabaseManager
    async with DatabaseManager("test.db") as db:
        # Perform database operations here
"""


import aiosqlite


class DatabaseManager:
    """
    A database manager class for interacting with the SQLite database.

    This class provides methods to connect to and interact with an SQLite database. It supports context management
    for handling database connections and transactions.

    Args:
        db_name (str): The name of the SQLite database.

    Example:
        # Initialize a DatabaseManager
        async with DatabaseManager("test.db") as db:
            # Perform database operations here
    """
    def __init__(self, db_name):
        self.db_name = db_name

    async def __aenter__(self):
        self.conn = await aiosqlite.connect(self.db_name)
        await self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = await self.conn.cursor()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.commit()
        await self.conn.close()

    async def create_tables(self):
        """Creates subscribers table"""
        await self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS subscribers (
                email TEXT,
                first_name TEXT,
                last_name TEXT,
                program_title TEXT
                                                    )
                            """)

        await self.cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS all_users (
                        email TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        telegram_id INTEGER,
                        telegram_username INTEGER,
                        main_group_id INTEGER,
                        small_group_id INTEGER,
                        privacy TEXT,
                        last_homework DATE,
                        last_practice DATE,
                        ghl_id TEXT,
                        ghl_opp_id TEXT,
                        first_date DATE,
                        user_program INTEGER,
                        FOREIGN KEY(user_program) REFERENCES programs(id) ON DELETE CASCADE
                                                            )
                                    """)

        await self.cursor.execute(f"""
                           CREATE TABLE IF NOT EXISTS admins (
                               first_name TEXT,
                               last_name TEXT,
                               telegram_id INTEGER
                                                                   )
                                           """)

        await self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS programs (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    program_name TEXT,
                                    program_end DATE,
                                    ghl_pipeline_id TEXT,
                                    ghl_students_id TEXT,
                                    ghl_no_pop_id TEXT
                                );
                            """)

        await self.cursor.execute(f"""
                                   CREATE TABLE IF NOT EXISTS super_admins (
                                       first_name TEXT,
                                       last_name TEXT,
                                       telegram_id INTEGER
                                                                           )
                                                   """)

        await self.cursor.execute(f"""
                                   CREATE TABLE IF NOT EXISTS pending_admins (
                                       first_name TEXT,
                                       last_name TEXT,
                                       telegram_id INTEGER
                                                                           )
                                                   """)

        await self.cursor.execute(f"""
                                   CREATE TABLE IF NOT EXISTS groups (
                                        group_title TEXT,
                                        group_id INTEGER,
                                        group_spreadsheet_id TEXT, 
                                        group_invite_link TEXT,
                                        current_members INTEGER,
                                        program INTEGER,
                                        FOREIGN KEY(program) REFERENCES programs(id) ON DELETE CASCADE
                                                                     )
                                   """)

    async def insert_data(self, table_name: str, data: dict):
        """Receives table name and data need to be inserted"""
        placeholders = ', '.join(['?'] * (len(data.values())))
        columns = ', '.join(data.keys())
        values = tuple(list(data.values()))

        await self.cursor.execute(f"""
                                          INSERT INTO {table_name} ({columns})
                                          VALUES ({placeholders})
                                       """, values)

        last_row_id = self.cursor.lastrowid
        return last_row_id

    async def update_data(self, table_name: str, data: dict, telegram_id: int):
        set_values = ', '.join([f'{key} = ?' for key in data.keys()])
        values = tuple(list(data.values()) + [telegram_id])

        query = f"""
                UPDATE {table_name}
                SET {set_values}
                WHERE telegram_id = ?
            """

        await self.cursor.execute(query, values)

    async def update_program_data(self, table_name: str, data: dict, group_title: str):
        set_values = ', '.join([f'{key} = ?' for key in data.keys()])
        values = tuple(list(data.values()) + [group_title])

        query = f"""
                UPDATE {table_name}
                SET {set_values}
                WHERE program_main_group_title = ?
            """

        await self.cursor.execute(query, values)

    async def check_existence(self, table_name: str, parameters: dict):
        """Receives table name and parameters in dict, featuring key as column name and value as value in database"""
        column = parameters["column"]
        value = parameters["value"]
        query = f"SELECT * FROM {table_name} WHERE {column} = ?"

        await self.cursor.execute(query, (value, ))
        result = await self.cursor.fetchone()
        if result:
            columns = [description[0] for description in self.cursor.description]
            result_dict = {columns[i]: result[i] for i in range(len(columns))}
            return result_dict

        else:
            return False

    async def get_all_user_data(self, table_name: str, telegram_id: int):
        """Receives user ID and table name anr return all user data"""
        query = f"SELECT * FROM {table_name} WHERE telegram_id = ?"

        await self.cursor.execute(query, (telegram_id,))
        result = await self.cursor.fetchone()

        if result:
            columns = [description[0] for description in self.cursor.description]
            result_dict = {columns[i]: result[i] for i in range(len(columns))}
            return result_dict

        else:
            return False

    async def drop_table(self, table_name: str):
        query = f"DROP TABLE {table_name}"

        await self.cursor.execute(query)

    async def get_all_table_data(self, table_name: str):
        query = f"SELECT * FROM {table_name}"
        await self.cursor.execute(query)
        result = await self.cursor.fetchall()

        if result:
            columns = [description[0] for description in self.cursor.description]
            result_list = [dict(zip(columns, row)) for row in result]
            return result_list

        else:
            return []

    async def delete_user_from_db(self, table_name: str, telegram_id: int):
        query = f"DELETE FROM {table_name} WHERE telegram_id = ?"
        await self.cursor.execute(query, (telegram_id, ))

    async def get_program_data(self, parameters: dict):
        query = "SELECT * FROM programs"

        placeholders = []
        values = []
        for key, value in parameters.items():
            placeholders.append(f"{key} = ?")
            values.append(value)

        query += " WHERE " + " AND ".join(placeholders)

        await self.cursor.execute(query, tuple(values))
        result = await self.cursor.fetchall()

        return result

    async def custom_query(self, query: str):
        await self.cursor.execute(query)

        result = await self.cursor.fetchall()

        if result:
            columns = [description[0] for description in self.cursor.description]
            result_list = [dict(zip(columns, row)) for row in result]
            return result_list

        else:
            return False

    async def delete_program(self, program_id: int):
        query = f"""DELETE FROM programs WHERE id = {program_id}"""

        await self.cursor.execute(query)

    # also there is some GoHighLevel related methods that could not be disclosed due to NDA.
