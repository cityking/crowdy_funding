from django.shortcuts import render
from .serializers import UserSerializer
from rest_framework.views import APIView
from django.http import Http404
from django.shortcuts import render
#from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from .models import MyUser
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.http import JsonResponse,HttpResponse
from django.forms.models import model_to_dict
from django.db.utils import IntegrityError
from urllib.parse import urljoin
from rest_framework import status
from .forms import UserForm
#from crowdy_funding.project_content.models import get_user_support_items, get_user_item, ItemInfo, get_collections, Comment, Thumb_up, Report, UserPayBack
from crowdy_funding.project_content.models import * 
from crowdy_funding.personal_center.models import * 
from config.myredis import MyRedis
import json
import urllib
import requests
# Create your views here.
from config.tool import certificate, upload_file, authentication, make_password, make_identity, pagination, bankcard_check
from rest_framework import viewsets
from config.PhoneNumberVerificator import PhoneNumberVerificator

def get_user_by_identity(identity):
    user_id = get_user_id_by_identity(identity)
    user = MyUser.objects.get(user_id=user_id)
    return user


@csrf_exempt
@authentication
def support_item(request):
    if request.method == 'POST':
        try:
            data = request.body
            data = data.decode()
            try:
                data = json.loads(data)
            except Exception as e:
                result = {'status':'400', 'message':'json数据解析错误 %s' % data, 'content':'none'}
                return JsonResponse(result, safe=False)


            item_id = data['item_id']
            item = ItemInfo.objects.get(id=item_id)
            item_user = item.initiator
            data['item_user'] = item_user

                
            order = Order.create(data) 
            result = {'status':'200', 'message':'订单生成成功', 'content':'none'}
        except Exception as e:
            print(e)
            result = {'status':'400', 'message':'fail %s' % str(e), 'content':'none'}
        print(result)        
        return JsonResponse(result, safe=False)

    if request.method == 'GET':
        try:
            item_type = request.GET.get('item_type') 
            
            identity = request.GET.get('identity')

#            version = request.GET.get('version')

    #        rds = MyRedis()
    #        rds.set('crowdy_funding_version', version)

            
            #发起的项目
            user = MyUser.get_user_by_identity(identity)
            print("user")
            initiate_items = get_user_item(user, item_type)

            #支持的项目

            support_items = get_user_support_items(user, item_type)

            #项目列表
            if int(item_type):
                items = ItemInfo.objects.filter(item_type=item_type).filter(examination_status='1')
            else:
                items = ItemInfo.objects.all().filter(examination_status='1')

            item_list = []
            for item in items:
                item_list.append(item.get_item_dict())

            content={'initiate_item':initiate_items, 'support_items':support_items, 'item_list':item_list}
            
            result = {'status':'200', 'message':'success', 'content':content}
        except Exception as e:
            print(e)
            result = {'status':'400', 'message':'fail', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

@authentication
@pagination
def get_initiate_items(request):
    if request.method=='GET':
        try:
            status = request.GET.get('status')
            identity = request.GET.get('identity')
            user = MyUser.get_user_by_identity(identity)
            items = get_user_item(user, status)
            result = {'status':'200', 'message':'获取成功', 'content':items}
        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'}
        return JsonResponse(result, safe=False)

@authentication
@pagination
def get_support_items(request):
    if request.method=='GET':
        try:
            identity = request.GET.get('identity')
            user = MyUser.get_user_by_identity(identity)
            item_list = get_user_support_items(user)
            result = {'status':'200', 'message':'获取成功', 'content':item_list}
        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'}
        return JsonResponse(result, safe=False)

       
        
@authentication
def score_rank(request):
    if request.method == 'GET':
        try:
            identity = request.GET.get('identity')
            user = MyUser.get_user_by_identity(identity)            
            rank_type = request.GET.get('rank_type')
            if not rank_type:
                rank_type = 'day'
            content = user.get_rank(rank_type)
            result = {'status':'200', 'message':'success', 'content':content}
        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)
           
@csrf_exempt
@authentication
@pagination
def collection(request):
    if request.method == 'GET':
        try:
            identity = request.GET.get('identity') 
            user = MyUser.get_user_by_identity(identity)
            collections = get_collections(user)      
            result = {'status':'200', 'message':'success', 'content':collections}
        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'}
        print(result) 
        return JsonResponse(result, safe=False)
    elif request.method == 'POST':
        try:
            data = request.body
            data = data.decode()
            data = json.loads(data)
            identity = data['identity']
            item_id = data['item_id']
            collected = int(data['collected'])
            user = MyUser.get_user_by_identity(identity)
            item = ItemInfo.objects.get(pk=item_id)
            if collected:
                item.collect_users.remove(user)
            else:
                item.collect_users.add(user)
            item.save()
            result = {'status':'200', 'message':'success', 'content':'none'}
            
             
        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)
            


