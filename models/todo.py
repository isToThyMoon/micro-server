from models import Model


# 继承自 Model 的 Todo 类model
class Todo(Model):                   # (id title user_id )
    def __init__(self, form):
        self.id = form.get('id', None)
        self.title = form.get('title', '')
        self.user_id = int(form.get('user_id', -1))      # user_id属性值对应User类里的id值 标识此Todo实例属于哪一个User实例
        # 还应该增加 时间 等数据
