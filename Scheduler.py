# -*- coding: UTF-8 -*-
"""
    Start the function ,and determine the current directory
    ---------------------------------- ----------------------------------
        __version__ = "V1.0"
        __completion__ = "2018-08-09"
        __author__ = "yewei"
        Recorded :
                1. 2018-08-09 Release V1.0
    ---------------------------------- ----------------------------------
"""

import re
import os
import argparse
import subprocess
from core import pdffile_parser
from core import case_parser
from formats import myformat
from tools.mongo import save_read_db


class Run():
    def __init__(self, filepath):
        # filepath: 项目名称或者项目所在目录路径
        self.path = filepath
        myformat.MyLog()
    
    @myformat.banner_conclusion("获取cases目录下pdf文件")
    def get_pdf_file(self, folder):
        """
            -d 参数传入项目路径时,遍历该目录，获取所有pdf文件
        """
        pdffile = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if re.search(r"\.pdf", file) != None:
                    pdffile.append(file)
        return pdffile

    @myformat.banner_conclusion("PDF文件解析并存入数据库",critical=True)
    def pdfparser(self):
        """
            调用 core/pdffile_parser 模块解析pdf文档
            解析完成后,调用 tools/save_and_read 模块将解析数据存入数据库
        """
        if os.path.isfile(self.path): 
            if self.path.endswith(".pdf"):
                self.pdfname = os.path.basename(self.path)
            else:print("-d 参数传入文件路径后缀名应是pdf")
        else:
            pdf_folder = self.get_pdf_file(os.getcwd()+"\\cases")
            self.pdfname = myformat.fuzzymate(self.path, pdf_folder)[1]
        pdffile_parser.PdfParser().get_pdf_info(self.pdfname)
        self.name = self.pdfname.replace(".pdf","")
        save = save_read_db.case_save2_db()
        save.json_notin_db(self.name)

    @myformat.banner_conclusion("CASES解析生成FEATURES文件",critical=True)
    def caseparser(self):
        """
            调用 core/case_parser 模块解析Cases并生成feature文件
            解析完成后,调用 tools/save_and_read 模块将解析数据存入数据库
        """
        case = case_parser.CaseParser()
        case.get_info_from_db(self.name)
        case.analysis()
        self.featuresave()

    @myformat.banner_conclusion("FEATURES文件存入数据库",critical=True)
    def featuresave(self):
        """
            解析完成后,调用 tools/save_and_read 模块将feature文件存入数据库
        """
        save_read_db.feature_save2_db(self.name)

    @myformat.banner_conclusion("BEHAVE自动化运行", critical=True)
    def behave_exe(self,feature="",tags=""):
        # Todo 对feature参数进行限制判定
        """
            调用CMD执行behave
            目前对behave命令行的封装只支持少量命令,更多命令待后续支持
        """
        if tags == "":
            subprocess.run("behave  %s --no-capture  --summary"%feature)
        else:
            subprocess.run("behave %s --tags %s --no-capture  --summary" %(feature,tags))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=u" 基于 behave 设计自动化框架，命令行解析 ")
    parser.add_argument("-p","--pdf", help="Test cases pdf file path", dest="pdf_path", default="")
    parser.add_argument("-m","--mongodb", help="Whether to open MongoDB database service", dest="mongo", default=True,type=bool)
    parser.add_argument("-f","--feature", help="Features folder or file", dest="feature_path", default="")
    parser.add_argument("-t","--tag", help="Features tags", dest="tags", default="")

    args = parser.parse_args()

    if args.pdf_path != "":
        p = Run(args.pdf_path)
        p.pdfparser()
        p.caseparser()
    elif args.feature_path != "":
        if args.tags !="":
            Run(args.feature_path).behave_exe(args.feature_path,args.tags)
        else:
            Run(args.feature_path).behave_exe(args.feature_path)
    else:
        print("命令输入格式不正确")

