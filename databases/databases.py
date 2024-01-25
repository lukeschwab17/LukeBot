import sqlite3
from datetime import datetime
import os
from typing import Self
from cryptography.fernet import Fernet

class Database:
    def __init__(self):
        self.db_file_location = r"C:\Users\schwa\Desktop\discBot\LukeBot\LukeBot\databases\database.db"
        
        with open(r"C:\Users\schwa\Desktop\API_KEYS\filekey.key", "rb") as key_file:
            self.key = Fernet(key_file.read())
            
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
    
    # THE FOLLOWING ARE ALL FUNCTIONS FOR AVATAR COMMAND
    # stores all avatar urls and images

    @classmethod
    def check_existing_avatar_url(cls, avatar_url: str):
        """Returns True if avatar URL already exists in database's avatar table."""
        with cls() as db:
            db.curs.execute("Select image_url FROM avatars WHERE image_url = ?", (avatar_url,))
            selected_url = db.curs.fetchone()
            
            if selected_url:
                return True
            
            return False
        
    @classmethod
    def store_avatar_data(cls, avatarURL: str, avatarName: str, submitterID: str):
        with cls() as db:
            db.curs.execute("""CREATE TABLE IF NOT EXISTS avatars (
                                image_url text,    
                                file_path text,
                                avatar_name text,
                                submitter_id text
                            )""")
            
            db.curs.execute("INSERT INTO avatars (image_url, avatar_name, submitter_id) VALUES (?, ?, ?)",
                        (avatarURL, avatarName, submitterID))


            file_path = f"assets/avatars/{db.curs.lastrowid}.png"# Generate file path using the ID and file extension

            db.curs.execute("UPDATE avatars SET file_path = ? WHERE rowid = ?", (file_path, db.curs.lastrowid)) # Update the file path for the last inserted row

    @classmethod
    def get_table(cls, table_name: str):
        with cls() as db:
            db.curs.execute(f"SELECT rowid, * FROM {table_name}")
            return db.curs.fetchall()
            
    @classmethod
    def get_avatar_file_path(cls, avatarURL: str):
        with cls() as db:
            db.curs.execute("SELECT file_path FROM avatars WHERE image_url = ?", (avatarURL,))
            selectedURL = db.curs.fetchone()
            
            return selectedURL
        
    @classmethod
    def get_ids(cls, table_name: str):
        with cls() as db:
            db.curs.execute(f"SELECT rowid FROM {table_name}")
            all_ids = [row[0] for row in db.curs.fetchall()]
            return all_ids
        
    @classmethod
    def get_largest_primary_key(cls, table_name: str): # yes its redundant i couldnt figure out how to call getIDS() inside this function
        with cls() as db:
            db.curs.execute(f"SELECT rowid FROM {table_name}")
            all_ids = [row[0] for row in db.curs.fetchall()]
            return max(all_ids)
        
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
            
    @classmethod
    def get_last_item(cls, table_name: str):
        with cls() as db:
            db.curs.execute(f"SELECT rowid, * FROM {table_name} ORDER BY rowid DESC LIMIT 1")
            return db.curs.fetchone()
            
     
    @classmethod
    def get_usernames(cls):
        with cls() as db:
            db.curs.execute(f"SELECT username FROM user_accounts")
            return db.curs.fetchall()

    @classmethod
    def get_discord_ids(cls, table_name: str):
        with cls() as db:
            db.curs.execute(f"SELECT discord_id FROM {table_name}")
            return db.curs.fetchall()

    @classmethod
    def create_account(cls, acc_info: list): # list -> username, password, discord id
        with cls() as db:
            db.curs.execute("""CREATE TABLE IF NOT EXISTS user_accounts (
                            username text,
                            password text,
                            discord_id text,
                            guilds text,
                            PRIMARY KEY (username, discord_id)
                            )""")
            
            db.curs.execute("SELECT server_id FROM server_users WHERE member_id = ?", (acc_info[2],)) # grab guilds user is in
            guilds = db.curs.fetchall()
            guild_str = ""
            for guild in guilds:
                guild_str += str(guild)[2:-3] + " " # weird format? tuples messing up. idk
                
            print(guild_str)
            db.curs.execute("INSERT INTO user_accounts VALUES (?, ?, ?, ?)", (acc_info[0], acc_info[1], acc_info[2], guild_str))
            return "success"
    