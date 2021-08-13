from instagramy import InstagramHashTag

# Connecting the profile
hashtag = InstagramHashTag("cat")

# printing the basic details like
# followers, following, bio
print(hashtag.number_of_posts)
# print(hashtag.popularity())
# print(hashtag.get_biography())

# return list of dicts
# posts = hashtag.get_posts_details()

# print('\n\nLikes', 'Comments')
# for post in posts:
#     likes = post["likes"]
#     comments = post["comment"]
#     print(likes, comments)