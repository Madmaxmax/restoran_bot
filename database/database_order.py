

async def get_courier_id_order(self, order_id):
    self.cursor.execute("SELECT Courier_id FROM Orders WHERE order_id = ?", (order_id,))
    customer_id = self.cursor.fetchall()
    return customer_id


async def get_order_details_by_id(self, order_id):
    self.cursor.execute(
        "SELECT Courier_name, Customer_name, Restaurant_name, Order_type, Price, Point_A, Point_B, Comment, Courier_Id, Customer_id "
        "FROM Orders WHERE Order_Id=?",
        (order_id,))
    row = self.cursor.fetchone()
    if row is not None:
        Courier_name, Customer_name, Restaurant_name, Order_type, Price, Point_A, Point_B, Comment, Courier_Id, Customer_id = row
        return [Courier_name, Customer_name, Restaurant_name, Order_type, Price, Point_A, Point_B, Comment, Courier_Id,
                Customer_id]
    else:
        return None


async def get_customer_id_order(self, order_id):
    self.cursor.execute("SELECT Customer_id FROM Orders WHERE order_id = ?", (order_id,))
    customer_id = self.cursor.fetchall()
    return customer_id[0]


# async def get_last_order(self, user_id):
#     self.cursor.execute(f"SELECT * FROM Orders ORDER BY {user_id} DESC LIMIT 1;")
#     last_row = self.cursor.fetchone()
#     return last_row

async def check_finish_order(self, order_id):
    self.cursor.execute(f"SELECT Courier_Id FROM Orders WHERE Order_Id = ?", (order_id,))
    courier_id = self.cursor.fetchall()
    if courier_id[0][0] == None:
        return True
    else:
        return False