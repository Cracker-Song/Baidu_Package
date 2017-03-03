# -*- coding: utf-8 -*-
import re
import json
import time
import random
import MySQLdb
import requests
from urllib import unquote, quote
from flask import Flask, request, render_template

import Get_Mail
import Get_Name
import Get_Other_Info
import Get_Phone
import Background_Manage as manage
import Get_Phone_Another_Way as get_phone_all


log = open('bduss.txt', 'r')
info = log.read()
bduss_pattern = re.compile(r'\[BDUSS=(.+?)\]')
bduss_list = bduss_pattern.findall(info)
cookies = []
for bduss in bduss_list:
        tmp = {'BDUSS':bduss}
        cookies.append(tmp)


def check_key(key, right, ip):
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
        cur = conn.cursor()
        cur.execute('select start_time, avaliable from %s where personal_key="%s"' % (right, quote(key.encode('utf-8'))))
        start_time, status = cur.fetchone()
        start_time = time.mktime(time.strptime(str(start_time), '%Y-%m-%d %H:%M:%S'))
        if status and time.time() - start_time < 30 * 24 * 60 *60:# and check_location(ip, key)):
            return True
        else:
	    cur.execute('update admin_keys set avaliable = false where personal_key="%s"' % quote(key.encode('utf-8')))
	    cur.execute('update guest_keys set avaliable = false where personal_key="%s"' % quote(key.encode('utf-8')))
	    conn.commit()
            return False
    except Exception, e:
        return False
    finally:
	cur.close()
	conn.close()


def get_location(ip):
    url = 'http://apis.baidu.com/apistore/iplookupservice/iplookup?ip=%s' % ip
    header = {
        'apikey':'fc9e6ac7e5c99cda6eea29ee8fa59f00'
    }
    return requests.get(url, headers=header).content


def match_location(ip_new, ip_old):
    try:
        location_new = json.loads(get_location(ip_new))
        location_old = json.loads(get_location(ip_old))
	#print type(location_new), location_new
	print location_new['retData']['city'].encode('utf-8'), location_old['retData']['city'].encode('utf-8')
        if location_new['retData']['province'] == location_old['retData']['province'] and location_new['retData']['city'] == location_old['retData']['city']:
            return True
        else:
            return False
    except:
        return False


def check_location(ip, key):
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
        cur = conn.cursor()
        cur.execute('select ip from site_log where personal_key="%s" order by log_time desc limit 1, 1' % quote(key.encode('utf-8')))
        ip_last = cur.fetchone()[0]
        return match_location(ip, ip_last)
    except:
        return False



def site_log(ip, name, key = '', city = ''):
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
        cur = conn.cursor()
        cur.execute('insert ignore into site_log (ip, personal_key, id, city) values ("%s", "%s", "%s", "%s")' % (ip, quote(key.encode('utf-8')), quote(name.encode('utf-8')), quote(city.encode('utf-8'))))
        conn.commit()
        cur.close()
        conn.close()
    except Exception, e:
        print e


app = Flask(__name__)
running_list = []
running_slow = []


@app.route('/index')
def index():
    ip = request.remote_addr
    return render_template('index.html', ip = ip)


@app.route('/info/<string:key>/<string:name>/<string:city>')
def get_phone_with_city(name, key, city):
    try:
        site_log(request.remote_addr, name, key, city)
        if not check_key(key, 'guest_keys', request.remote_addr):
            return 'key error'
        city = unquote(city)
        city = city.replace('+', '')
        city = city.replace(' ', '')
        if city == '':
            return 'key error'
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
            cur = conn.cursor()
            cur.execute('select * from info where id="%s"' % quote(name.encode('utf-8')))
            result = ''
            for line in cur.fetchall():
                result += 'id:%s phone:%s\n' % (unquote(line[0]), line[1])
            cur.close()
            conn.close()
            if result != '':
                print result
            else:
                raise Exception('not in sql')
            return result
        except Exception, e:
            print e
        try:
            info = Get_Phone.print_phone(name, city, cookies, threads_numbers = 10)
        except Exception, e:
            info = e
        return info
    except:
        return 'error'


@app.route('/info/<string:key>/<string:name>')
def get_phone(name, key):
    try:
        site_log(request.remote_addr, name, key)
        if not check_key(key, 'admin_keys', request.remote_addr):
            return 'key error'
        if key not in running_list:
            running_list.append(key)
        else:
            return '查询中，禁止多开，请勿重复点击!如造成严重影响将视为对服务器的攻击进行封禁屏蔽处理!'
	print running_list
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
            cur = conn.cursor()
            cur.execute('select * from info where id="%s"' % quote(name.encode('utf-8')))
            result = ''
            for line in cur.fetchall():
                result += 'id:%s phone:%s\n' % (unquote(line[0]), line[1])
            cur.close()
            conn.close()
            if result != '':
                print result
            else:
                raise Exception('not in sql')
            running_list.remove(key)
            return result
        except Exception, e:
            pass
        try:
            if key == 'guesshwat':
                info = Get_Phone.print_phone(name, '', cookies)
            else:
                info = Get_Phone.print_phone(name, '', cookies, threads_numbers = 45)
        except Exception, e:
            info = e
        running_list.remove(key)
        return info
    except:
        return 'error'


