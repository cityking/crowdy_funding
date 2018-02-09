import requests
import json
import os, random, sys, requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

identity = '5b4c20ff0980f9fdbef9bc0694506e97'
base_url = 'http://192.168.123.100:8000'
def get_user_info():
    data = {
        'unionid': 'oOtoNwlr6enlnJ7zoFZUAaniI2SA',
        'access_token': 'JFuUUo_WTwapJm4CF36piJZcFd7gbmiyYP5JucprbHdHKSh5QjfwyFcjcL6CSmosPrRUOCMn0D40D3cTyf7nNMGnMsEaNcmTlk-9mYFRH4k',
        'scope': 'snsapi_base',
        'expires_in': 7200,
        'openid': 'ooqo9049VvzMKCifxXPGHc3_s0sM',
        'refresh_token': 'euGi8_rnp4XucwrQH6vFqS0Inz1vPmT0rRp2nVUq4BuTyBGLNHZpiAMrsKhYRxR6tlUHEz_p17KJzl1P00sryR9Q3FK4LokdCDUFTlyHJyQ'
        }
    info_url = "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN" % (data['access_token'], data['openid'])
    print(info_url)
    data = requests.get(info_url)
    data = data.text.encode('raw_unicode_escape')
    data = data.decode()
    data = json.loads(data)
    print(data)
def add_consignee():
    url = 'http://192.168.3.59:8000/personal_center/add_consignee'
    data = dict(identity='123444',
            consignee_name='hhjjj',
            consignee_phone='12345673453',
            consignee_address='hjjkkdsfhhgkjakahfjkfjks') 
    print(data)
    response = requests.post(url, json=data)
    print(response.json())
def report():
    url = 'http://192.168.3.59:8000/personal_center/report'
    data = dict(identity='123444',
            item_id='4',
            reason='虚假信息',
            images='["http://hhjk.com"]') 
    print(data)
    response = requests.post(url, data=data)
    print(response.json())
def cetification():
    url = 'http://192.168.3.59:8000/personal_center/certificate'
    data = dict(identity='123444',
            cardno='511381198901065410',
            code='4379',
            name='王城',
            phone='18221339272')
    response = requests.post(url, json=data)
    print(response.json())
def update_user_info():
    url = 'http://192.168.3.59:8000/personal_center/update_user_info'
    data = dict(identity='123444',nick_name='cityking')
    response = requests.post(url, json=data)
    print(response.json())

def register(code):
    url = 'http://192.168.3.59:8000/personal_center/register' 
    data = dict(phone = '18221339272',
            code=code,
            password='ct065410',
            password_again='ct065410')
    response = requests.post(url, json=data)
    print(response.json())
def update_password(code):
    url = 'http://192.168.3.59:8000/personal_center/update_password' 
    data = dict(phone = '18221339272',
            code=code,
            password='ct989016',
            password_again='ct989016')
    response = requests.post(url, json=data)
    print(response.json())

def login():
    url = '%s/personal_center/login' % base_url
    data = dict(identity='011ZkoOI0NiS9i2LNaOI0mA9OI0ZkoOy')
#    data = dict(mobile='18321339272', password='ct989016') 
    response = requests.post(url, json=data)
    print(response.json())
def login_by_code():
    url = '%s/personal_center/login_by_code' % base_url
    data = dict(phone='18221339272', code='3864') 
    response = requests.post(url, json=data)
    print(response.json())

def admin_login():
    url = 'http://192.168.3.59:8000/item/admin_login'
    data = dict(nick_name='cityking', password='123456') 
    response = requests.post(url, json=data)
    print(response.json())
def add_adminastrator():
    url = 'http://192.168.3.59:8000/item/add_adminastrator'
    data = dict(nick_name='cityking000', password='123456', password_repeat='123456', identity='7de10ddcc54b92376bb77dd61f4b27cb') 
    response = requests.post(url, json=data)
    print(response.json())
def collect():
    url = 'http://192.168.3.59:8000/personal_center/collect_item'
    data = dict(identity='0016gv1N1JKGX51ZOH1N1vGM1N16gv1B',
            item_id=4,
            collected=0,)
    response = requests.post(url, json=data)
    print(response.json())

def bindcard():
    url = 'http://192.168.3.59:8000/personal_center/bind_bankcard'
    data = dict(identity='021IMcbc2M2N9Q0xVcbc2lTgbc2IMcb8',
            id_no='511381198901065410',
            card_no='6228480038166309971',
            bank='中国农业银行',
            code='1078',
            name='王城',
            phone='18221339272')
    response = requests.post(url, json=data)
    print(response.json())

def bankcard_info():
    apix_key = '20d5b90afa61493259b85ddc66b9fd17'

    url = "http://e.apix.cn/apixcredit/bankcardinfo/bankcardinfo"
    
    querystring = {"cardno":"6228480038166309971"}
    
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'apix-key': apix_key
        }
    
    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)

