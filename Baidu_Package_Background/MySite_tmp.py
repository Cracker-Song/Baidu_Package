# -*- coding: utf-8 -*-
from flask import Flask,request,render_template
app = Flask(__name__)
@app.route('/<string:key1>')
@app.route('/<string:key1>/<string:key2>')
@app.route('/<string:key1>/<string:key2>/<string:key3>')
@app.route('/<string:key1>/<string:key2>/<string:key3>/<string:key4>')
def tmp_page(key1, key2=0, key3=0, key4=0):
    return '更新中'
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)#, debug=True)
