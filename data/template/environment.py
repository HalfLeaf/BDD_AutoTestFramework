# -*- coding: UTF-8 -*-
"""
before_step(context, step), after_step(context, step)
    These run before and after every step.
    The step passed in is an instance of Step.

before_scenario(context, scenario), after_scenario(context, scenario)
    These run before and after each scenario is run.
    The scenario passed in is an instance of Scenario.

before_feature(context, feature), after_feature(context, feature)
    These run before and after each feature file is exercised.
    The feature passed in is an instance of Feature.

before_tag(context, tag), after_tag(context, tag)

"""

import os
import sys
import json
import copy
import datetime
import collections
from core import Converter
from formats import myformat
from tools.mongo import save_read_db
from xml.etree import ElementTree as ET

featurefile = sys._getframe().f_code.co_filename

def timeformat():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def before_all(context):
    myformat.MyLog("BehaveTestRun")
    feature_folder = save_read_db.log_save2_db(featurefile).clearall()
    Converter.import_command_result(feature_folder)
    context._feature_exe_total = 0
    context._analysis = {}
    _all_start_time = timeformat()
    context._analysis['CaseName'] = feature_folder
    context._analysis["BeginTime"] = _all_start_time
    context._xml_root = ET.Element("root",{'AutoTest':feature_folder,"BeginTime":_all_start_time})
    begin = ET.SubElement(context._xml_root,"Begin")
    begin.text = "\n" + 8 * "=" + "   开始执行 Behave 自动化测试   " + 8 * "=" +"\n"
    myformat.logged("Notice: 开始执行 Behave 自动化测试   ")
    context._analysis["scenario_pass"] = []
    context._analysis["scenario_failed"] = []
    context._analysis["scenario_skipped"] = []

    context._analysis["feature_pass"] = []
    context._analysis["feature_failed"] = []
    context._analysis["feature_skipped"] = []
    
    context._feature_temp_list = []

def before_feature(context, feature):
    context.reply = {}
    context._log_for_mongo = {}
    _feature_start_time = timeformat()

    context._feature_temp_dict = {}
    context._scenario_temp_list = []
    
    _scenario_num = len(feature.scenarios)
    context._xml_feature = ET.SubElement(context._xml_root,"feature",{'Feature':feature.name ,"BeginTime":_feature_start_time,
                                                            "ScenariosTotal":"%s"%_scenario_num,})
    begin = ET.SubElement(context._xml_feature, "Begin")
    begin.text ="\n" + 8 * "*" + "   开始执行自动化 Case - Feature:  %s   "%feature.name+ 8 * "*" +"\n"
    des = ET.SubElement(context._xml_feature, "description")
    descrip = ("\n".join(feature.description))
    des.text ="\n" + 8 * " " + "Case - Feature - description :  %s   "%descrip + 8 * " " +"\n"
    myformat.logged("Notice: 开始执行自动化 Case - Feature:  %s "%feature.name)
    context._feature_temp_dict["Begintime"] = _feature_start_time
    context._feature_temp_dict["Description"] = descrip
    context._feature_temp_dict["Feature"] = feature.name
    context._feature_temp_dict["ScenariosTotal"] = _scenario_num

def before_scenario(context, scenario):
    context.response = {}
    context._step_pass = []
    context._step_failed = []
    context._step_skipped = []

    context._scenario_temp_dict = {}
    context._step_temp_list = []

    _scenario_start_time = timeformat()
    _step_num = len(scenario.steps)
    context._xml_scenario = ET.SubElement(context._xml_feature,"scenario",{'Scenario':scenario.name,"BeginTime":_scenario_start_time,
                                                                "StepsTotal":"%s"%_step_num,})
    begin = ET.SubElement(context._xml_scenario, "Begin")
    begin.text = "\n" + 8 * "-" + "   开始执行自动化 Case - Scenario:  %s   "%scenario.name + 8 * "-" +"\n"
    des = ET.SubElement(context._xml_scenario, "description")
    descrip = "\n\t\t".join(scenario.description)
    des.text ="\n" + 8 * " " + "Case - Scenario - description :\n  %s   "%descrip + 8 * " " +"\n"
    myformat.logged("Notice: 开始执行自动化 Case - Scenario:  %s "%scenario.name)
    
    context._scenario_temp_dict["Begintime"] = _scenario_start_time
    context._scenario_temp_dict["Texts"] = descrip
    context._scenario_temp_dict["Scenario"] = scenario.name
    context._scenario_temp_dict["StepsTotal"] = _step_num