@csrf_exempt
@authentication
@pagination
def comment(request):
    if request.method == 'GET':
        try:
            order_id = request.GET.get('order_id')
            order = Order.objects.get(order_id=order_id)
            comments = Comment.objects.filter(order=order).filter(up_comment=None)
            comments = [comment.get_info() for comment in comments]
            
            result = {'status':'200', 'message':'success', 'content':comments}
        except Exception as e:
            print(e)
            result = {'status':'400', 'message':'fail', 'content':'none'}
        print(result) 
        return JsonResponse(result, safe=False)
    elif request.method == 'POST':
        try:
            data = request.body
            data = data.decode()
            data = json.loads(data)
            identity = data['identity']
#            support_user_id = data['support_user_id'] 
            user = MyUser.get_user_by_identity(identity)
            content = data['content']
            
            order_id = data['order_id']
            order = Order.objects.get(order_id=order_id)
            support_user = order.user 
            item_id = order.item_id
            item = ItemInfo.objects.get(pk=item_id)
            
            up_comment_id = data.get('up_comment_id')
            if up_comment_id:
                up_comment = Comment.objects.get(id=up_comment_id)
            else:
                up_comment = None
            comment = Comment.objects.create(order=order, user=user, item=item, support_user=support_user, content=content, up_comment=up_comment)
            comment.save()
            result = {'status':'200', 'message':'success', 'content':'none'}
            
             
        except Exception as e:
            print(e)
            result = {'status':'400', 'message':'fail', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

@authentication
@pagination
def get_user_comment(request):
    if request.method == 'GET':
        try:
            identity = request.GET.get('identity')
            user = MyUser.get_user_by_identity(identity)
            comments = Comment.get_comments(user)
            
            result = {'status':'200', 'message':'success', 'content':comments}
        except Exception as e:
            print(e)
            result = {'status':'400', 'message':'fail', 'content':'none'}
        print(result) 
        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def thumb_up(request):
    if request.method == 'POST':
        try:
            data = request.body
            data = data.decode()
            data = json.loads(data)
            identity = data['identity']
            item_id = data['item_id']
            support_user_id = data['support_user_id']
            support_user = MyUser.objects.get(user_id=support_user_id)
            user = MyUser.get_user_by_identity(identity)
            item = ItemInfo.objects.get(pk=item_id)

            order_id = data['order_id']
            order = Order.objects.get(order_id=order_id)

            thumb = Thumb_up.objects.filter(order=order).filter(user=user)
            if thumb:
                result = {'status':'300', 'message':'该用户已经点赞', 'content':'none'}
            else:
    
                thumb = Thumb_up.objects.create(order=order, user=user, item=item, support_user=support_user)
                thumb.save()
            
                result = {'status':'200', 'message':'success', 'content':'none'}
            
             
        except Exception as e:
            result = {'status':'400', 'message':'fail %s' % str(e), 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)
        
@authentication
def get_consignee(request):
    if request.method=='GET':
        try:
            identity = request.GET.get('identity') 
            user = MyUser.get_user_by_identity(identity)
            consignees = UserConsignee.objects.filter(user=user)
            consignees = [consignee.get_dict() for consignee in consignees] 
            consignees.sort(key=lambda x : x.get('consignee_default'), reverse=True) 
            result = {'status':'200', 'message':'success', 'content':consignees}
        except Exception as e:
            result = {'status':'400', 'message':'fail %s' % str(e), 'content':'none'}
        return JsonResponse(result, safe=False)
@csrf_exempt
@authentication
def add_consignee(request):
     if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            identity = data.get('identity')
            user = MyUser.get_user_by_identity(identity)
            data['user'] = user
            consignee = UserConsignee.create(data)
            result = {'status':'200', 'message':'success', 'content':'none'}
        except Exception as e:
            print(e)
            result = {'status':'400', 'message':'fail %s' % str(e), 'content':'none'}
        return JsonResponse(result, safe=False)

@authentication
def operate_consignee(request):
    if request.method=='GET':
        try:
            data = request.GET.dict()
            consignee_id = data.get('consignee_id') 
            if not consignee_id:
                result = {'status':'400', 'message':'请传入consignee_id', 'content':'none'}
                return JsonResponse(result, safe=False)
            consignee = UserConsignee.objects.get(id=consignee_id)
            method = data.get('method')
            if not method:
                result = {'status':'400', 'message':'请传入method', 'content':'none'}
                return JsonResponse(result, safe=False)
            if method=='get_details':
                data = consignee.get_dict()
                result = {'status':'200', 'message':'success', 'content':data}
            elif method=='delete':
                consignee.delete()
                result = {'status':'200', 'message':'success', 'content':'none'}
            elif method=='set_default':
                user = consignee.user
                try:
                    default_consignee = UserConsignee.objects.filter(user=user).get(consignee_default='1')
                    default_consignee.consignee_default='0'
                    default_consignee.save()
                except Exception as e:
                    pass
                consignee.consignee_default='1'
                consignee.save()
                
                    
                result = {'status':'200', 'message':'success', 'content':'none'}
                pass
            else:
                result = {'status':'400', 'message':'请传入正确的method', 'content':'none'}

        except Exception as e:
            result = {'status':'400', 'message':'fail %s' % str(e), 'content':'none'}
        print(result)            
        return JsonResponse(result, safe=False)
@csrf_exempt
@authentication
def update_consignee(request):
     if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)

            identity = data.get('identity')
            user = MyUser.get_user_by_identity(identity)
            data['user'] = user

            consignee_id = data.get('consignee_id')
            if consignee_id:
                consignee = UserConsignee.objects.get(id=consignee_id)
                consignee.update(data)
                result = {'status':'200', 'message':'success', 'content':'none'}
        except Exception as e:
            print(e)
            result = {'status':'400', 'message':'fail %s' % str(e), 'content':'none'}
        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def report(request):
     if request.method == 'POST':
        try:
            data = request.POST.dict()

            try:
                identity = data.get('identity')
                user = MyUser.get_user_by_identity(identity)
                data['user'] = user
            except Exception:
                result = {'status':'400', 'message':'获取用户信息失败' , 'content':'none'}
                return JsonResponse(result, safe=False)
                

            item_id = data.get('item_id')
            try:
                if item_id:
                    item = ItemInfo.objects.get(id=item_id)
                    data['item'] = item
                else:
                    result = {'status':'400', 'message':'请传入item_id' , 'content':'none'}
                    return JsonResponse(result, safe=False)
            except Exception:
                result = {'status':'400', 'message':'获取项目信息失败' , 'content':'none'}
                return JsonResponse(result, safe=False)

            files = request.FILES.getlist('images')
            bucket_domain = 'http://cdn.hopyun.com/'
            images = []
            if files:
                for _file in files:
                    url = upload_file(_file.file.read(), name=_file.name)
                    url = urljoin(bucket_domain, url)
                    print(url)
                    images.append(url)
                data['images'] = str(images)
            else:
                data['images'] = ''

            report = Report.create(data)
            if report:
                result = {'status':'200', 'message':'举报成功', 'content':'none'}
            else:
                result = {'status':'400', 'message':'举报失败', 'content':'none'}
        except Exception as e:
            print(e)
            result = {'status':'400', 'message':'fail %s' % str(e), 'content':'none'}
        return JsonResponse(result, safe=False)

