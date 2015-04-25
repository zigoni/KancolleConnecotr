import os
import random
from flask import Flask, request, abort, session, render_template
from requests.exceptions import ReadTimeout
from kcc import get_play_url, DmmTokenError, TokenError, AjaxRequestError, LoginError

app = Flask(__name__)


def get_random_string(length=16, allowed_chars='abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
    return ''.join(random.choice(allowed_chars) for i in range(length))


@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = get_random_string()
    return session['_csrf_token']


app.jinja_env.globals['csrf_token'] = generate_csrf_token
app.secret_key = os.environ.get('KCC_KEY', "89twejd$f8w598t823yt%732ft9w/efghqp")
app.debug = bool(os.environ.get('KCC_DEBUG', False))

@app.route('/connector/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('form.html', error=False)
    else:
        login_id = request.form.get('login_id', '')
        password = request.form.get('password', '')
        if login_id == '' or password == '':
            return render_template('form.html', error=True, message='请输入正确的登录ID和密码')
        shimakezego = bool(os.environ.get('KCC_SHIMAKAZEGO', False))
        if shimakezego:
            REQUESTS_PROXIES = {'http': 'http://127.0.0.1:8099', 'https': 'http://127.0.0.1:8099'}
        else:
            REQUESTS_PROXIES = None
        try:
            play_url = get_play_url(login_id, password, REQUESTS_PROXIES)
        except (DmmTokenError, TokenError, AjaxRequestError, ReadTimeout):
            return render_template('form.html', error=True, message='登录DMM网站失败，可能原因为DMM本身出现故障或服务器网络拥堵')
        except LoginError:
            return render_template('form.html', error=True, message='登录DMM网站失败，可能原因为登录ID或密码输入错误，或者DMM要求您更改密码')
        return render_template('play.html', play_url=play_url)

if __name__ == '__main__':
    app.run()
