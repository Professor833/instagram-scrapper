import json

import pandas
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd

# user_n = input("TYPE THE USER NAME OF THE ACCOUNT (it should be accurate)--> ")
user_n = 'jennifergoenka'
# passwd = input("TYPE PASSWORD OF THE ACCOUNT --> ")
passwd = '111213'
# acc_to_scrape = input("TYPE THE ACCOUNT TO SCRAPE --> ")
acc_to_scrape = 'lv_1601'
# ask_file = input("DO YOU WANT TO STORE DATA IN CSV FILE? [y/n] -->")
ask_file = 'y'

file_n = 'lv_fol'

# if ask_file.lower() == 'y':
#     file_n = input('ENTER THE FILE NAME (ex: My File)---> ')
CHROME_DRIVER_PATH = r"E:\Lalit's Projects\BROWSER_DRIVERS\chromedriver_win32\chromedriver.exe"


def instagram_tags_scraper(username, password, file, file_name, tag, next_page):
    driver = webdriver.Chrome(CHROME_DRIVER_PATH)
    a, b = True, True

    print(f'-----STARTED FETCHING DATA FOR #{tag}------')

    driver.get("https://www.instagram.com/")

    u_id = WebDriverWait(driver, 10).until(
        # EC.presence_of_element_located((By.CSS_SELECTOR, ".FBi-h+ .-MzZI .zyHYP"))
        EC.presence_of_element_located((By.CSS_SELECTOR, "#loginForm > div > div:nth-child(1) > div > label > input"))
    )

    u_id.clear()
    u_id.send_keys(username)  # username

    pwd = WebDriverWait(driver, 10).until(
        # EC.presence_of_element_located((By.CSS_SELECTOR, ".-MzZI+ .-MzZI .zyHYP"))
        EC.presence_of_element_located((By.CSS_SELECTOR, "#loginForm > div > div:nth-child(2) > div > label > input"))
    )
    pwd.clear()
    pwd.send_keys(password)  # password

    login_button = WebDriverWait(driver, 10).until(
        # EC.presence_of_element_located((By.CSS_SELECTOR, ".-MzZI+ .DhRcB"))
        EC.presence_of_element_located((By.CSS_SELECTOR, "#loginForm > div > div:nth-child(3) > button"))
    )
    login_button.click()
    try:
        not_now = WebDriverWait(driver, 10).until(
            # EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div/div/div[3]/button[2]"))
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "body > div.RnEpo.Yx5HN > div > div > div > div.mt3GC > button.aOOlW.HoLwm"))
        )
        not_now.click()

        url_with_tag = f'https://www.instagram.com/explore/tags/{tag}/?__a=1'

        driver.get(url_with_tag)
        # body > pre
        res_data = WebDriverWait(driver, 10).until(
            # EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div/div/div[3]/button[2]"))
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "body"))
        )

        # print("json response >> ", type(res_data.text), res_data.text)
        json_response = json.loads(res_data.text)
        # print("json response >> ", type(json_response))
        # print("json response >> ", json.dumps(json_response, indent=3))

        # IG provides two types of posts:
        # 1. top
        # 2. recent
        # We need to fetch all the users for both kind of posts and save it to DF

        # FOR NEXT PAGE:
        # Check "more_available" variable in JSON & if true find "next_max_id" in json to go to next page
        # so the next page URL would look like : https://www.instagram.com/explore/tags/{tag}/?__a=1/max_id={next_max_id}
        # Example "max_id" : QVFDTXBXb3B4NUlMLXNvM3dVN2lkSzg3Zk00dHB1ZU5ZbUhMTnp0bTVHN20zTHFzUm52TUM1MnNWcC10SnI0ek1Ib3FUMjIyRkpYWnV3TWZ0MkUyM21YTA==
        # Example Nxt page Link: https://www.instagram.com/explore/tags/cat/?__a=1&max_id=QVFDTXBXb3B4NUlMLXNvM3dVN2lkSzg3Zk00dHB1ZU5ZbUhMTnp0bTVHN20zTHFzUm52TUM1MnNWcC10SnI0ek1Ib3FUMjIyRkpYWnV3TWZ0MkUyM21YTA==
        # Sometimes we won't get a response object back even on passing valid "max_id" so we need to handle that error too
        # Max id located at 2 places in response:
        # 1. data["top"]["next_max_id"]
        # 2. data["recent"]["next_max_id"]

        # for fetching top posts:
        top_posts_sections_arr = json_response["data"]["top"]["sections"]
        tag_followers = []
        for item in top_posts_sections_arr:
            medias = item["layout_content"]["medias"]
            for media_item in medias:
                user = media_item["media"]["user"]
                user["instagram url"] = f'https://www.instagram.com/{user["username"]}/'
                tag_followers.append(user)
                print("user >> ", user)

        # for fetching recent posts:
        print(f"{'*' * 10} fetching recent posts {'*' * 10}")
        recent_posts_sections_arr = json_response["data"]["recent"]["sections"]
        for item in recent_posts_sections_arr:
            medias = item["layout_content"]["medias"]
            for media_item in medias:
                user = media_item["media"]["user"]
                user["instagram url"] = f'https://www.instagram.com/{user["username"]}/'

                tag_followers.append(user)
                # TODO: check if the user is already added as we can have dulpicate users too
                # TODO: instead of printing append to a list.
                print("user >> ", user)

        tag_followers_dict = {
            "username": [],
            "instagram url": [],
            "Name": []
        }

        for user in tag_followers:
            tag_followers_dict["username"].append(user["username"])
            tag_followers_dict["instagram url"].append(user["instagram url"])
            tag_followers_dict["Name"].append(user["full_name"])

        # print(json.dumps(tag_followers_dict, indent=2))

        data_frame = pandas.DataFrame(tag_followers_dict)
        data_frame.to_csv(f'{tag}_followers.csv')
        return

    except TimeoutException:
        a = False
        return "----------U DIDN'T ENTERED CORRECT USER_ID OR PASSWORD-------------"


# tag = 'aassdd'
# tag = 'cat'
tag = 'paytmgirlsindia'
print(instagram_tags_scraper(user_n, passwd, ask_file.lower(), file_n, tag, next_page=False))
