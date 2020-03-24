import json
from utils import log


# ____________________________________________model操作方法 save等____________________________________________________          # [{},{}]
def save(data, path):
    """
    data 是 dict 或者 list
    path 是保存文件的路径
    """
    s = json.dumps(data, indent=2, ensure_ascii=False)
    with open(path, 'w+', encoding='utf-8') as f:
        # log('save', path, s, data)
        f.write(s)


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
        # log('load', s)
        return json.loads(s)
# ________________________________________________基类___________________________________________________________________
'''
    Model 是所有 model 的基类
    @classmethod 是一个套路用法
    例如
    user = User()
    user.db_path() 返回 User.txt
'''


class Model(object):

    @classmethod
    def new(cls, form):
        m = cls(form)                       # cls 是类名, 谁调用的类名就是谁的
        return m

    def save(self):
        """
        用 all 方法读取文件中的所有 model 并生成一个 list
        把 self 添加进去并且保存进文件
        """
        log('debug Model的save函数')
        models = self.all()
        log('all（）函数得到的models', models, 'models显示结束')
        first_index = 0
        if self.__dict__.get('id') is None:
            # 加上 id
            if len(models) > 0:
                # 不是第一个数据
                self.id = models[-1].id + 1
            else:
                # 是第一个数据
                log('first index', first_index)
                self.id = first_index
            models.append(self)
        else:
            # 有 id 说明已经是存在于数据文件中的数据
            # 那么就找到这条数据并替换之
            index = -1
            for i, m in enumerate(models):
                if m.id == self.id:
                    index = i
                    break
            # 看看是否找到下标
            # 如果找到，就替换掉这条数据
            if index > -1:
                models[index] = self
        # 保存
        l = [m.__dict__ for m in models]
        path = self.db_path()
        save(l, path)

    @classmethod
    def all(cls):                            # all 方法(类里面的函数叫方法)使用 load 函数得到所有的 models
        path = cls.db_path()
        models = load(path)
        ms = [cls.new(m) for m in models]    # 这里用了列表推导生成一个包含所有 实例 的 list 。m 是 dict, 用 cls.new(m) 可以初始化一个 cls 的实例
        return ms

    @classmethod
    def db_path(cls):                           # cls 是类名, 谁调用的类名就是谁的
        classname = cls.__name__                # classmethod 有一个参数是 class(这里我们用 cls 这个名字)
        path = 'data/{}.txt'.format(classname)  # 所以我们可以得到 class 的名字
        return path

    @classmethod
    def find_by(cls, **kwargs):
        """
        用法如下，kwargs 是只有一个元素的 dict
        u = User.find_by(username='gua')
        """
        log('find_by kwargs是 ', kwargs, '显示结束')
        k, v = '', ''
        for key, value in kwargs.items():
            k, v = key, value
        all = cls.all()
        for m in all:
            # getattr(m, k) 等价于 m.__dict__[k]
            if v == m.__dict__[k]:
                return m
        return None

    @classmethod
    def find_all(cls, **kwargs):
        """
        用法如下，kwargs 是只有一个元素的 dict
        u = User.find_by(username='gua')
        """
        log('kwargs, ', kwargs)
        k, v = '', ''
        for key, value in kwargs.items():
            k, v = key, value
        all = cls.all()  # 返回的是一个list包含所有的对象
        data = []
        for m in all:
            # getattr(m, k) 等价于 m.__dict__[k]
            if v == m.__dict__[k]:
                data.append(m)
        return data  # 返回的是一个list包含所有的对象

    def __repr__(self):
        """
        __repr__ 是一个魔法方法
        简单来说, 它的作用是得到类的 字符串表达 形式
        比如 print(u) 实际上是 print(u.__repr__())
        比如当调用str(o)的时候 实际上调用了o.__str__() 当没有__str__()的时候 就调用__repr__()
        """
        classname = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} >\n'.format(classname, s)
