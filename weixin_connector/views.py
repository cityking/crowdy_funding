from django.shortcuts import render
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect
from config.myredis import MyRedis
import hashlib
import requests
import json
# Create your views here.
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
   

def get_webchat_info(request):
    if request.method == "GET":
        try:
            AppSecret = '46e2fe9c5ece4f8606b604c66147e513'
            AppID = 'wx0ef97e264e05810f'
            code = request.GET.get('code')
            print('code',code)
            token_url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" % (AppID, AppSecret, code)
            data = requests.get(token_url).json()

            data = get_user_info(data)
            redis = MyRedis()
            key = 'identity' + code
            redis.set(key, str(data))
            redis.expire(key, 7200)
            data = {'identity':code}
            result = {'status':'200', 'message':'获取成功', 'content':data}
            url = "http://192.168.3.164:8085/#/auth_user?identity=%s" % code
            return HttpResponseRedirect(url)
        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'}
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
        


