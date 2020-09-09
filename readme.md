Web Api Test
===========================

python开发的web api测试框架,可使用json与csv编写用例，与post_man无缝衔接。


安装
-------

        pip install webapitest
        注：如果直接用源码执行webapitest，将以下所有命令中的webapitest替换为python -m webapitest.main即可
    

 运行
------------
    
1、配置你的网站地址、数据库连接等基本参数。
   
2、部署并启动你的网站
    
3、执行如下命令，获得测试报告
    
    webapitest run

4、或执行如下命令，分步执行测试

    a、webapitest cleandb
    b、webapitest initdb
    c、webapitest startwebserver
    d、webapitest runcase xxx
 
 
基本概念
-------

-   用例

    测试行为的基本概念。一个用例用于测试基本的某个特性，其中有若干参数。同用户同url的用例，会集成为一个场景。
    
-   场景
    
    模拟某个用户使用某个接口的情景。一个场景下会有多个用例。每个场景都用一份json文件来描述。用例数据是一个文件夹，里面包含了多个场景文件。
    

部署 & 准备
------

webapitest可以帮助你完成自动化接口测试。执行run命令即可完成完整测试流程。但在执行它之前，您必须思考解答以下问题：

-   测试的接口是否需要登录？
    
    测试是模拟真实用户场景，与正常用户的操作仅是缺少网站界面而已。未登录进行接口测试会得到网站对未登录状态的响应。
    
    想要进行登录再测试，需要在conf中配置登录场景。并可一次性配置多个用户登录，在执行各测试场景时自由切换用户。

-   如何切换模拟测试用户？

    方法一、在测试用例场景文件中指定user属性
    
    方法二、执行webapitest runcase 命令时加参数 --user=xxx
    
  
-   测试接口是否进行了持久化动作？
    
    注意你的测试数据会被保存到数据库中。这可能导致糟糕的结果：同样的测试不断执行，接口可能响应不同结果。例如，测试新增用户，第一次新增用户"张三"成功，第二次执行测试新增"张三"失败。因为发生了同名。
    直接在测试环境和线上环境测试GET(只读)接口，一般不会构成不良影响。但很多接口，可能无法这样执行。
    
-   是否需要准备测试数据库？
    
    当必须测试持久化接口时，webapitest提供的标准解决方案是：每次测试使用全新数据库。
    测试总是会生产测试数据，在下一次执行测试前清理掉数据库。命令:webapitest cleandb。
    网站需要提供数据库初始化命令，保证网站的正常运作。命令：webapitest initdb。
    cleandb和initdb命令需要用户在conf中做好配置。
    
-   预订的测试目标网站已稳定部署，准备好迎接测试了吗？ 
    
    做好配置，确保执行如下命令时：webapitest startwebserver，网站可正常启动。人为在浏览器中输入url模拟测试，应能获得预期结果。
    执行命令webapitest execute，开始运行测试，结果会存储到一份json文件中。
    分布完成测试命令后，可以执行webapitest run一次完成流程。
    
配置
------

-   测试网站配置

    
    
-   测试用例配置

-   测试数据库清理配置

-   测试网站初始化配置

与Postman
---------

-   Postman是接口测试最常见的工具之一，具有用例执行、导出等功能。webapitest完美支持Postman的使用。
    
-   在Postman中选择文件夹，右键导出，可得一份xxx.collection.json用例文件。
    
-   执行如下命令，可以获得标准用例并执行。
    
-   分步执行：
     
        a、webapitest parse xxx.collection.json --casedir cases
        b、webapitest execute cases
    
    
-   一步执行：
    
    webapitest run_postman_collection xxx.collection.json
    
    
其它常见命令
---------

-   执行webapitest --help查看所有命令;执行webapitest xx --help查看该命令参数和说明

-   将用例文件转化为Postman的json文件

        webapitest parse2postmanfile <casedir> --postmanfile xxx.json
    
-   用用例文件中的json文件生产csv文件，如已经存在csv，直接覆盖。(注：使用git管理用例，每个版本文件都在，不担心丢~)

        webapitest createcsv <casedir>

-   用用例文件中的csv文件生产json文件，如已经存在json，直接覆盖。

        webapitest resetjsonbycsv <casedir>
    
