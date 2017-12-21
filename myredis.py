import redis
import threading

class MyRedis:
    def __init__(self):
        self.rds = redis.Redis(host='127.0.0.1', port=6379)
#        self.rds = redis.Redis(host='127.0.0.1', port=6379, password='lpiu)(7s@!')
    def get(self, key):
        data = self.rds.get(key)
        if data:
            data = data.decode()
        return data
    def set(self, key, value):
        self.rds.set(key, value)
    def delete(self, key):        
        self.rds.delete(key)
    def expire(self, key, time):
        self.rds.expire(key, 24*3600)

    def keys(self):
        return self.rds.keys()
    def get_values(self):
        return [self.get(key) for key in self.keys() if 'identity' in key.decode()]


if __name__ == '__main__':
    rds = MyRedis()
#    rds.set('crowdy_funding_version','3.6.2')
    #rds.delete('players_count')
    data = rds.get_values()
    print(data)



