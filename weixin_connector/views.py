from django.shortcuts import render
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect
from config.myredis import MyRedis
from config.tool import *

import hashlib
import requests
import string
import time
import json
import random
# Create your views here.

redis = MyRedis()
AppSecret = '46e2fe9c5ece4f8606b604c66147e513'
AppID = 'wx0ef97e264e05810f'

def check_webchat(req):
    if req.method=='GET':
        signature = req.GET['signature']
        timestamp = req.GET['timestamp']
        nonce = req.GET['nonce']
        echostr = req.GET['echostr']
        token = "tradebook" #请按照公众平台官网\基本配置中信息填写

        list = [token, timestamp, nonce]
        list.sort()
        sha1 = hashlib.sha1()
        map(sha1.update, list)
        hashcode = sha1.hexdigest()
        print("handle/GET func: hashcode, signature: ", hashcode, signature)
        if hashcode == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse('..')
def get_user_info(data):
    info_url = "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN" % (data['access_token'], data['openid'])
    print(info_url)
    data = requests.get(info_url)
    data = data.text.encode('raw_unicode_escape')
    data = data.decode()
    data = json.loads(data)
    print(data)
    return data

def get_token(data):
    identity = data.get('identity')
    appid = data.get('appid')
    if identity:
        token_key = 'access_token' +identity 
        token_data = redis.get(token_key)
        refresh_token_key = 'refresh_token' + identity
        if not token_data:
            refresh_token = redis.get(refresh_token_key)
            url = "https://api.weixin.qq.com/sns/oauth2/refresh_token?appid=%s&grant_type=refresh_token&refresh_token=%s" %(appid, refresh_token)
            data = requests.get(url).json()
        else:
            data = eval(token_data)

    else:
        appsecret = data.get('appsecret')
        code = data.get('code')
        url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" % (appid, appsecret, code)
        data = requests.get(url).json()
        token_key = 'access_token' + code
        refresh_token_key = 'refresh_token' + code

        redis.set(token_key, str(data))
        redis.expire(token_key, 7000)

        redis.set(refresh_token_key, data.get('refresh_token'))
        redis.expire(refresh_token_key, 3600*24)

    return data


def get_credential_token():
    key = 'credential_token'
    access_token = redis.get(key)
    if not access_token:
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(AppID,AppSecret)
        info = requests.get(url=url).json()
        access_token = info['access_token']
        redis.set(key, access_token)
        redis.expire(key, 7100)
    return access_token
# 获取js-sdk-ticket
def get_ticket():
    key = 'jsapi_ticket'
    ticket = redis.get(key)
    if not ticket:    
        access_token = get_credential_token()
        url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi" % access_token
        data = requests.get(url).json()
        if not data.get('ticket', None):
            raise ValueError("missing parameter ticket")
        # 因为ticket调用有上限，需存入redis
        ticket = data['ticket']
        redis.set(key, ticket)
        redis.expire(key, 7180)
    return ticket
#字典序排序
def map_(params):
    sorted_key = sorted(params.keys())
    key_value = (key + '=' + params[key] + '&' for key in sorted_key)
    _string = ''.join(key_value)[:-1]
    return _string

# sha1加密
def get_sha1(default):
    md = hashlib.sha1()
    md.update(default.encode())
    return md.hexdigest()

def get_signature(noncestr, jsapi_ticket, timestamp, url):
    data = dict(noncestr=noncestr,
            jsapi_ticket=jsapi_ticket,
            timestamp=timestamp,
            url=url)
    data = map_(data)
    return get_sha1(data)

   
def get_verification_data(request):
    if request.method == "GET":
        try:
            data = request.GET.dict()
            url = data.get('url')
            
            identity = data.get('identity')
            params = dict(identity=identity,
                    appid=AppID)

            token_data = get_token(params) 
            access_token = token_data.get('access_token')
            jsapi_ticket = get_ticket()
            timestamp = str(int(time.time()))

            char = string.ascii_letters + string.digits
            nonceStr =  "".join(random.choice(char) for _ in range(32))

            signature = get_signature(nonceStr, jsapi_ticket, timestamp, url)

            content = dict(appId=AppID,
                    timestamp=timestamp,
                    nonceStr=nonceStr,
                    signature=signature)
            
            result = {'status':'200', 'message':'获取成功', 'content':content}
            return JsonResponse(result) 
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
            return JsonResponse(result) 
def get_webchat_info(request):
    if request.method == "GET":
        try:
            code = request.GET.get('code')
            state = request.GET.get('state')
            if state == 'pc':
                appid = 'wx805a822a3bb34203'
                appsecret = '4b359a34355661f32d4870a823082848'
                params = dict(appsecret=appsecret,
                    appid=appid,
                    code=code)
            else:
                params = dict(appsecret=AppSecret,
                    appid=AppID,
                    code=code)

           
            data = get_token(params)
            data = get_user_info(data)

            key = 'identity' + code
            redis.set(key, str(data))
            redis.expire(key, 300)
    
            data = {'identity':code}
            result = {'status':'200', 'message':'获取成功', 'content':data}
            if state == 'pc':
#                url = 'http://xin.long:3000/inject?identity=%s' % code
                url = 'http://gf.globalleague.cn/inject?identity=%s' % code
            else:
                url = "http://cf.globalleague.cn/crowdy_webchat_html5/#/auth_user?identity=%s" % code
            return HttpResponseRedirect(url)
        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'}
            print(result)
            return JsonResponse(result) 
#        return HttpResponseRedirect('http://www.baidu.com')

def get_user_by_identity(request):
    if request.method == 'GET':
        try: 
            identity = request.GET.get('identity')
            key = 'identity' + identity
            redis = MyRedis()
            data = redis.get(key)
            data = eval(data)
            result = {'status':'200', 'message':'获取成功', 'content':data}
        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'}
        return JsonResponse(result)
        


