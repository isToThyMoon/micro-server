import socket
import urllib.parse
from utils import log
from routes import route_dict
from routes import error
from routes_todo import route_dict as todo_route
'''
服务器的 host 为空字符串, 表示接受任意 ip 地址的连接  post 是端口, 这里设置为 3000, 随便选的一个数字
host = ''          # 不同的系统定义不同的字符代表接受任意ip地址
port = 2000        # 定义的也是服务器端开放给外界的自身的端口
'''


# _____________________定义一个Request类保存请求的数据_______________________________________________
class Request(object):
    def __init__(self):
        self.method = 'GET'
        self.path = ''
        self.query = {}
        self.headers = {}
        self.cookies = {}             # cookies这个dict里存的是{ user：session_id }     传过来的是user=随机字符串
        self.body = ''

    def add_headers(self, header):    # header是由transmitting_request字符串split()得到的，是一个包含所有请求中header字段的list
        '''                             用add_headers函数转化成dict 存入request里的headers 属性
        [
            'Accept-Language: zh-CN,zh;q=0.8'
            'Cookie: height=169; user=gua'
        ]
        '''
        self.headers = {}              # 清空headers属性值
        lines = header
        for line in lines:
            k, v = line.split(':', 1)
            self.headers[k] = v        # 存储headers属性
        self.cookies = {}              # 清空cookies
        self.add_cookies()             # 相当于request.add_cookies()

    def add_cookies(self):             # 浏览器发来的请求如果有cookies 就存入在request里 增加cookies属性的值 分离请求里header部分的Cookie属性
        """
            height=169; user=gua
            :return:
        """
        cookies = self.headers.get('Cookie', '')       # headers 是一个dict get函数取到的是str  split()函数对str分割 返回的是一个包含分割后各个str的list
        kvs = cookies.split(' ')                      # !!!!!!!!!!!!!这里是'; '   有一个空格
        log('请求传到服务器的cookie:', kvs)
        log('cookie显示结束')
        for kv in kvs:
            if '=' in kv:
                k, v = kv.split('=')
                self.cookies[k] = v

    def form(self):                                    # form 函数用于把表单传递post时的字符串 body 解析为一个字典并返回   body 的格式是 a=b&c=d&e=1
        body = self.body                               # 发送一个注册请求时content-type里的urlencoded编码方式会把url里特殊字符转换
        args = body.split('&')                         # username=g u&a?&password= ----->username=g+u%26a%3F&password=
        f = {}                                         # 需要urllib把它转回来
        for arg in args:                               # {'id':1, username':gua, 'password':123}
            k, v = arg.split('=')
            v = urllib.parse.unquote(v)
            f[k] = v
        return f


# 创建Request实例
request = Request()

# __________________________________________解析函数________________________________________________
def response_for_path(path_include_query):
    path, query = parsed_path(path_include_query)
    request.path = path
    request.query = query
    log('path and query', path, query)
    log('path and query显示结束\n\n')
    # 根据 path 调用相应的处理函数 没有处理的 path 会返回 404
    r = {}
    r.update(route_dict)
    r.update(todo_route)
    response = r.get(path, error)  # 根据路由寻找路由字典里对应的处理函数 找不到返回error函数处理
    return response(request)


def parsed_path(path_include_query):
    """ 将包含query的path解析成path和query两部分 分别是str和dict返回
        message=hello&author=gua
        {
            'message': 'hello',
            'author': 'gua',
        }
        """
    if path_include_query.find('?') == -1:
        return path_include_query, {}
    else:
        path, query_string = path_include_query.split('?', 1)
        args = query_string.split('&')
        query = {}
        for arg in args:
            k, v = arg.split('=')
            query[k] = v
        return path, query

# ________________________________run!!___________________________________________________
def run(host='', port=3000):
    # 启动服务器 初始化socket          ！！！主要业务是根据接收到的request返回对应应该的response！！！
    log('start at', '{}:{}'.format(host, port))
    with socket.socket() as s:               # s 是一个 socket 实例 这里表示是http方式。 用with保证程序中断时正确关闭socket释放占用的端口
        s.bind((host, port))                  # s.bind 用于绑定 表示绑定这个端口 接下来可以监听这个端口上名为host主机传过来的信息  注意 bind 函数的参数是一个 tuple
        while True:                          # 用一个无限循环来处理请求
            s.listen(5)                       # 套路, 先要 s.listen 开始监听
            connection, address = s.accept()  # 当有客户端过来连接的时候, s.accept 函数就会返回 2 个值 分别是 连接 和 客户端 ip 地址
            buffer_size = 1024                # connection的type也是一个socket  address的type是一个tuple 内容是ip+端口
            transmitting_message = b''
            while True:                                                  # 用一个循环处理接受到的数据 存在transmitting_message里
                temporary_message = connection.recv(buffer_size)          # recv 可以接收客户端发送过来的数据 参数是要接收的字节数 返回值是一个 bytes 类型
                transmitting_message += temporary_message
                if len(temporary_message) < buffer_size:
                    break
            transmitting_message = transmitting_message.decode('utf-8')  # bytes 类型调用 decode('utf-8') 来转成一个字符串(str)
            log('ip and request, {}\n{}显示ip和完整request结束了2333333333'.format(address, transmitting_message))
                                                                          # 因为 chrome 会发送空请求导致 split 得到空 list 所以这里判断一下防止程序崩溃
            if len(transmitting_message.split()) < 2:                     # split()函数返回一个list 包含分割后的str   len()函数看有几个str
                continue
            request.method = transmitting_message.split()[0]              # 把请求中的请求方式存入request实例 定义在line14
            path_include_query = transmitting_message.split()[1]          # 这里的path_include_query暂时包括query
            request.add_headers(transmitting_message.split('\r\n\r\n', 1)[0].split('\r\n')[1:]) # 存了request的headers 和cookies属性
            request.body = transmitting_message.split('\r\n\r\n', 1)[1]      # 存了request的body属性值
            response = response_for_path(path_include_query)              # 用 response_for_path 函数来得到 path 对应的响应内容 存了request的path和query属性
            connection.sendall(response)                                  # 把响应发送给客户端
            connection.close()


if __name__ == '__main__':
    config = dict(
        host='',
        port=3000,
    )
    run(**config)
