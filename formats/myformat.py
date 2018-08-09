# -*- coding: UTF-8 -*-

"""
    Initialize the logging service,and define the output format to make it uniform
    ---------------------------------- ---------------------------------- -------------------------------
        __version__ = "V1.0"
        __completion__ = "2018-08-09"
        __author__ = "yewei"
        Recorded :
                1. 2018-07-25 Mylog类支持 features 目录下运行代码时建立日志
                2. 2018-07-26 修复bug，format_log函数包含相同字段的误匹配，如Password
                3. 2018-07-26 修复bug，format_log函数同级日志下持续输出
                4. 2018-08-09 Release V1.0 create_html_report 和 open_report 移到myformat模块下处理
    ---------------------------------- ---------------------------------- -------------------------------
"""

import os
import re
import sys
import queue
import logging
import datetime
import functools


temp_log_save = []
temp_log_save_for_mongodb = []

class MyLog():
    def __init__(self, name = "TestRun"):
        logname = name + '_brief.txt'
        detailname = name + '_detail.txt'
        briefname = name + '_result.txt'
        runname = "TestRun"+ '_runlog.txt' # 存入所有脚本执行痕迹

        workingpath = os.getcwd()
        if (os.path.basename(workingpath))== "features":
            current = os.path.dirname(workingpath)
        else :current = workingpath

        logpath = os.path.join(current, 'external\\logs\\' + logname)
        detailpath = os.path.join(current, 'external\\logs\\' + detailname)
        briefpath = os.path.join(current, 'external\\logs\\' + briefname)
        runpath = os.path.join(current, 'external\\logs\\' + runname)

        global logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        general = logging.FileHandler(logpath, 'w')
        general.setLevel(logging.INFO)

        detail = logging.FileHandler(detailpath, 'w')
        detail.setLevel(logging.DEBUG)

        brief = logging.FileHandler(briefpath, 'w')
        brief.setLevel(logging.WARNING)

        runlog = logging.FileHandler(runpath, 'a+')
        runlog.setLevel(logging.DEBUG)

        logger.addHandler(general)
        logger.addHandler(detail)
        logger.addHandler(brief)
        logger.addHandler(runlog)

        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        # runformatter = logging.Formatter()
        detail.setFormatter(formatter)
        brief.setFormatter(formatter)
        general.setFormatter(formatter)
        runlog.setFormatter(formatter)

        logger.debug("\n\n"+25 * '*' + '  Started  ' + 25 * '*'+"\n\n")

def logged(s=""):
    nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(s,str):
        if re.search("(Assert|Error)[:|：]", s, re.I) != None:
            level = 50
        elif re.search("Pass[:|：]", s, re.I) != None:
            level = 40
        elif re.search("Failed[:|：]", s, re.I) != None:
            level = 30
        elif re.search("Debug[:|：]", s, re.I) != None:
            level = 20
        elif re.search("Return|Send|Read|Read|Write|Info(?= ：|:)", s, re.I) != None:
            level = 10
        else:level = 0

        for line in s.splitlines(False):
            if level == 50:
                logger.error(5 * "!" + '   %s   '%line)
                temp_log_save.append("[%s  ERROR]  %s"%(nowtime,line))
                temp_log_save_for_mongodb.append("[%s  ERROR]  %s"%(nowtime,line))
    
            elif level == 40:
                logger.warning(5 * "=" + '   %s   ' % line)
                temp_log_save.append("[%s  WRANING]  %s"%(nowtime,line))
                temp_log_save_for_mongodb.append("[%s  WRANING]  %s"%(nowtime,line))

            elif level == 30:
                logger.warning(5 * "=" + '   %s   '%line)
                temp_log_save.append("[%s  WRANING]  %s"%(nowtime,line))
                temp_log_save_for_mongodb.append("[%s  WRANING]  %s"%(nowtime,line))

            elif level == 20:
                logger.debug(5 * "?" + '   %s   ' % line)
                temp_log_save.append("[%s  INFO]  %s"%(nowtime,line))
                temp_log_save_for_mongodb.append("[%s  INFO]  %s"%(nowtime,line))

            elif level == 10:
                logger.info(5 * "-" + '   %s   ' % line)
                temp_log_save.append("[%s  INFO]  %s"%(nowtime,line))
                temp_log_save_for_mongodb.append("[%s  INFO]  %s"%(nowtime,line))

            else:
                logger.debug(5 * "*" + '   %s   '%line)
                temp_log_save.append("[%s  DEBUG]  %s"%(nowtime,line))
                temp_log_save_for_mongodb.append("[%s  DEBUG]  %s"%(nowtime,line))
    else:
        logger.debug(5 * "?" + '   格式化输出失败，输出语句应为 String 类型    ')
        temp_log_save.append("[%s  DEBUG]  %s" % (nowtime, s))
        temp_log_save_for_mongodb.append("[%s  DEBUG]  %s" % (nowtime, s))

