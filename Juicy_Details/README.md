# Juicy Details

## Description

A popular juice shop has been breached! Analyze the logs to see what had happened...

## [Task 1] Introduction

### Introduction

You were hired as a SOC Analyst for one of the biggest Juice Shops in the world and an attacker has made their way into your network. 

Your tasks are:

* Figure out what techniques and tools the attacker used
* What endpoints were vulnerable
* What sensitive data was accessed and stolen from the environment

An IT team has sent you a zip file containing logs from the server. Download the attached file, type in "I am ready!" and get to work! There's no time to lose!


Are you ready?

Answer: `I am ready!`

## [Task 2] Reconnaissance

Analyze the provided log files.

Look carefully at:

* What tools the attacker used
* What endpoints the attacker tried to exploit
* What endpoints were vulnerable

### 2.1 - What tools did the attacker use? (Order by the occurrence in the log)

After downloading the zip file, extract the files inside it and start analyzing `access.log`. You can use an IDE to look through the logs, or use the shell tools to make the proccess faster.

* **Note: some of the tools and switches you see me use, are just for the purpose of beautifying the answers for you.**

You can use the following command to exclude the repeating logs and take out the unique ones:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Juicy_Details/files]
└─$ cat access.log | cut -d '"' -f 6 | uniq
-
Mozilla/5.0 (compatible; Nmap Scripting Engine; https://nmap.org/book/nse.html)
Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
Mozilla/5.0 (Hydra)
Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
sqlmap/1.5.2#stable (http://sqlmap.org)
Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
curl/7.74.0
feroxbuster/2.2.1
Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0

Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
~~~

As you can see the attacker used the following tools. (Sorted in order of use):

* Nmap
* Hydra
* sqlmap
* curl
* feroxbuster

Answer: `Nmap, Hydra, sqlmap, curl, feroxbuster`

### 2.2 - What endpoint was vulnerable to a brute-force attack?

You can find the vulnerable endpoint in the part of the log, where the hydra brute-force is happening:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Juicy_Details/files]
└─$ cat access.log | grep "Hydra" | cut -d '"' -f 2 | head -n1
GET /rest/user/login HTTP/1.0
~~~

Answer: `/rest/user/login`

### 2.3 - What endpoint was vulnerable to SQL injection?

You can find the answer to this question where the sqlmap is trying to inject queries:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Juicy_Details/files]
└─$ cat access.log | grep "sqlmap" | cut -d '"' -f 2 | head -n1
GET /rest/products/search?q=1 HTTP/1.1
~~~

Answer: `/rest/products/search`

### 2.4 - What parameter was used for the SQL injection?

You can see the parameter that was used for the SQL injection in the same place:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Juicy_Details/files]
└─$ cat access.log | grep "sqlmap" | cut -d '"' -f 2 | head -n1
GET /rest/products/search?q=1 HTTP/1.1
                          ^
~~~

Answer: `q`

### 2.5 - What endpoint did the attacker try to use to retrieve files? (Include the /)

In the last few lines of the log, you can see that the attacker used `/ftp` to retrieve two files with `.bak` extention:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Juicy_Details/files]
└─$ cat access.log | cut -d '"' -f 2 | uniq | tail -n4
GET /ftp HTTP/1.1
GET /ftp/www-data.bak HTTP/1.1    <------------
GET /ftp/coupons_2013.md.bak HTTP/1.1
GET /favicon.ico HTTP/1.1
~~~

Answer: `/ftp`

## [Task 3] Stolen data

Analyze the provided log files.

Look carefully at:

* The attacker's movement on the website
* Response codes
* Abnormal query strings

### 3.1 - What section of the website did the attacker use to scrape user email addresses?

Hint: Where can customers usually comment on a shopping website?

Where a customer gives feedback, is where you can gather information from them. This a shop, so there must be a section for reviews and checking the logs proves the existence of it:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Juicy_Details/files]
└─$ cat access.log| grep "reviews" | cut -d '"' -f 2 | uniq | head -n5
GET /rest/products/1/reviews HTTP/1.1
GET /rest/products/24/reviews HTTP/1.1
GET /rest/products/6/reviews HTTP/1.1
GET /rest/products/42/reviews HTTP/1.1
GET /rest/products/3/reviews HTTP/1.1
~~~

Answer: `product reviews`

### 3.2 - Was their brute-force attack successful? If so, what is the timestamp of the successful login? (Yay/Nay, 11/Apr/2021:09:xx:xx +0000)

We can check if the brute-force was successful or not, by searching for code 200 in hydra brute-force period logs:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Juicy_Details/files]
└─$ cat access.log | grep -i "hydra" | grep 200
::ffff:192.168.10.5 - - [11/Apr/2021:09:16:31 +0000] "POST /rest/user/login HTTP/1.0" 200 831 "-" "Mozilla/5.0 (Hydra)"
~~~

Answer: `Yay, 11/Apr/2021:09:16:31 +0000`

### 3.3 - What user information was the attacker able to retrieve from the endpoint vulnerable to SQL injection?

I checked the logs, and after the sqlmap was done, we can see that they retrieved `email` and `password` (The following commands are just to show you where it was):

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Juicy_Details/files]
└─$ cat access.log | grep email | cut -d '"' -f 2 | uniq
GET /rest/products/search?q=qwert%27))%20UNION%20SELECT%20id,%20email,%20password,%20%274%27,%20%275%27,%20%276%27,%20%277%27,%20%278%27,%20%279%27%20FROM%20Users-- HTTP/1.1
~~~

Answer: `email, password`

### 3.4 - What files did they try to download from the vulnerable endpoint? (endpoint from the previous task, question #5)

They tried to download two backup files:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Juicy_Details/files]
└─$ cat access.log | cut -d '"' -f 2 | uniq | tail -n3
GET /ftp/www-data.bak HTTP/1.1           <-------------
GET /ftp/coupons_2013.md.bak HTTP/1.1    <-------------
GET /favicon.ico HTTP/1.1
~~~

Answer: `coupons_2013.md.bak, www-data.bak`

### 3.5 - What service and account name were used to retrieve files from the previous question? (service, username)

Hint: What other log files do you have?

We are done with this log. Let's head to `vsftpd.log`. We can confirm the downlaoded files in the last two lines. The attacker used the username `anonymous` on the `ftp` service.

Answer: `ftp, anonymous`

### 3.6 - What service and username were used to gain shell access to the server? (service, username)

For the last question, we go to `auth.log` and we can see that the attacker brute-forced the `ssh` service to find user `www-data`'s password and they were successful:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Juicy_Details/files]
└─$ cat auth.log | grep -i accepted       
Apr 11 09:41:19 thunt sshd[8260]: Accepted password for www-data from 192.168.10.5 port 40112 ssh2
Apr 11 09:41:32 thunt sshd[8494]: Accepted password for www-data from 192.168.10.5 port 40114 ssh2
~~~

Answer: `ssh, www-data`

# D0N3! ; )

Thanks to the creator(s).

Hope you had fun and learned some new ways of analyzing logs.

Have a g00d one! : )