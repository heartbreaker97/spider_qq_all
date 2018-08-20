import urllib
import requests
import json
import re
import threadpool
import threading
import queue
import time
import DB

#切换qq
def change_qq(i):
    global cookie,spider
    if i > 1:
        i = 0
    with open('cookie_dict' + str(i) + '.txt', 'r') as f:
        cookie = json.load(f)
    print('我换个cookie啦')
    spider.g_tk = spider.get_gtk()
    spider.uin = spider.get_uin()
    tmp = i+1
    t = threading.Timer(300, change_qq,[tmp])
    t.start()

#爬虫类
class Spider:
    #初始化
    def __init__(self):
        self.g_tk = self.get_gtk()
        self.uin = self.get_uin()
        self.qq = self.get_qq()
    # 算出来gtk
    def get_gtk(self):
        p_skey = cookie['p_skey']
        h = 5381
        for i in p_skey:
            h += (h << 5) + ord(i)
            g_tk = h & 2147483647
        return g_tk

    # 得到uin
    def get_uin(self):
        uin = cookie['ptui_loginuin']
        return uin

    #将时间戳改成YMDHMS格式
    def transfer_time(self,tramp):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tramp))

    #自定义发送http请求，解析响应json内容方法，返回dict格式
    def get_http_response(self, url, data):
        data_encode = urllib.parse.urlencode(data)
        url += data_encode
        res = requests.get(url, headers=header, cookies=cookie)
        # 踩坑，这里必须加不然会乱码！！！！çŸ³å®¶åº„å想这样子的乱码！
        res.encoding = 'UTF-8'
        try:
            r = re.findall('\((.*)\)', res.text, re.S)[0]
            # 将json数据变成字典格式
            r = json.loads(r)
        except Exception as e:
            print('json格式解析错误: '+str(e))
            r = 0
        finally:
            return r

    # 找出好友列表，昵称+qq的
    def get_friend(self):
        url_friend = 'https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/friend_ship_manager.cgi?'
        g_tk = self.get_gtk()
        uin = self.get_uin()
        data = {
            'uin': uin,
            'do': 1,
            'g_tk': g_tk
        }
        friend_dict = self.get_http_response(url_friend, data)
        friend_result_list = []
        # 循环将好友的姓名qq号存入list中
        for friend in friend_dict['data']['items_list']:
            friend_result_list.append([friend['name'], friend['uin']])
        # 得到的好友list是[[name1,qqNum1],[name2,qqNum2],.....]格式的
        return friend_result_list

    #得到自己的qq好友，开始第一层
    def get_qq(self):
        qq_list = []
        friend_list = self.get_friend()
        for friend in friend_list:
            qq_list.append(friend[1])
        return qq_list

    #得到其他人的qq好友，从所有说说的点赞得到该qq的好友
    def get_others_qq(self,qq):
        #初始化该qq的好友qq_list,以便查重
        qq_list = []
        page = 1
        #循环获得好友前5页的说说，conti循环的标志，当为false时退出循环
        conti = True
        pos = 0
        #用第一条说说更新消息
        is_first = True
        while conti:
            # url必须在循环内，每次循环必须重置
            url = 'https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?'
            data = {
                'uin': qq[0],
                'pos': pos,
                'num': 20,
                'hostUin': self.uin,
                'replynum': 100,
                'callback': '_preloadCallback',
                'code_version': 1,
                'format': 'jsonp',
                'need_private_comment': 1,
                'g_tk': self.g_tk,
            }
            # 下次翻页
            pos += 20
            msg = self.get_http_response(url, data)
            # 如果没有说说就返回
            if 'msglist' not in msg:
                return 0
            #只爬5页说说
            if msg['msglist'] == None or page == 2:
                return 0
            page += 1
            #通过点赞得到该qq的好友
            mutex = threading.Lock()
            if mutex.acquire():
                try:
                    for m in msg['msglist']:
                        self.get_qq_others_by_like(m,qq_list, qq)
                        #将说说记录到插入队列中
                        try:
                            topic_insert_db.put((m['content'],self.transfer_time(m['created_time']), m['uin']))
                        except Exception as e:
                            print('获取说说失败, '+ str(e))

                        #用第一条信息更新数据表
                        if is_first:
                            db = DB.Db()
                            db.update_infor(m['content'], m['source_name'], m['uin'])
                            db.commit()
                            db.close()
                            is_first = False

                except Exception as e:
                    print('读取好友说说错误，错误信息为：'+str(e))
                finally:
                    mutex.release()
            print('现在是第' + str(qq[1]) + '层 的好友: ' + str(qq[0]))


    #从单个说说获得好友的qq
    #qq_list是该qq的好友
    def get_qq_others_by_like(self, m, qq_list, qq):
        global already_exits
        url_like = 'https://user.qzone.qq.com/proxy/domain/users.qzone.qq.com/cgi-bin/likes/get_like_list_app?'
        if m['content'] is None:
            return 0
        tid = m['tid']
        #转发的说输咯跳过
        if 'rt_uin' in m.keys() and 'rt_tid' in m.keys():
            return 0
        data_like = {
            'uin': self.uin,  # 注意这里的uin是自己的qq
            'unikey': 'http://user.qzone.qq.com/' + str(qq[0]) + '/mood/' + str(tid) + '.1',
            'begin_uin': 0,
            'query_count': 60,
            'if_first_page': 1,
            'g_tk': self.g_tk
        }
        r = self.get_http_response(url_like, data_like)
        try:
            for like in r['data']['like_uin_info']:
                #一个qq下的好友查重
                if like['fuin'] not in already_exits:
                    already_exits.append(like['fuin'])
                    if len(already_exits) > 50000:
                        already_exits = []
                    new_qq.put([like['fuin'], qq[1], qq[0]])
        except Exception as e:
            print('获取说说点赞信息失败，错误信息为：'+str(e))

        #print('等待队列长度: '+str(waiting_get.qsize()))
        #print('新qq队列长度: ' + str(new_qq.qsize()))


    #写入数据库队列，等积累到一定的量再批量写入数据库
    def write_infor(self,qq):
        # 写入基本信息到入库队列中
        url_infor = 'https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/user/cgi_userinfo_get_all?'
        data_infor = {
            'uin': qq[0],
            'vuin': self.uin,  # 自己的qq
            'fupdate': 1,
            'g_tk': self.g_tk
        }

        r = self.get_http_response(url_infor, data_infor)
        #如果得到json数据错误，那么就返回
        if r == 0:
            return 0
        print(r)
        mutex = threading.Lock()
        if mutex.acquire():
            # 如果没有权限
            if 'data' in r :
                is_access = 1
                data = {
                    'qq': qq[0],
                    'parent_qq': qq[2],
                    'depth': qq[1],
                    'is_access': is_access,
                    'sex': r['data']['sex'],
                    'nick_name': r['data']['nickname'],
                    'qzone_name': r['data']['spacename'],
                    'last_message': '',
                    'ptime': self.transfer_time(r['data']['ptimestamp']),
                    'birth_year': r['data']['birthyear'],
                    'birth_day': r['data']['birthday'],
                    'tool': '',
                    'province': r['data']['province'],
                    'city': r['data']['city'],
                    'hp': r['data']['hp'],
                    'hc': r['data']['hc'],
                    'marriage': r['data']['marriage']
                }

            else:
                is_access = 0
                data = {
                    'qq': qq[0],
                    'parent_qq': qq[2],
                    'depth': qq[1],
                    'is_access': is_access,
                }
            mutex.release()

        #将信息入队
        #信息包括资料和是否可以有权限，有无权限写入数据库方式不一样
        infor_insert_db.put([data, is_access])
        #如果队列中超过设定的值那么批量写入数据库
        if infor_insert_db.qsize() > 5:
            print('现在等待插入队列长度 '+ str(infor_insert_db.qsize()))
            db = DB.Db()
            for i in range(5):
                infor = infor_insert_db.get()
                values = ()
                for item in infor[0].items():
                    #变成元组
                    values += (item[1],)
                db.insert_infor(values, infor[1])
            db.commit()
            db.close()
        if topic_insert_db.qsize() > 100:
            print('现在说说等待插入队列长度 ' + str(topic_insert_db.qsize()))
            db = DB.Db()
            for i in range(100):
                topic = topic_insert_db.get()
                values = ()
                for data in topic:
                    # 变成元组
                    values += (data,)
                db.insert_topic(values)
            db.commit()
            db.close()



    #得到数据，写进入库队列，qq结构[自己的qq，层次，父节点的qq]
    def get_data(self,qq):
        #层次在在这里加上，因为这是从一个好友扩展出来的qq，层次+1
        qq[1] += 1

        #将该qq的信息写到入库队列中
        self.write_infor(qq)
        #从该qq获得其他qq，想办法把这个从这里分离，提高并发性
        self.get_others_qq(qq)

        #如果等待队列中少于200个，那么就从新获取qq队列中出队500，再入队到等待队列中
        #为了控制多线程重复加值，应该要顺序读值，则需要加上锁更好
        #刚开始因为新qq队列里面没有，所以，刚开始还是会重复加值
        mutex = threading.Lock()
        if mutex.acquire():
            if waiting_get.qsize() < 200 and new_qq.qsize() > 500:
                for i in range(500):
                    try:
                        waiting_get.put(new_qq.get())
                    except Exception as e:
                        print('从新获得qq队列出队失败，错误信息为:'+str(e))

            #避免等待队列过长，超过一定值那么全部出队：
            if new_qq.qsize() > 50000:
                print('我要插入了')
                for i in range(new_qq.qsize()):
                    waiting_get.put(new_qq.get())

            mutex.release()
        '''print('等待队列大小'+str(waiting_get.qsize()))
        print('新队列大小' + str(new_qq.qsize()))'''


    #开始入口
    def start(self):
        #开始第一层
        for qq in self.qq:
            #刚开始层次设置为第一层
            waiting_get.put([qq,0,self.uin])

        #开始出队20线程爬数据,这里不使用threading的原因是每次出队20个线程执行都要join，20个线程中只要还剩一个没执行完，在其他的都要
        #等，效率太慢,而线程池就可以一次性放入200个，再20线程，提高效率
        while waiting_get.qsize() >= 0:
            #一次性出队200个，然后放入线程池
            wating_qq_list = []
            for i in range(waiting_get.qsize()):
                wating_qq_list.append(waiting_get.get())
            pool_size = 20
            pool = threadpool.ThreadPool(pool_size)
            # 创建工作请求
            reqs = threadpool.makeRequests(self.get_data, wating_qq_list)
            # 将工作请求放入队列
            [pool.putRequest(req) for req in reqs]
            pool.wait()

if __name__ == '__main__':
    # 假装是浏览器
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0",
        "Accepted-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    #先拿出自己的cookie
    with open('cookie_dict0.txt', 'r') as f:
        cookie = json.load(f)
    spider = Spider()
    #然后再定时切换cookie
    change_qq(0)
    #初始化一个list,用来判断已经写到数据库没
    already_exits = []
    #初始化三种队列，等待获取信息队列，新获得qq队列，等待写入数据库队列
    waiting_get = queue.Queue()
    new_qq = queue.Queue()
    infor_insert_db = queue.Queue()
    topic_insert_db = queue.Queue()
    spider.start()