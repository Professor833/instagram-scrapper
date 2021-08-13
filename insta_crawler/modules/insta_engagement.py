from instaloader import Instaloader, Profile


def count_ig_engagement(target_profile):
    loader = Instaloader()
    try:
        profile = Profile.from_username(loader.context, target_profile)

        num_followers = profile.followers
        total_num_likes = 0
        total_num_comments = 0
        total_num_posts = 0

        for post in profile.get_posts():
            total_num_likes += post.likes
            total_num_comments += post.comments
            total_num_posts += 1

        engagement = float(total_num_likes + total_num_comments) / (num_followers * total_num_posts)
        return engagement * 100
    except:
        return 'User with this username does not exist!'
