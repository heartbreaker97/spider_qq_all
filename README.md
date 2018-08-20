# spider_qq_all
爬取所有qq资料和说说，预计一天爬取20w条资料和150w条说说

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
>1. 修改配置文件config.ini的配置
>2. 运行cookie.py，生成cookie文件
>3. 运行spider.py，爬取数据

## 后续改进目标
    1.切换多个小号爬取数据，防止qq被封
    2.加入数据分析功能
    3.代码重构修改加快爬虫速度
