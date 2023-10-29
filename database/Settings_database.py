import sqlite3


class Settings_database:
    def __init__(self):
        self.database_path = f'database/database_storage/Settings.db'
        self.conn = sqlite3.connect(self.database_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Admin_settings(
                                               ID PRIMARY KEY,
                                               Message_info TEXT,
                                               Message TEXT
                                               );""")
        self.conn.commit()

    async def get_admin_settings_item(self, message_info):
        self.cursor.execute("SELECT Message FROM Admin_settings WHERE Message_info=?", (message_info,))
        message = self.cursor.fetchall()
        print(message)
        return message[0][0]

    def update_admin_settings_item(self, message_info):
        self.cursor.execute("UPDATE Admin_settings SET Message WHERE Message_info=?", (message_info,))
        self.conn.commit()

    def get_admin_settings_item_js(self, message_info):
        self.cursor.execute("SELECT Message FROM Admin_settings WHERE Message_info=?", (message_info,))
        message = self.cursor.fetchall()
        print(message)
        return message[0][0]

    def get_all_messages(self):
        self.cursor.execute("SELECT * FROM Admin_settings")
        messages = self.cursor.fetchall()
        return messages

    def update_message(self, message_type, new_text):
        self.cursor.execute("UPDATE Admin_settings SET Message = ? WHERE Message_info = ?", (new_text, message_type))
        self.conn.commit()


