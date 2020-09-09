import subprocess
import os
import logging
from webapitest.project import Project, logger

formatter_msg = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter_msg)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


current_project = 'MyProject'

project_params = {
    "env": {'host': 'www.mydomain.com'},
    "path": "cases",
    "cookie_key": 'remember_token',
    "cookie_file_path": 'conf/login.json'
}

shell_paths = {
    'clean_db': 'clean_db.sh',
    'init_db': 'init_db.sh',
    'start_webserver': 'start_webserver.sh',
}

ROOT = os.path.dirname(os.path.dirname(__file__))

try:
    from .local_settings import *
except Exception as e:
    logger.DEBUG("从(conf/local_settings.py)加载本地配置信息失败：%s，确认文件是否存在？" % str(e))
    pass


def get_path(key):
    if key in shell_paths:
        return shell_paths['key']
    else:
        return '%s.sh' % key


class MyProject(Project):
    @classmethod
    def gen(cls, **kwargs):
        project_params.update(kwargs)
        return cls(**project_params)

    def clean_db(self):
        """重写方法完成清理数据库动作"""
        filepath = os.path.join(ROOT, 'shell', get_path('clean_db'))
        code = subprocess.Popen(r'sh %s' % filepath).wait()
        logger.info(code)

    def init_db(self):
        """重写方法完成初始化数据库动作"""
        filepath = os.path.join(ROOT, 'shell', get_path('init_db'))
        code = subprocess.Popen(r'sh %s' % filepath).wait()
        logger.info(code)

    def start_webserver(self):
        """重写方法完成启动网站动作"""
        filepath = os.path.join(ROOT, 'shell', get_path('start_webserver'))
        code = subprocess.Popen(r'sh %s' % filepath).wait()
        logger.info(code)


