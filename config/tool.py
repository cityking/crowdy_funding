import urllib
import uuid
import json
import requests
import random
import time
import re
import os
from dateutil import tz  
from datetime import datetime, timedelta
from qiniu import Auth, put_data, BucketManager, put_file
from qiniu import PersistentFop, build_op, op_save, urlsafe_base64_encode
#from config.myredis import MyRedis
from .myredis import MyRedis
from .log import logger
import hashlib
from urllib.parse import urljoin
from django.http import JsonResponse
import traceback
trade_url = 'http://192.168.3.37:8000'
#trade_url = 'http://120.76.137.157:47623'
#version = '3.6.2'

access_key = 'nh_CyPoBjC5iVIfNVZJDz3WBErnvJoTunIptd_4U'
secret_key = 'UL48VV2STK3CnCblGhyZeUUydrN6Idfd-EMKa3Xm'
bucket_name = 'qql-vshop'
bucket_domain = 'http://cdn.hopyun.com/'

apix_key = '20d5b90afa61493259b85ddc66b9fd17'
redis = MyRedis()

def make_password(data):
    data = data.encode()
    m = hashlib.md5()
    m.update(data)
    psw = m.hexdigest()
    return psw

def make_identity(mobile, user):
    identity = make_password(mobile+'%.2f' % random.random())
    redis = MyRedis()
    key = 'identity_user' + identity 
    redis.set(key, user.id)
    redis.expire(key, 3600*24)
    return identity
def make_admin_identity(nick_name, adminastrator):
    identity = make_password(nick_name+'%.2f' % random.random())
    redis = MyRedis()
    key = 'identity' + identity 
    value = 'admin%s' % adminastrator.nick_name
    redis.set(key, value)
    redis.expire(key, 3600*24)
    return identity

def log_exception():
    logger.info(traceback.format_exc())
    print('traceback.format_exc():\n%s' % traceback.format_exc())


#def get_user_identity(identity):
#    user_id = redis.get(identity) 
#    if user_id:
#        user = MyUser.objects.get(id=user_id)
#        if user:
#            return user
#        else:
#            return None
#    else:
#         return None
def authentication(fun):
    def wrapper(request):
        identity = None
        if request.method == 'GET':
            identity = request.GET.get('identity')
            
        elif request.method == 'POST':
            identity = request.POST.get('identity')
            if not identity:
                try:
                    data = request.body
                    data = json.loads(data.decode())
                    identity = data.get('identity')
                except:
                    identity = None
        if identity:
            key = 'identity_user' + identity
            user_id = redis.get(key)
            
            if not user_id:
                result = {'status':'301', 'message':'identity过期，请重新登录'}
                print(result)
                return JsonResponse(result)
            redis.expire(key, 3600*24)
        else:
            result = {'status':'300', 'message':'未登录'}
            print(result)
            return JsonResponse(result)
        response = fun(request)
        return response

    return wrapper
def admin_authentication(fun):
    def wrapper(request):
        identity = None
        if request.method == 'GET':
            identity = request.GET.get('identity')
            
        elif request.method == 'POST':
            identity = request.POST.get('identity')
            if not identity:
                try:
                    data = request.body
                    data = json.loads(data.decode())
                    identity = data.get('identity')
                except:
                    identity = None
        if identity:
            key = 'identity' + identity
            value = redis.get(key)
            
            if not value:
                result = {'status':'400', 'message':'identity过期，请重新登录'}
                return JsonResponse(result)
            else:
                if re.match('admin.*', value):
                    redis.expire(key, 3600*24)
                else:
                    result = {'status':'300', 'message':'未登录'}
                    return JsonResponse(result)
        else:
            result = {'status':'300', 'message':'未登录'}
            return JsonResponse(result)
        response = fun(request)
        return response

    return wrapper

def pagination(fun):
    def wrapper(request):
        if request.method == 'GET':
            page_no = request.GET.get('page_no')
            page_count = request.GET.get('page_count')
            response = fun(request)
            data = response.content
            data = data.decode()
            data = json.loads(data)
            content = data.get('content')
            if content and content != 'none':
                length = len(content)
                if not page_no:
                    page_no = 1
                else:
                    page_no = int(page_no)
                if not page_count:
                    page_count = 5
                else:
                    page_count = int(page_count)

                pages = length/page_count
                if length % page_count:
                    pages += 1
       
                start = (page_no-1)*page_count
                if page_no == int(pages):
                    end = length 
                else:
                    end = page_no*page_count

                if page_no > pages:
                    content = []
                else:
                    content = content[start:end]
                data['content'] = content
                data['length'] = length
                return JsonResponse(data)
            else:
                data['length'] = 0
                return JsonResponse(data)
        else:
            return fun(request)

    return wrapper


 