@app.route('/info_without_detail/<string:name>')
def get_info(name):
    try:
        ppid = Get_Other_Info.get_userid(name)
        print ppid
        if ppid:
            info = Get_Other_Info.get_numbers(ppid)
            return str(info)
        else:
            return 'ID不存在，或被禁登'
    except:
        return 'error'


@app.route('/get_name/<int:phone>')
def get_name(phone):
    try:
        try:
            return Get_Name.get_info(str(phone), cookies[random.randint(1, 10000)])
        except:
            return 'not exist'
    except:
        return 'error'

@app.route('/get_phone/<string:key>/<string:name>')
@app.route('/get_phone/<string:key>/<string:name>/<string:city>')
def get_phone_with_city_all(name, key, city = ''):
    return 'updating'
    try:
        site_log(request.remote_addr, name, key, city)
        if not check_key(key, 'guest_keys', request.remote_addr) or city == '':
            return 'key error'
        if key not in running_slow:
            running_slow.append(key)
        else:
            return '查询中，禁止多开，请勿重复点击!如造成严重影响将视为对服务器的攻击进行封禁屏蔽处理!'
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
            cur = conn.cursor()
            cur.execute('select * from info where id="%s"' % quote(name.encode('utf-8')))
            result = ''
            isnum = False
            for line in cur.fetchall():
                print line[1][-4:]
                if line[1][-4:] != '':
                    isnum = True
                    result += 'id:%s phone:%s\n' % (unquote(line[0]), line[1])
            cur.close()
            conn.close()
            if isnum == True:
                running_slow.remove(key)
                return result
            else:
                raise Exception('null')
        except Exception, e:
            pass
        try:
            respond = get_phone_all.print_phone(name, city, cookies)
            running_slow.remove(key)
            return respond
        except:
            running_slow.remove(key)
            return '未绑定手机或账号不存在'
    except:
        return 'error'



@app.route('/background/baidu/info/', methods=['POST', 'GET'])
def background_management():
    if request.method == 'POST':
        conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
        cur = conn.cursor()
        cur.execute('select * from management where username="%s" and passwd1="%s" and passwd2="%s"' % (quote(request.form['username']), quote(request.form['passwd1']), quote(request.form['passwd2'])))
        status = cur.fetchall()
        cur.close()
        conn.close()
        if len(status) != 0:
            try:
                #int(request.form['action'])
                return manage.management(request.form['key'], int(request.form['action']), request.form['username'])
            except:
                return 'action error'
        else:
            return 'fuck you cracker'
    else:
        return render_template('management.html')


@app.route('/phone_html', methods=['GET'])
def get_phone_html():
    try:
        key = request.args.get('key', '')
        name = request.args.get('name', '')
        city = request.args.get('city', '')
        site_log(request.remote_addr, name, key)
        if not check_key(key, 'admin_keys', request.remote_addr):
            return 'key error'
        if key not in running_list:
            running_list.append(key)
        else:
            return 'running'
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
            cur = conn.cursor()
            cur.execute('select * from info where id="%s"' % quote(name.encode('utf-8')))
            result = ''
            for line in cur.fetchall():
                result += 'id:%s phone:%s\n' % (unquote(line[0]), line[1])
            cur.close()
            conn.close()
            if result != '':
                print result
            else:
                raise Exception('not in sql')
            running_list.remove(key)
            return result
        except Exception, e:
            pass
        try:
            if key == 'guesshwat':
                info = Get_Phone.print_phone(name, '', cookies, city)
            else:
                info = Get_Phone.print_phone(name, '', cookies, threads_numbers = 20, city=city)
        except Exception, e:
            info = e
        running_list.remove(key)
        return info
    except:
        return 'error'


@app.route('/webpage/phone')
def webpage_phone():
    return render_template('webpage_phone.html')


@app.route('/info_mail/<string:key>/<string:name>/<int:type>')
def get_mail(name, key, type):
    try:
        site_log(request.remote_addr, name, key)
	#site_log(request.remote_addr, name, request.headers['User-Agent'], key)
        if not check_key(key, 'admin_keys', request.remote_addr):
            return 'key error'
        if key not in running_list:
            running_list.append(key)
	    print running_list
        else:
            return 'running'
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
            cur = conn.cursor()
            cur.execute('select * from info_mail where id="%s"' % quote(name.encode('utf-8')))
            result = ''
            for line in cur.fetchall():
                result += 'id:%s mail:%s\n' % (unquote(line[0]), line[1])
            cur.close()
            conn.close()
            if result != '':
                print result
            else:
                raise Exception('not in sql')
            running_list.remove(key)
            return result
        except Exception, e:
            pass
        try:
            if key == 'guesshwat':
		print type(name), name
                info_mail = Get_Mail.print_mail(name, type, cookies)
            else:
                info_mail = Get_Mail.print_mail(name, type, cookies, threads_numbers = 25)
        except Exception, e:
	    print e
            info_mail = 'null'
        #running_list.remove(key)
        return info_mail
    except Exception, e:
	print e
        return 'error'
    finally:
	try:
	    running_list.remove(key)
	except:
	    pass
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)#, debug=True)


