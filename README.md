# pweb2
[![Website irahorecka.com](https://img.shields.io/website-up-down-green-red/https/irahorecka.com.svg)](https://irahorecka.com/)

Production setup of my personal website. Check it out here: [irahorecka.com](https://irahorecka.com).

This application is written in Python using the Flask framework. The frontend is comprised of HTML (with web templating engine Jinja2), simple jQuery, and Tailwind CSS. This repository is configured for a production environment.

I intend this README to serve as a guide to launch a Flask web application on a virtual private server (VPS) running [CentOS 7](http://mirror.centos.org/centos/7/).

## Technical Specs:
- Python 3.9.6
- PostgreSQL 13.3
- Nginx 1.20.1
- 2GB Ryzen VPS
    - CPU Cores: 2 Ryzen CPU cores
    - RAM: 2GB DDR4 RAM
    - OS: 64 Bit CentOS Linux release 7.9.2009

## VPS / Nginx / Flask Application setup guidelines

<details>
<summary>Where to find a cheap VPS</summary>
<br>

Check out this [Reddit post](https://www.reddit.com/r/selfhosted/comments/5c93f1/any_cheap_vps_services/).
I ended up searching through [LowEndBox](https://lowendbox.com/) to find my VPS.
</details>

<details>
<summary>Setting up your Flask application on your CentOS VPS</summary>
<br>

Please follow these excellent guidelines in order:

1. [Initial Server Setup with CentOS7](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-centos-7)

2. [Configuring a Basic Firewall](https://www.digitalocean.com/community/tutorials/additional-recommended-steps-for-new-centos-7-servers#configuring-a-basic-firewall)

3. [How To Serve Flask Applications with uWSGI and Nginx on CentOS 7](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-centos-7)
</details>

<details>
<summary>Common troubleshooting tips and tricks</summary>
<br>

View these common tips and tricks to make your setup experience a little less painful.

1. Firewall configuration
    - Follow the Firwall setup guideline article posted above. If you are testing and/or hosting your application on a port, use

        `$ sudo firewall-cmd --permanent --add-port=8000/tcp`

        then

        `$ sudo firewall-cmd --reload`
    
        to allow access to your application from the world wide web.

2. Bad Gateway Error (502)
    - If by the end of your setup you receive a bad gateway error, try running the following commands if you plan to have SELinux enabled:

        `$ sudo setenforce 0`

        then 

        `$ sudo chown -R user:user /var/lib/nginx/` (where `user` is your CentOS username) [[ref](https://stackoverflow.com/questions/29872174/wsgi-nginx-error-permission-denied-while-connecting-to-upstream)].

        `$ sudo chgrp user ~/app` (where `user` is your CentOS username and `app` is your project directory's name) [[ref](https://stackoverflow.com/questions/62225597/nginx-gunicorn-flask-502-bad-gateway-permission-denied-on-socket-file/67625668#67625668)].

        and finally

        `$ sudo systemctl restart nginx`

    - If you plan to have SELinux disabled, follow Jonny's advice on this [Stack Overflow article](https://stackoverflow.com/questions/17079670/httpd-server-not-started-13permission-denied-make-sock-could-not-bind-to-ad) to disable SELinux. With SELinux enabled, using `$ sudo setenforce 0` alleviates this issue, albeit temporarily (at least in my experience).

3. Permission denied (Error 13) for *.sock
    - Ties closely with error 502 (above). This is usually a permission error. Check out this [Stack Overflow article](https://stackoverflow.com/questions/23948527/13-permission-denied-while-connecting-to-upstreamnginx/24830777#24830777) for troubleshooting this error. This article appears have the more widely accepted solution. NOTE: you must be logged in as root to execute
    
        `$ setsebool -P httpd_can_network_connect 1`
    
        (i.e. the accepted solution by joebarbere).
    
    - Check out this other [Stack Overflow article](https://stackoverflow.com/questions/22071681/permission-denied-nginx-and-uwsgi-socket) if further troubleshooting is required.

4. Troubleshooting 500 Internal Server Error
    - Check out this [Digital Ocean discussion](https://www.digitalocean.com/community/questions/500-internal-server-error-in-my-site) to troubleshoot a 500 Internal Server Error.

5. Using environment variables in your Flask application
    - Use [python-dotenv](https://github.com/theskumar/python-dotenv) for configuring and fetching your environment variables.
    - (Optional) Make sure to delete exported environment variables configured in your system.
        `$ unset YOUR_ENV_VARIABLE`
    

</details>

<details>
<summary>Useful shell commands</summary>
<br>

1. `$ sudo su -`
    - Log in as root from a sudo-user ssh session. Root password is required.

2. `$ sudo su - user`
    - Log in as `user` from a sudo-user ssh session. `user` password is required.

3. `$ tail -30 /var/log/nginx/error.log`
    - Check the last 30 lines of your Nginx error log.

4. `$ journalctl -xe`
    - Check Python trace through the system journal. Very useful for troubleshooting faulty applictaion code.

5. `$ sudo systemctl restart nginx`
    - Restart your Nginx server.

6. `$ sudo systemctl enable nginx`
    - Enable your Nginx server to start if server undergoes reboot.

7. `$ sudo systemctl restart pweb2`
    - Restart your Flask application. Must run if you make changes to your app.
    - Run this command if you make changes to `*.ini`, `*.sock`, and `*.system`.

8. `$ sudo systemctl enable pweb2`
    - Enable your Flask application to start if server undergoes reboot.

</details>

<details>
<summary>Misc. articles and tips</summary>
<br>

1. [Migrating DNS from Namecheap to Cloudflare](https://www.youtube.com/watch?app=desktop&v=3gSxVzxoaPg)

2. [Nginx configuration structure](https://www.digitalocean.com/community/tutorials/understanding-the-nginx-configuration-file-structure-and-configuration-contexts)

3. [Gmail SMTPAuthError when using `smtp.gmail.com` via Python](https://stackoverflow.com/questions/26852128/smtpauthenticationerror-when-sending-mail-using-gmail-and-python)

4. Viewing spool file (i.e. 'You have mail')
    - `$ cat /var/spool/mail/user` (where `user` is your CentOS username).

</details>

<details>
<summary>For Ira: Setting up the web app properly.</summary>
<br>

1. Clone this repository. Create a virtual environment named `webenv` in the project root. Install project requirements via `pip` in the virtual environment.

2. Download and setup PostgreSQL and create a database named `irahorecka`. Ensure all of your environment variables are declared in a file named `.env` stored in the project root. Afterwards, run `setup_db.py` to ensure correct database and environment variable configurations.

3. This web app relies on timed updates and cleaning of the `irahorecka` database. These are done with `update_db.py` and `rm_expired_db.py`. Execute `update_db.py` to populate the `irahorecka` database. Ensure no runtime exceptions are thrown. Afterwards, run `rm_expired_db.py`. Troubleshoot as necessary (commonly due to configuration issues). Proceed to the next step when both scripts execute without error.

4. Setup your cron tasks. Open the crontab tasklist and delete undesired cron tasks via `$ crontab -e`. To delete EVERYTHING, you can execute  `$ crontab -r` (NOTE: make sure you are OK with deleting every cron task). Once satisfied, execute `$ sudo bash cron.sh` to concatenate timed executions of `update_db.py` and `rm_expired_db.py`.

5. Though missing in this repository, it is helpful to create a bash script to restart your web app and the NGINX server using `sudo systemctl restart *`. This way, you can simply run `$ sudo bash restart.sh` anytime you make or pull changes.

</details>
