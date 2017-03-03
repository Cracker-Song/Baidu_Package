# -*- coding: utf-8 -*-
import json
import requests


def get_info(phone, cookies):
    url = r'http://m.baidu.com/searchbox?action=userx&type=search&service=bdbox&osname=baidubox&data=%%7B%%22content%%22:%%22%s%%22%%7D' % phone
    try:
        respond = requests.get(url, cookies=cookies)
        info_json = json.loads(respond.content)
        name = info_json['data']['userx']['search']['dataset']['display_name']
        return name
    except:
        print 'null'
        return 'not exist'
