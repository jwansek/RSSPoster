import os
os.chdir("/root/RSSPoster/")

from textblob import TextBlob
import feedparser
import datetime
import logging
import json
import praw
import time
import csv
import sys

BLACKLIST_FILE = "blacklist.csv"
CONFIG_FILE = "config.json"

with open(CONFIG_FILE, "r") as f:
    CONFIG = json.load(f)

logging.basicConfig(
    format = "[%(asctime)s]\t%(message)s",
    level = logging.INFO,
    handlers = [
        logging.FileHandler(CONFIG["logfile"]),
        logging.StreamHandler()
    ]
)

REDDIT = praw.Reddit(**CONFIG["redditapi"])

def blacklist(link):
    with open(BLACKLIST_FILE, "a") as f:
        f.write(link + "\n")

def link_posted(link):
    if not os.path.exists(BLACKLIST_FILE):
        return False

    with open(BLACKLIST_FILE, "r") as f:
        links = f.read().splitlines()
    return link in links

def check_sites():
    out = []
    for site in CONFIG["sites"]:
        d = feedparser.parse(site)
        for entry in d.entries:
            if link_posted(entry.link):
                break
            else:
                if TextBlob(entry.title).detect_language() in CONFIG["language_whitelist"]:
                    out.append([d["feed"]["title"], entry.title, entry.link])
                    blacklist(entry.link)

    return out

def post_to_reddit(site_name, title, link):
    for subname in CONFIG["subreddits"]:
        submission = REDDIT.subreddit(subname).submit(
            title = "[%s] %s" % (site_name.upper(), title), 
            url = link
        )
        if CONFIG["redditapi"]["flair"]:
            submission.mod.flair(text = site_name)
        if CONFIG["redditapi"]["approve"]:
            submission.mod.approve()
        logging.info("Successfully posted %s article to https://redd.it/%s" % (site_name, submission.id))


if __name__ == "__main__":
    logging.info("Checked at: " + str(datetime.datetime.now())[:23])
    for site_name, title, link in check_sites():
        post_to_reddit(site_name, title, link)
