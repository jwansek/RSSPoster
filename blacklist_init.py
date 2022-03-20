import configparser
import feedparser
import langdetect
import logging
import pymysql
import praw
import sys
import os

import rssposter

with rssposter.Database() as db:
    for subname in rssposter.CONFIG.get("reddit", "subreddits")[1:].split("\n"):
        subreddit = rssposter.REDDIT.subreddit(subname)
        for submission in subreddit.new(limit = None):
            if type(submission) is praw.models.reddit.submission.Submission:
                db.append_blacklist(submission.url)
                print(submission.url)