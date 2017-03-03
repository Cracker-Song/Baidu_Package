# -*- coding: utf-8 -*-
import re
import time
import json
import requests


def get_userid(name):
    get_id_url = 'http://tieba.baidu.com/home/main?un=%s&ie=utf-8&fr=pb' % (name)
    id_request = requests.get(get_id_url)
    id_pattern = re.compile(r'"user_id":(\d+),"homeUserName":')
    try:
        id = id_pattern.search(id_request.content).group(1)
    except:
        id = None
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
    get_info_url = 'http://koubei.baidu.com/home?fr=header&ppid=%s' % (ppid)
    print get_info_url
    info_request = requests.get(get_info_url, headers=headers)
    info_pattern = re.compile(r'userInfo: ({.+})')
    try:
        info = info_pattern.search(info_request.content).group(1)
    except:
        print get_info_url
    info_json = json.loads(info)
    info_str = r'ID:%s enter 注册时间:%s enter UID:%s' % (info_json['username'].encode('utf-8'), time.strftime('%Y年-%m月-%d日 %H:%M:%S', time.localtime(info_json['regtime'])), info_json['userid'])
    try:
        info_str += ' enter 绑定手机:%s' % info_json['securemobil'].encode('utf-8')
        info_str += ' enter 绑定邮箱:%s' % info_json['secureemail'].encode('utf-8')
    except:
        pass
    return info_str
