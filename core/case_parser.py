# - * - coding: utf-8 -*-

"""
    Read the PDF document, parse the document, and generate the json and xml file
    ---------------------------------- ---------------------------------- ------------------------------
        __version__ = "V1.0"
        __completion__ = "2018-08-09"
        __author__ = "yewei"
        Recorded :
                1. 2018-07-24 SR文本编号转移到 pdffile_parser 模块处理,get_effective_data方法相关代码优化
                2. 2018-07-24 添加wipe()方法，文本字符串去除空格,首尾特殊字符
                3. 2018-07-26 修复bug，GWT字段后不能接:,否则用例无法运行
                4. 2018.08-09 Release V1.0 添加Create_Project类,复制项目运行所需目录及文件
    ---------------------------------- ---------------------------------- -------------------------------
"""

import re
import os
import shutil
from tools.mongo import save_read_db
from formats import myformat

class Create_Project():
    @myformat.banner_conclusion("创建框架文件结构")
    def __init__(self,name):
        """
            查询 features 目录下指定文件夹信息
            获取得到 feature 文件的上一级目录信息
        """
        root_dirpath = os.getcwd() + "\\features\\"
        folder_ = os.path.join(root_dirpath, name)
        if not os.path.isdir(folder_):
            shutil.copytree(os.getcwd() + "\\data\\template",folder_)

