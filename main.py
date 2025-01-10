import time
from datetime import datetime
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId  
import json

TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')


def get_driver():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome()
    return driver



# ProxyMesh credentials and URL
# proxy_url = "us.proxymesh.com:31280"  # Replace with your ProxyMesh proxy
# username = "your-username"  # Replace with your ProxyMesh username
# password = "your-password"  # Replace with your ProxyMesh password



def login_to_twitter(driver, username, password):
    try:
        driver.get("https://x.com/login")
        print("Navigated to login page.")

        wait = WebDriverWait(driver, 10)
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "text")))
        print("Username field found.")

        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)
        print("Username entered.")

        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        print("Password field found.")

        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        print("Password entered.")

        time.sleep(5)

        if "home" in driver.current_url:
            print("Login successful!")
            return True
        else:
            print("Login failed! Check credentials or 2FA.")
            return False

    except Exception as e:
        print("Error occurred during login:", e)
        return False


def click_explore_button(driver):
    try:
        print("Looking for Explore button...")
        explore_xpath = "/html/body/div[1]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[2]"
        explore_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, explore_xpath))
        )
        explore_button.click()
        print("Clicked Explore button!")

        time.sleep(5)
        return True

        
    except Exception as e:
        print(f"Failed to click Explore: {str(e)}")
        return False

def get_trending_topics(driver):
    try:
    
        trending_button = driver.find_element(By.CSS_SELECTOR, "a[href='/explore/tabs/keyword']")

       
        trending_button.click()
        print("Trending button clicked.")

        print("Trending content loaded.")


    except TimeoutException:
        print("Timeout: Trending button not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    print("Fetching trending topics...")
    time.sleep(10)  # Wait for trends to load
    
    trends = []
    xpaths = [
        '/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/section/div/div/div[3]/div/div/div/div/div[2]',
        '/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/section/div/div/div[4]/div/div/div/div/div[2]',
        '/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/section/div/div/div[5]/div/div/div/div/div[2]',
        '/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/section/div/div/div[6]/div/div/div/div/div[2]',
        '/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/section/div/div/div[7]/div/div/div/div/div[2]'   
    ]

    for xpath in xpaths:
        try:
            element = driver.find_element(By.XPATH, xpath)
            trends.append(element.text.strip())
            print(f"Found trend: {element.text.strip()}")
        except NoSuchElementException:
            trends.append("N/A")
            print(f"Could not find trend for xpath: {xpath}")

    return trends[:5]  # Ensure we only return 5 trends


def save_to_mongo(trends, ip):
    try:
        print("Saving to MongoDB...")
        
        # MongoDB connection with TLS 1.2 enforced
        client = MongoClient(
            "mongodb+srv://abhaydev2901:abhaydev2901@cluster0.zcaqe.mongodb.net/",
            tls=True, tlsAllowInvalidCertificates=False
        )
        db = client["trending_topics_db"]  # Database name
        collection = db["trends"]  # Collection name
        
        # Data to insert
        data = {
            "_id": f"{ip}_{datetime.now().timestamp()}",  # Custom _id field
            "datetime": datetime.now().isoformat(),
            "ip_address": ip,
            "trends": trends
        }
        
        # Insert into MongoDB
        collection.insert_one(data)
        
        print("Successfully saved to MongoDB!")
        return data
    except Exception as e:
        print(f"Failed to save to MongoDB: {str(e)}")
        raise




def main(username, password):
    driver = None
    try:
        print("Starting scraping process...")
        driver = get_driver()

        if not login_to_twitter(driver, username, password):
            raise Exception("Failed to login to Twitter")

        if not click_explore_button(driver):
            raise Exception("Failed to navigate to Explore page")

        trends = get_trending_topics(driver)
        if not trends:
            raise Exception("Failed to get trending topics")

        ip = requests.get('https://api.ipify.org').text
        result = save_to_mongo(trends, ip)
        return result

    except Exception as e:
        print(f"Error in main function: {str(e)}")
        raise
    finally:
        if driver:
            driver.quit()
            print("Browser closed.")

if __name__ == "__main__":
    main(TWITTER_USERNAME, TWITTER_PASSWORD)
