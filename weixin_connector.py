# 标准库应用
import hashlib, time, random, json, string

# 三方库引用
import requests, redis

# 内部引用
from weixin.settings import AppSecret, AppID


# 连接redis
class RedisConnector():
    def __init__(self):
        # 用于存储Token
        self.TokenRedis = redis.Redis(
            host='127.0.0.1',
            port='6379',
            db=8,
            # password='',
        )
        self.TicketRedis = redis.Redis(
            host='127.0.0.1',
            port='6379',
            db=9,
            # password='',
        )


# global connect
connect = RedisConnector()


def get_md5(pwd, salt=',./'):
    """get MD5"""
    return hashlib.md5((pwd + salt).encode()).hexdigest()


# sha1加密
def get_sha1(default):
    md = hashlib.sha1()
    md.update(default.encode())
    return md.hexdigest()


# 字典序排序
def map_(params):
    sorted_key = sorted(params.keys())
    key_value = (key + '=' + params[key] + '&' for key in sorted_key)
    _string = ''.join(key_value)[:-1]
    return _string


# 获取access_token
def get_token():
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(AppID,
                                                                                                           AppSecret)
    info = requests.get(url=url).json()
    access_token = info['access_token']
    connect.TokenRedis.setex('access_token', access_token, 7180)
    return access_token


# 获取js-sdk-ticket
def get_ticket():
    try:
        access_token = connect.TokenRedis.get('access_token').decode()
    except Exception as e:
        access_token = get_token()

    url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket'
    params = dict(
        access_token=access_token,
        type='jsapi'
    )
    data = requests.get(url, params=params).json()
    if not data.get('ticket', None):
        raise ValueError("missing parameter ticket")
    # 因为ticket调用有上限，需存入redis
    ticket = data['ticket']
    connect.TicketRedis.setex('ticket', ticket, 7180)
    return ticket


# 签名算法
def wx_info(url):
    try:
        ticket = connect.TicketRedis.get('ticket').decode()
    except Exception as e:
        ticket = get_ticket()

    salt = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    timestamp = str(int(time.time()))
    obj = dict(
        url=url,
        noncestr=salt,
        timestamp=timestamp,
        jsapi_ticket=ticket,
    )
    # 进行字典排序
    string_ = map_(obj)
    # sha1加密
    signature = get_sha1(string_)
    obj['signature'] = signature
    obj['appId'] = AppID
    return obj
