import sqlite3
import datetime
import threading


class DatabaseManagment():

    def __init__(self) -> None:
        self.con = sqlite3.connect(r"C:\Users\logan\OneDrive\Documents\Programming\Python\apis\BL_API\website\db.sqlite3", check_same_thread=False)
        self.cursor = self.con.cursor()
        self.lock = threading.Lock()


    def add_price_info(self, item) -> None:
        today = datetime.date.today().strftime('%Y-%m-%d')
        try:
            self.cursor.execute(f"""
                INSERT INTO App_price (
                    'item_id','date','avg_price',
                    'min_price','max_price','total_quantity'
                )
                VALUES
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
        try:
            self.lock.acquire(True)
            result = self.cursor.execute(f"""
                SELECT App_item.item_id, item_type
                FROM App_item, App_theme
                WHERE App_item.item_id = App_theme.item_id
                    AND theme_path = '{theme_path}'
            """)
            return result.fetchall()      
        finally:
            self.lock.release()

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
        print(parent_theme)
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


    def get_user_items(self, user_id, view) -> list[str]:

        sql_select = "SELECT I.*,avg_price, min_price, max_price, total_quantity"
        if view == "portfolio":
            sql_select += ", condition, quantity"

        result = self.cursor.execute(f"""
            {sql_select}
            FROM App_{view} _view, App_item I, App_price P
            WHERE user_id = {user_id}
                AND (date, I.item_id) IN (SELECT MAX(date), item_id FROM App_price GROUP BY item_id)
                AND I.item_id = _view.item_id 
                AND I.item_id = P.item_id
            GROUP BY I.item_id
        """)
        return result.fetchall()


    def portfolio_total_item_price(self, user_id) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT ROUND(avg_price * PO.quantity, 2), I.item_id, condition
            FROM App_portfolio PO, App_price PR, App_item I
            WHERE PO.user_id = {user_id}
                AND PO.item_id = I.item_id
                AND I.item_id = PR.item_id
            GROUP BY I.item_id, condition
        """)
        return result.fetchall()


    def total_portfolio_items(self, user_id) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT SUM(quantity)
            FROM App_portfolio 
            WHERE user_id = {user_id}
        """)
        return result.fetchall()[0][0]

    def user_items_total_price(self, user_id, metric, view) -> list[str]:
        if view == "portfolio":
            select_string = f"SELECT ROUND(SUM({metric} * quantity), 2)"
        else:
            select_string = f"SELECT ROUND(SUM({metric}), 2)"

        result = self.cursor.execute(f"""
        {select_string}
        FROM App_{view} _view, App_item I, App_price P
        WHERE user_id = {user_id}
            AND (date, I.item_id) IN (SELECT MAX(date), item_id FROM App_price GROUP BY item_id)
            AND I.item_id = _view.item_id 
            AND I.item_id = P.item_id
        """)

        return result.fetchall()[0][0]


    def update_portfolio_item_quantity(self, user_id, item_id, condition, quantity) -> None:
        self.cursor.execute(f"""
            UPDATE App_portfolio
            SET quantity = quantity + {quantity}
            WHERE item_id = '{item_id}'
                AND user_id = {user_id}
                AND condition = '{condition}'
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


    def get_portfolio_price_trends(self, user_id) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT date, ROUND(SUM(avg_price * quantity) ,2)
            FROM App_portfolio PO, App_price PR, App_item I
            WHERE user_id = {user_id}
                AND PO.item_id = I.item_id
                AND PR.item_id = I.item_id
            GROUP BY date
        """)
        return result.fetchall()


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

    
    def if_username_or_email_already_exists(self, username, email) -> bool:
        result = self.cursor.execute(f"""
            SELECT username, email
            FROM App_user
            WHERE username = '{username}' 
                OR email = '{email}'
        """)
        if len(result.fetchall()) > 0:
            return True
        return False


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


    def get_portfolio_items_condition(self, user_id) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT item_id, condition
            FROM App_portfolio
            WHERE user_id = {user_id}
        """)
        return result.fetchall()


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


    def get_all_itemIDs(self) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT item_id
            FROM App_item
            WHERE item_id LIKE 'sw%' 
                AND item_type = 'M'
        """)
        return result.fetchall()

    def insert_item_info(self, item_info) -> None:
        type_convert = {"MINIFIG":"M", "SET":"S"}
        self.cursor.execute(f"""
            INSERT INTO App_item
            ('item_id', 'item_name', 'year_released', 'item_type')
            VALUES ('{item_info["no"]}', '{item_info["name"].replace("'", "")}', '{item_info["year_released"]}', '{type_convert[item_info["type"]]}')
        """)
        self.con.commit()


    def update_password(self, user_id, old_password, new_password) -> None:
        self.cursor.execute(f"""
            UPDATE App_user
            SET password = '{new_password}'
            WHERE password = '{old_password}'
                AND user_id = {user_id}
        """)
        self.con.commit()


    def check_password_id_match(self, user_id, old_password) -> bool:
        result = self.cursor.execute(f"""
            SELECT *
            FROM App_user
            WHERE user_id = {user_id}
                AND password = '{old_password}'
        """)
        if len(result.fetchall()) > 0:
            return True
        return False


    def change_username(self, user_id, username) -> None:
        self.cursor.execute(f"""
            UPDATE App_user
            SET username = '{username}'
            WHERE user_id = {user_id}
        """)

    def add_to_user_items(self, user_id, item_id, view, **kwargs) -> None:
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        
        sql_fields = "('user_id', 'item_id', 'date_added'"
        sql_values = f"VALUES ({user_id},'{item_id}','{date}'"

        print(kwargs)

        if view == "portfolio":
            condition = kwargs["condition"]
            quantity = kwargs["quantity"]

            sql_fields += ",'condition', 'quantity')"
            sql_values += f",'{condition}', {quantity})"
        else:
            sql_fields += ")"
            sql_values += ")"

        print(sql_fields, "\n", sql_values)

        self.cursor.execute(f"""
            INSERT INTO App_{view}
            {sql_fields}
            {sql_values}
        """)
        self.con.commit()


    def get_user_item_graph_info(self, user_id, item_id, metric, view) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT {metric}, date
            FROM App_price P, App_{view} View, App_item I
            WHERE user_id = {user_id}
                AND I.item_id = '{item_id}'
                AND P.item_id = I.item_id
                AND I.item_id = View.item_id
            GROUP BY I.item_id, P.date
        """)
        return result.fetchall()


    def parent_themes(self, user_id:int, view:str) -> list[str]:
        if view == "portfolio":
            select_string = "SELECT theme_path, COUNT(), ROUND(SUM(avg_price * quantity),2), P.item_id"
        else:
            select_string = "SELECT theme_path, COUNT(), ROUND(SUM(avg_price),2), P.item_id"
           

        result = self.cursor.execute(f"""
            {select_string}
            FROM App_price P, App_theme T, App_{view} _view, App_item I
            WHERE user_id = {user_id}
                AND theme_path NOT LIKE '%~%'
                AND (date, P.item_id) IN (SELECT MAX(date), item_id FROM App_price GROUP BY item_id)
                AND I.item_id = P.item_id
                AND I.item_id = _view.item_id
                AND I.item_id = T.item_id
            GROUP BY theme_path

        """)
        return result.fetchall()


    def sub_themes(self, user_id:int, theme_path:str, view:str) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT theme_path, COUNT(), ROUND(SUM(avg_price),2), P.item_id
            FROM App_price P, App_theme T, App_{view} _view, App_item I
            WHERE user_id = {user_id}
                AND theme_path LIKE '{theme_path}%'
                AND theme_path != '{theme_path}'
                AND (date, P.item_id) IN (SELECT MAX(date), item_id FROM App_price GROUP BY item_id)
                AND I.item_id = P.item_id
                AND I.item_id = _view.item_id
                AND I.item_id = T.item_id
            GROUP BY theme_path
        """)
        return result.fetchall()
