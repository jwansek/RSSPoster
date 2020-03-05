import feedparser
import datetime
import json
import praw
import time
import csv
import sys
import os

BLACKLIST_FILE = "blacklist.csv"
CONFIG_FILE = "config.json"

with open(CONFIG_FILE, "r") as f:
    CONFIG = json.load(f)

REDDIT = praw.Reddit(
    client_id = CONFIG["redditapi"]["client_id"],
    client_secret = CONFIG["redditapi"]["client_secret"],
    username = CONFIG["redditapi"]["username"],
    password = CONFIG["redditapi"]["password"],
    user_agent = CONFIG["redditapi"]["user_agent"],
)

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
        if not link_posted(d.entries[0].link):
            out.append([d["feed"]["title"], d.entries[0].title, d.entries[0].link])
            blacklist(d.entries[0].link)
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
        print("Successfully posted %s article to https://redd.it/%s" % (site_name, submission.id))


if __name__ == "__main__":
    while True:
        print("Checked at: " + str(datetime.datetime.now())[:23])
        for site_name, title, link in check_sites():
            post_to_reddit(site_name, title, link)
        print()
        time.sleep(CONFIG["waitafter"])