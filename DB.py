import configparser
import pymysql

#定义数据操作类
class Db:
    #数据库连接
    def __init__(self):
        #读取数据库配置
        conf = configparser.ConfigParser()
        conf.read('config.ini')
        host = conf.get('db','host')
        user = conf.get('db','user')
        pwd = conf.get('db','pwd')
        db_name = conf.get('db','db_name')
        #连接数据库
        try:
            self.con = pymysql.connect(host, user, pwd, db_name)
            self.cursor = self.con.cursor()
        except Exception as e:
            print('数据库连接错误')
        #print(type(con))

    #创建数据库表
    def db_create(self):
        #qq用户信息表
        sql_qq_infor = """CREATE TABLE qq_infor (
                    `qq` BIGINT NOT NULL,
                    `parent_qq` BIGINT NOT NULL,
                    `depth` INT NOT NULL,
                    `is_access` INT(1),
                    `sex` INT(1),
                    `nick_name` VARCHAR(100),
                    `qzone_name` VARCHAR(100),
                    `last_message` VARCHAR(500),
                    `ptime` DATETIME,
                    `birth_year` INT,
                    `birth_day` CHAR(5),
                    `tool` VARCHAR(50),
                    `province` VARCHAR(10),
                    `city` VARCHAR(10),
                    `hp` VARCHAR(10),
                    `hc` VARCHAR(10),
                    `marriage` INT(1),
                    PRIMARY KEY(`qq`))"""
        #说说表
        sql_topic = """CREATE TABLE qq_topic (
                   `tid` INT NOT NULL AUTO_INCREMENT,
                   `content` VARCHAR(500),
                   `time` DATETIME,
                   `qq` BIGINT,
                   UNIQUE KEY(`tid`)
                   )"""
        try:
            self.cursor.execute(sql_qq_infor)
            self.cursor.execute(sql_topic)
        except Exception as e:
            print('创建表失败,错误信息为: '+str(e))

    #插入infor表数据方法
    def insert_infor(self,my_infor, flag):
        if flag == 1:
            sql_insert = """INSERT INTO qq_infor VALUES {infor}""".format(infor = my_infor)
            print(sql_insert)
        else:
            sql_insert = """INSERT INTO qq_infor(`qq`,`parent_qq`,`depth`,`is_access`) VALUES {infor}""".format(infor = my_infor)
        try:
            self.cursor.execute(sql_insert)
        except Exception as e:
            print('数据插入信息表错误,错误信息为：'+str(e))


    #插入topic表数据方法
    def insert_topic(self, my_topic):
        sql_insert = """INSERT INTO qq_topic(`content`,`time`,`qq`) VALUES {topic}""".format(topic = my_topic)
        try:
            self.cursor.execute(sql_insert)
        except Exception as e:
            print('数据插入说说表错误,错误信息为：'+str(e))

    #更新
    def update_infor(self, my_last_message, my_tool,my_qq):
        sql_update = """UPDATE qq_infor SET `last_message`='{last_message}',`tool`='{tool}' WHERE `qq`={qq}""".format(last_message=my_last_message,tool=my_tool,qq=my_qq)
        try:
            self.cursor.execute(sql_update)
        except Exception as e:
            print('数据更新信息表错误,错误信息为：' + str(e))

    #统一提交
    def commit(self):
        try:
            self.con.commit()
        except Exception as e:
            self.con.rollback()
            print('数据提交错误,错误信息为：'+str(e))

    #关闭连接
    def close(self):
        try:
            self.con.close()
        except Exception as e:
            print('数据库关闭异常，错误信息为'+str(e))

    #定义初始化入口,构建数据表
    def start(self):
        self.db_create()

if __name__ == '__main__':
    db = Db()
    db.start()