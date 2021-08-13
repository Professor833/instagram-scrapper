from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import time, csv
# from .modules.async_get_ig_res_paginated import instagram_tags_scraper
from .modules.get_ig_res_paginated import instagram_tags_scraper
from .modules.insta_engagement import count_ig_engagement
from .forms import CalculateInstagramEngagement


# Create your views here.


def home(request):
    return render(request, 'index.html')


def calculate_ig_engagement(request):
    form = CalculateInstagramEngagement()  # blank form object just to pass context if not post method
    context = {"form": form}
    if request.method == 'POST':
        username = request.POST["username"]
        print("username >> ", username)

        form = CalculateInstagramEngagement(request.POST)  # if post method then form will be validated
        if form.is_valid():
            username = request.POST["username"]

            engagement_count = count_ig_engagement(username)
            if engagement_count == 'User with this username does not exist!':
                context["engagement"] = 'User with this username does not exist!'
            else:
                context["engagement"] = f"{round(engagement_count, 2)} %"
            context["username"] = username
            return render(request, 'calculate_instagram_engagement.html', context)

    return render(request, 'calculate_instagram_engagement.html', context=context)


def get_hashtag_details(request):
    if request.method == 'POST':
        tag = request.POST["tag"]
        print("tag >> ", tag)
        user_n = 'jennifergoenka'
        passwd = '111213'
        tag_followers_dict = instagram_tags_scraper(user_n, passwd, tag)
        print("tag_followers_dict >> ", tag_followers_dict)
        # return HttpResponse("success")

        response = HttpResponse(content_type='text/csv',
                                headers={'Content-Disposition': f'attachment; filename="{tag}_followers.csv"'},
                                )
        # tag_info_dict =
        # response['Content-Disposition'] = f'attachment; filename="{tag}_followers.csv"'
        # writer = csv.writer(response, delimiter=',')  # I always like to specify the delimeter

        writer = csv.writer(response)
        writer.writerow(['instagram url', 'Name', 'followers'])

        # Then you may actually want to write some data to the CSV file, currently, you've only defined the headers (first row). An example would be like:
        for i in range(len(tag_followers_dict["instagram url"])):
            writer.writerow([
                tag_followers_dict["instagram url"][i],
                tag_followers_dict["Name"][i],
                tag_followers_dict["followers"][i]
            ])

        return response

    tag = request.GET["hashtag_inp"]
    print("tag >> ", tag)
    user_n = 'jennifergoenka'
    passwd = '111213'
    tag_followers_dict = instagram_tags_scraper(user_n, passwd, tag)
    print("tag_followers_dict >> ", tag_followers_dict)
    # return HttpResponse("success")

    response = HttpResponse(content_type='text/csv',
                            headers={'Content-Disposition': f'attachment; filename="{tag}_followers.csv"'},
                            )
    # tag_info_dict =
    # response['Content-Disposition'] = f'attachment; filename="{tag}_followers.csv"'
    # writer = csv.writer(response, delimiter=',')  # I always like to specify the delimeter

    writer = csv.writer(response)
    writer.writerow(['instagram url', 'Name', 'followers'])

    # Then you may actually want to write some data to the CSV file, currently, you've only defined the headers (first row). An example would be like:
    for i in range(len(tag_followers_dict["instagram url"])):
        writer.writerow([
            tag_followers_dict["instagram url"][i],
            tag_followers_dict["Name"][i],
            tag_followers_dict["followers"][i]
        ])

    return response
    # return HttpResponse("Bad Request")
