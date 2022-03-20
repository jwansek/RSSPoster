import configparser
import feedparser
import langdetect
import logging
import pymysql
import praw
import sys
import os

os.chdir(sys.argv[1])

CONFIG = configparser.ConfigParser()
CONFIG.read("poster.conf")
REDDIT = praw.Reddit(**CONFIG["redditapi"])

logging.basicConfig(
    format = "[%(asctime)s]\t%(message)s",
    level = logging.INFO,
    handlers = [
        logging.FileHandler(CONFIG.get("logging", "logfile")),
        logging.StreamHandler()
    ]
)

class Database:
    def __enter__(self):
        self.__connection = pymysql.connect(
            **CONFIG["mysql"]
        )
        return self

    def __exit__(self, type, value, traceback):
        self.__connection.commit()
        self.__connection.close()

    def is_blacklisted(self, url):
        with self.__connection.cursor() as cursor:
            cursor.execute("SELECT * FROM blacklist WHERE url = %s;", (url, ))
            return len(cursor.fetchall()) > 0

    def read_blacklist(self, csvpath):
        with open(csvpath, "r") as f:
            with self.__connection.cursor() as cursor:
                for line in f.readlines():
                    print(line[:-1])
                    try:
                        cursor.execute("INSERT INTO blacklist VALUES(%s);", (line[:-1], ))
                    except pymysql.IntegrityError:
                        print("Duplicate... Skipping...")

    def append_blacklist(self, url):
        with self.__connection.cursor() as cursor:
            try:
                cursor.execute("INSERT INTO blacklist VALUES(%s);", (url, ))
            except pymysql.IntegrityError:
                print("Duplicate... Skipping...")

def search_sites():
    with Database() as db:
        for site in CONFIG.get("sites", "sites")[1:].split("\n"):
            rss = feedparser.parse(site)
            for entry in rss.entries:
                if db.is_blacklisted(entry.link):
                    logging.info("Skipping %s" % entry.link)
                    break

                if langdetect.detect(entry.title) in CONFIG.get("sites", "languages")[1:].split("\n"):
                    post_to_reddit(rss["feed"]["title"], entry.title, entry.link)
                    db.append_blacklist(entry.link)

def post_to_reddit(site_name, title, link):
    for subname in CONFIG.get("reddit", "subreddits")[1:].split("\n"):
        submission = REDDIT.subreddit(subname).submit(
            title = "[%s] %s" % (site_name.upper(), title), 
            url = link
        )
        submission.mod.flair(text = site_name)
        submission.mod.approve()
        logging.info("Successfully posted %s article to https://redd.it/%s" % (site_name, submission.id))             

if __name__ == "__main__:":
    search_sites()