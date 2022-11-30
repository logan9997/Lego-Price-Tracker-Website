import sqlite3
import datetime

class DatabaseManagment():

    def __init__(self) -> None:
        self.con = sqlite3.connect(r"C:\Users\logan\OneDrive\Documents\Programming\Python\api's\BL_API\Website\db.sqlite3")
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
            print("££££",item)
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
                pass
        self.con.commit()


    def get_all_items(self) -> list[str]:
        #return a list of all items inside 'Price' table
        result = self.cursor.execute(f"""
            SELECT itemID
            FROM Price
            GROUP BY itemID
        """)
        return [str(fig_id).split("'")[1] for fig_id in result.fetchall()]