def format_log(s=""):
    """
    格式化打印log信息,控制台print 信息

    传参声明：
    s:需要输出到控制台以及日志文件的信息字段
    
    信息格式分4级：
    
    ERROR：测试结果判定信息
           logging.error("Assert: ")
           控制台打印:蓝色字体输出控制台,! 引导输出

            
    WARNING：测试结果，结论性语句
             logging.warning("Pass:/Failed:")
                Pass:测试结果与预期一致
                Failed：测试结果与预期不一致
             控制台打印:绿色(Pass)/红色(Failed)字体输出控制台,= 引导输出

    INFO：测试过程返回值等相关信息
          logging.info("Return:/Send:/Read:/Write:")
                Return:由调用函数返回语句
                Send： 向调用函数传参语句
                Read:  由外部设备读取语句
                Write: 向外部设备写入语句
          控制台打印: 正常输出，- 引导输出

    DEBUG：程序执行消息，要求指明出现异常的具体函数位置
           logging.debug("Debug:/Notice: %s  -- 错误信息 --"%正在执行的模块名)
                Debug: 异常性信息，主要用于告知代码执行异常中断
                Notice：引导式语句，主要用于指明模块执行
           控制台打印：debug 蓝色字体输出控制台,? 引导输出
                       notice 正常输出, * 引导输出
    
    """
    if isinstance(s,str):
        if re.search("(Assert|Error)[:|：]", s, re.I) != None:
            level = 50
        elif re.search("Pass[:|：]", s, re.I) != None:
            level = 40
        elif re.search("Failed[:|：]", s, re.I) != None:
            level = 30
        elif re.search("Debug[:|：]", s, re.I) != None:
            level = 20
        elif re.search("Return|Send|Read|Read|Write|Info(?= ：|:)", s, re.I) != None:
            level = 10
        else:level =0

        for line in s.splitlines(False):
            if level == 50:
                print("\033[1;36m"+ "%s"%line +"\033[0m")
                logger.error(5 * "!" + '   %s   '%line)

            elif level == 40:
                print("\033[0;32m"+"%s"%line+ "\033[0m")
                logger.warning(5 * "=" + '   %s   ' % line)

            elif level == 30:
                print("\033[0;31m"+"%s"%line+ "\033[0m")
                logger.warning(5 * "=" + '   %s   '%line) 

            elif level == 20:
                print("\033[1;34m" + "%s" % line + "\033[0m")
                logger.debug(5 * "?" + '   %s   ' % line)

            elif level == 10:
                print(line)
                logger.info(5 * "-" + '   %s   ' % line)

            else:
                print(line)
                logger.debug(5 * "*" + '   %s   '%line)
    else:
        print("\033[1;34m" + " Debug: 格式化输出失败，输出语句应为String类型 " + "\033[0m")
        logger.debug(5 * "?" + '   格式化输出失败，输出语句应为String类型    ')

def banner_conclusion(description,critical=False):
    """
       函数方法执行前欢迎语句，结束语句，以及执行的异常处理
       方法执行出现异常之后，需要指明方法名称，以便于调试
       传参声明：
       description:需要在函数执行前后打印的语句
       critical:方法严重性标志，此标志为真时，如执行方法时出现异常，则上报异常，终止程序运行
       """
    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            try:
                format_log("Notice: 正在执行: %s  ..." % description)
                result = func(*args, **kwargs)
                # format_log("Notice: 执行完成: %s  ..." % description)
                if result != None: return result
            except Exception as e:
                format_log("Debug: 执行函数 %s 出错 -- 错误信息: %s --" % (func.__name__, e))
                format_log("Debug: 异常TrackBack 追踪信息:\n %s\n%s\n%s\n"%(sys.exc_info()))
                if critical:
                    raise Exception
            finally:format_log("Notice: 执行完成: %s  ..." % description)
        return inner
    return outer
 
@banner_conclusion("模糊匹配获取最优值", critical=True)
def fuzzymate(query_value, match_source):
    """
        对输入的query_value 字段在列表match_source中寻找近似匹配:
            1. 全值匹配，优先级最高
            2. 全局匹配，优先级次之
            3. 未匹配命中，不存入队列
    """
    suggestions = queue.PriorityQueue()
    pattern = '.*'.join(query_value)
    reg = re.compile(pattern, re.I)
    for priorty, item in enumerate(match_source):
        if re.search(query_value, item, re.I):
            suggestions.put((priorty, item))
        elif reg.search(item):
            suggestions.put((priorty+10, item))
    if not suggestions.empty():
        return suggestions.get()
    else:
        raise ValueError("Debug:fuzzymate: 队列值为空，无法获取")

class TestFailedError(Exception):
    def __init__(self, ErrorInfo = "Failed Error"):
        super().__init__(self)
        if not re.match("Failed[：|:]",ErrorInfo,re.I): ErrorInfo = "Failed:  %s"%ErrorInfo
        self.errorinfo = ErrorInfo
        import traceback
        self.f = traceback.extract_stack()[-2][2]
        format_log("Failed:方法:%s 测试失败 -- 失败信息 --%s" % (self.f, self.errorinfo))

    def __str__(self):
        return "Failed:方法:%s 测试失败 -- 失败信息 --%s"%(self.f,self.errorinfo)
    
@banner_conclusion("生成html格式报告文件", critical=True)
def create_html_report(context, name="AutoTest"):
    from jinja2 import Environment, FileSystemLoader
    PATH = os.getcwd() + "\\template"
    TEMPLATE_ENVIRONMENT = Environment(loader=FileSystemLoader(PATH), keep_trailing_newline=True, autoescape=True)
    fname = os.getcwd() + '\\external\\reports\\AutoTest_Reports_For_%s.html' % name
    with open(fname, 'w', encoding="utf-8") as f:
        html = TEMPLATE_ENVIRONMENT.get_template("index.html",PATH).render(context)
        f.write(html)
    open_report(fname)

@banner_conclusion("默认浏览器打开报告", critical=True)
def open_report(path):
    import webbrowser
    webbrowser.open(path)