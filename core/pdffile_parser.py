# - * - coding: utf-8 -*-

"""
    Read the PDF document, parse the document, and generate the json and xml file
    ---------------------------------- ---------------------------------- ------------------------------
        __version__ = "V1.0"
        __completion__ = "2018-08-09"
        __author__ = "yewei"
        Recorded :
                1. 2018-07-17 修正TableParser_By_string()类代码,字符串分割改为列表分割
                2. 2018-07-22 优化TableParser_By_string()类代码,利用yield特性遍历文本,支持无序遍历
                3. 2018-07-23 优化代码,SR部分提取序号移到TableParser_By_string()类处理
                4. 2018-07-24 优化CaseParser()类代码,可支持表格分页处理
                5. 2018-08-09 Release V1.0 pdf解析只针对特定项目,不再支持目录遍历
    ---------------------------------- ---------------------------------- -------------------------------
"""

import re
import os
import json
import tabula
import shutil
import collections
from formats import myformat
from core import Test_Title
from xml.etree import ElementTree as ET
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFTextExtractionNotAllowed

global_id = 0

class PdfParser():
    """
        解析pdf文件
            get_pdf_info:  获取cases目录下pdf文件,开始进行文件解析
            get_pdf_outlines: 通过pdfminer第三方模块解析pdf文件目录信息
            get_chapter:  获取目录章节号
            catalog_parser: 生成xml目录树信息文件
            pdftable_parser: 分割pdf表格信息，形成单个表格
            get_table_text:  获取单个表格中的文字信息
            info_save_to_json: 生成json字典信息文件
    """
    @myformat.banner_conclusion("解析pdf表格")
    def pdftable_parser(self, source):
        """
            遍历所有表格
            每完整获取一个表格，立即深度解析，生成信息字典
                source: tabula解析得到的所有表格数据
        """
        self.process = TableParser_By_string()
        self.datadict = collections.OrderedDict()
        self.first = 0
        self.register = []
        for first in source:
            text = []
            for second in first["data"]:
                text.append(second)
            self.get_table_text(texts=text)
        self.process.get_data(self.register, self.datadict)
        self.info_save_to_json()

    @myformat.banner_conclusion("获取表格数据",critical=True)
    def get_table_text(self, texts):
        """
            获取表格中txt文档信息，并剔除非[Test_Name]开头的表格
                index: 表格索引信息
                texts: 单个表格数据
        """
        self.tabletext = []
        for first in texts:
            for second in first:
                if second["text"] !="":
                    self.tabletext.append(second["text"])
        # 剔除修订记录表格,要求表格必须以规定字段起始
        self.backward()

    @myformat.banner_conclusion("向后匹配,确定文本",critical= True)
    def backward(self):
        """
            从get_table_text方法获取到的解析文本,再此进行判定是否是需要的测试用例文本:
                1. 测试用例文本必须以 Test_Title.Test_Name 中的字段开头，否则认为该数据为：
                    1.1 修订记录等文本,该数据直接丢弃,一般认为该文本出现在首个 Test_Name 之前
                    1.2 因篇幅造成分页，使得一张table表分在两页的情况，此类情况需要将数据拼接在其原有的Table表上
                2. 执行时，后面获取一个表格，若该表以 Test_Name 起始，则认为获取到的数据为一个完整表单，立即进行数据处理
        """
        if self.first:
            if self.tabletext[0] in Test_Title.Test_Name:
                self.process.get_data(self.register, self.datadict)
                self.register.clear()
                self.register.extend(self.tabletext)
            else:
                self.register.extend(self.tabletext)
        else:
            if self.tabletext[0] in Test_Title.Test_Name:
                self.first = 1
                self.register = self.tabletext

    @myformat.banner_conclusion("保存信息生成json文件", critical=True)
    def info_save_to_json(self):
        """
            将解析到的表格数据，保存生成json文件
        """
        jsonpath = os.getcwd()+"\\data\\json\\"+'%s.json'%self.filecopy
        with open(jsonpath, "w", encoding='utf-8') as f:
            f.write(json.dumps(self.datadict))

    @myformat.banner_conclusion("解析pdf文件", critical=True)
    def get_pdf_info(self,file):
        """
            获取cases目录下pdf文件 
            通过pdfminer第三方函数解析pdf目录
            通过tabula第三方函数解析pdf表格
        """
        dir = os.getcwd() + "\\data\\cases"
        self.filecopy,extention =  os.path.splitext(file)
        shutil.copyfile(dir+"\\"+file, dir+"\\"+self.filecopy+"_复件"+extention)
        filecopy_path = dir+"\\"+self.filecopy+"_复件"+extention
        global global_id
        global_id = 0
        try:
            myformat.format_log("Notice:CaseParser.get_pdf_info -- 正在解析pdf文件: %s"%self.filecopy)
            self.catalog_parser(filecopy_path)
            df = tabula.read_pdf(filecopy_path,encoding='gb2312',output_format="json",pages="all")
            self.pdftable_parser(df)
        except :
            myformat.format_log("Debug:CaseParser.get_pdf_info -- 错误信息 --  pdf文档解析失败")
        finally:
            os.remove(filecopy_path)

    @myformat.banner_conclusion("解析pdf目录")
    def get_pdf_outlines(self, pdffile):
        """
            通过pdfminer函数获取目录信息
        """
        self.catalog = []
        with  open(pdffile, 'rb') as fp:
            parser = PDFParser(fp)
            document = PDFDocument(parser)
            if not document.is_extractable:
                raise PDFTextExtractionNotAllowed
            outlines = document.get_outlines()
            for (level, title, dest, a, se) in outlines:
                self.catalog.append(title)

    def get_chapter(self,context):
        """
            获取目录中章节号信息，目前只支持1-3级
            通过信息中(.1)格式的个数来判断目录级别
            章节号只能解析两者格式：
                1) 1.1
                2) 1.1.
                return: 目录级别
        """
        id = len(re.findall("(\.\d)", context))
        chapter = re.findall("(\d\.?\d?\.?\d?)", context)
        return "level%s"%(id+1),chapter

    @myformat.banner_conclusion("解析目录生成xml文件", critical=True)
    def catalog_parser(self, filecopy_path):
        """
            生成xml目录树文件
            要求pdf文件中的目录，按照 一级目录 二级目录 三级目录 有序生成
            不允许跳开上一级目录，直接生成下一级目录的情况出现
            目前最多支持三级目录
                filecopy_path: pdf复件文件路径
        """
        self.get_pdf_outlines(filecopy_path)
        root = ET.Element('project', {'projectname':self.filecopy})
        for context in self.catalog:
            id,chapter = self.get_chapter(context)
            chapter = "".join(chapter)
            if id == "level2":
                try:
                    sencond = ET.SubElement(frist, id, {"title": "test case", "chapter": chapter})
                    sencond.text = context
                except Exception as e:
                    myformat.format_log("DEBUG:CaseParser.catalog_parser -- 错误信息 -- %s 的一级目录无法获取%s "%(chapter,e))
            elif id == "level3":
                try:
                    thrid = ET.SubElement(sencond, id, {"title": "test case", "chapter": chapter})
                    thrid.text = context
                except Exception as e:
                    myformat.format_log("DEBUG:CaseParser.catalog_parser -- 错误信息 -- %s 的二级目录无法获取,%s "%(chapter,e))
            else:
                frist = ET.SubElement(root, id, {"title": "test case", "chapter": chapter})
                frist.text = context
        tree = ET.ElementTree(root)
        path = os.getcwd()+"\\data\\xml\\"+'%s.xml'%self.filecopy
        tree.write(path)


