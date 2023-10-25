import sqlite3

class Settings_database:
    def __init__(self):
        self.database_path = f'database/database_storage/Settings.db'
        self.conn = sqlite3.connect(self.database_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Admin_settings(
                                               ID PRIMARY KEY,
                                               Message_info TEXT,
                                               Message TEST
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