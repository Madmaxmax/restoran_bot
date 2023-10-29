import json
import sqlite3


class Database:
    def __init__(self):
        self.database_path = f'database/database_storage/bot_info.db'
        self.conn = sqlite3.connect(self.database_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
                User_Id INTEGER PRIMARY KEY,
                Username TEXT,
                User_type TEXT,
                Phone_number TEXT,
                Privileges_type INT,
                Count_orders INT,
                Count_good_orders INT,
                Receiving_order INT,
                Restaurant_name TEXT,
                Address TEXT
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
                        Courier_name TEXT,
                        Customer_name TEXT,
                        Restaurant_name TEXT,
                        Point_A TEXT,
                        Point_B TEXT,
                        Deliver_start_time TEXT,
                        Deliver_end_time TEXT,
                        Phone TEXT,
                        Price INT,
                        Comment TEXT,
                        Start_time INT,
                        End_time INT,
                        Messages TEXT
                        );""")
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Purchase(
                        Purchase_Id INTEGER PRIMARY KEY,
                        Courier_Id TEXT,
                        Customer_id TEXT,
                        Courier_name TEXT,
                        Customer_name TEXT,
                        Restaurant_name TEXT,
                        Point_A TEXT,
                        Point_B TEXT,
                        Count TEXT,
                        Weight TEXT,
                        Purchase_end_time TEXT,
                        Price INT,
                        Comment TEXT,
                        Start_time INT,
                        End_time INT,
                        Messages TEXT
                        );""")
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS links(
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Link TEXT,
                        Link_type TEXT
                        );""")
        self.conn.commit()

    async def get_all_admin(self):
        self.cursor.execute("SELECT * FROM Admin_settings")
        rows = self.cursor.fetchall()
        return rows

    async def add_user_db(self, user_id, username, user_type=None, privileges_type=1, phone_number=None, count_orders=0,
                          count_good_orders=0, receiving_order=1, restaurant_name=None, Address=None):
        self.cursor.execute("""INSERT OR IGNORE INTO Users (User_Id, Username, User_type, Phone_number,
         Privileges_type,Count_orders, Count_good_orders, Receiving_order,Restaurant_name, Address)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                            (user_id, username, user_type, phone_number, privileges_type, count_orders,
                             count_good_orders, receiving_order, restaurant_name, Address))
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

    async def check_user(self, user_id):
        self.cursor.execute("SELECT COUNT(*) FROM Users WHERE User_Id = ?", (user_id,))
        count = self.cursor.fetchall()[0]
        return count

    async def update_privileges_type(self, user_id, number):
        self.cursor.execute(f"UPDATE Users SET Privileges_type = Privileges_type + {number} WHERE User_Id = ? ", (user_id,))
        self.conn.commit()

    def update_privilege(self, user_id, privilege_value):
        self.cursor.execute(f"UPDATE Users SET Privileges_type = '{privilege_value}' WHERE User_Id = '{user_id}'")
        self.conn.commit()
    async def update_restaurant_phone_phone_number(self, user_id, phone):
        self.cursor.execute("UPDATE Users SET Phone_number = ? WHERE User_Id = ? ", (phone, user_id))
        self.conn.commit()

    async def update_restaurant_phone_phone_address(self, user_id, address):
        self.cursor.execute("UPDATE Users SET Address = ? WHERE User_Id = ? ", (address, user_id))
        self.conn.commit()

    async def get_restaurant_address(self, user_id):
        self.cursor.execute("SELECT Address FROM Users WHERE user_id = ?", (user_id,))
        adress = self.cursor.fetchall()
        return adress[0][0]

    async def get_user_phone(self, user_id):
        self.cursor.execute("SELECT Phone_number FROM Users WHERE user_id = ?", (user_id,))
        phone = self.cursor.fetchone()
        return phone


    async def update_restaurant_name(self, user_id, restaurant_name):
        self.cursor.execute("UPDATE Users SET Restaurant_name =? WHERE User_Id = ? ", (restaurant_name, user_id))
        self.conn.commit()

    async def delete_user(self, user_id):
        self.cursor.execute("DELETE FROM Users WHERE User_Id = ? AND EXISTS (SELECT 1 FROM Users WHERE User_Id = ?)",
                            (user_id, user_id))
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

    async def get_restaurant_name(self, user_id):
        self.cursor.execute("SELECT Restaurant_name FROM Users WHERE User_Id = ?", (user_id,))
        count = self.cursor.fetchall()
        return count

    async def update_count_orders(self, user_id):
        self.cursor.execute("UPDATE Users SET Count_orders = Count_orders + 1 WHERE User_Id = ?", (user_id,))
        self.conn.commit()

    async def update_good_count_orders(self, user_id):
        print(user_id)
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
        user_type = self.cursor.fetchall()[0]
        return user_type

    async def add_new_link(self, link, link_type):
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

    async def get_all_admins(self):
        self.cursor.execute("SELECT * FROM Admins")
        ids = self.cursor.fetchall()
        return ids

    def get_all_orders_sort_data(self):
        self.cursor.execute("SELECT Order_id, Courier_name, Customer_name, Restaurant_name, Price, Point_A,"
                            " Point_B, Comment, Start_time, End_time, 'Заказ' as Type FROM Orders ORDER BY End_time DESC")
        rows_orders = self.cursor.fetchall()
        self.cursor.execute("SELECT Purchase_id, Courier_name, Customer_name, Restaurant_name, Price, Point_A,"
                            " Point_B, Comment, Start_time, End_time, 'Закупка' as Type FROM Purchase ORDER BY End_time DESC")

        rows_purchase = self.cursor.fetchall()
        return rows_orders + rows_purchase

    def get_all_courier(self):
        self.cursor.execute(f"SELECT User_id, Username, User_type, Privileges_type, Count_orders, Count_good_orders,"
                            " Receiving_order, Phone_number FROM Users WHERE User_type =  'courier'")
        rows = self.cursor.fetchall()
        return rows

    def get_all_customers(self):
        self.cursor.execute(
            "SELECT User_id, Username, User_type, Count_orders,"
            " Restaurant_name, Address FROM Users WHERE User_type = 'customer'")
        rows = self.cursor.fetchall()
        return rows

    def get_all_settings(self):
        self.cursor.execute("SELECT * FROM Admin_settings ")
        rows = self.cursor.fetchall()
        column_names = [description[0] for description in self.cursor.description]
        orders = [dict(zip(column_names, row)) for row in rows]
        return json.dumps(orders)

    async def add_orders_db(self, order_id, customer_id, customer_name, restaurant_name,
                            point_A, point_B, deliver_start_time, deliver_end_time, phone, price, comment):
        self.cursor.execute("""
            INSERT INTO Orders (
                Order_id, 
                Courier_Id, 
                Customer_id, 
                Courier_name, 
                Customer_name, 
                Restaurant_name, 
                Point_A, 
                Point_B, 
                Deliver_start_time, 
                Deliver_end_time, 
                Phone, 
                Price,
                Comment, 
                Start_time, 
                End_time, 
                Messages
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
                            (order_id, None, customer_id, None, customer_name, restaurant_name, point_A, point_B,
                             deliver_start_time,
                             deliver_end_time, phone, price, comment, None, None, None)
                            )
        self.conn.commit()

    async def update_order(self, parametr, order_id, table):
        self.cursor.execute(f"UPDATE Orders SET {table} = ? WHERE Order_Id = ?", (parametr, order_id))
        self.conn.commit()

    async def get_messages_from_db(self, order_id, table, parametr):
        self.cursor.execute(f"SELECT Messages FROM {table} WHERE {parametr}=?", (order_id,))
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

    # async def get_courier_id_application(self, application_id, table, parameter):
    #     self.cursor.execute(f"SELECT Courier_id FROM {table} WHERE {parameter} = ?", (application_id,))
    #     customer_id = self.cursor.fetchall()
    #     return customer_id

    async def get_point_B_application(self, application_id, table, parameter):
        self.cursor.execute(f"SELECT Point_B FROM {table} WHERE {parameter} = ?", (application_id,))
        customer_id = self.cursor.fetchall()
        return customer_id

    async def get_order_details_by_id(self, order_id):
        self.cursor.execute(
            """SELECT 
                Courier_Id, Customer_id, Courier_name, Customer_name, Restaurant_name, Point_A, Point_B,
                 Deliver_start_time, Deliver_end_time, Phone, Price, Comment, Start_time, End_time
            FROM Orders WHERE Order_Id=?""",
            (order_id,))
        row = self.cursor.fetchone()
        if row is not None:
            (Courier_Id, Customer_id, Courier_name, Customer_name, Restaurant_name, Point_A, Point_B,
             Deliver_start_time, Deliver_end_time, Phone, Price, Comment, Start_time, End_time) = row
            return [Courier_Id, Customer_id, Courier_name, Customer_name, Restaurant_name, Point_A, Point_B,
                    Deliver_start_time, Deliver_end_time, Phone, Price, Comment, Start_time, End_time]
        else:
            return None

    async def get_customer_id_application(self, application_id, table, parameter):
        self.cursor.execute(f"SELECT Customer_id FROM {table} WHERE {parameter} = ?", (application_id,))
        customer_id = self.cursor.fetchall()
        return customer_id[0]

    async def check_finish_application(self, application_id, table, parameter):
        self.cursor.execute(f"SELECT Courier_Id FROM {table} WHERE {parameter} = ?", (application_id,))
        courier_id = self.cursor.fetchall()
        if courier_id[0][0] is None:
            return True
        else:
            return False

    async def add_purchase_db(self, purchase_id, customer_id, customer_name, restaurant_name,
                              point_A, point_B, count, weight, purchase_end_time, price, comment):
        self.cursor.execute("""INSERT INTO Purchase (Purchase_Id, Courier_Id, Customer_id, Courier_name, Customer_name, 
                            Restaurant_name, Point_A, Point_B, Count, Weight, Purchase_end_time, Price,
                             Comment, Start_time, End_time, Messages)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                            (purchase_id, None, customer_id, None, customer_name, restaurant_name,
                             point_A, point_B, count, weight, purchase_end_time, price, comment, None,
                             None, None))
        self.conn.commit()

    async def update_purchase(self, parametr, purchase_id, table):
        self.cursor.execute(f"UPDATE Purchase SET {table} = ? WHERE Purchase_Id = ?", (parametr, purchase_id))
        self.conn.commit()

    async def get_purchase_details_by_id(self, purchase_Id):
        self.cursor.execute(
            """SELECT 
                Courier_Id, Customer_id, Courier_name, Customer_name, Restaurant_name, Point_A, Point_B, 
                Count, Weight, Purchase_end_time, Price, Comment, Start_time, End_time
            FROM Purchase WHERE Purchase_Id=?""",
            (purchase_Id,)
        )
        row = self.cursor.fetchone()
        if row is not None:
            (Courier_Id, Customer_id, Courier_name, Customer_name, Restaurant_name, Point_A, Point_B, Count, Weight,
             Purchase_end_time, Price, Comment, Start_time, End_time) = row
            return [Courier_Id, Customer_id, Courier_name, Customer_name, Restaurant_name, Point_A, Point_B, Count,
                    Weight, Purchase_end_time, Price, Comment, Start_time, End_time]
        else:
            return None

    async def get_data_and_column_names(self, table, start, finish):
        self.cursor.execute(f"PRAGMA table_info({table})")
        table_info = self.cursor.fetchall()
        column_names = tuple(info[1] for info in table_info)

        self.cursor.execute(f"SELECT * FROM {table} WHERE Start_time >= ? AND End_time <= ?", (finish, start))
        data = self.cursor.fetchall()

        data_with_column_names = [column_names] + data
        return data_with_column_names


