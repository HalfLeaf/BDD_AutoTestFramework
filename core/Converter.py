# - * - coding: utf-8 -*-

"""
    Read the commands from Commands.py,and then issued to the device
    ---------------------------------- ---------------------------------- ------------------------------
        __version__ = "V1.0"
        __completion__ = "2018-08-09"
        __author__ = "yewei"
        Recorded :
                1. Release V1.0
    ---------------------------------- ---------------------------------- -------------------------------
"""

import re
import time
import importlib
import telnetlib
from formats import myformat

def import_command_result(moudle):
    """
        动态导入Commands 和 Results 模块
    """
    global Commands
    Commands = importlib.import_module("features.%s.libs.Commands"%moudle)
    global Results
    Results =  importlib.import_module("features.%s.libs.Results"%moudle)

class Acquire():
    def get(self,func,*args, **kwargs):
        """
            func: 函数名 或者 常量变量值
            args: 可变参数,若 args 第一个变量值是整数值,则将其提取出来,作为 telnet 下发命令时time 等待值
            kwargs: 关键值参数,用于类方法传参
        """
        self.func = func

        if args != () and isinstance(args[0],int):
            self.timeT = int(args[0]) 
            args = args[1:]
        else:
            self.timeT = 0.3

        views = [v for v in dir(Results) if not v.startswith("__")]
        for view in views:
            if self.func == view:
                return self._get_results()

        self.p = []
        coms = [v for v in dir(Commands) if not v.startswith("__")]
        for c in coms:
            p = eval("Commands.%s" % c)
            if isinstance(p,type):
                if self.func in dir(eval("Commands.%s()" % c)):
                    self.p.append(c) 
            else:
                if self.func == c:
                    return self._get_commands_globals()
        if len(self.p) > 1:raise ValueError("Debug: Issue.get: 方法 %s 在Command中有多个实现")
        elif len(self.p) == 1:return self._get_commands(*args, **kwargs)
        else:
            raise NotImplemented("Debug:Obtain.get: 方法 %s 未在Command中实现")

    @myformat.banner_conclusion("获取命令集实例属性",critical=True)
    def _get_commands(self,*args, **kwargs):
        """
            获取 Commands 命令集中的类实例方法属性值,不会获取函数属性值,全局常量属性值
            cls: 类初始化
            attributes:类实例属性
        """
        myformat.logged("Read: 获取方法 %s 属性值 " %self.func)
        self.commands = [Commands.login_in_dut, Commands.passwd_for_dut]
        cls = eval("Commands.%s()"%("".join(self.p)))
        getattr(cls,self.func)(*args, **kwargs)
        attributes = cls.__dict__
        for v in attributes.values():
            self.commands.append(v)
        return self._issue()

    @myformat.banner_conclusion("获取命令集全局变量",critical=True)
    def _get_commands_globals(self):
        """
            获取 Commands 命令集中的常量参数,不会获取函数方法属性值
            要求 Commands 命令集中的常量参数 位于 全局
        """
        value = self.func.replace(" ", "")
        attribute =  getattr(Commands, value)
        myformat.logged("Read: 获取Results中属性值(%s = %s) " % (self.func, attribute))
        return attribute

    @myformat.banner_conclusion("获取Results结果集参数")
    def _get_results(self):
        """
            获取 Results 结果集中的常量参数,不会获取函数方法属性值
            要求 Results 结果集中的常量参数 位于 全局
        """
        value = self.func.replace(" ", "")
        attribute =  getattr(Results, value)
        myformat.logged("Read: 获取Results中属性值(%s = %s) " % (self.func,attribute))
        return attribute

    @myformat.banner_conclusion("Telnet设备下发命令,并获取回显",critical=True)
    def _issue(self):
        """
            向指定的设备下发获取到命令集中的命令,并进行初步校验,确保命令正确下发到设备
                return：所有命令下发完成后,返回抓取到回显
        """
        tn = telnetlib.Telnet(Commands.remote_dut_ip, Commands.remote_dut_port, timeout=20)
        for cmd in self.commands:
            myformat.logged("Write: 正在向 %s 下发命令: %s"%(Commands.remote_dut_ip, cmd))
            tn.write(cmd.encode('utf-8') + b"\n")
            time.sleep(self.timeT)
            rtn_ = tn.read_very_eager()
            if re.search("ERROR: Error command|Unknown command|Too many parameters",rtn_.decode("utf-8")):
                myformat.logged("Read: 获取设备回显信息\n-*--*-\n %s  \n-*--*- "%rtn_.decode("utf-8"))
                raise myformat.TestFailedError("命令(%s)下发失败,无法继续进行测试"%cmd)
            else:
                tn.cookedq = rtn_
        time.sleep(5)
        rtn = tn.read_very_eager(). decode('utf-8')
        myformat.logged("Read: 获取设备回显信息\n-*--*-\n %s  \n-*--*- "%rtn)
        return rtn


def get(func,*args, **kwargs):
    p = Acquire()
    return p.get(func,*args, **kwargs)

def GET(func,*args, **kwargs):
    p = Acquire()
    return p.get(func, *args, **kwargs)

def Get(func,*args, **kwargs):
    p = Acquire()
    return p.get(func, *args, **kwargs)