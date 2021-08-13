# Name -> done
# Instagram URL -> done
# Insta Followers -> half done
# Insta Engagement
# Insta Avg Likes
# Avg Reach
# Avg Video Views
# State
# City
# Email
# Mobile

import json
import pandas
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd
from .count_number_of_followers import count_followers_from_username
import asyncio, aiohttp
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CHROME_DRIVER_PATH = Path(BASE_DIR, "..", 'chromedriver.exe')
# CHROME_DRIVER_PATH =
print("chrome driver path > ", CHROME_DRIVER_PATH)


def merge_lists(results_from_fc):
    """
    Function for merging multiple lists
    """
    combined_list = []
    for li in results_from_fc:
        combined_list.extend(li)
    return combined_list


def merge_dicts(dict1, dict2):
    """merge the fields of current + prev dict"""
    dict1["users"].extend(dict2["users"])
    dict1["usernames"].extend(dict2["usernames"])
    return dict1


def instagram_tags_scraper(username, password, tag, page=0, max_id=""):
    driver = webdriver.Chrome(CHROME_DRIVER_PATH)
    print(f'-----STARTED FETCHING DATA FOR #{tag}------')

    tag_followers_dict = {
        # "username": [],
        "instagram url": [],
        "Name": [],
        "followers": []
    }

    async def _process_ig_response(response):
        next_max_id, processed_response = "", {}

        # handle error case
        if response == "Oops, an error occurred.":
            driver.back()
            return next_max_id, processed_response

        json_response = json.loads(response.text)

        # print("json response >> ", type(json_response))
        # print("json response >> ", json.dumps(json_response, indent=3))

        # ==============================================================================================================
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
        # ==============================================================================================================

        more_available = json_response["data"]["recent"]["more_available"]
        if more_available:
            next_max_id_from_res = json_response["data"]["recent"]["next_max_id"]
            next_max_id += next_max_id_from_res
        tag_followers = []

        # Note: Not fetching top posts as it only has few posts and it keeps on repeating
        # for fetching top posts:
        # top_posts_sections_arr = json_response["data"]["top"]["sections"]
        # for item in top_posts_sections_arr:
        #     medias = item["layout_content"]["medias"]
        #     for media_item in medias:
        #         user = media_item["media"]["user"]
        #         user["instagram url"] = f'https://www.instagram.com/{user["username"]}/'
        #         tag_followers.append(user)
        #         print("user >> ", user)

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

        # tag_followers_dict = {
        #     "username": [],
        #     "instagram url": [],
        #     "Name": []
        # }
        tasks = []
        for user in tag_followers:
            # tag_followers_dict["username"].append(user["username"])
            tag_followers_dict["instagram url"].append(user["instagram url"])
            tag_followers_dict["Name"].append(user["full_name"])

            # no_of_followers = asyncio.ensure_future(count_followers_from_username(username=user["username"])) # means get this process started and move on
            # tag_followers_dict["followers"].append(no_of_followers)

            task = asyncio.ensure_future(
                count_followers_from_username(username=user["username"]))  # means get this process started and move on
            tasks.append(task)
        # .gather() will collect the result from every single task from tasks list
        # here we use await to wait till all the requests have been satisfied
        all_results = await asyncio.gather(*tasks)

        # all_followers = merge_lists(all_results)
        tag_followers_dict["followers"].extend(all_results)

        # print(json.dumps(tag_followers_dict, indent=2))

        return next_max_id, tag_followers_dict

    # Login into IG if page==0 else hit the next page url directly and recursively call the instagram_tags_scraper
    # instagram_tags_scraper func with new next max_id
    def _login_into_ig():
        ig_url = "https://www.instagram.com/"
        driver.get(ig_url)

        u_id = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#loginForm > div > div:nth-child(1) > div > label > input"))
        )

        u_id.clear()
        u_id.send_keys(username)  # username

        pwd = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#loginForm > div > div:nth-child(2) > div > label > input"))
        )
        pwd.clear()
        pwd.send_keys(password)  # password

        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#loginForm > div > div:nth-child(3) > button"))
        )

        login_button.click()

        not_now = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#react-root > section > main > div > div > div > div > button"))
        )

        not_now.click()

        url_with_tag = f'https://www.instagram.com/explore/tags/{tag}/?__a=1'

        driver.get(url_with_tag)

        res_data = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "body"))
        )

        # next_max_id, followers_of_tag_dict = _process_ig_response(
        #     response=res_data)  # returns next_max_id & processed dict
        next_max_id, followers_of_tag_dict = asyncio.get_event_loop().run_until_complete(_process_ig_response(
            response=res_data))  # returns next_max_id & processed dict

        # json_response = json.loads(res_data.text)
        if next_max_id:
            _go_to_next_page(page=page + 1, max_id=next_max_id, followers_of_tag_dict=followers_of_tag_dict)

        # return json_response
        return followers_of_tag_dict

    def _go_to_next_page(page, followers_of_tag_dict, max_id=max_id, tag=tag):
        if page == 0:
            return
        next_pg_url = f"https://www.instagram.com/explore/tags/{tag}/?__a=1&max_id={max_id}"
        driver.get(next_pg_url)

        res_data = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "body"))
        )
        print(f"--------- I'm on PAGE: {page} ---------")

        # next_max_id, followers_of_tag_dict = _process_ig_response(
        #     response=res_data)  # returns next_max_id & processed dict
        next_max_id, followers_of_tag_dict = asyncio.get_event_loop().run_until_complete(_process_ig_response(
            response=res_data))  # returns next_max_id & processed dict

        if next_max_id:
            _go_to_next_page(page=page + 1, followers_of_tag_dict=followers_of_tag_dict, max_id=next_max_id, tag=tag)

        return followers_of_tag_dict

    if page == 0:
        json_response = _login_into_ig()

        return json_response
    print("total users got >> ", len(tag_followers_dict["username"]))

    return tag_followers_dict


# tag_to_search = 'aassdd'
# tag_to_search = 'kapurchand'
# tag_to_search = 'cat'
# tag_to_search = 'paytmgirlsindia'

#
# # user_n = input("TYPE THE USER NAME OF THE ACCOUNT (it should be accurate)--> ")
# user_n = 'jennifergoenka'
# # passwd = input("TYPE PASSWORD OF THE ACCOUNT --> ")
# passwd = '111213'
# t1 = time.time()
# tag_followers_dict = instagram_tags_scraper(user_n, passwd, tag=tag_to_search, page=0, max_id="")
# print("total data gathered >> ", len(tag_followers_dict["Name"]))
# print("tag_followers_dict >> ", tag_followers_dict)
# df = pd.DataFrame(tag_followers_dict)
# filename = f"{tag_to_search}_follwers_data.csv"
# df.to_csv(filename)
# t2 = time.time()
# print("total time taken >> ", t2 - t1)
# # took 1748 sec -> 29.1 min to scrape 1580 posts
