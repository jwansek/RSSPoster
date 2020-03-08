# A simple script for automatically posting links from RSS feeds to reddit (and twitter later)

Useage:

Clone the repository and cd to it

`mv exampleconfig.json config.json`

Use your favourite text editor like vim or nano to change the settings as you require

`sudo pip3 install -r requirements.txt`

Run this if you need to ignore posts you've already submitted:

`python3 blacklist_posts.py`

`python3 feeder.py`

TODO:

- [ ] Add twitter posting
