class Chain(object):

    def __init__(self, path='dada'):
        self._path = path

    def __getattr__(self, path):
        return Chain('%s/%s' % (self._path, path))  # 创建一个新对象 参数是self.path+path再赋值给这个新对象的self._path属性

    def __str__(self):
        return self._path

    __repr__ = __str__

    def __call__(self, path):
        return Chain('%s/%s' % (self._path, path))



print(Chain().user('ayrikiya').des.por)
