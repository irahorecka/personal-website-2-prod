#!/usr/bin/env bash

crontab -l > mycron
# For executing clean_craigslist_housing
echo "0 6-22/2 * * * python update_db.py" >> mycron
# For executing rm_expired_craigslist_housing
echo "0 2 * * * python rm_expired_db.py" >> mycron
crontab mycron
rm mycron
