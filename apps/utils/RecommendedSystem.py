# -*- encoding: utf-8 -*-
from Redis import Redis
from courses.models import Type


class Recommended:
    def __init__(self, username):
        # redis操作实体，绑定用户
        self.redis = Redis(username)

    def get_user_info(self):
        """对type进行排序"""
        # 获取用于所有标签以及对应值组成的字典
        data = self.redis.get_all()
        # 依据值对字典进行排序
        data_sorted = sorted(data.iteritems(), key=lambda x: x[1], reverse=True)
        return data_sorted

    def get_recommend_types(self):
        """返回前三的type,如果小于三个，则返回所有"""
        # 排列后的标签
        data = self.get_user_info()
        types = []
        # 获取所有标签对应的实体数据
        for item in data:
            types.append(Type.objects.get(name=item[0]))
        # 如果特征标签小于三个，则返回所有
        if len(types) < 3:
            return types
        # 返回前三的特征
        return types[:3]

