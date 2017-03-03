# -*- coding: utf-8 -*-
import MySQLdb
from urllib2 import quote


def management(key, action, username):
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
        cur = conn.cursor()
        if action == 1:#添加用户
            cur.execute('insert ignore into guest_keys (personal_key) values ("%s")' % quote(key.encode('utf-8')))
            cur.execute('insert ignore into admin_keys (personal_key) values ("%s")' % quote(key.encode('utf-8')))
        elif action == 2:#封禁/解封用户
            cur.execute('select avaliable from guest_keys where personal_key="%s"' % quote(key.encode('utf-8')))
            status = bool(cur.fetchone()[0])
            status = not status
            print status
            cur.execute('update guest_keys set avaliable=%s where personal_key="%s"' % (status, quote(key.encode('utf-8'))))
            cur.execute('update admin_keys set avaliable=%s where personal_key="%s"' % (status, quote(key.encode('utf-8'))))
        elif action == 3:#用户续费
            cur.execute('update guest_keys set start_time=CURRENT_TIMESTAMP where personal_key="%s"' % quote(key.encode('utf-8')))
            cur.execute('update admin_keys set start_time=CURRENT_TIMESTAMP where personal_key="%s"' % quote(key.encode('utf-8')))
        elif action == 4:
            cur.execute('select start_time, avaliable from admin_keys where personal_key="%s"' % (quote(key.encode('utf-8'))))
	    #print cur.fetchone()
	    start_time, avaliable = cur.fetchone()
            log_str = 'start time: %s  avaliable: %s<br><br>' % (str(start_time), str(avaliable))
            cur.execute('select ip, log_time from site_log where personal_key="%s"' % (quote(key.encode('utf-8'))))
            #log_str = ''
            for log in cur.fetchall():
                #print log
                log_str += 'ip: %s&nbsp &nbsp &nbsp &nbsp &nbsptime: %s <br>' % (log[0], log[1])
            return log_str
        else:
            raise Exception('wrong choose')
        return 'success'
    except Exception, e:
        print e
        return 'error'
    finally:
        conn.commit()
        cur.close()
        conn.close()
	try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='0010', db='baidu_info', port=3306)
            cur = conn.cursor()
            cur.execute('insert into manage_log (username, personal_key, movement) values ("%s", "%s", %d);' % (quote(username.encode('utf-8')), quote(key.encode('utf-8')), action))
	    conn.commit()
	    cur.close()
	    conn.close()
	except Exception, e:
	    print e
