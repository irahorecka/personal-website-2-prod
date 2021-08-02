# pweb2
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
    - If by the end of your setup you receive a bad gateway error, try running the following commands:

        `$ sudo setenforce 0`

        then 

        `$ sudo chown -R user:user /var/lib/nginx/` (where `user` is your CentOS username)

        and finally

        `sudo systemctl restart nginx`

3. Permission denied (Error 13) for *.sock
    - This is usually a permission error. Check out this [Stack Overflow article](https://stackoverflow.com/questions/22071681/permission-denied-nginx-and-uwsgi-socket).

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

1. `$ tail -30 /var/log/nginx/error.log`
    - Check the last 30 lines of your Nginx error log.

2. `$ journalctl -xe`
    - Check Python trace through the system journal. Very useful for troubleshooting faulty applictaion code.

3. `$ sudo systemctl restart nginx`
    - Restart your Nginx server.

4. `$ sudo systemctl enable nginx`
    - Enable your Nginx server to start if server undergoes reboot.

5. `$ sudo systemctl restart pweb2`
    - Restart your Flask application. Must run if you make changes to your app.
    - Run this command if you make changes to `*.ini`, `*.sock`, and `*.system`.

6. `$ sudo systemctl enable pweb2`
    - Enable your Flask application to start if server undergoes reboot.

</details>

<details>
<summary>Misc. articles and tips</summary>
<br>

1. [Migrating DNS from Namecheap to Cloudflare](https://www.youtube.com/watch?app=desktop&v=3gSxVzxoaPg)

2. [Nginx configuration structure](https://www.digitalocean.com/community/tutorials/understanding-the-nginx-configuration-file-structure-and-configuration-contexts)

3. [Gmail SMTPAuthError when using `smtp.gmail.com` via Python](https://stackoverflow.com/questions/26852128/smtpauthenticationerror-when-sending-mail-using-gmail-and-python)

4. Viewing spool file (i.e. 'You have mail')
    - `$ cat /var/spool/mail/user` (where `user` is your CentOS username)

</details>