def before_step(context, step):
    _step_start_time = timeformat()
    context._step_temp_dict = {}
    context._xml_step = ET.SubElement(context._xml_scenario,"step",{'Step':step.name,"BeginTime":_step_start_time })
    begin = ET.SubElement(context._xml_step, "Begin")
    begin.text = "\n" + 8 * ">" + "   开始执行自动化 Case - Step:  %s   "%step.name + 8 * ">" +"\n"
    myformat.logged("Notice: 开始执行自动化 Case - Step:  %s   "%step.name)
    
    context._step_temp_dict["Begintime"] = _step_start_time
    context._step_temp_dict["Step"] = step.name

def after_step(context, step):
    _step_end_time = timeformat()
    context._xml_step.set("EndTime",_step_end_time)
    context._xml_step.set("Uptime","%s"%step.duration)
    context._xml_step.set("Status","%s"%step.status)
    end = ET.SubElement(context._xml_step, "End")
    end.text = "\n" + 8 * "<" + "   执行完成自动化 Case - Step:  %s   "%step.name + 8 * "<" +"\n"
    myformat.logged("Notice: 执行完成自动化 Case - Step:  %s   "%step.name)
    if step.status == "passed":    context._step_pass.append(step.name)
    elif step.status == "failed": 
        context._step_failed.append(step.name)
        myformat.logged("Debug:异常追踪信息:\n%s\n%s\n%s"%sys.exc_info())
    else:context._step_skipped.append(step.name)
    
    log = ET.SubElement(context._xml_step, "Log")
    log.text ="\n".join(myformat.temp_log_save)
    
    context._step_temp_dict["Endtime"] = _step_end_time
    context._step_temp_dict["Uptime"]="%.3f"%float(step.duration)
    context._step_temp_dict["Status"] = "%s"%step.status
    context._step_temp_dict["Logs"] = copy.deepcopy(myformat.temp_log_save)
    context._step_temp_list.append(context._step_temp_dict)
    myformat.temp_log_save.clear()
  
def after_scenario(context, scenario):
    _scenario_end_time = timeformat()
    context._xml_scenario.set("EndTime",_scenario_end_time)
    context._xml_scenario.set("Uptime", "%s"%scenario.duration)
    context._xml_scenario.set("Status","%s"% scenario.status)
    context._xml_scenario.set("StepsPassNum", "%s" % len(context._step_pass))
    context._xml_scenario.set("PassSteps", "%s" %context._step_pass)
    context._xml_scenario.set("StepsFailedNum", "%s" % len(context._step_failed))
    context._xml_scenario.set("FailedSteps", "%s" % context._step_failed)
    context._xml_scenario.set("StepsSkippedNum", "%s" % len(context._step_skipped))
    context._xml_scenario.set("SkippedSteps", "%s" %context._step_skipped)
    end= ET.SubElement(context._xml_scenario, "End")
    end.text = "\n" + 8 * "-" + "   执行完成自动化 Case - Scenario:  %s   "%scenario.name + 8 * "-" +"\n"
    myformat.logged("Notice: 执行完成自动化 Case - Scenario:  %s  "%scenario.name)
    if scenario.status == "passed":    context._analysis["scenario_pass"].append(scenario.name)
    elif scenario.status == "failed": 
        context._analysis["scenario_failed"].append(scenario.name)
        myformat.logged("Debug:异常追踪信息:\n%s\n%s\n%s" % sys.exc_info())
    else:context._analysis["scenario_skipped"].append(scenario.name)
    
    context._scenario_temp_dict["Endtime"] = _scenario_end_time
    context._scenario_temp_dict["Uptime"]="%.3f"%float(scenario.duration)
    context._scenario_temp_dict["Status"] = "%s"%scenario.status
    context._scenario_temp_dict["StepsPassNum"] = len(context._step_pass)
    context._scenario_temp_dict["PassSteps"] = context._step_pass
    context._scenario_temp_dict["StepsFailedNum"] = len(context._step_failed)
    context._scenario_temp_dict["FailedSteps"] = context._step_failed
    context._scenario_temp_dict["StepsSkippedNum"] = len(context._step_skipped)
    context._scenario_temp_dict["SkippedSteps"] = context._step_skipped
    context._scenario_temp_dict["steps"] = context._step_temp_list
    context._scenario_temp_list.append(context._scenario_temp_dict)