def get_certification_code(request):
    if request.method == 'GET':
        try:
            phone = request.GET.get('phone')
            use = request.GET.get('use')

            if not phone:
                result = {'status':'400', 'message':'请传入手机号', 'content':'none'}
                return JsonResponse(result, safe=False)
            #获取验证码
            verificator=PhoneNumberVerificator()
            code = verificator.VerificationCode()
            if use == 'certification':
                msg = "你正在进行众筹实名认证，验证码为%s, 5分钟失效" % code
            elif use == 'password':
                msg = "你正在进行密码修改，验证码为%s, 5分钟失效" % code
            elif use == 'register':
                msg = "你正在进行注册，验证码为%s, 5分钟失效" % code
            elif use == 'bind':
                msg = "你正在进行绑定银行卡，验证码为%s, 5分钟失效" % code

            if verificator.phonecheck(phone):
                verificator.send(phone, msg)
                verificator.writeCodeToRedis(code, phone, 300)

            result = {'status':'200', 'content':'none'}
        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'}
        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def certification(request):
    if request.method == 'POST':
        data = request.body.decode()
        data = json.loads(data)
        identity = data['identity']
        user = MyUser.get_user_by_identity(identity)
        phone = data['phone']
        code = data['code']
        verificator=PhoneNumberVerificator()
        if not verificator.CheckVerificationCode(phone, code):
            return JsonResponse({'status':'400', 'message':'验证码错误', 'content':'none'})
        
        #认证
        response = certificate(data)
        if response['code'] == 0:
            user.real_name = data['name']
            user.mobile = data['phone']
            user.id_card = data['cardno']
            user.certification = '1'
            user.save()
            result = {'status':'200', 'message':'认证成功', 'content':'none'}
        else:
            result = {'status':'400', 'message':response['msg'], 'content':'none'}

        return JsonResponse(result, safe=False)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            phone = data['phone']
            code = data['code']
            password = data['password']
            password_again = data['password_again']
            verificator=PhoneNumberVerificator()
            if not verificator.CheckVerificationCode(phone, code):
                return JsonResponse({'status':'400', 'message':'验证码错误', 'content':'none'})
            if not verificator.phonecheck(phone):
                return JsonResponse({'status':'400', 'message':'输入的手机号码有误', 'content':'none'})
            if password != password_again:
                return JsonResponse({'status':'400', 'message':'两次输入的密码不一样', 'content':'none'})
            try:
                user = MyUser.objects.create(mobile=phone,
                    password=make_password(password),
                    nick_name=phone)
            except IntegrityError:
                return JsonResponse({'status':'400', 'message':'手机号已经被注册', 'content':'none'})
            user.save()
            result = {'status':'200', 'message':'注册成功,请返回登录', 'content':'none'}
        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)
