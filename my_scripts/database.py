import sqlite3
import datetime

class DatabaseManagment():

    def __init__(self) -> None:
        self.con = sqlite3.connect(r"C:\Users\logan\OneDrive\Documents\Programming\Python\api's\BL_API\database.db")
        self.cursor = self.con.cursor()


    def add_category_info(self, categories) -> None:
        for category in categories:
            self.cursor.execute(f'''
                INSERT INTO Category VALUES
                ("{category["category_id"]}", "{category["category_name"]}")
            ''')
        self.con.commit()


    def add_price_info(self, items) -> None:
        #add all prices for current day
        today = datetime.date.today()
        for item in items:
            print(item["item"]["no"])
            try:
                self.cursor.execute(f"""
                    INSERT INTO Price VALUES
                    (
                        '{item["item"]["no"]}', '{today}', '{round(float(item["avg_price"]), 2)}',
                        '{round(float(item["min_price"]),2)}', '{round(float(item["max_price"]),2)}',
                        '{item["total_quantity"]}'
                    )
                """)
            except sqlite3.IntegrityError:
                print("sqlite3.IntegrityError")
                pass
        self.con.commit()


    def get_all_items(self) -> list[str]:
        #return a list of all items inside 'Price' table
        result = self.cursor.execute(f"""
            SELECT item_id
            FROM Price
            GROUP BY item_id
        """)
        return [str(fig_id).split("'")[1] for fig_id in result.fetchall()]


    def check_for_todays_date(self) -> int:
        today = datetime.date.today()
        result = self.cursor.execute(f"""
            SELECT COUNT()
            FROM Price
            WHERE date = '{today}'
        """)
        return result.fetchall()


    def get_minifig_prices(self, minifig_id) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT date, avg_price, min_price, max_price, total_qty
            FROM Price
            WHERE item_id = '{minifig_id}'
        """)
        return result.fetchall()

    def get_dates(self, minifig_id) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT date
            FROM Price
            WHERE item_id = '{minifig_id}'
        """)
        return result.fetchall()     

    def save_item_names(self, item_names):
        for item in item_names:
            item_id = item.get('no') ; item_name = item.get('name')
            thumbnail_url = item.get('thumbnail_url')
            if "'" in item_name:
                item_name = item_name.replace("'", '')

            if "'" in thumbnail_url:
                thumbnail_url = thumbnail_url.replace("'", '"')
                
            print(item_name)
            try:
                self.cursor.execute(f'''
                    INSERT INTO item VALUES
                    ('{item_id}','{item_name}','{thumbnail_url}') 
                ''')
                self.con.commit()
            except sqlite3.IntegrityError:
                pass  
        

    def get_item_names(self) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT *
            FROM item
        """)
        return result.fetchall()

    
    def get_biggest_trends(self) -> list[str]:
        result = self.cursor.execute('''
            SELECT name, P1.item_id, round(avg_price - (
                SELECT avg_price
                FROM price P2
                WHERE P2.item_id = P1.item_id
                    AND date = (
                        SELECT max(date)
                        FROM price
                    ) 
            ),2) as [£ change]

            FROM price P1, item I
            WHERE I.item_id = P1.item_id 
                AND date = (
                    SELECT min(date)
                    FROM price
                ) 
            ORDER BY [£ change] desc
        ''')

        result = result.fetchall()
        losers = result[len(result)-10:][::-1]
        winners = result[:10]
        return losers, winners