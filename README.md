# spider_qq_all
爬取所有qq资料和说说，预计一天爬取20w条资料和300w条说说

## 目录文件说明
    ├── config.ini  配置文件
    ├── cookie.py  生成cookie
    ├── DB.py  操作数据库类
    └── spider.py 爬虫类

## 运行环境
    python版本 -> python3.7
    mysql版本 -> mysql5.7
    pip版本 -> pip3

## 代码运行流程
>1. 修改配置文件config.ini的配置，[qq]下的name1和pwd1填写自己的qq和密码，qq_count是小号的个数(5~6个小号最好)
>2. 运行cookie.py，生成多个cookie文件
>3. 运行DB.py,生成数据库表
>4. 运行spider.py，爬取数据并写入数据库

## 目前存在问题
>1. 爬虫运行一段时间后报错： Process finished with exit code -1073741819 (0xC0000005)，目前还不知道原因
>2. 轮着换小号来爬数据，还是会被封，只不过是时间延后了

## 后续优化方向
>1. 加入数据分析功能
>2. 加强运行稳定性
>3. 如果遇到禁止ip访问，那么需要加入代理IP池更改ip进行访问