@csrf_exempt
def update_user_password(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            phone = data['phone']
            code = data['code']
            password = data['password']
            password_again = data['password_again']
            verificator=PhoneNumberVerificator()
            user = MyUser.objects.filter(mobile=phone)
            if not user:
                return JsonResponse({'status':'400', 'message':'该用户不存在', 'content':'none'})

            if not verificator.CheckVerificationCode(phone, code):
                return JsonResponse({'status':'400', 'message':'验证码错误', 'content':'none'})
            if password != password_again:
                return JsonResponse({'status':'400', 'message':'两次输入的密码不一样', 'content':'none'})
            user = user[0]
            user.password = make_password(password)
            user.save()
            result = {'status':'200', 'message':'修改成功, 请返回登录', 'content':'none'}
        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)



        
@authentication
def get_user_info(request):
    if request.method == 'GET':
        try:
            identity = request.GET.get('identity') 
            user = MyUser.get_user_by_identity(identity)
            info = user.get_info()
            result = {'status':'200', 'content':info}
        except Exception as e:
            result = {'status':'400', 'message':'fail %s' % str(e)}
        print(result)
        return JsonResponse(result, safe=False)
        
@csrf_exempt
@authentication
def update_user_info(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            identity = data['identity']
            user = MyUser.get_user_by_identity(identity)
            nick_name = data.get('nick_name')
            if nick_name:
                user.nick_name = nick_name
            about_me = data.get('about_me')
            if about_me:
                user.about_me = about_me
            address = data.get('address')
            if address:
                user.address = address
            user.save()
            result = {'status':'200', 'message':'修改成功'}
        except Exception as e:
            result = {'status':'400', 'message':'fail %s' % str(e)}
        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def update_user_avatar(request):
    if request.method == 'POST':
        try:
            data = request.POST.dict()
            identity = data['identity']
            user = MyUser.get_user_by_identity(identity)

            try: 
                images = []
                files = request.FILES.getlist('avatar')
                bucket_domain = 'http://cdn.hopyun.com/'
                if files:
                    for image in files:
                        url = upload_file(image.file.read())
                        url = urljoin(bucket_domain, url)
                        user.avatar_url = url
            except Exception as e:
                result = {'status':'400', 'message':'上传图片失败 %s' % str(e), 'content':'none'}
                return JsonResponse(result, safe=False) 

            user.save()
            result = {'status':'200', 'message':'修改成功'}
        except Exception as e:
            result = {'status':'400', 'message':'fail %s' % str(e)}
        return JsonResponse(result, safe=False)

def webchat_login(identity):
    url = "http://120.77.237.80/crowdy/get_user_by_identity?identity=%s" % identity
    response = requests.get(url).json()
    if response['status'] == '200':
        info = response['content']
        openid = info['openid']
        user = MyUser.objects.filter(openid=openid)
        redis = MyRedis()
        key = 'identity' + identity
        if user:
            user = user[0]
        else:
            user = MyUser.create_weixin_login(info)
        redis.set(key, user.id)
        redis.expire(key, 7200)
        return user
    else:
        return None

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)

            identity = data.get('identity')
            if identity:
                user = webchat_login(identity)        
                if user:
                    result = {'status':'200', 'message':'登录成功', 'content':data}
            else:
                mobile = data.get('mobile')
                password = data.get('password')
                identity = MyUser.create_moblie_login(mobile, password)
                
                if identity == '0':
                    result = {'status':'400', 'message':'密码错误'}
                elif identity == '1':
                    result = {'status':'400', 'message':'用户不存在'}
                else:
                    data = {'identity':identity}
                    result = {'status':'200', 'message':'登录成功', 'content':data}
                 
        except Exception as e:
            result = {'status':'400', 'message':'fail %s' % str(e)}
        return JsonResponse(result, safe=False)

