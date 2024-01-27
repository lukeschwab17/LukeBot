import sqlite3
from datetime import datetime
import os
from typing import Self
from cryptography.fernet import Fernet
from all_keys import DATABASE_KEY

class Database:
    def __init__(self):
        self.db_file_location = 'databases/database.db'
        
        self.key = Fernet(DATABASE_KEY)
            
        with open(self.db_file_location, "rb") as db_file:
            original = db_file.read()
        
        decrypted = self.key.decrypt(original)
        
        with open(self.db_file_location, "wb") as dec_file:
            dec_file.write(decrypted)
          
        self.database = (self.db_file_location);
        self.conn = None
        self.curs = None

    def connect(self):
        self.conn = sqlite3.connect(self.database)
        self.curs = self.conn.cursor()

    def close(self):
        # opening the original file to encrypt
        with open(self.db_file_location, 'rb') as file:
            original = file.read()
        
        # encrypting the file
        encrypted = self.key.encrypt(original)
 
        # opening the file in write mode and 
        # writing the encrypted data
        with open(self.db_file_location, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
            
        if self.conn:
            self.conn.close()

    def commit(self):
        if self.conn:
            self.conn.commit()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.commit()
        self.close()

    # adds command call to database table
    @classmethod
    def cmd_to_db(cls, cmd: str, server: str, user: str, context: str = None):
        with cls() as db:
            db.curs.execute("""CREATE TABLE IF NOT EXISTS command_calls ( 
                              command_name text,
                              calling_server_id text,
                              calling_user_id text,
                              time_called text,
                              command_context text
                              )""")

            if context:
                context = context.lower()

            # add command call data to command_calls table
            db.curs.execute("INSERT INTO command_calls VALUES (?, ?, ?, ?, ?)", (cmd, server, user, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), context))

    # store all servers bot is in as well as all members of those servers
    @classmethod
    def store_servers_data(cls, serverData: set):
        with cls() as db:
            db.curs.execute("""CREATE TABLE IF NOT EXISTS server_users (
                                  server_id text,
                                  server_name text,
                                  member_id text,
                                  member_name text,
                                  member_avatar text,
                                  PRIMARY KEY (server_id, member_id)
                              )""")
            
            for data in serverData:
                db.curs.execute("INSERT OR IGNORE INTO server_users VALUES (?, ?, ?, ?, ?)", data)
    
    # get all rows from given table
    @classmethod
    def get_table(cls, table_name: str) -> tuple:
        with cls() as db:
            db.curs.execute(f"SELECT rowid, * FROM {table_name}")
            return db.curs.fetchall()
            

    # get all table rowids from given table
    @classmethod
    def get_ids(cls, table_name: str) -> tuple:
        with cls() as db:
            db.curs.execute(f"SELECT rowid FROM {table_name}")
            all_ids = [row[0] for row in db.curs.fetchall()]
            return all_ids
        
    # get largest rowid from given table
    @classmethod
    def get_largest_rowid(cls, table_name: str) -> int: # yes its redundant i couldnt figure out how to call getIDS() inside this function
        with cls() as db:
            db.curs.execute(f"SELECT rowid FROM {table_name}")
            all_ids = [row[0] for row in db.curs.fetchall()]
            return max(all_ids)
        
    # get last item from given table
    @classmethod
    def get_last_item(cls, table_name: str) -> tuple:
        with cls() as db:
            db.curs.execute(f"SELECT rowid, * FROM {table_name} ORDER BY rowid DESC LIMIT 1")
            return db.curs.fetchone()
            
    # THE FOLLOWING ARE METHODS FOR AVATAR COMMANDS #
    @classmethod
    def check_existing_avatar_url(cls, avatar_url: str) -> bool:
        """Returns True if avatar URL already exists in database's avatar table."""
        with cls() as db:
            db.curs.execute("Select image_url FROM avatars WHERE image_url = ?", (avatar_url,))
            selected_url = db.curs.fetchone()
            
            if selected_url:
                return True
            
            return False
        
    # store new avatar data in database
    @classmethod
    def store_avatar_data(cls, avatar_url: str, avatar_name: str, submitter_id: str):
        with cls() as db:
            db.curs.execute("""CREATE TABLE IF NOT EXISTS avatars (
                                image_url text,    
                                file_path text,
                                avatar_name text,
                                submitter_id text
                            )""")
            
            db.curs.execute("INSERT INTO avatars (image_url, avatar_name, submitter_id) VALUES (?, ?, ?)",
                        (avatar_url, avatar_name, submitter_id))


            file_path = f"assets/avatars/{db.curs.lastrowid}.png"# Generate file path using the ID and file extension

            db.curs.execute("UPDATE avatars SET file_path = ? WHERE rowid = ?", (file_path, db.curs.lastrowid)) # Update the file path for the last inserted row

    # get file path of avatar given the URL
    @classmethod
    def get_avatar_file_path(cls, avatar_url: str) -> str:
        with cls() as db:
            db.curs.execute("SELECT file_path FROM avatars WHERE image_url = ?", (avatar_url,))
            selected_url = db.curs.fetchone()
            
            return selected_url

    # FOLLOWING METHODS ARE FOR record_session COMMAND IN Media.py #
    @classmethod
    def submit_video(cls, user_ids: set, numclips: int, clip_name: str, guild_id: str):
        user_id_string = ""
        for user in user_ids:
            user_id_string += (user + " ")

        with cls() as db:
            #db.curs.execute("DROP TABLE recording_session_compilations")
            db.curs.execute("""CREATE TABLE IF NOT EXISTS recording_session_compilations ( 
                                user_ids text,
                                number_of_clips integer,
                                recording_name text,
                                guild_id text,
                                file_path text
                            )""")

            db.curs.execute("INSERT into recording_session_compilations (user_ids, number_of_clips, recording_name, guild_id) VALUES (?, ?, ?, ?)", (user_id_string, numclips, clip_name, guild_id))
            
            file_path = rf"C:\Users\schwa\Desktop\video_website\video_website\video_website\static\videos\{db.curs.lastrowid}.mp4"# Generate file path using the ID and file extension
            db.curs.execute("UPDATE recording_session_compilations SET file_path = ? WHERE rowid = ?", (file_path, db.curs.lastrowid)) # Update the file path for the last inserted row
            
 