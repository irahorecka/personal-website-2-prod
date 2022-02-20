#!/usr/bin/env bash

crontab -l > mycron
# Setup cron headers
echo "SHELL=/bin/bash" >> mycron
# For executing update_db.py every four hours every day.
echo "0 */4 * * * source /home/irahorecka/pweb2/webenv/bin/activate && python /home/irahorecka/pweb2/update_db.py" >> mycron
# For executing rm_expired_db.py at 02:00 every day.
# echo "0 2 * * * source /home/irahorecka/pweb2/webenv/bin/activate && python /home/irahorecka/pweb2/rm_expired_db.py" >> mycron
crontab mycron
rm mycron
