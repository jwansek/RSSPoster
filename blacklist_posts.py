import feeder

for subreddit in feeder.CONFIG["subreddits"]:
    for submission in feeder.REDDIT.subreddit(subreddit).new():
        feeder.blacklist(submission.url)