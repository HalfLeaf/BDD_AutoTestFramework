
## AutomatedTestFramework-Design-Basedon-Behave 

**BDD framework built using Python and Behave to support automation testing**

### Prerequisities

*   **Python version  >=  3.6.2**
*   **java version    >=  SE 8**    
*   **MongoDB version >=  3.6.5**


**And installation required python module, you can input the following command in cmd window:**


>> pip install -r requirements.txt


### Tutorial

##### _First you need to prepare a test case PDF document, which is presented in tabular form with the necessary information in the following format:_

![casestable][/formats/case.png]

> The left column represents the title, which was marked * and must appear in the document, which can cause an unknowable error.
>
> And the contents of this column must be written with top alignment 

> The column on the right is what it says
>
> And the first line represents Casename, where the "*" appears anywhere, indicating that the use case does not support automation
>
> The test step must be indicated with a 1.2.2.step-up sequence number.
> Each sequence number is a complete test process, and its execution result is consistent with the corresponding sequence number in the expected result column
>

##### _Then you can  execute the following command to create the feature files that behave runs_

>> python -3 Scheduler.py [-p|--pdf]  pdf_file_name


##### _Next you need to write a test script, use the behave framework, suggest a feature file corresponding to a python script file_


> Place Commands and Results in the libs directory;These two files are used to store the variable parameters required for the test
> The environment file will be imported automatically without importing when used. 
> To invoke the relevant parameters in these two files, the script must be called through the converter function.
> so the following statement must be written in the script: 
>> from core.Converter import get 
> or  
>>from core.Converter import GET 
> or 
>> from core.Converter import Get


> These three forms are equivalent



> The Results file gets only global variables, and function and class instance properties are not obtained
> Commands has already created some global attributes in advance, and these variable names are not allowed to change.
> You can also create some other global constants with unique names.
> In addition, the commands sent to the device are reflected in the class instance attribute.
> And the order in which they are created is the order in which the commands are sent to the device. 
> Such as:


>>
>> class cmd():
>>>   def __init__(self):
>>>>       self.c1 = "comand1"
 
>>>   def command(self):
>>>>      self.c2 = "comand2"
>>>>      self.c3 = "comand3"
>>>>      self.c4 = "comand4"
>>



> The last thing to note:
> 
> The Results and Commands files are in the libs directory, and all your scripts should be in the steps directory


##### _After you've written all the scripts, how do you run the scripts for testing_

> Just input the following command in cmd window,and wait,then get test results:


>>
>> python -3 Scheduler.py [-f|--feature]   [feature filename|project folder]  or
>> python -3 Scheduler.py [-f|--feature]   project folder [-t|--tag] tags
 

> feature filename,Specify file name,and run only the script corresponding to this feature file
>
> project folder,all scripts in this folder will be ran
