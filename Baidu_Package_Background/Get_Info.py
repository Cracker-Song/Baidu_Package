# -*- coding: utf-8 -*-
import re
import json
import base64
import requests
from urllib import quote

key_full = [59, 31, 6, 201, 129, 171, 28, 169, 63, 180, 252, 44, 140, 6, 122, 189, 27, 240, 32, 252, 107, 86, 210, 189, 224, 19, 245, 79, 26, 157, 45, 61, 80, 108, 247, 207, 22, 75, 245, 183, 115, 78, 13, 244, 157, 189, 227, 38, 112, 114, 158, 210, 161, 223, 192, 91, 198, 13, 217, 213, 180, 9, 87, 2, 64, 154, 74, 143, 51, 124, 142, 186, 248, 131, 4, 139, 136, 68, 118, 64, 22, 243, 52, 75, 242, 65, 15, 229, 23, 242, 186, 18, 68, 117, 115, 123, 8, 197, 8, 73, 131, 133, 92, 213, 159, 184, 24, 112, 13, 223, 101, 143, 183, 69, 156, 176, 122, 240, 151, 44, 187, 195, 18, 147, 35, 228, 207, 193, 205, 241, 116, 29, 194, 215, 100, 21, 100, 226, 92, 113, 115, 190, 182, 250, 191, 143, 120, 205, 63, 50, 109, 65, 133, 139, 245, 225, 209, 149, 61, 14, 129, 192, 125, 68, 192, 23, 180, 138, 22, 234, 41, 95, 236, 50, 206, 16, 163, 21, 155, 135, 219, 115, 139, 233, 250, 32, 23, 246, 128, 180, 87, 146, 60, 195, 128, 198, 182, 252, 36, 253, 236, 61, 112, 142, 168, 212, 10, 190, 209, 160, 176, 9, 157, 146, 211, 220, 69, 90, 225, 158, 123, 225, 64, 202, 71, 68, 178, 19, 112, 32, 242, 220, 15, 162, 64, 1, 121, 67, 38, 188, 32, 246, 41, 239, 82, 163, 215, 249, 134, 173, 123, 245, 136, 87, 91, 174, 31, 37, 39, 126, 183, 255, 202, 185, 12, 61, 41, 76, 120, 70, 15, 28, 115, 155, 187, 1, 170, 39, 158, 42, 165, 187, 152, 17, 169, 21, 164, 78, 169, 120, 25, 89, 168, 135, 218, 204, 53, 59, 247, 28, 39, 93, 82, 47, 161, 242, 219, 24, 72, 207, 239, 145, 130, 133, 214, 194, 69, 17, 214, 254, 123, 186, 118, 2, 54, 11, 10, 110, 111, 19, 247, 36, 239, 173, 89, 38, 199, 25, 155, 140, 65, 126, 75, 176, 195, 187, 147, 67, 78, 138, 94, 197, 20, 215, 114, 92, 100, 136, 65, 69, 95, 168, 92, 5, 249, 20, 103, 47]

def xor(a, b):
    return a ^ b


def xor_str(str):
    str_xor = []
    str_bin = map(ord, str)
    for count in range(min(len(str), 140)):
        str_xor.append(xor(str_bin[count], key_full[count]))
    return str_xor


def list_to_str(init_list):
    tmp = ''
    for i in init_list:
        tmp += chr(i)
    return tmp


def get_info(phone, cookies):
    phone = '["%s"]' % phone
    phone_xor_list = xor_str(phone)
    phone_xor = list_to_str(phone_xor_list)
    phone_based = base64.encodestring(phone_xor)
    url = 'http://yun.baidu.com/api/user/search?need_relation=1&user_list=%s&encrypt=1' % quote(phone_based[:-1])
    info_request = requests.get(url, cookies=cookies)
    info_based = info_request.content
    try:
        info_xor = base64.decodestring(info_based)
    except:
        return 'cookies失效'
    info_xor_list = xor_str(info_xor)
    info = list_to_str(info_xor_list)
    uid_pattern = re.compile(r'"uk":(\d+)')
    name_pattern = re.compile(r'"uname":"(.+?)"')
    error_pattern = re.compile(r'"errno":(-*\d+),')
    error = error_pattern.search(info).group(1)
    if error != '0':
        return 'error'
    try:
        uid = uid_pattern.search(info).group(1)
        try:
            name = name_pattern.search(info).group(1)
            name = name.decode('raw_unicode_escape')
        except:
            name = ''
    except:
        name = ''
        uid = ''
    data_dist = {'name':name, 'uid':uid}
    data = json.dumps(data_dist)
    return data