def update_item():
    url = 'http://192.168.3.59:8000/item/update_initiate' 
    data = {"item_id":"6",
    "identity":"081hINsF16Rpa10GRZuF19yYsF1hINsW",
    "item_type":"1", 
    "objective_money":"3000",
    "item_name":"救助山区儿童",
    "item_content":"WebGL 本质上是基于光栅化的 API，而不是基于 3D 的 API。WebGL 只关注两个方面，即投影矩阵的坐标和投影矩阵的颜色。使用 WebGL 程序的任务就是实现具有投影矩阵坐标和颜色的 WebGL 对象即可。可以使用“着色器”来完成上述任务。顶点着色器可以提供投影矩阵的坐标，片段着色器可以提供投影矩阵的颜色。",
    "is_reback":"0",
    "fund_use":"WebGL 本质上是基于光栅化的 API，而不是基于 3D 的 API。WebGL 只关注两个方面，即投影矩阵的坐标和投影矩阵的颜色。使用 WebGL 程序的任务就是实现具有投影矩阵坐标和颜色的 WebGL 对象即可。可以使用“着色器”来完成上述任务。顶点着色器可以提供投影矩阵的坐标，片段着色器可以提供投影矩阵的颜色。",
    "last_time":"60"
    }
    response = requests.post(url, data=data)
    print(response.json())
def update_item_status():
    url = 'http://192.168.3.59:8000/admin/update_item_status' 
    data = {"item_id":"6",
    "identity":"a09781ee34c418ab968b367dce048432",
    "status":"0",
    }
    response = requests.post(url, json=data)
    print(response.json())
def upload_file(file_name):
    url = 'http://192.168.123.186:8000/item/upload_file'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0',
        'Referer': url
        }
    multipart_encoder = MultipartEncoder(
        fields={
            'files': (os.path.basename(file_name) , open(file_name, 'rb'), 'application/octet-stream')
            #file为路径
            },
            boundary='-----------------------------' + str(random.randint(1e28, 1e29 - 1))
        )
    
    headers['Content-Type'] = multipart_encoder.content_type
    #请求头必须包含一个特殊的头信息，类似于Content-Type: multipart/form-data; boundary=${bound}
    
    r = requests.post(url, data=multipart_encoder, headers=headers)
    print(r.text)
def support_item():
    url = 'http://192.168.3.59:8000/personal_center/support_item'
    data = {
   "identity":"081hINsF16Rpa10GRZuF19yYsF1hINsW",
   "support_money":200,
   'item_id':6,
   'payback':'0',
    }
    response = requests.post(url, json=data)
    print(response.json())
def add_announce():
    url = 'http://192.168.3.59:8000/admin/add_announcement' 
    data = {"title":"公告",
    "identity":identity,
    "content":"公告内容", 
    }
    response = requests.post(url, json=data)
    print(response.json())
def update_announce():
    url = 'http://192.168.3.59:8000/admin/update_announcement' 
    data = {"title":"公告",
    "identity":identity,
    "announce_id":'1',
    "content":"公告内容", 
    }
    response = requests.post(url, json=data)
    print(response.json())
def delete_announce():
    url = 'http://192.168.3.59:8000/admin/del_announcement' 
    data = {"identity":identity,
    "announce_id":'1',
    }
    response = requests.post(url, json=data)
    print(response.json())
def delete_item_type():
    url = 'http://192.168.3.59:8000/admin/del_item_type'
    data = dict(identity=identity,
            type_id=1)
    response = requests.post(url, json=data)
    print(response.json())
   
def admin_update_item():
    url = 'http://192.168.3.59:8000/admin/update_item' 
    data = {"item_id":"4",
    "identity":identity,
    "item_type":"1", 
    "objective_money":"4000",
    "item_name":"项目名称",
    "item_content":"使用 WebGL 程序的任务就是实现具有投影矩阵坐标和颜色的 WebGL 对象即可。可以使用“着色器”来完成上述任务。顶点着色器可以提供投影矩阵的坐标，片段着色器可以提供投影矩阵的颜色。",
    "is_reback":"0",
    "fund_use":"可以使用“着色器”来完成上述任务。顶点着色器可以提供投影矩阵的坐标，片段着色器可以提供投影矩阵的颜色。",
    "last_time":"30"
    }
    response = requests.post(url, data=data)
    print(response.json())



#get_user_info()
#add_consignee()
#report()
#cetification()
#update_user_info()
#login()
login_by_code()
#collect()
#register('8413')
#update_password('3820')
#bankcard_info()
#update_item()
#support_item()
#admin_login()
#add_adminastrator()
#update_item_status()
#add_announce()
#update_announce()
#delete_announce()
#delete_item_type()
#admin_update_item()
#upload_file('mm.jpg')
