import re
import os
import requests
from .base import *
from .case import Header
from .utils import read_csv


@dataclass
class EnvironParam(DataClassMixin):
    key: str
    value: str
    description: Optional[str] = None

    def to_dict(self) -> dict:
        return {'key': self.key, 'value': self.value}


@dataclass
class Scene(DataClassMixin, FileLoaderMixin):
    """
        场景
        一个场景下可以有一个或多个测试用例
        对应标准测试用例的一个文件夹或一个文件（当只有一个测试用例时）
    """
    name: str
    url: str
    user: Optional[str]
    method: Optional[str]#MethodEnum
    cases: List[Case]
    header: List[Header] = None

    @property
    def envs(self):
        return self._envs

    def set_envs(self, envs):
        self._envs = envs   # [EnvironParam()]

    @property
    def user_cookie(self):
        return self._user_cookie

    def _get_host_port(self):
        url = self.url
        for s in ['http://', 'https://']:
            if url.startswith(s):
                url = url[len(s):]
                break
        return url.split('/')[0]
        # todo@hy 优雅写法应该是正则，只是一下子搞不定非贪婪模式
        # pattern = re.compile('[http|https]*://(.*)/.*$')
        # return pattern.match(self.url).groups()[0]

    def get_host(self):
        return self._get_host_port().split(':')[0]

    def get_port(self):
        if ':' in self._get_host_port():
            return self._get_host_port().split(':')[1]
        return None

    def get_path(self):
        url = self.url
        for s in ['http://', 'https://']:
            if url.startswith(s):
                url = url[len(s):]
                break
        path = '/'.join(url.split('/')[1:])
        return path.split('?')[0]
        # todo@hy 优雅写法应该是正则，只是一下子搞不定非贪婪模式
        # pattern = re.compile('[http|https]*://.*/(.*)\[?]*.*$')
        # return pattern.match(self.url).groups()[0]

    def set_user_cookie(self, user_cookie):
        self._user_cookie = user_cookie # "session=xxx"

    def set_project(self, project):
        self.project = project
        self.set_envs(project.envs)
        if self.user:
            self.set_user_cookie(project.cookie_users[self.user])

    @staticmethod
    def from_dict(obj: Any) -> 'Scene':
        name = from_str(obj.get("name"))
        url = from_str(obj.get("url"))
        user = obj.get("user", None)
        # method = MethodEnum(obj.get('method'))
        method = obj.get('method')
        cases = from_list(Case.from_dict, obj.get('cases'))
        return Scene(name, url, user, method, cases)

    def to_dict(self) -> dict:
        result = {}
        result['name'] = self.name
        result['url'] = self.url
        result['method'] = self.method# to_enum(MethodEnum, self.method)
        result['cases'] = from_list(lambda x: to_class(Case, x), self.cases)
        return {k: result[k] for k in result if k in self.get_changed_keys()}

    def to_csv(self):
        """
            csv format:

        """
        res = [
            ['场景名', self.name],
            ['URL', self.url],
        ]
        if self.user:
            res.append(['用户', self.user])
        cases_data = []
        max_key_count = 0
        for case in self.cases:
            line = [case.name]
            max_key_count = max(max_key_count, len(case.params))
            for k, v in case.params.items():
                line.extend([k, v])
            cases_data.append(line)
        res.append(['CASE名'] + ['K', 'V'] * max_key_count)
        res.extend(cases_data)
        return res

    @staticmethod
    def load_from_csv(path):
        dirpath, filename = os.path.split(path)
        json_path = os.path.join(dirpath, filename.replace('.csv', '.json'))
        scene = Scene.load_from_file(json_path)
        if path.endswith('.json'):
            return scene
        l = read_csv(path)
        scene_attrs = {
            '场景名': 'name',
            'URL': 'url',
            '用户': 'user',
        }
        for index, line in enumerate(l):
            if line[0] in scene_attrs:
                setattr(scene, scene_attrs[line[0]], line[1])
            elif line[0] == 'CASE名':
                break
        cases = []
        for line in l[index:]:
            case_name = line[0]
            case_params = {}
            for _index, i in enumerate(line[1:]):
                if _index % 2 == 0:
                    case_params[i] = line[_index + 1]
            cases.append(Case(
                name=case_name,
                params=case_params
            ))
        scene.cases = cases
        return scene


    @staticmethod
    def gen_by_post_man_items(post_man_items):
        res = []
        for _index, pcase in enumerate(post_man_items):
            line = pcase.name.split('-', 1)
            if len(line) == 1:
                line = [line[0], 'case%s' % _index]
            res.append(line)
        assert len(set([i[0] for i in res])) > 1    #scene的名称不能冲突
        cases = []
        for index, (_scene_name, case_name) in enumerate(res):
            pcase = post_man_items[index]
            case = Case(
                name=case_name,
                params=pcase.get_params_dict()
            )
            cases.append(case)
        s = Scene(
            name=res[0][0],
            url=post_man_items[0].request.url.get_standard_url(),
            metmod=post_man_items[0].request.url.method,# MethodEnum(post_man_items[0].request.url.method),
            cases=cases
        )
        return s

    def gen_postman_url(self, case):
        from ..postman import URLClass, QueryParam
        if self.name == '添加note':
            print(self.name, self.get_host(), self.get_path())
        return URLClass(
            host=self.get_host(),
            path=self.get_path(),
            hash=None,
            port=self.get_port(),
            protocol="https" if 'https:' in self.url else 'http',
            query=[QueryParam(description=None, disabled=None, key=k, value=v) for k, v in case.params.items()]

        )

    def gen_postman_requests(self):
        # todo 完善参数
        from ..postman import RequestClass
        res = []
        for case in self.cases:
            req = RequestClass(
                description=None,
                header=self.get_postman_headers(),
                url=self.gen_postman_url(case),
                auth=None,
                body=None,
                certificate=None,
                method=self.method,
                proxy=None
            )
            res.append(req)
        return res

    @staticmethod
    def gen_by_post_man_collection(post_man_collection):
        return

    def get_headers(self) -> dict:
        if self.user:
            h = Header(description='Cookie', key='Cookie', value= self.user_cookie)
            if self.header:
                self.header.append(h)
            else:
                self.header = [h]
        return {i.key: i.value for i in self.header} if self.header else {}

    def get_postman_headers(self):
        return self.header

    def get_response(self) -> dict:
        res = {}
        url = self.url
        headers = self.get_headers()
        for e in self.envs:
            url = url.replace('{{%s}}' % e.key, e.value)
            headers = {k:v.replace('{{%s}}' % e.key, e.value) for k, v in headers.items()}
        for case in self.cases:
            data = case.get_payload()
            for e in self.envs:
                data = {k: v.replace('{{%s}}' % e.key, e.value) for k, v in data.items()}
            if self.method in [None, "GET"]:
                res[case.name] = requests.get(url, params=data, headers=headers)
            else:
                res[case.name] = requests.request(self.method or "GET", url, headers=headers, data=data)
        return res

    def run(self):
        try:
            print(self.url)
            responses = self.get_response()
            for case_name, resp in responses.items():
                try:
                    print(case_name, resp.status_code, resp.content)
                except Exception as e2:
                    print('case-' + case_name + ' run error:' + str(e2))
        except Exception as e1:
            print('scene-' + self.name + ' run error:' + str(e1))


def get_json():
    f = open('/Users/huangyan/work/tianshang/proj-nwow/skvbackend/tests/cases/hackroute_login2.json')
    s = f.read()
    f.close()
    return json.loads(s)


if __name__ == "__main__":
    j = get_json()
    obj = Scene.from_dict(j)
    r = obj.to_dict()
    print(json.dumps(r, indent=4))
