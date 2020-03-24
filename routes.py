from utils import log
from models.user import User
import random
# from models.message import Message


message_list = []        # 这个函数用来保存所有的 messages
session = {}           # session 可以在服务器端实现过期功能
'''  session这个dict里存的是 {session_id: username,}      '''


# ________________________________以下是路由处理函数中要用到的函数________________________________
def template(name):        # 根据名字读取 templates 文件夹里的一个网页文件并返回 用于路由处理函数返回body部分
    path = 'templates/' + name
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()      # 返回的是字符串str 以utf-8编码


# 从request的cookies dict得到user属性对应值session_id  从session dict里按session_id属性查到对应username
def current_user(request):
    log('查找当前请求里cookie是否有值 session里存了什么？', session)
    session_id = request.cookies.get('user', '')
    username = session.get(session_id, '【游客】')
    return username


def random_str():                        # 生成一个随机字符串
    seed = 'dsfsgfdsgfhgjhgfdsafgdsrfhgfhfgjhghjghhdfgsdgfdhgf'
    s = ''
    for i in range(16):
        random_indedx = random.randint(0,len(seed)-1)
        s += seed[random_indedx]
    return s


def response_with_headers(headers, code=200):           # 将login是要设置set-cookies时产生的headers dict 变成包含响应头的header字符串
    """
    Content-Type: text/html
    Set-Cookie: user=gua
    """
    header = 'HTTP/1.1 {} VERY OK\r\n'.format(code)
    header += ''.join(['{}: {}\r\n'.format(k, v)
                       for k, v in headers.items()])
    return header

def redirect(url):
    """
    浏览器在收到 302 响应的时候
    会自动在 HTTP header 里面找 Location 字段并获取一个 url
    然后自动请求新的 url
    """
    headers = {
        'Location': url,
    }
    # 增加 Location 字段并生成 HTTP 响应返回
    # 注意, 没有 HTTP body 部分
    r = response_with_headers(headers, 302) + '\r\n'
    return r.encode('utf-8')


#  _________________________________以下路由处理函数_____________________________________
def error(request, code=404):           # 路由error处理函数
    e = {                                 # 根据 code 返回不同的错误响应 目前只有 404
        404: b'HTTP/1.1 404 NOT FOUND\r\n\r\n<h1>NOT FOUND PAGE</h1>',
    }                                     # 之前上课说过不要用数字来作为字典的key 但是在 HTTP 协议中 code 都是数字似乎更方便所以打破了这个原则
    return e.get(code, b'')


def route_index(request):               # 主页处理函数 返回主页的响应  bytes对象
    header = 'HTTP/1.1 210 OK\r\nContent-Type: text/html\r\n\r\n'
    body = template('index.html')
    username = current_user(request)
    body = body.replace('{{username}}', username)
    r = header + body
    return r.encode(encoding='utf-8')


def route_static(request):         # 静态资源(gif)的处理函数, 读取图片并生成响应返回bytes
    filename = request.query.get('file', '1.gif')
    path = 'static/' + filename
    with open(path, 'rb') as f:
        header = b'HTTP/1.1 200 ok\r\nContent-Type: image/gif\r\n\r\n'
        img = header + f.read()
        return img


def route_register(request):
    header = 'HTTP/1.1 210 OK\r\nContent-Type: text/html\r\n'
    if request.method == 'POST':
        form = request.form()
        u = User.new(form)
        if u.validate_register:
            u.save()
            result = '注册成功<br> <pre>{}</pre>'.format(User.all())       # all方法返回的是一个包含所有实例的list
        else:
            result = '用户名或者密码长度必须大于2'
    else:
        result = ''
    body = template('register.html')
    body = body.replace('{{result}}', result)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def route_login(request):                    # 登录页面路由处理函数 登录成功返回登录成功提示
    headers = {
        'Content-Type': 'text/html',
    }
    log('注册时查看已有login,cookies', request.cookies, 'cookies显示结束')
    username = current_user(request)
    if request.method == 'POST':
        form = request.form()
        u = User.new(form)
        if u.validate_login():
            session_id = random_str()
            session[session_id] = u.username
            headers['Set-Cookie'] = 'user={}'.format(session_id)
            result = '登录成功'
        else:
            result = '用户名或密码错误'
    else:
        result = ''
    body = template('login.html')
    body = body.replace('{{result}}', result)
    body = body.replace('{{username}}', username)
    header = response_with_headers(headers)
    r = header + '\r\n' + body
    log('注册login路由的响应', r, '响应显示结束')
    return r.encode(encoding='utf-8')


# _________________________________路由字典____________________________________
# 路由字典 key是路由 也就是path value 是路由处理函数(就是响应)  注意函数的参数都是request  是由server.py里response_for_path()定义的
route_dict = {
    '/': route_index,         # 主页处理函数
    '/static': route_static,  # 静态资源（js css 图片）的处理函数, 读取图片并生成响应返回
    '/register': route_register,  # 注册处理函数
     '/login': route_login,   # 登录处理函数
    # '/messages': route_message,   # 信息页处理函数
}
