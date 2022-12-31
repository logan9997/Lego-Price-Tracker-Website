import sqlite3
import datetime


class DatabaseManagment():

    def __init__(self) -> None:
        self.con = sqlite3.connect(r"C:\Users\logan\OneDrive\Documents\Programming\Python\api's\BL_API\website\db.sqlite3", check_same_thread=False)
        self.cursor = self.con.cursor()


    def add_price_info(self, item) -> None:
        #add all prices for current day
        today = datetime.date.today().strftime('%Y-%m-%d')
        print(item["item"]["no"])
        try:
            self.cursor.execute(f"""
                INSERT INTO App_price VALUES
                (
                    '{item["item"]["no"]}', '{today}', '{round(float(item["avg_price"]), 2)}',
                    '{round(float(item["min_price"]),2)}', '{round(float(item["max_price"]),2)}',
                    '{item["total_quantity"]}'
                )
            """)
        except sqlite3.IntegrityError:
            pass
        self.con.commit()


    def get_all_items(self) -> list[str]:
        #return a list of all items inside 'Price' table
        result = self.cursor.execute(f"""
            SELECT item_id
            FROM App_price
            GROUP BY item_id
        """)
        return [str(fig_id).split("'")[1] for fig_id in result.fetchall()]


    def check_for_todays_date(self) -> int:
        today = datetime.date.today()
        result = self.cursor.execute(f"""
            SELECT COUNT()
            FROM App_price
            WHERE date = '{today}'
        """)
        return result.fetchall()


    def get_minifig_prices(self, minifig_id) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT date, avg_price, min_price, max_price, total_quantity
            FROM App_price
            WHERE item_id = '{minifig_id}'
        """)
        
        return result.fetchall()

    def get_dates(self, minifig_id) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT date
            FROM App_price
            WHERE item_id = '{minifig_id}'
        """)
        return result.fetchall()     

    
    def get_biggest_trends(self) -> list[str]:
        result = self.cursor.execute('''
            SELECT item_name, P1.item_id, round(avg_price - (
                SELECT avg_price
                FROM App_price P2
                WHERE P2.item_id = P1.item_id
                    AND date = (
                        SELECT max(date)
                        FROM App_price
                    ) 
            ),2) as [£ change]

            FROM App_price P1, App_item I
            WHERE I.item_id = P1.item_id 
                AND date = (
                    SELECT min(date)
                    FROM App_price
                ) 
            ORDER BY [£ change] DESC
        ''')

        result = result.fetchall()
        losers = result[len(result)-10:][::-1]
        winners = result[:10]
        return losers, winners


    def check_if_price_recorded(self) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT item_id
            FROM App_price
            WHERE date = '{datetime.datetime.today().strftime('%Y-%m-%d')}'
        """)
        return result.fetchall()


    def group_by_items(self) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT item_id, item_type
            FROM App_item
            GROUP BY item_id
        """)
        return result.fetchall()


    def get_parent_themes(self) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT REPLACE(REPLACE(theme_path, '/', ''), ' ', '-')
            FROM App_item, App_theme
            WHERE theme_path NOT LIKE '%~%'
                AND item_type = 'M'
                AND App_item.item_id = App_theme.item_id
            GROUP BY theme_path
        """)
        return result.fetchall()


    def get_theme_items(self, theme_path) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT App_item.item_id, item_type
            FROM App_item, App_theme
            WHERE App_item.item_id = App_theme.item_id
                AND theme_path = '{theme_path}'
        """)
        return result.fetchall()      


    def get_item_ids(self) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT App_item.item_id
            FROM App_item
        """)
        return result.fetchall()


    def insert_year_released(self, year_released, item_id) -> None:
        self.cursor.execute(f"""
            UPDATE App_item
            SET year_released = '{year_released}'
            WHERE item_id = '{item_id}'
        """)
        self.con.commit()


    def get_item_info(self, item_id) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT item_id, item_name, year_released 
            FROM App_item
            WHERE item_id = '{item_id}'
            GROUP BY item_id
        """)
        return result.fetchall()

    def get_not_null_years(self) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT item_id
            FROM App_item
            WHERE year_released is null
        """)
        return result.fetchall()


    def transfer_to_theme(self) -> None:
        result = self.cursor.execute(f"""
            SELECT App_item.item_id, theme_path
            FROM App_item, App_theme
            WHERE App_item.item_id = App_theme.item_id
                AND item.item_type = 'S'

        """)   
        results = result.fetchall()

        for result in results:
            self.cursor.execute(f"""
                INSERT INTO theme VALUES
                    ('{result[0]}', '{result[1]}')
            """)
            self.con.commit()


    def get_sub_themes(self, parent_theme) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT REPLACE(theme_path, '{parent_theme}~', '')
            FROM App_theme, App_item
            WHERE App_theme.item_id = App_item.item_id
                AND theme_path LIKE '{parent_theme}_%'
            GROUP BY theme_path
        """)
        return result.fetchall()  


    def get_starwars_ids(self) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT item_id
            FROM App_item
        """)
        return result.fetchall()


    def fetch_theme_details(self) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT item_type, theme_path
            FROM App_item I, App_theme T
            WHERE I.item_id = T.item_id
        """)
        return result.fetchall()


    def add_theme_details(self, theme_details, item_type) -> None:
        for item in theme_details[item_type]:
            self.cursor.execute(f"""
                INSERT INTO App_theme ('theme_path', 'item_id') VALUES ('{theme_details["path"]}', '{item}')
            """)
            self.con.commit()


    def get_portfolio_items(self, user_id) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT PO.item_id, condition, quantity, item_name, item_type, year_released
            FROM App_portfolio PO, App_user U, App_item I
            WHERE U.user_id = {user_id}
                AND I.item_id = PO.item_id 
                AND PO.user_id = U.user_id 
        """)
        return result.fetchall()


    def add_to_portfolio(self, item_id, condition, quantity, user_id) -> None:
        self.cursor.execute(f"""
            INSERT INTO App_portfolio ('item_id', 'condition', 'quantity', 'user_id')
            VALUES ('{item_id}','{condition}','{quantity}','{user_id}')
        """)
        self.con.commit()


    def update_portfolio_item_quantity(self, item_id, condition, quantity, user_id) -> None:
        self.cursor.execute(f"""
            UPDATE App_portfolio
            SET quantity = quantity + {quantity}
            WHERE item_id = '{item_id}'
                AND user_id = {user_id}
                AND condition = '{condition}'
        """)


    def decrement_portfolio_item_quantity(self, item_id, user_id, condition, delete_quantity) -> None:
        self.cursor.execute(f"""
            UPDATE App_portfolio
            SET quantity = quantity - {delete_quantity}
            WHERE item_id = '{item_id}'
                AND user_id = '{user_id}'
                AND condition = '{condition}';
        """)
        self.con.commit()

        self.cursor.execute("""
            DELETE FROM App_portfolio
            WHERE quantity < 1;
        """)
        self.con.commit()


    def get_portfolio_item_quantity(self, item_id, condition, user_id) -> int:
        result = self.cursor.execute(f"""
            SELECT quantity
            FROM App_portfolio
            WHERE item_id = '{item_id}'
                AND condition = '{condition}'
                AND user_id = '{user_id}'
        """)
        return int(result.fetchall()[0][0])


    def biggest_portfolio_changes(self, user_id) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT item_name, I.item_id, portfolio.condition, quantity, round(avg_price - (
                SELECT avg_price
                FROM App_price P2
                WHERE P2.item_id = P1.item_id
                    AND date = (
                        SELECT max(date)
                        FROM App_price
                    ) 
            ),2) as [£ change]

            FROM App_price P1, App_item I, App_portfolio portfolio, App_user user
            WHERE I.item_id = P1.item_id 
                AND I.item_id = portfolio.item_id
                AND portfolio.user_id = user.user_id
                AND user.user_id = {user_id}
                AND date = (
                    SELECT min(date)
                    FROM App_price
                ) 
            GROUP BY portfolio.item_id, condition
            ORDER BY [£ change] DESC
        """)
        return result.fetchall()


    def check_login(self, username, password) -> bool:
        result = self.cursor.execute(f"""
            SELECT *
            FROM App_user
            WHERE username = '{username}'
                AND password = '{password}'
        """)
        if len(result.fetchall()) == 1:
            return True
        return False

    
    def check_if_username_or_email_exists(self, username, email) -> bool:
        result = self.cursor.execute(f"""
            SELECT username, email
            FROM App_user
            WHERE username = '{username}' 
                OR email = '{email}'
        """)
        if len(result.fetchall()) > 0:
            return False
        return True


    def add_user(self, username, email, password) -> None:
        self.cursor.execute(f"""
            INSERT INTO App_user ('username','email','password')
            VALUES ('{username}', '{email}', '{password}')
        """)
        self.con.commit()


    def sample_prices(self, portfolio_items) -> None:
        from random import randint
        for p in portfolio_items:
            self.cursor.execute(f"""
                INSERT INTO App_price ('date','avg_price','min_price','max_price','total_quantity','item_id')
                VALUES ('2022-12-26',{randint(1,55)},'{randint(1,55)}','{randint(1,55)}','{randint(1,55)}','{p[0]}')
            """)
            self.con.commit()


    def total_portfolio_price_trend(self, user_id) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT SUM(max_price), date
            FROM App_price price, App_portfolio portfolio, App_item item, App_user user
            WHERE user.user_id = {user_id}
                AND price.item_id = item.item_id
                AND item.item_id = portfolio.item_id
                AND portfolio.user_id = user.user_id
            GROUP BY date
        """)
        return result.fetchall()

    #########################################TRANSER##########################
def get_all(table):
    con = sqlite3.connect(r"C:\Users\logan\OneDrive\Documents\Programming\Python\api's\BL_API\database.db")
    cursor = con.cursor()        
    result = cursor.execute(f"""
        SELECT *
        FROM {table}
    """)
    return result.fetchall()


def insert(table, info):
    con = sqlite3.connect(r"C:\Users\logan\OneDrive\Documents\Programming\Python\api's\BL_API\website\db.sqlite3")
    cursor = con.cursor()
    for row in info:
        
        print(f"""INSERT INTO App_{table} VALUES {row}""")
        cursor.execute(f"""
            INSERT INTO App_{table} ('item_id','item_name')
            VALUES ('{row[0]}', '{row[1]}')
        """)
        con.commit()


#update database without calling a view
def main():
    db = DatabaseManagment()

    tables = ['item']
    
    for table in tables:
        info = get_all(table)
        print(info)
        insert(table, info)

    
if __name__ == "__main__":
    main()



    # from responses import Response
    # db = DatabaseManagment()
    # resp = Response()
    # #insert prices for today

    # items = db.get_item_ids()
    # items_recorded = [item[0] for item in db.check_if_price_recorded()]

    # type_convert = {"M":"MINIFIG", "S":"SET"}

    # print(items_recorded)

    # for item in items:
    #     if item[0] in items_recorded:
    #         continue
    #     item = resp.get_response_data(f'items/{type_convert[item[1]]}/{item[0]}/price')
    #     db.add_price_info(item)