import os
import re
from builtins import NotImplementedError
from .src.scene import Scene, EnvironParam
from .src.utils import write_csv, logger


class Project:
    """
        功能集成对外接口
    """
    env: dict = {}
    path: str
    cookie_key: str = 'session'
    cookie_file_path: str
    cookie_users = {}
    scenes = []
    scene_structure = {}
    login_url = ''

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def envs(self):
        return [EnvironParam(
            key=k, value=v
        ) for k, v in self.env.items()]

    def load_cookie(self):
        """
            使用flask-login的cookie设置与解析，如网站使用其它方式设置cookie，可重写此方法。
        :return:
        """
        cookie_file_path = self.cookie_file_path
        if not self.cookie_file_path.startswith('/'):
            current_dir = os.getcwd()
            cookie_file_path = os.path.join(current_dir, self.cookie_file_path)

        scene = Scene.load_from_file(cookie_file_path)
        scene.set_project(self)
        response_dict = scene.get_response()
        pattern = re.compile('^' + self.cookie_key + '=(.*?);.*$')
        for user, resp in response_dict.items():
            try:
                set_cookie_line = resp.headers._store['set-cookie'][1]
                self.cookie_users[user] = pattern.match(set_cookie_line).groups()[0]  # 没记录过期时间
                logger.info('成功登陆用户 %s，后续场景中可切换此用户。' % user)
            except Exception as e:
                logger.info('登陆用户 %s 失败，后续场景使用此用户等同于未登录。' % user)

    def callback(self, path, structure):
        """
            重写本方法，以修改获得场景后的默认行为
        :param path:
        :return:
        """
        scene = Scene.load_from_file(path)
        scene.set_project(self)
        self.scenes.append(scene)
        if scene.name not in structure:
            structure[scene.name] = scene
        scene.run()

    def load_scene(self, callback, target='json'):
        """
            识别路径下所有json文件，载入场景，执行回调
            也支持识别csv文件
        :return:
        """
        self.scene_structure = {}

        def search(root, target, callback=callback, current_data={}):
            items = os.listdir(root)
            for item in items:
                path = os.path.join(root, item)
                if item.startswith('.'):
                    # 忽略隐藏文件
                    continue
                elif os.path.isdir(path):
                    if item not in current_data:
                        current_data[item] = {}
                    logger.info('scan dir ' + path)
                    search(path, target, callback=callback, current_data=current_data[item])
                elif path.split('/')[-1].split('.')[-1] == target:
                    logger.info('load file ' + path)
                    callback(self, path, current_data)

        search(self.path, target, callback=callback, current_data=self.scene_structure)

    def run(self):
        self.load_scene(callback=Project.callback)

    def get_scene_items(self):
        from .postman import Items

        def get_item(current_data):
            items = []
            for key, v in current_data.items():
                if type(v) is Scene:
                    item = Items(
                        description=None,
                        request=v.gen_postman_requests()[0],
                        name=key,
                        protocol_profile_behavior=None
                    )
                else:
                    item = Items(
                        description=None,
                        request=None,
                        name=key,
                        protocol_profile_behavior=None,
                        response=None,
                        variable=None,
                        item=get_item(current_data[key])
                    )
                items.append(item)
            return items

        items = get_item(self.scene_structure)
        return items

    def _callback_create_csv(self, path, structure):
        scene = Scene.load_from_file(path)
        scene.set_project(self)
        self.scenes.append(scene)
        if scene.name not in structure:
            structure[scene.name] = scene

        dirpath, filename = os.path.split(path)
        csv_path = os.path.join(dirpath, filename.replace('.json', '.csv'))
        write_csv(csv_path, scene.to_csv())

    def create_scv(self):
        self.load_scene(callback=Project._callback_create_csv)

    def _callback_with_csv(self, path, structure, need_write_csv=False):
        scene = Scene.load_from_csv(path)
        scene.set_project(self)
        self.scenes.append(scene)
        if scene.name not in structure:
            structure[scene.name] = scene

        dirpath, filename = os.path.split(path)
        csv_path = os.path.join(dirpath, filename.replace('.json', '.csv'))
        if need_write_csv:
            write_csv(csv_path, scene.to_csv())

    def _callback_reset_json_by_csv(self, path, structure):
        self._callback_with_csv(path, structure=structure, need_write_csv=True)

    def check_csv(self):
        self.load_scene(callback=Project._callback_with_csv, target='csv')

    def reset_json_by_csv(self):
        self.load_scene(callback=Project._callback_reset_json_by_csv, target='csv')

    @classmethod
    def gen(cls):
        """
            重写此方法，以生产你项目所需对象
        :return:
        """
        return cls()

    def clean_db(self):
        """重写方法完成清理数据库动作"""
        raise NotImplementedError

    def start_webserver(self):
        """重写方法完成启动网站服务动作"""
        raise NotImplementedError

    def init_db(self):
        """重写方法完成初始化数据库动作"""
        raise NotImplementedError
