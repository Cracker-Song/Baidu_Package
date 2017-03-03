# -*- coding: utf-8 -*-
import re
#import json
import time
import random
import Get_Name
import Get_Other_Info
import MySQLdb
import Get_Phone
import Background_Manage as manage
import Get_Phone_Another_Way as get_phone_all
from urllib import unquote, quote
from flask import Flask,request,render_template

log = open('bduss.txt', 'r')
info = log.read()
bduss_pattern = re.compile(r'\[BDUSS=(.+?)\]')
bduss_list = bduss_pattern.findall(info)
cookies = []
for bduss in bduss_list:
        tmp = {'BDUSS':bduss}
        cookies.append(tmp)


def check_key(key, right):
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
	#print right, quote(key.encode('utf-8'))
        cur = conn.cursor()
        cur.execute('select start_time, avaliable from %s where personal_key="%s"' % (right, quote(key.encode('utf-8'))))
        start_time, status = cur.fetchone()
	#status = cur.fetchone()[1]
	print start_time, status
        start_time = time.mktime(time.strptime(str(start_time), '%Y-%m-%d %H:%M:%S'))
        if time.time() - start_time < 30 * 24 * 60 *60 and status:
            return True
    except Exception, e:
	print e
        return False


def site_log(ip = '', name = '', key = '', city = ''):
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
        if not check_key(key, 'guest_keys'):
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
	    print info
	    return info
        except Exception, e:
            raise Exception('error')
    except:
        return 'error'


@app.route('/info/<string:key>/<string:name>')
def get_phone(name, key):
    try:
        site_log(request.remote_addr, name, key)
	#site_log(request.remote_addr, name, request.headers['User-Agent'], key)
        if not check_key(key, 'admin_keys'):
            return 'key error'
        if key not in running_list:
            running_list.append(key)
	    print running_list
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
                info = Get_Phone.print_phone(name, '', cookies)
            else:
                info = Get_Phone.print_phone(name, '', cookies, threads_numbers = 25)
        except Exception, e:
            info = 'null'
        #running_list.remove(key)
        return info
    except Exception, e:
	print e
        return 'error'
    finally:
	try:
	    running_list.remove(key)
	except:
	    pass

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

#@app.route('/get_phone/<string:key>/<string:name>')
@app.route('/get_phone/<string:key>/<string:name>/<string:city>')
def get_phone_with_city_all(name, key, city = ''):
    try:
        site_log(request.remote_addr, name, key, city)
        #site_log(request.remote_addr, name, request.headers['User-Agent'], key, city)
        if not check_key(key, 'guest_keys') or city == '':
            return 'key error'
        if key not in running_slow:
            running_slow.append(key)
        else:
            return 'running'
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
            cur = conn.cursor()
            cur.execute('select * from info where id="%s"' % quote(name.encode('utf-8')))
            result = ''
            isnum = False
            for line in cur.fetchall():
                print line[1][-4:]
                if line[1][-4:] != 'null':
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
            #running_slow.remove(key)
            return respond
        except:
            #running_slow.remove(key)
            return '未绑定手机或账号不存在'
    except:
        return 'error'
    finally:
        try:
            running_slow.remove(key)
        except:
            pass

@app.route('/background/baidu/info/<string:username>/<string:passwd>/<string:key>/<int:action>')
def background_management(username, passwd, key, action):
    if username != 'test' and passwd != 'test':
        return 'fuck you cracker'
    return manage.management(key, action)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)#, debug=True)

