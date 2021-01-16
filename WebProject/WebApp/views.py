
from datetime import datetime, timedelta, time
import sys
from itertools import islice
from time import sleep

import pandas as pd
from tqdm import tqdm
import GetOldTweets3 as got


# from GetOldTweets3 import models
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import LocalTweet

User = get_user_model()
# Create your views here.


def homepage(request):
    return render(request, 'WebApp/home.html')


def about(request):
    return render(request, 'WebApp/about.html')


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'WebApp/home.html', {"customers": 10})


def get_data(request, *args, **kwargs):
    data = {
        "sales": 100,
        "customers": 10,
    }
    return JsonResponse(data)


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        qs_count = User.objects.all().count()
        labels = ['Users', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange']
        default_items = [qs_count, 23, 2, 3, 12, 2]
        data = {
            "labels": labels,
            "default": default_items
        }
        return Response(data)

def tweet_scraper(request):
    start = '2021-01-14'
    until = datetime.now().date() - timedelta(days=1)
    datelist = pd.date_range(start, end=until).tolist()
    query = 'coronavirus OR covid OR covid-19 OR covid19'
    sleep_mins = 16
    max_attempts = 3

    tweets_dict = {}

    error = None
    for (i, date) in tqdm(enumerate(datelist)):
        attempts_at_date = 0
        if error != 'KeyboardInterrupt':
            if attempts_at_date < max_attempts:
                while True:
                    if attempts_at_date < max_attempts:
                        attempts_at_date += 1
                        try:
                            print('\nAttempt {} of {} retrieving {}' \
                                  .format(attempts_at_date, max_attempts, str(date)[:10]))
                            tweets_dict[str(date)[:10]] = getoldtweets(str(date)[:10],
                                                                       str(date + timedelta(days=1))[:10],
                                                                       query)
                            num_tweets = len(tweets_dict[str(date)[:10]])
                            print('Success retrieving {} tweets for {}: {} of {} dates' \
                                  .format(num_tweets, str(date)[:10], i + 1, len(datelist)))
                            break

                        except KeyboardInterrupt:
                            error = 'KeyboardInterrupt'
                            break

                        except:
                            try:
                                print(
                                    '\nError retrieving {} on attempt {} of {}. Sleeping for {} minutes.\nMinutes Slept:' \
                                    .format(str(date)[:10], attempts_at_date, max_attempts,
                                            sleep_mins + attempts_at_date))
                                for t in range(sleep_mins + attempts_at_date):
                                    sys.stdout.write(str(t) + '.. ')
                                    sys.stdout.flush()
                                    sleep(6)
                            except KeyboardInterrupt:
                                break
                    else:
                        print('Attempt {} at {} failed. Exiting.'.format(max_attempts, str(date)[:10]))
                        break
            else:
                break
        else:
            break

    tweets_ls = []
    batch_size = 100
    for tweetquery in list(tweets_dict.values()):
        for tweet in tweetquery:
            local_tweet = LocalTweet(text=tweet["text"], date=tweet["date"])
            tweets_ls.append(local_tweet)

    while True:
        batch = list(islice(tweets_ls, batch_size))
        if not batch:
            break
        LocalTweet.objects.bulk_create(batch, batch_size)

    print('\nTotal No. Tweets retrieved: {}'.format(len(tweets_ls)))

def getoldtweets(since, until, query, near='London, UK', lang='en', maxtweets=10):
    tweetCriteria = got.manager.TweetCriteria().setQuerySearch('{}'.format(query)) \
                                           .setSince('{}'.format(since)) \
                                           .setUntil('{}'.format(until)) \
                                           .setNear('{}'.format(near)) \
                                           .setLang('{}'.format(lang)) \
                                           .setMaxTweets(maxtweets)
    tweets = got.manager.TweetManager.getTweets(tweetCriteria)
    return tweets