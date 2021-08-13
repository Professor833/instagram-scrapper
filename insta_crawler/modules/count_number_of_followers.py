# import requests
# import re
#
# user = "lv_1601"
# url = 'https://www.instagram.com/' + user
# r = requests.get(url).text
# print("r >> ", r)
# # followers = re.search('"edge_followed_by":{"count":([0-9]+)}',r).group(1)
#
# print(followers)

from instaloader import Instaloader, Profile
import time
import aiohttp, asyncio


def count_followers_from_username(username):
    followers = 0
    try:
        L = Instaloader()
        profile = Profile.from_username(L.context, username)
        followers += int(profile.followers)
    except:
        pass
    return followers

# async def count_followers_from_username(username):
#     followers = 0
#     try:
#         L = Instaloader()
#         profile = Profile.from_username(L.context, username)
#         followers += int(profile.followers)
#     except:
#         pass
#     return followers

# unames = ['lv_1601', 'geeks_for_geeks', 'fire._.2310']
# print(f"followers for {uname} : {count_followers_from_username(uname)}")
