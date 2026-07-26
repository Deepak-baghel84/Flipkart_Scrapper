import csv
import time
import re
import os
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
from selenium import webdriver

driver = webdriver.Chrome()

class web_scrapper():
    def __init__(self,output_dir:str='data'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def get_top_reviews(self,product_link,review_count:int=3):
        print("browser setup initiated for geting top reviews")
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")   # cracking chrome or website security through arguments
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = uc.Chrome(version_main=150,options=options, use_subprocess=True)
        print("browser opened and verifying product link")
        if not product_link.startswith('http'):
            driver.quit()
            return "not a valid url"
        try:
            print("opening product link")
            driver.get(product_link)
            time.sleep(3)

            # print("closing pop up if exist else continue")
            # try:
            #     close_btn = WebDriverWait(driver, 5).until(
            #         EC.element_to_be_clickable((By.CSS_SELECTOR, "button._2KpZ6l._2doB4z"))
            #     )
            #     close_btn.click()
            #     # driver.find_element(By.XPATH,"//button[contains(text(), '✕')]").click()
            # except Exception:
            #     traceback.print_exc()
            print('pop up closed, page scrolling starts')
            for _ in range(4):            # scrolls to the bottom of the page four times in a row
                ActionChains(driver).send_keys(Keys.END).perform()
                time.sleep(1.5)
            print("now beautiful soup working starts")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            print("setup complete")
            review_blocks = soup.select("div._27M-vq, div.col.EPCmJX, div._6K-7Co")  #Flipkart changes these class names frequently.
            print("getting block of reviews")
            seen = set()
            reviews = []
            print("taking top reviews one by one")
            for block in review_blocks:
                text = block.get_text(separator=" ", strip=True)
                if text and text not in seen:
                    reviews.append(text)
                    seen.add(text)
                if len(reviews) >= review_count:
                    break

        except Exception:
            traceback.print_exc()
            reviews = []
        finally:
            driver.quit()
        print("returning top reviews")
        return " || ".join(reviews) if reviews else "No reviews found"


    def scrape_flipkart(self,product_info:str,top_review:int=1,max_products:int=2):
        print("browser setup initiated")
        options = uc.ChromeOptions()
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-blink-features=AutomationControlled")
        driver = uc.Chrome(version_main=150,options=options, use_subprocess=True)
        print("browser opened")
        search_url = f"https://www.flipkart.com/search?q={product_info.replace(' ', '+')}"
        #search_url = f"https://www.1mg.com/?wpsrc=Bing+Organic+Search={product_info.replace(' ', '+')}"

        driver.get(search_url)
        time.sleep(4)
        print("searching flipkart.com done")

        try:
            close_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '✕')]"))
            )
            close_btn.click()
            #driver.find_element(By.XPATH,"//button[contains(text(), '✕')]").click()
        except Exception:
            traceback.print_exc()



        time.sleep(3)
        products=[]

        print("starting extracting items")
        items=driver.find_elements(By.CSS_SELECTOR, "div[data-id]")[:max_products]
       # print(driver.current_url)
        #print(driver.title)
        for item in items:
            print("extracted item",item)
            #print(item.get_attribute("outerHTML")[:1000])
            #print(item.get_attribute("outerHTML"))  # for getting entire html page(entire classes)
            #print(item.find_elements(By.CSS_SELECTOR, "div.RG5Slk")) #to verify the class
            # for div in item.find_elements(By.TAG_NAME, "div"):
            #     cls = div.get_attribute("class")
            #     txt = div.text[:40]
            #     print(cls, "->", txt)
            try:
                title = item.find_element(By.CLASS_NAME, "RG5Slk").text.strip()
                print("extracted title",title)
                price = item.find_element(By.CSS_SELECTOR, "div.hZ3P6w").text.strip()
                print("extracted price",price)
                rating = item.find_element(By.CSS_SELECTOR, ".MKiFS6").text.strip()
                print("extracted rating",rating)
                reviews_text = item.find_element(By.CLASS_NAME, "PvbNMB").text
                print(reviews_text)

                match = re.search(r"\d+(,\d+)?(?=\s+Reviews)", reviews_text)
                total_reviews = match.group(0) if match else "N/A"
                print("total reviews",total_reviews)
                #link_el = item.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
                #href = link_el.get_attribute("href")
                href = item.find_element(By.CSS_SELECTOR, "a.k7wcnx").get_attribute("href")
                product_link = href if href.startswith("http") else "https://www.flipkart.com" + href
                print("extracted product_link",product_link)
                match = re.findall(r"/p/(itm[0-9A-Za-z]+)", href)
                product_id = match[0] if match else "N/A"

            except Exception:
                traceback.print_exc()
                continue
            print("item extracted with product id",product_id)
            top_reviews = self.get_top_reviews(product_link,
                                           review_count=4) if "flipkart.com" in product_link else "Invalid product URL"
            print("reviews added to the final data")
            products.append([product_id, title, rating, total_reviews, price, top_reviews])

        driver.quit()
        return products





    def save_csv(self,data,file_name:str='product_reviews.csv'):
        if os.path.isabs(file_name):
            path=file_name
        elif os.path.dirname(file_name):
            path=file_name
            os.makedirs(os.path.dirname(file_name),exist_ok=True)
        else:
            path=os.path.join(self.output_dir,file_name)

        with open(path, "w", newline="", encoding="utf-8-sig") as f:  # encoding for symbols $
            writer = csv.writer(f)
            writer.writerow([
                "product_id",
                "product_title",
                "rating",
                "total_reviews",
                "price",
                "top_reviews"
            ])
            writer.writerows(data)
            print("data is saved as csv file")

def run_etl():

    product_info = "Apple Phone"

    obj = web_scrapper(output_dir="output")

    data = obj.scrape_flipkart(
        product_info=product_info,
        max_products=3
    )

    obj.save_csv(data)

    print("ETL completed successfully.")

if __name__=="__main__":
    print("starting")
    run_etl()

