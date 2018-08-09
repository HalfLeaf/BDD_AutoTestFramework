# -*- coding: UTF-8 -*-

"""
    Call the MongoDB database server and store the data
    ---------------------------------- ---------------------------------- -------------------------------
        __version__ = "V1.0"
        __completion__ = "2018-08-09"
        __author__ = "yewei"
        Recorded :
                1. 2018-08-09 Release V1.0
    ---------------------------------- ---------------------------------- -------------------------------
"""

import re
import os
import time
import pymongo
import collections
from formats import myformat
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

class DB_Server():
    """
        首次连接数据库时，启用该库，尝试启动MongoDB服务
    """
    def __init__(self):
        self.num = 0

    @myformat.banner_conclusion("开启MongoDB服务", critical=True)
    def lanuch_server(self):
        """
            尝试启动MongoDB服务
            对于Windows系统：
            
            对于Linux系统：

        """
        # import platform
        # if platform.system() == "Windows":
        #     import subprocess
        pass
    #Todo 不同平台下启动MongoDB Server

    @myformat.banner_conclusion("查询MongoDB服务是否开启", critical=True)
    def query_open(self):
        """
            通过socket响应对应的本地端口来判断MongoDB服务是否开启
            服务如未开启，会主动尝试启动服务3次，如3次之后仍无法启动服务，则告知异常
        """
        if self.num > 3:
            raise ServerSelectionTimeoutError("ERROR:DB_Operation.query_open -- 错误信息 -- MongoDB服务启动失败")
        else:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            time.sleep(0.5)
            try:
                s.connect(("localhost",27017))
                s.shutdown(2)
                # 利用shutdown()函数使socket双向数据传输变为单向数据传输。shutdown()需要一个单独的参数，
                # 该参数表示了如何关闭socket。具体为：0表示禁止将来读；1表示禁止将来写；2表示禁止将来读和写。
                return DB_Operation()
            except Exception:
                self.num += 1
                self.lanuch_server()
                self.query_open()

class DB_Operation():
    """
        封装常用的MongoDB数据库操作
    """
    def __init__(self):
        self.username = "sysadmin"
        self.password = "symxmyz"

    @myformat.banner_conclusion("集合名约束条件判定",critical=True)
    def convention(self, obj, level:int=1):
        """
            level == 1  集合命名约定：
                            集合命名只允许在以下4种：
                                1) Cxx  用于存放测试用例文档解析结果，一旦存储不允许修改！
                                2) Fxx  用于存放features测试用例解析结果，一旦存储不允许修改！
                                3) Lxx  用于存放测试过程产生的log等数据，每次执行测试时自动清空数据
                                4）Info  用于存放测试关键信息表，主要用于控制测试，每个数据唯一
            level == 2  插入数据约定：
                             要求插入集合中的元素必须是可遍历的字典属性
            level == 3  清空集合数据约定：
                             只允许清空 Lx.x 集合的数据，其他集合不允许做清除操作
        """
        if level == 1:
            if re.match(r"[AGCLF]",obj.replace(" ",""),re.I) == None :
                raise ValueError("集合命名不符合约定, 集合名称: %s,"%obj)
        elif level == 3:
            if re.match("[L|A]",obj.replace(" ",""),re.I) == None:
                raise TypeError("该集合不允许清除操作, 集合名称: %s,"%obj)
        elif level == 2 :
            if not isinstance(obj,dict) :
                raise ValueError("向集合中插入值只支持字典类型，不支持多值同时插入")

    @myformat.banner_conclusion("MongoDB认证并建立数据库", critical=True)
    def auth(self, dbname="Temporary"):
        self.client.admin.authenticate(self.username, self.password)
        self.db = self.client[dbname]
        return self.db

    @myformat.banner_conclusion("数据库下所有集合查询")
    def cols(self):
        return  reversed(self.db.list_collection_names())

    @myformat.banner_conclusion("创建集合", critical=True)
    def create(self, collection):
        myformat.format_log("GET:DB_Operation.create.collection = %s"% collection)
        self.convention(collection)
        self.collection = self.db[collection]

    @myformat.banner_conclusion("插入数据", critical=True)
    def add(self, dic):
        myformat.format_log("GET:DB_Operation.insert.dict = %s" % dic)
        self.convention(dic, level=2)
        self.collection.insert(dic)

    @myformat.banner_conclusion("查找集合所有数据")
    def findall(self):
        return self.collection.find()

    @myformat.banner_conclusion("查找集合指定数据")
    def find(self, value):
        myformat.format_log("GET:DB_Operation.find.value = %s" % value)
        array = self.findall()
        for element in array:
            if element.find(value)!= -1:
                return element

    @myformat.banner_conclusion("删除集合所有数据", critical = True)
    def clear(self, collection):
        myformat.format_log("GET:DB_Operation.remove.collection = %s"% collection)
        self.convention(collection, level=3)
        self.db[collection].remove({})

    @myformat.banner_conclusion("MongoDB连接", critical = True)
    def __enter__(self):
        self.client = pymongo.MongoClient(host="localhost", port=27017)
        try:
            self.client.admin.command('ismaster')
            return self
        except ConnectionFailure:
            myformat.format_log("Debug:DB_Operation.connec_to_mongodb -- 错误信息 -- 连接MongoDB服务器超时 ")
            DB_Server().query_open()

    @myformat.banner_conclusion("关闭MongoDB连接", critical = True)
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

