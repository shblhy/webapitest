import sys
import getopt
import json
from .postman import Collection
from .project import Project
from .src.case import Information


def parse_postman_collection_to_casefile(path):
    obj = Collection.load_from_file(path)
    obj.gen_web_test_case_file()


def parse_casefile_to_postman_collection(path, out_path, name='auto api test'):
    project = Project(path=path)
    project.run()
    c = Collection(
        info=Information(
            description='auto parsed from webapitest. https://gitee.com/wow_1/webapitest',
            name=name,
            postman_id=None,
            schema='https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
            version=None
        ),
        item=project.get_scene_items(),
        auth=None,
        event=None,
        protocol_profile_behavior=None,
        variable=None
    )
    res = json.dumps(c.to_dict(), indent=4)
    f = open(out_path, 'w')
    f.write(res)
    f.close()
    return c


def main(argv):
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print
            'test.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print
    '输入的文件为：', inputfile
    print
    '输出的文件为：', outputfile


if __name__ == '__main__':
    main(sys.argv[1:])
