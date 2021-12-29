#!/usr/bin/env python3

hash = 'dxeedxebdwemdwesdxdtdweqdxefdxefdxdudueqduerdvdtdvdu'

def rev_str_to_int(numArr):
    res = ""
    for n1, n2 in zip(numArr[0::2], numArr[1::2]):
        res += (chr((n1 * 26) + n2))
    return res

def rev_int_to_str(txt):
    res = []
    for elm in txt:
        res.append(ord(elm) - 97)
    return res

print(rev_str_to_int(rev_int_to_str(rev_str_to_int(rev_int_to_str(hash)))))