def trans_to_localtime(utc_time):
    # UTC Zone  
    from_zone = tz.gettz('UTC')  
    # China Zone  
    to_zone = tz.gettz('CST')  
      
      
    # Tell the datetime object that it's in UTC time zone  
    utc = utc_time.replace(tzinfo=from_zone)  
      
    # Convert time zone  
    local = utc.astimezone(to_zone)  
    return local

def ndays_time(days):
    now = datetime.now()
    delta = timedelta(days=days)
    n_days = now + delta
    return n_days
def get_upload_token():
    auth = Auth(access_key, secret_key)
    upload_token = auth.upload_token(bucket_name)
    return upload_token

def upload_file(data, header='', name=''):
    """
    upload file(byte) to qiuniu
    :param data: file(byte)
    :param header: file name header
    :return:url (not bucket_domain)
    """
    try:
        if name:
            tail = '.' + name.split('.')[-1]
        else:
            tail = '.' + data.name.split('.')[-1]
    except Exception:
        tail = ''
   
    filename = str(header) + str(uuid.uuid1()) + tail
    auth = Auth(access_key, secret_key)
    print(filename)
    policy = {
        "deadline":int(time.time()+3600),
     }
    upload_token = auth.upload_token(bucket_name, filename, 3600, policy)

    with open(filename, 'wb') as temp_file:
        temp_file.write(data)

    ret, info = put_file(upload_token, filename, filename)

    

    #ret, info = put_data(upload_token, filename, data)

    if info.status_code == 200:
        file_url = filename
        os.remove(filename)
        return file_url
    else:
        raise False

def del_uploaded(filename):
    auth = Auth(access_key, secret_key)
    bucket = BucketManager(auth)
    ret, info = bucket.delete(bucket_name, filename)
    print(info)

def get_uploaded(filename):
    auth = Auth(access_key, secret_key)
    bucket = BucketManager(auth)
    ret, info = bucket.stat(bucket_name, filename)
    if info:
        info = eval(info.text_body)
        return info
    else:
        return 0

def is_img_or_video(url):
    print(url)
    if url:
        key = url.split('/')[-1]
        info = get_uploaded(key)
    if info:
        mimeType = info.get('mimeType')
        is_img = False
        is_video = False
        if mimeType:
            if re.match('^image/.*', mimeType):
                is_img = True
            elif re.match('^video/.*', mimeType):
                is_video = True
        data = dict(is_img=is_img,
                is_video=is_video)
    else:
        data = dict(is_img=False,
                    is_video=False)
    return data    
def get_screenshot(url):
    try:
        key = url.split('/')[-1]
        auth = Auth(access_key, secret_key)
        
        #截图使用的队列名称。
        pipeline = 'mpsdemo'
        
        #要进行的截图操作。
        fops = 'vframe/jpg/offset/1/w/480/h/360/rotate/90'
        
        #可以对截取后的图片进行使用saveas参数自定义命名，当然也可以不指定文件会默认命名并保存在当前空间
        file_name = key.split('.')[0] + '.jpg'
        saveas_key = urlsafe_base64_encode('%s:%s' % (bucket_name,file_name))
        fops = fops+'|saveas/'+saveas_key
        
#        pfop = PersistentFop(auth, bucket_name, pipeline)
        pfop = PersistentFop(auth, bucket_name)
        ops = []
        ops.append(fops)
        ret, info = pfop.execute(key, ops, 1)
        print(info)
        assert ret['persistentId'] is not None
    except:
        return None
    return urljoin(bucket_domain, file_name)





#实名认证
def certificate(data):
#    url = "http://v.apix.cn/apixcredit/idcheck/mobile"
    url = "http://v.apix.cn/apixcredit/idcheck/idcard"

    cardno = data['cardno']
    name = data['name']
    phone = data['phone']
    
    querystring = {"type":"idcard","cardno":cardno,"name":name, "phone":phone}
    
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'apix-key': apix_key 
        }
    
    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.text)
    return response.json()

def bankcard_check(data):
    url = "http://v.apix.cn/apixcredit/idcheck/bankcard"

    check_type = 'bankcard_four' 
    bankcardno = data.get('card_no')
    name = data.get('name')
    idcardno = data.get('id_no')
    phone = data.get('phone')
    querystring = {"type":check_type,"bankcardno":bankcardno,"name":name,"idcardno":idcardno,"phone":phone}
    
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'apix-key': apix_key 
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    
    print(response.text)
    return response.json()
if __name__ == "__main__":
    del_uploaded('3c21ac0c-ea28-11e7-b32f-9cf387d3f78e.jpg')
#    get_uploaded('citykingfile.jpg')
#    is_img_or_video('http://cdn.hopyun.com/48686626-e0a3-11e7-92b5-9cf387d3f78e.MOV')
#    file_name = get_screenshot('c8d06918-e0a4-11e7-8b93-9cf387d3f78e.MOV')
#    file_name = '/Users/cityking/WechatIMG24.jpeg'
#    with open(file_name, 'rb') as data:
#        print(data.name)
#        url = upload_file(data.read())
#        print(url)

