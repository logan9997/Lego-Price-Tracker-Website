from selenium import webdriver
from selenium.webdriver.common.by import By
from themes import THEMES

import json, time

class Scraper():

    def __init__(self) -> None:
        self.driver = webdriver.Chrome()
        self.url = "https://www.bricklink.com/catalogTree.asp?itemType=S"


    def setup(self) -> None:
        self.driver.get(self.url)
        #accept cookies 
        self.driver.find_element(By.XPATH, """//*[@id="js-btn-save"]/button[2]""").click()


    def parse_themes(self, num_spaces) -> None:
        #get all themes from table
        self.table = self.driver.find_element(By.XPATH, '//*[@id="id-main-legacy-table"]/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[2]')
        self.themes = [theme.split("(")[0] for theme in self.table.text.rsplit("\n") if theme != ''] 
        #set lists 
        self.paths = [] ; details = [] ; parents = []
        #loop through every theme / sub-theme in the table
        for index, theme in enumerate(self.themes):
            #find first char in theme name to split.
            for char in theme:
                if char != " ":
                    first_letter = char
                    break
            #split theme from its first char to get the level of indentation (lvl of sub theme)
            num_spaces = len(theme.split(first_letter)[0])
            #if a new parent theme, reset the list
            if num_spaces == 0:
                parents = []
           #store a list of dicts storing "theme" and "num_spaces" to compare current theme with previous theme(s)
            details.append({"theme":theme.strip("     ") + "//", "num_spaces":num_spaces})
            #if a new level of indentaion is reached add the current theme as a new sub-parent theme
            if details[index]["num_spaces"] > details[index-1]["num_spaces"]:
                parents.append(details[index-1]["theme"])
            #if the previous themes spaces is < than current themes spaces the remove last element from parents as it is not a parent to any sub themes
            elif details[index]["num_spaces"] < details[index-1]["num_spaces"] and len(parents) > 0:
                parents.pop(-1)
            #complete the path "parent//sub/sub-sub" and append to list
            path = "".join(parents) + theme.strip("     ")
            self.paths.append(path)

        #[print(p) for p in self.paths]


    def get_theme_ids(self) -> None:
        
        theme_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="catalogList.asp?catType=S&catString"]')
        print(len(theme_links))
        for t in theme_links:
            print("BEOFRE CLICK")
            t.click()

            
            num_items = int(self.driver.find_element(By.XPATH, '//*[@id="id-main-legacy-table"]/tbody/tr/td/table/tbody/tr[3]/td/div/div[2]/div[2]/b[1]').text)
            page_counter = 1
            row_counter = 2

            for index in range(num_items):
                #click next page if 50th item on page is parsed
                if row_counter % 50 == 0:
                    print("MOD")
                    page_counter += 1
                    row_counter = 2
                    
                    #set up url for next page, (selecting 'next page' with xpath not working)
                    next_page_url = self.driver.current_url.split("?")
                    next_page_url.insert(1, f"?pg={page_counter}&")
                    next_page_url = "".join(next_page_url)
                    print(next_page_url)
                    self.driver.get(next_page_url)

                #select the item id from current row
                try:
                    item_id = self.driver.find_element(By.XPATH, f'//*[@id="ItemEditForm"]/table[1]/tbody/tr/td/table/tbody/tr[{row_counter}]/td[2]/font/a[1]').text
                    print(item_id)
                except:
                    print("ID ERROR...")
                
                row_counter += 1
                
            print("BEFORE BACK")
            self.driver.get('https://www.bricklink.com/catalogTree.asp?itemType=S')
            time.sleep(5)

#https://www.bricklink.com/catalogList.asp?pg=1catType=S&catString=516 NO SETS
#https://www.bricklink.com/catalogList.asp?pg=1&catType=S&catString=516 SETS



    def store_as_json(self) -> None:
        theme_dicts = []
        with open("theme_details.json", "w") as file:
            for theme_path in self.paths:
                theme_dicts.append({
                    "path":theme_path,
                    "items":{
                        "minifigs":[],
                        "sets":[],
                    }
                })
            themes_json = json.dumps(theme_dicts, indent=4)
            file.write(themes_json)

           
#    themes = [theme for theme in THEMES.rsplit("\n") if theme != ''] 

def main():
    scraper = Scraper()
    scraper.setup()
    scraper.parse_themes(0)
    #scraper.store_as_json()
    scraper.get_theme_ids()


if __name__ == "__main__":
    main()

