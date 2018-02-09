"""crowdy_funding URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from rest_framework import routers
from django.contrib import admin
from django.views import static
from django.conf import settings
#from crowdy_funding.personal_center.views import support_item, score_rank, collection, comment, thumb_up, get_consignee, add_consignee, operate_consignee, update_consignee, report, get_user_info, certification, update_user_info, update_user_avatar, login, get_certification_code, get_initiate_items, get_support_items, register, update_password, get_user_comment
from crowdy_funding.personal_center.views import * 
#from crowdy_funding.project_content.views import item_initiate, item_detail, item_list, item_bref_detail, operate, update_item,index, get_item_type, filter_items, get_item_comments, item_management, get_payback_detail
from crowdy_funding.project_content.views import * 
from admin_project.views import *
from weixin_connector.views import check_webchat, get_webchat_info, get_user_by_identity, get_verification_data 

#router = routers.DefaultRouter()
#router.register(r'users', UserViewSet)

#urlpatterns = [
#    url(r'^', include(router.urls)),
#    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
#]

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^media_root/(?P<path>.*)$', static.serve, {'document_root':settings.MEDIA_ROOT}),

    #微信接口
    url(r'^check_webchat', check_webchat),
#    url(r'^get_webchat_info', get_webchat_info),
    url(r'^crowdy/get_webchat_info', get_webchat_info),
    url(r'^crowdy/get_user_by_identity', get_user_by_identity),
    url(r'^crowdy/get_verification_data', get_verification_data),
    #注册
    url(r'^personal_center/register', register),
    #登录
    url(r'^personal_center/login/?$', user_login),
    url(r'^personal_center/login_by_code', user_login_by_code),
    #修改密码
    url(r'^personal_center/update_password', update_user_password),
    #获取用户信息
    url(r'^personal_center/get_user_info', get_user_info),
    #更新用户信息
    url(r'^personal_center/update_user_info', update_user_info),
    #更新用户头像
    url(r'^personal_center/update_user_avatar', update_user_avatar),


    #获取验证码
    url(r'^personal_center/get_certification_code', get_certification_code),
    #实名认证
    url(r'^personal_center/certificate', certification),

    #获取钱包余额
    url(r'^personal_center/get_balance', get_balance),
    #提现
    url(r'^personal_center/apply_cash', apply_cash),


    #首页
    url(r'^item/index', index),
    #支持/支持列表
    url(r'^personal_center/support_item', support_item),
    #获取用户发起的项目
    url(r'^personal_center/get_initiate_items', get_initiate_items),
    #获取用户支持的项目
    url(r'^personal_center/get_support_items', get_support_items),
    #获取用户支持订单列表
    url(r'^personal_center/get_user_orders', get_user_orders),
    #删除用户订单
    url(r'^personal_center/delete_support_order', delete_support_order),


    #收藏
    url(r'^personal_center/collect_item', collection),
    #爱心榜单
    url(r'personal_center/score_rank', score_rank),

    #收货地址
    url(r'personal_center/add_consignee', add_consignee),
    url(r'personal_center/get_consignee', get_consignee),
    url(r'personal_center/operate_consignee', operate_consignee),
    url(r'personal_center/update_consignee', update_consignee),
    #举报
    url(r'personal_center/report', report),

    #获取银行列表
    url(r'personal_center/get_bank_list', get_bank_list),

    #绑定银行卡
    url(r'personal_center/bind_bankcard', bind_bankcard),
    #获取绑定的银行卡
    url(r'personal_center/get_bindcards', get_bindcards),
    #解绑银行卡
    url(r'personal_center/unbind_bindcard', unbind_bindcard),
    #检查手机号是否被绑定
    url(r'personal_center/judge_phone_bind', judge_phone_bind),
    #检查手机号是否被绑定
    url(r'personal_center/bind_phone', bind_phone),


    #项目发起/发起的项目
    url(r'^item/initiate', item_initiate),
    #修改发起的项目
    url(r'^item/update_initiate', item_update),
    #项目详情
    url(r'^item/details', item_detail),
    #项目类型列表
    url(r'^item/types', get_item_type),
    #筛选
    url(r'^item/filter', filter_items),
    #获取项目评论
    url(r'^item/get_comments', get_item_comments),
    #获取我的评论
    url(r'^item/get_user_comments', get_user_comment),

    #获取轮播列表
    url(r'^item/get_carousel_list', get_carousel),

    #获取项目回报列表-pc端
    url(r'^item/get_pc_paybacks', get_pc_paybacks),


    #项目管理
    url(r'^item/management', item_management),

    #获取回报信息
    url(r'^payback/get_info', get_payback_detail),

    #发货订单
    url(r'^payback/commit', payback_commit),

    #获取回报订单列表
    url(r'^payback/get_order_list', get_order_list),

    #获取订单详情
    url(r'^payback/get_order_detail', get_order_detail),



    #删除订单
    url(r'^payback/delete', delete_order),




    #评论
    url(r'^item/comment', comment),



    #点赞
    url(r'^item/thumb_up', thumb_up),


    #后台操作
    #获取项目列表
    url(r'^admin/item_list', item_list),
    #删除项目
    url(r'^admin/del_item$', del_item),
    #获取支持列表
    url(r'^admin/get_support_list', get_support_list),

    url(r'^admin/bref_details', item_bref_detail),
    url(r'^admin/operate', operate),
    url(r'^admin/update_item$', update_item),
    url(r'^admin/update_item_status', update_item_status),
    url(r'^admin/admin_login', admin_login),

    #添加管理员
    url(r'^admin/add_adminastrator', add_adminastrator),
    #查询所有管理员列表
    url(r'^admin/get_adminastrators', get_adminastrators_info),
    #获取管理员信息
    url(r'^admin/get_adminastrator_info', get_adminastrator_info),
    #删除管理员
    url(r'^admin/delete_adminastrator', del_adminastrator),
    #修改管理员密码
    url(r'^admin/update_password', update_password),
    
    #添加公告
    url(r'^admin/add_announcement', add_announce),
    #修改公告
    url(r'^admin/update_announcement', update_announce),
    #删除公告
    url(r'^admin/del_announcement', delete_announce),
    #获取公告列表
    url(r'^admin/get_announcement_list', get_announce_list),
    #通过ID获取公告
    url(r'^admin/get_announcement', get_announce),

    #获取项目分类列表
    url(r'^admin/item_types', get_item_type),
    #添加项目分类
    url(r'^admin/add_item_type', add_item_type),
    #删除项目分类
    url(r'^admin/del_item_type', del_item_type),

    #获取会员列表
    url(r'^admin/get_user_list', get_user_list),
    #锁定会员
    url(r'^admin/lock_user', lock_user),
    #解锁会员
    url(r'^admin/unlock_user', unlock_user),

    #获取一段时间收支列表
    url(r'^admin/get_payment_list', get_payment_list),
    #获取一段时间支持列表
    url(r'^admin/get_support_list', get_support_list),

    #添加轮播
    url(r'^admin/add_carousel', add_carousel),
    #删除轮播
    url(r'^admin/del_carousel', del_carousel),
    #获取轮播列表
    url(r'^admin/get_carousel_list', get_carousel_list),

    #修改项目手续费
    url(r'^admin/update_item_fee', update_item_fee),
    #修改充值手续费
    url(r'^admin/update_charge_fee', update_charge_fee),
    #获取手续费
    url(r'^admin/get_fees', get_fees),
    #获取举报列表
    url(r'^admin/get_report_list', get_report_list),
    #获取提现申请记录
    url(r'^admin/get_trade_records', get_trade_records),
    #更改提现状态
    url(r'^admin/update_cash_status', update_cash_status),
    #添加推荐
    url(r'^admin/add_recommand', add_recommand),
    #取消推荐
    url(r'^admin/cancel_recommand', cancel_recommand),

    #上传文件
    url(r'^item/upload_file', upload_media_file),
    #获取upload_token
    url(r'^item/get_token', get_token),
    #获取项目数量统计
    url(r'^item/counts', get_counts),
    
]
