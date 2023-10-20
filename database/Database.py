import json

import log
import sqlite3


import sqlite3

class Database:
    def __init__(self):
        self.database_path = f'database/database_storage/Settings.db'
        self.conn = sqlite3.connect(self.database_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
                User_Id INTEGER PRIMARY KEY,
                Username TEXT,
                access INT,
                User_type TEXT,
                Privileges_type INT,
                Count_orders INT,
                Count_good_orders INT,
                Count_application INT,
                Count_good_application INT,
                Receiving_order INT
                );""")
        self.conn.commit()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Admins(
                User_Id INTEGER PRIMARY KEY,
                Username TEXT
                );""")
        self.conn.commit()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Orders(
                        Order_Id INTEGER PRIMARY KEY,
                        Courier_Id TEXT,
                        Customer_id TEXT,
                        Order_type TEXT,
                        Point_A TEXT,
                        Point_B TEXT,
                        Comment TEXT,
                        Messages TEXT
                        );""")
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS links(
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Link TEXT,
                        Link_type TEXT
                        );""")
        self.conn.commit()

    async def add_user_db(self, user_id, username, access=0, user_type=None, privileges_type=1, count_orders=0, count_good_orders=0,
                          count_application=0, count_good_application=0, receiving_order=1):
        self.cursor.execute("""INSERT OR IGNORE INTO Users (User_Id, Username, access, User_type, Privileges_type, Count_orders,
         Count_good_orders, Count_application, Count_good_application, Receiving_order)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                            (user_id, username, access, user_type, privileges_type, count_orders, count_good_orders,
                             count_application, count_good_application, receiving_order))
        self.conn.commit()

    async def get_data(self, user_id):
        self.cursor.execute(f"SELECT * FROM Users WHERE user_id = ?", (user_id,))
        data = self.cursor.fetchall()
        # print(data)
        data_str = ', '.join(map(str, data[0]))
        data_list = data_str.split(",")
        return data_list

    async def get_user_for_mailing(self):
        self.cursor.execute(f"SELECT User_Id, Privileges_type FROM Users WHERE Receiving_order = 1 "
                            f"AND User_type = 'courier'"
                            f"ORDER BY Privileges_type DESC")
        rows = self.cursor.fetchall()
        return rows
    async def check_user(self,user_id):
        self.cursor.execute("SELECT COUNT(*) FROM Users WHERE User_Id = ?", (user_id, ))
        count = self.cursor.fetchall()[0]
        return count
    async def update_privileges_type(self, user_id):
        self.cursor.execute("UPDATE Users SET Privileges_type = Privileges_type + 1 WHERE User_Id = ? ", (user_id, ))
        self.conn.commit()

    async def delete_user(self, user_id):
        self.cursor.execute("DELETE FROM Users WHERE User_Id = ? AND EXISTS (SELECT 1 FROM Users WHERE User_Id = ?)", (user_id, user_id))
        self.conn.commit()

    async def get_user_id(self):
        self.cursor.execute("SELECT User_Id FROM Users")
        ids = self.cursor.fetchall()
        data_list = [item[0] for item in ids]
        # print(data_list)
        return data_list
    async def get_count_orders(self, user_id):
        self.cursor.execute("SELECT Count_orders FROM Users WHERE User_Id = ?", (user_id,))
        count = self.cursor.fetchall()
        return count

    async def update_count_orders(self, user_id):
        self.cursor.execute("UPDATE Users SET Count_orders = Count_orders + 1 WHERE User_Id = ?", (user_id,))
        self.conn.commit()

    async def update_good_count_orders(self, user_id):
        self.cursor.execute("UPDATE Users SET Count_good_orders = Count_good_orders + 1 WHERE User_Id = ?", (user_id,))
        self.conn.commit()

    async def get_receiving_order(self, user_id):
        self.cursor.execute(f"SELECT Receiving_order FROM Users WHERE User_Id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result

    async def update_receiving_order(self, user_id, receiving_order):
        self.cursor.execute("UPDATE Users SET Receiving_order = ? WHERE User_Id = ?", (receiving_order, user_id))
        self.conn.commit()

    async def get_count_user_type(self, user_type):
        self.cursor.execute(f"SELECT COUNT(*) FROM Users WHERE User_type = ?", (user_type,))
        count = self.cursor.fetchall()[0]
        # print(count)
        return count
    async def update_user_type(self, user_type, user_id):
        self.cursor.execute(f"UPDATE Users SET User_Type = ? WHERE User_Id = ?", (user_type, user_id))
        self.conn.commit()

    async def get_user_type(self, user_id):
        self.cursor.execute(f"SELECT User_Type FROM Users WHERE User_id = ?", (user_id,))
        type = self.cursor.fetchall()[0]
        return type

    async def update_access(self, access, username):
        self.cursor.execute("UPDATE Users SET access = ? WHERE Username = ?", (access, username))
        self.conn.commit()

    async def add_new_link(self, link,  link_type):
        self.cursor.execute("INSERT INTO Links (Link, Link_type) VALUES (?, ?)", (link, link_type))
        self.conn.commit()

    async def check_link(self, link, link_type):
        self.cursor.execute("SELECT COUNT(*) FROM Links WHERE Link = ? AND Link_type = ?", (link, link_type))
        count = self.cursor.fetchall()[0]
        # print(count)
        return count
    async def delete_link(self, link):
        self.cursor.execute("DELETE FROM Links WHERE LInk = ?", (link,))
        self.conn.commit()

    async def get_admin_id(self):
        self.cursor.execute("SELECT User_Id FROM Admins")
        ids = self.cursor.fetchall()
        data_list = [item[0] for item in ids]
        return data_list
    async def add_new_admin(self, admin_id, username):
        self.cursor.execute("INSERT INTO Admins (user_id, username)VALUES (? , ?)", (admin_id, username))
        self.conn.commit()
    async def delete_admin_db(self, admin_id):
        self.cursor.execute("DELETE FROM Admins WHERE user_id = ?", (admin_id,))
        self.conn.commit()

    async def get_all_admin(self):
        self.cursor.execute("SELECT * FROM Admins")
        ids = self.cursor.fetchall()
        return ids

    async def add_orders_db(self, order_id, customer_id, order_type, point_A, point_B, comment):
        self.cursor.execute("""INSERT INTO Orders (Order_id, Courier_Id, Customer_id, Order_type, Point_A, Point_B, Comment, Messages)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
                            (order_id, None, customer_id, order_type, point_A, point_B, comment, None))
        self.conn.commit()
    async def update_order(self, courier_id, order_id):
        self.cursor.execute("UPDATE Orders SET Courier_id = ? WHERE Order_Id = ?", (courier_id, order_id))
        self.conn.commit()

    async def update_messages(self, arr, order_id):
        arr_json = json.dumps(arr)
        self.cursor.execute("UPDATE Orders SET Messages = ? WHERE Order_Id = ?", (arr_json, order_id))
        self.conn.commit()

    async def get_messages_from_db(self, order_id):
        self.cursor.execute("SELECT Messages FROM Orders WHERE Order_Id=?", (order_id,))
        rows = self.cursor.fetchall()
        if rows:
            messages_list = []
            for row in rows:
                messages_data = row[0]
                messages = json.loads(messages_data)
                messages_list.append(messages)
            return messages_list
        else:
            return None

    async def get_courier_id_order(self, order_id):
        self.cursor.execute("SELECT Courier_id FROM Orders WHERE order_id = ?", (order_id,))
        customer_id = self.cursor.fetchall()
        return customer_id

    async def get_order_details_by_id(self, order_id):
        self.cursor.execute(
            "SELECT Courier_Id, Customer_id, Order_type, Point_A, Point_B, Comment FROM Orders WHERE Order_Id=?",
            (order_id,))
        row = self.cursor.fetchone()
        if row is not None:
            courier_id, customer_id, order_type, point_A, point_B, comment = row
            return [courier_id, customer_id, order_type, point_A, point_B, comment]
        else:
            return None

    async def get_customer_id_order(self, order_id):
        self.cursor.execute("SELECT Customer_id FROM Orders WHERE order_id = ?", (order_id,))
        customer_id = self.cursor.fetchall()
        return customer_id[0]