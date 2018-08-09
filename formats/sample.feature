格式约定：
@case-xx @                                               --- 标签
Feature: Test Subject                                    --- 特征
  Test Purpose                                           --- 描述
  
  Background: casex-bg                                   --- 背景
	Given Test Configuration                             --- 前置条件,针对所有场景
	  
  Scenario Outline: use data with <thing>                --- 场景大纲，按照示例表遍历场景大纲的case
	When I get "<vlaue>" from examples
	And  Do Square mathematical operations
	Then I get results from "<square>"

	Examples: casex-S1    # S2: 第2步测试步骤             --- 示例表
		| value | square | 
		| 1     | 1      |
		| 2     | 4      |
	
  Scenario: casex-R2    # R2: 第2步测试结果                --- 场景
	"""
		Steps:
			S1
			S2
		Results:
			R2
	"""                                                          
	When Test Procedure - S1                              --- 测试步骤
	And Test Procedure - S2                               --- 测试步骤
	Then Expected Results - R2                            --- 测试结果
	
	
	同级对齐，次级换行并空2格
	
	背景必须在场景及场景大纲前定义
	
	表格换行空4格
	
	  
	  
	  
  Tag (as Feature.tags)
Feature : TaggableModelElement
    Description (as Feature.description)

    Background
        Step
            Table (as Step.table)
            MultiLineText (as Step.text)

    Tag (as Scenario.tags)
    Scenario : TaggableModelElement
        Description (as Scenario.description)
        Step
            Table (as Step.table)
            MultiLineText (as Step.text)

    Tag (as ScenarioOutline.tags)
    ScenarioOutline : TaggableModelElement
        Description (as ScenarioOutline.description)
        Step
            Table (as Step.table)
            MultiLineText (as Step.text)
        Examples
            Table