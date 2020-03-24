from models import Model

class User(Model):               # (id username password )
    """
    User 是一个保存用户数据的 model
    现在只有两个属性 username 和 password
    """
    def __init__(self, form):
        self.id = form.get('id', None)
        if self.id is not None:
            self.id = int(self.id)
        self.username = form.get('username', '')
        self.password = form.get('password', '')

    def validate_login(self):
        # return self.username == 'gua' and self.password == '123'
        u = User.find_by(username=self.username)
        # us = User.all()
        # for u in us:
        #     if u.username == self.username and u.password == self.password:
        #         return True
        # return False
        return u is not None and u.password == self.password
        # 这样的代码是不好的，不应该用隐式转换
        # return u and u.password == self.password
        """
        0 None ''
        """

    def validate_register(self):
        return len(self.username) > 2 and len(self.password) > 2