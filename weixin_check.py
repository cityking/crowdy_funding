# 过微信验证
def check_wechat(req):
    if req.method == 'GET':
        # 3个计算信息
        token = 'tradebook'
        timestamp = req.GET['timestamp']
        nonce = req.GET['nonce']
        # 返回值和对比值
        echostr = req.GET['echostr']
        signature = req.GET['signature']
        # 排序
        list = [token, timestamp, nonce]
        list.sort()
        # sha1加密
        check_str = ''.join(list)
        hashcode = hashlib.sha1(check_str.encode()).hexdigest()

        if hashcode == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse('..')


# 获取js-sdk-info
def get_wx_info(req):
    url = req.GET
    info = wx_info(url)['url']
    return JsonResponse(info, safe=False)

# 过验证
url(r'^check_wechat', views.check_wechat),
# js-sdk接口
url(r'^get_wx_info', views.get_wx_info),
# 网页验证
url(r'^MP_verify_gGJ9da08SchMn5n3.txt', views.check),
