# A simple script for automatically posting links from RSS feeds to reddit (and twitter later)

Now dockerized!

## Setup:
 - Setup the config file (see the example), and rename it to `poster.conf`
 - You need to have a MariaDB / MySQL database for the blacklist. Set its IP address in the config file.
 - e.g. `CREATE TABLE blacklist (url varchar(300) NOT NULL, PRIMARY KEY (url))`
 - Build the docker container `sudo docker-compose build`
 - Start the docker container `sudo docker-compose up -d`
