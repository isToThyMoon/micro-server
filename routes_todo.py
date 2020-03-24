from utils import log
from models.todo import Todo
from models.user import User
from routes import current_user
from routes import template
from routes import response_with_headers
from routes import redirect


def login_required(route_function):                 # 验证登录函数  （发现每条Todo相关路由函数都要进行登录验证 把它抽象出来）
    def f(request):
        uname = current_user(request)
        u = User.find_by(username=uname)
        if u is None:
            return redirect('/login')
        return route_function(request)
    return f


# ______________________________________________路由函数________________________________________________________________________________
def index(request):                                  #  todo 首页的路由函数
    headers = {
        'Content-Type': 'text/html',
    }
    uname = current_user(request)
    u = User.find_by(username=uname)
    if u is None:
        return redirect('/login')
    todo_list = Todo.find_all(user_id=u.id)         #  查找Todo数据库里 todo类的user_id属性和当前用户相等的Todo实例  即属于此用户的Todo数据 # 返回的是一个list包含符合条件的所有对象实例
    # 下面这行生成一个 html 字符串
    # todo_html = ''.join(['<h3>{} : {} </h3>'.format(t.id, t.title)
    #                      for t in todo_list])
    # 上面一行列表推倒的代码相当于下面几行
    todos = []
    for t in todo_list:
        edit_link = '<a href="/todo/edit?id={}">编辑</a>'.format(t.id)
        delete_link = '<a href="/todo/delete?id={}">删除</a>'.format(t.id)
        s = '<h3>{} : {} {} {}</h3>'.format(t.id, t.title, edit_link, delete_link)
        todos.append(s)
    todo_html = ''.join(todos)
    # 替换模板文件中的标记字符串
    body = template('todo_index.html')
    body = body.replace('{{todos}}', todo_html)
    # 下面 3 行可以改写为一条函数, 还把 headers 也放进函数中
    header = response_with_headers(headers)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')

def edit(request):
    """
    todo edit 的路由函数
    """
    headers = {
        'Content-Type': 'text/html',
    }
    uname = current_user(request)
    u = User.find_by(username=uname)
    if u is None:
        return redirect('/login')
    # 得到当前编辑的 todo 的 id
    todo_id = int(request.query.get('id', -1))
    t = Todo.find_by(id=todo_id)
    if t.user_id != u.id:
        return redirect('/login')
    # if todo_id < 1:
    #     return error(404)
    # 替换模板文件中的标记字符串
    body = template('todo_edit.html')
    body = body.replace('{{todo_id}}', str(t.id))
    body = body.replace('{{todo_title}}', str(t.title))
    # 下面 3 行可以改写为一条函数, 还把 headers 也放进函数中
    header = response_with_headers(headers)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def add(request):
    """
    用于增加新 todo 的路由函数
    """
    headers = {
        'Content-Type': 'text/html',
    }
    uname = current_user(request)
    u = User.find_by(username=uname)
    if request.method == 'POST':
        # 'title=aaa'
        # {'title': 'aaa'}
        form = request.form()
        t = Todo.new(form)
        t.user_id = u.id
        t.save()
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/todo')               # 如果不重定向 直接返回发index（request）刷新 结果一样 但是网址是/todo/add 不应该这样


def update(request):
    """
    用于增加新 todo 的路由函数
    """
    uname = current_user(request)
    u = User.find_by(username=uname)
    if u is None:
        return redirect('/login')
    if request.method == 'POST':
        # 修改并且保存 todo
        form = request.form()
        print('debug update', form)
        todo_id = int(form.get('id', -1))
        t = Todo.find_by(id=todo_id)
        t.title = form.get('title', t.title)
        t.save()
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/todo')


def delete_todo(request):
    uname = current_user(request)
    u = User.find_by(username=uname)
    if u is None:
        return redirect('/login')
    # 得到当前编辑的 todo 的 id
    todo_id = int(request.query.get('id', -1))
    t = Todo.find_by(id=todo_id)
    if t.user_id != u.id:
        return redirect('/login')
    if t is not None:
        t.remove()
    return redirect('/todo')




# 路由字典______________________________________________________________________________________________________________________
route_dict = {
    # GET 请求, 显示页面
    '/todo': index,
    '/todo/edit': edit,
    # POST 请求, 处理数据
    '/todo/add': add,         # login_required(add)
    '/todo/update': update,
    '/todo/delete': delete_todo,
}
