# -*- encoding: utf-8 -*-
import redis
from OnlineCourses.settings import REDIS_DB, REDIS_HOST, REDIS_PORT


class Redis:
    def __init__(self, name):
        # 连接Redis数据库，并返回连接对象
        self.r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        # 姓名
        self.name = name

    def increase(self, tag, amount=1):
        """tag的值加amount，默认加1"""
        self.r.hincrby(self.name, tag, amount)

    def decrease(self, tag, amount=1):
        """tag的值减amount，默认减1"""
        self.r.hincrby(self.name, tag, -amount)

    def get_by_tag(self, tag):
        """获取指定的tag的value"""
        return self.r.hget(self.name, tag)

    def get_all(self):
        """获取所有tag及其value"""
        return self.r.hgetall(self.name)