class TableParser_By_string():
    def get_data(self, table, orderdict):
        """
            解析得到的数据由列表转为字符串
            此方法可避免多行数据分布在列表的不同位置的再处理
            需要pdf编写时保持固定的格式书写，以防信息解析错误
                table: 单个表格的txt文档信息
                orderdict: 信息字典
                id:  正在解析的单个表格相对整个表格的位置索引
        """
        self.data = table
        self.data.append("END")
        self.orderdict = orderdict
        self.dict = {}
        global global_id
        global_id += 1
        self.dict["id"] = global_id
        self.dict["Auto"] = False
        self.id = global_id
        self.regex = re.compile("(?:[#|s]?|(?:step)?)(\d{1,2})[、|\.](?!\d)", re.I)
        self.datacooked()
        self.parser_testname()  
        # Todo 表内嵌套表格的处理

    @myformat.banner_conclusion("按照标题分割文本", critical=True)
    def datasplit(self, keyword, SR):
        """
            遍历所有文本数据，一旦发现Test_Title中的字段，立即返回缓存列表中数据，并清空缓存列表
            利用 yield 生成器特性，下次循环时自动从上次暂停位置开始遍历，因此可以遍历整个列表
            由于最后一个元素无法yield返回，所以需要类初始化时给self.data加上结束语"END"
            对于 Steps和Results 文本数据需要抓取段落起始的编号，形成字典，所以要求SR文本必须符合如下格式：
                正则表达式：(?:[#|s]?|(?:step)?)(\d{1,2})\.(?!\d)
                具体形式：字母大小写不关心，空格不关心
                    1) #1.
                    2) S1.
                    3) step1.
                    4）为防止ip地址位于句首而造成无匹配，因此不允许出现1.后面继续出现数字的情况，如1.1
                        keyword: 表格中的标题，与Test_Title对应
                        SR:  Steps和Results表格中的标题
                        statement: 标志位，用于判定是否需要进行语句成句判断
                        partion :缓存文本语句
                        temp_dict:临时缓存SR文本字典
        """
        partion = []
        statement = 0
        temp_dict = {}
        for each in self.data:
            if each in keyword:
                if temp_dict != {}:
                    partion.append(temp_dict)
                yield partion
                partion = []
                temp_dict = {}
                statement = True if each in SR else False
            if statement and each not in SR: 
                m = self.regex.match(each.replace(" ",""))
                if m != None:
                    text = self.regex.split(each, maxsplit=1)[2]
                    key = m.group(1)
                    temp_dict[key] = text
                    continue
                else:
                    try:
                        value =temp_dict[key] + each
                        temp_dict[key]  = value
                        continue
                    except Exception as e:
                        raise IndexError("Debug:TableParser_By_string.datasplit:查找不到有效的编号信息 -- 错误信息 --%s"%e)
            partion.append(each) 

    @myformat.banner_conclusion("提取文本",critical=True)
    def datacooked(self):
        """
            预处理，从Test_Title.py文件中读取所有数据，并转化为一个整体的列表
            Steps 和 Results 需要单独再建立一个列表，用于成句判断
            利用 yield 生成器特性，获取到的列表：
            第一个元素是指定的标题，第二个元素及其之后的元素，为该标题对应的文本数据
        """
        section = ["Test_Date","Test_Subject", "Test_Purpose","Test_Instrument","DUT_Topology","Test_Configuration",
                   "Test_Procedure","Expected_Results","Criteria","Test_Results", "Notes","END"]
        keyword = []
        SR = []
        for cursor in section:
            a = eval("Test_Title.%s"%cursor)
            keyword.extend(a)
            if cursor == "Test_Procedure" or cursor == "Expected_Results":
                SR.extend(a)
        section.append("Test_Name")
        for texts in self.datasplit(keyword, SR):
            key ="".join([k for k in section if texts[0] in eval("Test_Title.%s" % k)])
            if key == "Test_Procedure"or key == "Expected_Results":
                self.dict[key] = texts[1:]
            else:
                self.dict[key] ="".join(texts[1:])  if len(texts) > 1  else  ""

    @myformat.banner_conclusion("解析Case Name", critical=True)
    def parser_testname(self):
        """
            信息字典中Test_Name字段，按照DUT进行分割，只取左半部，丢掉右半部分无用数据(如果有DUT字段的话)
            在Test_Name字段中任意地方出现*，表示该case不支持自动化测试，反之表示支持
        """
        casename = re.split("DUT","".join(self.dict["Test_Name"]),re.I)[0]
        testname = "".join([self.data[0],casename])
        if casename != "":
            if re.search("\*",testname)== None:
                self.dict["Auto"] = True
            else:
                self.dict["Auto"] = False
            self.dict["Test_Name"] = casename
            self.orderdict["C-%s"%self.id] = self.dict
        else:
            myformat.format_log("ERROR:TableParser_By_string.parser_testname -- 错误信息 -- casename为空 ")