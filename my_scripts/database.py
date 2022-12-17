import sqlite3
import datetime


class DatabaseManagment():

    def __init__(self) -> None:
        self.con = sqlite3.connect(r"C:\Users\logan\OneDrive\Documents\Programming\Python\api's\BL_API\database.db", check_same_thread=False)
        self.cursor = self.con.cursor()


    def add_price_info(self, item) -> None:
        #add all prices for current day
        today = datetime.date.today().strftime('%Y-%m-%d')
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


    def check_if_price_recorded(self) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT item_id
            FROM price
            WHERE date = '{datetime.datetime.today().strftime('%Y-%m-%d')}'
        """)
        return result.fetchall()


    def group_by_items(self) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT item_id, type
            FROM item
            GROUP BY item_id
        """)
        return result.fetchall()


    def get_parent_themes(self) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT REPLACE(theme_path, '/', ''), thumbnail_url
            FROM item, theme
            WHERE theme_path NOT LIKE '%~%'
                AND type = 'S'
                AND item.item_id = theme.item_id
            GROUP BY theme_path
        """)
        return result.fetchall()


    def get_theme_items(self, theme_path) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT item.item_id, type
            FROM item, theme
            WHERE item.item_id = theme.item_id
                AND theme_path = '{theme_path}'
        """)
        return result.fetchall()      


    def get_item_ids(self) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT item.item_id, type
            FROM item, theme
            WHERE item.item_id = theme.item_id
                AND theme_path LIKE '%Star Wars%'
        """)
        return result.fetchall()


    def insert_thumbnail_url_name(self, details) -> None:
        self.cursor.execute(f"""
            UPDATE item
            SET thumbnail_url = '{details.get("thumbnail_url")}', name = '{details.get("name")}'
            WHERE item_id = '{details.get("item_id")}'
        """)
        self.con.commit()


    def insert_year_released(self, year_released, item_id) -> None:
        self.cursor.execute(f"""
            UPDATE item
            SET year_released = '{year_released}'
            WHERE item_id = '{item_id}'
        """)
        self.con.commit()


    def get_item_info(self, item_id) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT item_id, name, year_released, thumbnail_url
            FROM item
            WHERE item_id = '{item_id}'
            GROUP BY item_id
        """)
        return result.fetchall()

    def get_not_null_years(self) -> list[str]:
        result = self.cursor.execute(f"""
            SELECT item_id
            FROM item
            WHERE year_released is null
        """)
        return result.fetchall()


    def get_thumbnail_url(self, item_id) -> str:
        result = self.cursor.execute(f"""
            SELECT thumbnail_url
            FROM item
            WHERE item_id = '{item_id}'
            GROUP BY item_id
        """)
        return result.fetchall()     


    def transfer_to_theme(self) -> None:
        result = self.cursor.execute(f"""
            SELECT item.item_id, theme_path
            FROM item, theme
            WHERE item.item_id = theme.item_id
                AND item.type = 'S'

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
            SELECT REPLACE(theme_path, '{parent_theme}~', ''), thumbnail_url
            FROM theme, item
            WHERE theme.item_id = item.item_id
                AND theme_path LIKE '{parent_theme}_%'
            GROUP BY theme_path
        """)
        return result.fetchall()    

    #########################################TRANSER##########################
    def get_all(self,table):

        result = self.cursor.execute(f"""
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
            INSERT INTO App_{table} ('theme_path','item_id')
            VALUES {row}
        """)
        con.commit()


#update database without calling a view
def main():
    db = DatabaseManagment()

    tables = ['user']
    
    for table in tables:
        info = db.get_all(table)

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