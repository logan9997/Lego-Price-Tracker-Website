from selenium import webdriver
from selenium.webdriver.common.by import By
from themes import THEMES

import json, time

class Scraper():

    def __init__(self) -> None:
        self.driver = webdriver.Chrome()
        self.url = "https://www.bricklink.com/catalogTree.asp?itemType=S"
        self.item_ids = [] #need seperate for minifig and sets


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
        with open("theme_details.json", "r") as file:
            file_content = file.read()
        #return all a tags with href including corisponding link text
        theme_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="catalogList.asp?catType=S&catString"]')
        for theme_path_index, theme in enumerate([theme.get_attribute("href") for theme in theme_links]):
            if self.paths[theme_path_index] in file_content:
                print("CONTINUE", self.paths[theme_path_index])
                continue
            self.driver.get(theme)
            time.sleep(1)

            #if there is only one set in a theme, bricklink redirects to catalog item page
            if "catalogitem.page" in self.driver.current_url:
                item_id = self.driver.current_url.strip("https://www.bricklink.com/v2/catalog/catalogitem.page?S=")
                item_id = item_id.split("#")[0]
                print(item_id)
                self.item_ids.append(item_id)
                continue

            #set defualt values for each new theme
            num_items = int(self.driver.find_element(By.XPATH, '//*[@id="id-main-legacy-table"]/tbody/tr/td/table/tbody/tr[3]/td/div/div[2]/div[2]/b[1]').text)
            page_counter = 1
            row_counter = 2

            for index in range(num_items):
                #click next page if 50th item on page is parsed
                if row_counter % 50 == 0:
                    page_counter += 1
                    print("NEXT PAGE")
                    #reset the row counter
                    row_counter = 2
                    #set url for the next page
                    current_url = self.driver.current_url
                    if "pg=" not in current_url: #page num = 1
                        current_url = current_url.split("?")
                        current_url.insert(1, f"?pg={page_counter}&")
                        new_url = "".join(current_url)
                    else:
                        old_page_num = current_url[current_url.index("=")+1:current_url.index("&")]
                        print("old_page_num", old_page_num)
                        new_url = current_url.replace(str(old_page_num), str(int(old_page_num)+1))

                    self.driver.get(new_url)
                          
                #select the item id from current row
                try: 
                    item_id = self.driver.find_element(By.XPATH, f'//*[@id="ItemEditForm"]/table[1]/tbody/tr/td/table/tbody/tr[{row_counter}]/td[2]/font/a[1]').text
                    print(item_id)
                    self.item_ids.append(item_id)
                except:pass

                row_counter += 1
            
            self.store_as_json(self.paths[theme_path_index])
            self.item_ids = []
                

    def store_as_json(self, theme_path) -> None:
        
        theme_dicts = []
        with open("theme_details.json", "a+") as file:
            theme_dicts.append({
                "path":theme_path,
                "items":{
                    "minifigs":[],
                    "sets":self.item_ids,
                }
            })
            themes_json = json.dumps(theme_dicts, indent=4)
            file.write(themes_json)

           
#    themes = [theme for theme in THEMES.rsplit("\n") if theme != ''] 

def main():
    '''
    cd OneDrive/Documents/programming/python/api's/bl_api/my_scripts
    '''
    scraper = Scraper()
    scraper.setup()
    scraper.parse_themes(0)
    #scraper.store_as_json()
    scraper.get_theme_ids()


if __name__ == "__main__":
    main()