def after_feature(context, feature):
    _feature_end_time = timeformat()
    context._xml_feature.set("EndTime",_feature_end_time)
    context._xml_feature.set("Uptime","%s"% feature.duration)
    context._xml_feature.set("Status","%s"%feature.status)
    context._xml_feature.set("ScenariosPassNum", "%s" % len(context._analysis["scenario_pass"]))
    context._xml_feature.set("PassScenarios", "%s" %context._analysis["scenario_pass"])
    context._xml_feature.set("ScenariosFailedNum", "%s" % len(context._analysis["scenario_failed"]))
    context._xml_feature.set("FailedScenario", "%s" %context._analysis["scenario_failed"])
    context._xml_feature.set("ScenariosSkippedNum", "%s" % len(context._analysis["scenario_skipped"]))
    context._xml_feature.set("SkippedScenario", "%s" %context._analysis["scenario_skipped"])

    context._feature_exe_total += 1
    end = ET.SubElement(context._xml_feature, "End")
    end.text ="\n" + 8 * "*" + "   执行完成自动化 Case - Feature:  %s   "%feature.name + 8 * "*" +"\n"
    myformat.logged("Notice: 执行完成自动化 Case - Feature:  %s   "%feature.name)
    context._log_for_mongo[feature.name] = myformat.temp_log_save_for_mongodb
    save_read_db.log_save2_db(featurefile).write2_db(context._log_for_mongo)
    myformat.temp_log_save_for_mongodb.clear()
    if feature.status == "passed":    context._analysis["feature_pass"].append(feature.name)
    elif feature.status == "failed": 
        context._analysis["feature_failed"].append(feature.name)
        myformat.logged("Debug:异常追踪信息:\n%s\n%s\n%s" % sys.exc_info())
    else:context._analysis["feature_skipped"].append(feature.name)
    
    context._feature_temp_dict["Filename"] = feature.filename
    context._feature_temp_dict["Endtime"] = _feature_end_time
    context._feature_temp_dict["Uptime"]="%.3f"%float(feature.duration)
    context._feature_temp_dict["Status"] ="%s"%feature.status
    context._feature_temp_dict["ScenariosPassNum"] = len(context._analysis["scenario_pass"])
    context._feature_temp_dict["PassScenarios"] = context._analysis["scenario_pass"]
    context._feature_temp_dict["ScenariosFailedNum"] = len(context._analysis["scenario_failed"])
    context._feature_temp_dict["FailedScenarios"] = context._analysis["scenario_failed"]
    context._feature_temp_dict["ScenariosSkippedNum"] = len(context._analysis["scenario_skipped"])
    context._feature_temp_dict["SkippedScenarios"] = context._analysis["scenario_skipped"]
    context._feature_temp_dict["scenarios"] = context._scenario_temp_list
    
    context._feature_temp_list.append(context._feature_temp_dict)