class CaseParser():
    """
        MongoDB中测试用例数据解析程序,生成feature文件
    """
    def __init__(self):
        """
            self.total        int,   存入所有case总数
            self.auto_num     int,   存入可执行自动化脚本的数目
            self.datadict     dict,  存入case源数据
            self.analydict    dict,  存入"A"集合初始数据
                "Total"   int  存入集合"C"cases总数目               "Auto"   int   存入集合"C"中可执行自动化程序的cases数目
                "Run"     int  存入本次执行自动化程序运行cases数目    "Pass"  int   存入运行结果通过的数目
                "Failed"  int  存入运行结果失败的数目         "Failed_Cases"  list  存入执行失败的cases索引序号列表
                "Uptime"  dict 存入各case运行时间及总运行时间 
        """
        self.total = 0
        self.auto_num = 0
        self.datadict = {}
        self.analydict = {"CasesTotal":0,"AutoCasesTotal":0}

    @myformat.banner_conclusion("获取集合", critical=True)
    def get_info_from_db(self,name):
        """
            获取MongoDB中指定数据库中所有"C"开头的集合,并读取该集合中所有的信息
                self.content      list,  存入写入feature文件中的字符串信息
        """
        self.name = name
        self.filepath = os.getcwd()+"\\features\\"+self.name
        Create_Project(self.name)
        with save_read_db.DB_Operation() as db:
            db.auth(self.name)
            db.create("C")
            data_obj = db.findall()
            # total 存入case总数
            for data in data_obj:
                self.content = []
                self.analydict["CasesTotal"] += 1
                if data["Auto"]:
                    # auto_num 存入可执行自动化脚本的数目
                    self.datadict = data
                    self.analydict["AutoCasesTotal"] += 1
                    self.processing_scheduler()

    @myformat.banner_conclusion("处理 case 文本")
    def processing_scheduler(self):
        """
            处理程序调度程序:
                1. 首先处理 Feature：
                2. 如果有Test Configuration字段，其次处理 Background
                3. Scenario Outlines 暂不列入支持
                4. 之后处理 Scenario
                5. 将self.content 列表中的数据写入feature文件
                6. 遍历所有集合,并将case分析数据写入"A"集合
        """
        self.feature_filepath = self.filepath + "\\C-%s-"%self.datadict["id"] + self.datadict["Test_Name"] + ".feature"
        if os.path.isfile(self.feature_filepath):
            myformat.format_log("Debug:  CaseParser.processing_scheduler -- %s 已写入文件中,不再重新写入"%self.datadict["Test_Name"])
            return False
        self.steps = self.datadict["Test_Procedure"][0]
        self.results = self.datadict["Expected_Results"][0]
        self.feature()
        if "Test_Configuration" in self.datadict.keys() and self.datadict["Test_Configuration"]!= []:
            self.background("".join(self.datadict["Test_Configuration"]))
        self.comparison()
        self.write_into_file()

    @myformat.banner_conclusion("生成 feature 特征")
    def feature(self):
        """
            用于生成behave文件中：@tags 标签; feature 特征; description
                @casexx                         --- 标签
                Feature: Test Subject           --- 特征
                  Test Purpose                    --- 描述
        """
        if self.datadict["Test_Subject"] != "": value = self.datadict["Test_Subject"]
        else: value = self.datadict["Test_Name"]
        b = self.wipe("".join(value))
        c = "".join(self.datadict["Test_Purpose"])
        self.content.append("Feature: %s\n  %s\n\n" % ( b, c))

    @myformat.banner_conclusion("生成 Background 背景")
    def background(self,text):
        """
            生成Behave用例中的背景信息，背景语句用于每个场景的前提条件，一般只有少量语句
                Background：name
                    Given：step
        """
        self.content.append("  Backgroup:case%s-bg\n\tGiven %s\n\n"%(self.datadict["id"], self.wipe(text.replace)))

    @myformat.banner_conclusion("比对 steps与results 序号")
    def comparison(self):
        """
            生成 Scenario 场景, 废弃 Given 语法，一律使用 When 语法
            首先获取Steps 和 Results 的标志序号:
                1) Step 序号不在 Result 中:
                    When -- S1
                    And  -- S1
                    But  -- S2
                    And  -- S2
                    Then -- R2
                2) Step 序号在 Result 中:
                    When -- S1
                    And  -- S2
                    Then -- R2
        """
        step_mark = sorted(self.steps.keys())
        result_mark = sorted(self.results.keys())
        temp = []
        for s in step_mark:
            temp.append(s)
            if s in result_mark:
                self.content.append("  Scenario:case%s-R%s\n" % (self.datadict["id"], s))
                # 生成说明文案Text
                self.content.append('\t"""\n\t\tSteps:\n\t\t\t%s\n' % self.steps[temp[0]])
                for i in temp[1:]:
                    self.content.append('\t\t\t%s\n'%self.steps[i])
                self.content.append('\t\tResult:\n\t\t\t%s \n\t"""\n'%self.results[s])
                # 生成behave用例
                self.scenario(temp, s)
                temp.clear()

    @myformat.banner_conclusion("写入 Scenario 场景")
    def scenario(self, s, r):
        """
            生成 Scenario 场景, 废弃 Given 语法，一律使用 When 语法
            首先获取Steps 和 Results 的标志序号:
                1) Step 序号不在 Result 中:
                    When -- S1
                    And  -- S1
                    But  -- S2
                    And  -- S2
                    Then -- R2
                2) Step 序号在 Result 中:
                    When -- S1
                    And  -- S2
                    Then -- R2
        """
        self.cut_sentence(self.steps[s[0]])
        if len(s) > 1:
            for i in s[1:]:
                self.cut_sentence(self.steps[i],state= False)
        self.content.append("\tThen %s\n\n" %self.wipe(self.results[r]))

    @myformat.banner_conclusion("按照标点分割 Steps 文本")
    def cut_sentence(self, sentence, state=True):
        """
            分割一段话,如果这句话超过20个字符，按照标点符号(,.，。;；)进行分割数据
                sentence: 步骤语句，必须是字符串str
                state : 表明语句是否有对应结果，用以区分 When or But
        """
        if state:
            when = "When"
        else:
            when = "But"

        if len(sentence) > 20:
            sentences = re.split(",|;|，|。|；|\.(?!\d)", sentence)
            self.content.append("\t%s %s\n" %(when,self.wipe(sentences[0])))
            for s in sentences[1:]:
                if s != "":
                    self.content.append("\tAnd %s\n" % self.wipe(s))
        else:
            self.content.append("\t%s %s\n" %(when, self.wipe(sentence)))

    def wipe(self, sentence):
        return sentence.replace(" ","").strip(";").strip("；").strip("\.").strip("。")

    @myformat.banner_conclusion("数据写入 features 文件")
    def write_into_file(self):
        with open(self.feature_filepath, mode="w", encoding="utf-8") as f:
                f.write("".join(self.content))

    @myformat.banner_conclusion("case分析写入数据库")
    def analysis(self):
        with save_read_db.DB_Operation() as db:
            db.auth(self.name)
            db.create("A")
            db.clear("A")
            db.add(self.analydict)