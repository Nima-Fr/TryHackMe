# Dig Dug

## Writer

First of all, thanks to the creators of this room for putting in the time.

And also, I have redacted the flag, so you can complete the room yourself.

Happy L34RN1N9. ; )

## Description

Room link: https://tryhackme.com/room/digdug

Created by [tryhackme](https://tryhackme.com/p/tryhackme) and [cmnatic](https://tryhackme.com/p/cmnatic)

Turns out this machine is a DNS server - it's time to get your shovels out!

Oooh, turns out, this **MACHINE_IP** machine is also a DNS server! If we could `dig` into it, I am sure we could find some interesting records! But... it seems weird, this only responds to a special type of request for a `givemetheflag.com` domain?


**Access this challenge** by deploying both the vulnerable machine by pressing the green "Start Machine" button located within this task, and the TryHackMe AttackBox by pressing the "Start AttackBox" button located at the top-right of the page.

Use some common DNS enumeration tools installed on the AttackBox to get the DNS server on **MACHINE_IP** to respond with the flag.


Check out similar content on TryHackMe:

* [DNS in detail](https://tryhackme.com/room/dnsindetail)
* [Passive Reconnaissance](https://tryhackme.com/room/passiverecon)
* [DNS Manipulation](https://tryhackme.com/room/dnsmanipulation)

## Flag

So the room has solved itself. We know the IP that we are given is a DNS server and it only responds to requests for a domain named `givemetheflag.com`.

Let's use `dig` and send a request to our DNS server for `givemetheflag.com` domain. Using `@`, we can specify the DNS server for the DNS lookup, so the command looks like this:

~~~
$ dig @<MACHINE_IP> givemetheflag.com
~~~

Add the machine IP that you are given and run the command above in your terminal and you can find the flag in the TXT record field:

~~~
└─$ dig @10.10.168.81 givemetheflag.com

; <<>> DiG 9.18.1-1-Debian <<>> @10.10.168.81 givemetheflag.com
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 4664
;; flags: qr aa; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;givemetheflag.com.		IN	A

;; ANSWER SECTION:
givemetheflag.com.	0	IN	TXT	"flag{ToldYouTheFlagWasRedactedM8}"

;; Query time: 359 msec
;; SERVER: 10.10.168.81#53(10.10.168.81) (UDP)
;; WHEN: Tue May 17 10:26:06 EDT 2022
;; MSG SIZE  rcvd: 86
~~~

Flag: `flag{ToldYouTheFlagWasRedactedM8}`

## D0N3! ; )

Thanks again to the creators of this room!

Hope you learned something new! : )

Have a G00D 0N3! ; )