@authentication
@pagination
def get_order_list(request):
    if request.method=='GET': 
        try:
            identity = request.GET.get('identity')
            user = MyUser.get_user_by_identity(identity)
            payback_list = UserPayBack.get_paybacks_by_user(user)
            result = {'status':'200', 'message':'获取成功', 'content':payback_list}
        except Exception as e:
            result = {'status':'400', 'message':'fail %s' % str(e)}
        return JsonResponse(result, safe=False)

@authentication
def get_order_detail(request):
    if request.method=='GET': 
        try:
            payback_id = request.GET.get('payback_id')
            payback = UserPayBack.objects.get(id=payback_id)
            info = payback.get_order_detail()
            result = {'status':'200', 'message':'获取成功', 'content':info}
        except Exception as e:
            result = {'status':'400', 'message':'fail %s' % str(e)}
        return JsonResponse(result, safe=False)

@authentication
def delete_order(request):
    if request.method=='GET': 
        try:
            payback_id = request.GET.get('payback_id')
            payback = UserPayBack.objects.get(id=payback_id)
            payback.delete_status = '1'
            
            payback.save()
            
            result = {'status':'200', 'message':'删除成功', 'content':'none'}
        except Exception as e:
            result = {'status':'400', 'message':'fail %s' % str(e)}
        return JsonResponse(result, safe=False)

def get_bank_list(request):
    if request.method=='GET':
        try:
            bank_list = Bank.get_list() 
            result = {'status':'200', 'message':'获取成功', 'content':bank_list}
        except Exception as e:
            result = {'status':'400', 'message':'fail %s' % str(e)}
        return JsonResponse(result, safe=False)
                
@csrf_exempt
@authentication
def bind_bankcard(request):                
    if request.method == 'POST':
        data = request.body.decode()
        data = json.loads(data)
        identity = data['identity']
        user = MyUser.get_user_by_identity(identity)

        bank_id = data['bank_id']
        bank = Bank.objects.get(id=bank_id)
        data['bank'] = bank

        phone = data['phone']
       
        #绑定
        response = bankcard_check(data)
        if response['code'] == 0:
            bank = response['data']['bankname']
            if bank in data['bank'].name:
                bankcard = BankCardInfo.create(data)
                user.banks.add(bankcard)
                user.save()
                result = {'status':'200', 'message':'绑卡成功', 'content':'none'}
            else:
                result = {'status':'400', 'message':'银行信息不一致', 'content':'none'}
        else:
            result = {'status':'400', 'message':response['msg'], 'content':'none'}

        return JsonResponse(result, safe=False)

   
@authentication
def get_bindcards(request):
    if request.method=='GET':
        try:
            identity = request.GET.get('identity')
            user = MyUser.get_user_by_identity(identity)
            banks = user.get_banks_list()
            result = {'status':'200', 'message':'获取成功', 'content':banks}
        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'}
        return JsonResponse(result, safe=False)
        
@authentication
def unbind_bindcard(request):
    if request.method=='GET':
        try:
            identity = request.GET.get('identity')
            user = MyUser.get_user_by_identity(identity)

            bankcardinfo_id = request.GET.get('bankcardinfo_id')
            bank = BankCardInfo.objects.get(id=bankcardinfo_id)
            
            user.banks.remove(bank)
            bank.delete()
            
            result = {'status':'200', 'message':'解绑成功', 'content':'none'}
        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'}
        return JsonResponse(result, safe=False)
            
@authentication
def get_balance(request):
    if request.method=='GET':
        try:
            identity = request.GET.get('identity')
            user = MyUser.get_user_by_identity(identity)
            balance = user.balance
            content = dict(balance=balance)
            result = {'status':'200', 'message':'获取成功', 'content':content}
        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'}
        return JsonResponse(result, safe=False)
 
@csrf_exempt
def apply_cash(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)

            record = TradeRecord.apply_cash(data)
            result = {'status':'200', 'message':'申请提现成功，请等待后台处理', 'content':'none'}
                
                 
        except Exception as e:
            result = {'status':'400', 'message':'fail %s' % str(e)}
        print(result)
        return JsonResponse(result, safe=False)