@myformat.banner_conclusion("获取数据库名列表")
def get_db_name():
    dbname = []
    with DB_Operation() as d:
        db = d.auth("admin")
        dbs = db.command("listDatabases")
    for dbnames in dbs["databases"]:
            dbname.append(dbnames["name"]) 
    return dbname

class case_save2_db():
    @myformat.banner_conclusion("查询数据库中是否录入相关数据")
    def json_notin_db(self,name):
        self.name = name
        with DB_Operation() as self.db:
            self.db.auth(name)
            cols = self.db.cols()
        if "C" not in cols: 
            self.read_json()
        else:
            myformat.format_log("Debug:case_save2_db.json_notin_db : %s 已存入数据库中"%name)

    @myformat.banner_conclusion("读取json文件存入数据库")
    def read_json(self):
        import json
        filedir = os.getcwd()+"\\data\\json\\"
        path = filedir+"\\"+ self.name + r".json"
        with open(path) as f:
            self.texts = json.load(f)
            self.save2_db()

    @myformat.banner_conclusion("读取case文本存入数据库", critical=True) 
    def save2_db(self):
        """
            case数据写入数据库,如数据库中已存在相关集合,进入写保护，拒绝更新数据
            如需强制写入,请使用 MongoDB 管理工具手动删除集合后再执行方法
        """
        self.db.create("C")
        for name, cases in self.texts.items():
            self.db.add(cases)

class log_save2_db():
    def __init__(self, featurefile):
        """
            featurefile: 执行behave 命令时，environment.py文件路径,其父目录即为项目名称,也即是数据库名称
        """
        files = featurefile.split("\\")
        with DB_Operation() as self.d:
            db = self.d.auth("admin")
            dbs = db.command("listDatabases")
            name = [dbname["name"] for dbname in dbs["databases"] if dbname["name"] in files]
            self.name = "".join(name)

    @myformat.banner_conclusion("清空数据库中Log集合数据", critical = True)
    def clearall(self):
        """
            behave 运行前清空 "L"集合的内容,并将数据库名称返回给behave
        """
        self.d.auth(self.name)
        self.d.clear("L")
        return self.name

    def write2_db(self, texts):
        """
            behave执行时产生的日志信息写入数据库中
        """
        self.d.auth(self.name)
        self.d.create("L")
        self.d.add(texts)

class feature_save2_db():
    def __init__(self,name):
        self.name = name
        self.features = collections.OrderedDict()
        self.get_feature_file()

    @myformat.banner_conclusion("获取features目录下feature文件")
    def get_feature_file(self):
        """
            获取指定目录下所有feature文件,并按照文件名中的数字进行排序
        """
        feature_files = {}
        self.sourcedir = os.getcwd() + "\\features\\" + self.name
        for folder in os.listdir(self.sourcedir):
            if  folder.startswith("C") and folder.endswith(".feature"):
                marknum = "".join(re.findall("C-(\d*)-",folder,re.I))
                feature_files[marknum] = folder
        self.feature_file = sorted(feature_files.items(),key =lambda x:int(x[0]))
        self.read_feature_contents()
        self.write_features()

    @myformat.banner_conclusion("向数据库中写入feature内容",critical=True)
    def write_features(self):
        with DB_Operation() as db:
            db.auth(self.name)
            if "F" in db.cols():
                myformat.format_log("Debug: feature_save2_db.query_features -- 数据库(%s)中已有集合('F') ")
            else:
                db.create("F")
                db.add(self.features)

    @myformat.banner_conclusion("读取feature文件内容")
    def read_feature_contents(self):
        """
            读取feature文件内容,并按照特定格式写入数据库中
            特定格式:
                tags:
                feature:
                description:
                background:
                scenario1:
                    texts:
                    steps:
                        when:
                        then:
                scenario2:
                    texts:
                    steps:
                        when:
                        then:
        """
        for files in self.feature_file:
            path = self.sourcedir + "\\" + files[1]
            with open(path,encoding="utf-8") as f:
                context = f.read()
            text = {}
            text["tags"] = "".join(re.findall("(@.*?)[F|f]eature",context,re.S))
            text["feature"] =  "".join(re.findall("(Feature.*?)\n",context,re.I))
            text["description"] = "".join(re.findall("[F|f]eature.*?\n(.*?)(?:[S|s]cen|[b|B]ack)",context,re.S))
            text["background"] = "".join(re.findall("([B|b]ackground.*?)[S|s]cen", context, re.S))
            scenarios = re.findall("([S|s]cen.*?)\n(.*?)([w|W]hen.*?)(?=[S|s]en|$)", context, re.S)
            text["scenario"] = {}
            for scenario in scenarios:
                content = {}
                content["texts"] = scenario[1]
                content["steps"] = scenario[2]
                text["scenario"][scenario[0]] =content
            self.features[files[0]] = text