def after_all(context):
    context._xml_root.set("CasesFeaturesExecuteTotal","%s"%context._feature_exe_total)
    context._xml_root.set("FeaturesPassNum","%s"%len(context._analysis["feature_pass"] ))
    context._xml_root.set("PassFeatures", "%s"%context._analysis["feature_pass"])
    context._xml_root.set("FeaturesFailedNum", "%s"%len(context._analysis["feature_failed"]))
    context._xml_root.set("FailedFeatures",  "%s"%context._analysis["feature_failed"])
    context._xml_root.set("FeaturesSkippedNum", "%s"%len(context._analysis["feature_skipped"]))
    context._xml_root.set("SkippedFeatures",  "%s"%context._analysis["feature_skipped"] )
    _all_end_time = timeformat()
    context._xml_root.set("EndTime",_all_end_time)
    start_time = datetime.datetime.strptime(context._analysis["BeginTime"],"%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.strptime(_all_end_time,"%Y-%m-%d %H:%M:%S")
    seconds = (end_time - start_time).seconds
    day = seconds // 86400
    hour = (seconds - day * 86400) // 3600
    minute = (seconds - hour * 3600) // 60
    second = (seconds - hour * 3600 - minute * 60)
    uptime = "(%s)D(%s)H(%s)M(%s)S" %(day,hour,minute,second)
    context._xml_root.set("Uptime", uptime)
    
    context._analysis["Endtime"] = _all_end_time
    context._analysis["Uptime"] = "(%s)天  (%s)时  (%s)分  (%s)秒 " %(day,hour,minute,second)
    context._analysis["FeaturesExecuteNum"] = context._feature_exe_total
    context._analysis["FeaturesPassNum"] = len(context._analysis["feature_pass"] )
    context._analysis["PassFeatures"] = context._analysis["feature_pass"]
    context._analysis["FeaturesFailedNum"] = len(context._analysis["feature_failed"])
    context._analysis["FailedFeatures"] = context._analysis["feature_failed"]
    context._analysis["FeaturesSkippedNum"] = len(context._analysis["feature_skipped"])
    context._analysis["SkippedFeatures"] = context._analysis["feature_skipped"]
    rate =  context._analysis["FeaturesPassNum"]/context._feature_exe_total
    context._analysis["PassedRate"] = rate
    
    name = context._analysis['CaseName']
    with save_read_db.DB_Operation() as db:
        db.auth(name)
        db.create("A")
        db_analysis = db.findall()
        for analy in db_analysis:
            context._xml_root.set("CasesTotal", "%s" %analy["CasesTotal"])
            context._xml_root.set("AutoCasesTotal", "%s" %analy["AutoCasesTotal"])
            context._analysis["CasesTotal"] = analy["CasesTotal"]
            context._analysis["AutoCasesTotal"] = analy["AutoCasesTotal"]
        db.clear("A")
        db.add(context._analysis)

    end = ET.SubElement(context._xml_root,"End")
    end.text = "\n" +8 * "=" + "   执行完成 Behave 自动化测试   " + 8 * "=" +"\n"
    tree = ET.ElementTree(context._xml_root)
    path = os.getcwd() + "\\external\\xml\\AutoTest_Reports_For_%s-%s.xml"%(name,_all_end_time.replace(":",""))
    tree.write(path, encoding="utf-8")
    
    runinfo = collections.OrderedDict()

    runinfo["AutoTest"]  = name
    runinfo["CasesTotal"]  = context._analysis["CasesTotal"]
    runinfo["AutoCasesTotal"] =  context._analysis["AutoCasesTotal"]  
    runinfo["CasesExecuteTotal"]= context._feature_exe_total
    runinfo["Begintime"] = context._analysis["BeginTime"]
    runinfo["Endtime"]   = _all_end_time
    runinfo["Uptime"]  = uptime
    runinfo["FeaturesPassNum"] =len(context._analysis["feature_pass"])
    runinfo["PassFeatures"] =context._analysis["feature_pass"]
    runinfo["FeaturesFailedNum"] =len(context._analysis["feature_failed"])
    runinfo["FailedFeatures"] =context._analysis["feature_failed"]
    runinfo["FeaturesSkippedNum"] =len(context._analysis["feature_skipped"])
    runinfo["SkippedFeatures"] = context._analysis["feature_skipped"]
    runinfo["PassedRate"] = rate
    runinfo["features"] = context._feature_temp_list
    
    jsonpath = os.getcwd() + "\\external\\json\\" + 'AutoRunFor_%s.json'%name
    with open(jsonpath, "w", encoding='utf-8') as f:
        f.write(json.dumps(runinfo))

    myformat.create_html_report(runinfo,name)

    myformat.logged("Notice: 执行完成 Behave 自动化测试   ")