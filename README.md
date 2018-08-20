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
>3. 运行spider.py，爬取数据并写入数据库

## 后续改善目标
>1. 加入数据分析功能
>2. 代码重构修改加快爬虫速度
>3. 如果遇到禁止ip访问，那么需要加入代理IP池更改ip进行访问
