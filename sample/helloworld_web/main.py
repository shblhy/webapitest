import datetime
from flask import Flask, request, render_template_string
from flask_login import current_user, LoginManager, UserMixin, login_user, logout_user
from dataclasses import dataclass

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pleasechangethis'
login_manager = LoginManager()
login_manager.init_app(app)


@dataclass
class Account(UserMixin):
    username: str
    password: str

    def check_password(self, password):
        return self.password == password

    def get_id(self):
        return self.username


accounts = [Account(username='user1', password='123456'),
            Account(username='user2', password='234567'),
            Account(username='user3', password='345678')]


@login_manager.user_loader
def get_account(username):
    for a in accounts:
        if a.username == username:
            return a


@app.route('/')
def index():
    return render_template_string('<html>hello world. 请 <a href="login">登录</a></html>')


login_page = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>登录</title>
</head>
<body>
    请登录。
    <form action="login" method="post">
        <div id="form">
            <div>
                <label>username：</label>
                <input name="username" type="text"/>
            </div>
            <div>
                <label>password：</label>
                <input name="password" type="password"/>
            </div>
            <br>
            <input type="submit" value="提交">
        </div>
    </form>
</body>
</html>
"""


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_account(username)
        user.check_password(password)
        login_user(user, remember=True, duration=datetime.timedelta(minutes=1))
        return render_template_string('<html>%s, 登录成功，欢迎您 <a href="info">个人信息页</a> <a href="logout">登出</a></html>' % current_user.username)
    else:
        if current_user.is_anonymous:
            return render_template_string(login_page)
        else:
            return render_template_string('<html>%s, 您已登录，欢迎您 <a href="info">个人信息页</a> <a href="logout">登出</a></html>' % current_user.username)


@app.route('/info')
def info():
    return render_template_string('<html>姓名:%s <a href="logout">登出</a></html>' % current_user.username)


@app.route('/logout')
def logout():
    logout_user()
    return render_template_string('<html>登出成功，<a href="login">登录</a></html>')


if __name__ == '__main__':
    app.run(debug=True)
