from selenium import webdriver
from time import sleep
import configparser
import json

#chromedriver = 'C:/Users/13180/AppData/Local/Google/Chrome/Application/chromedriver.exe'
#driver = webdriver.Chrome(chromedriver)

def create_cookie(qqs):
    for qq in qqs:
        driver = webdriver.Chrome()
        driver.get('https://user.qzone.qq.com/'+str(qq[0])+'/main')
        driver.switch_to.frame('login_frame')
        #找到账号密码登陆的地方
        driver.find_element_by_id('switcher_plogin').click()
        driver.find_element_by_id('u').send_keys(qq[0])
        sleep(1)
        driver.find_element_by_id('p').send_keys(qq[1])
        driver.find_element_by_id('login_button').click()
        #保存本地的cookie
        sleep(5)
        cookies = driver.get_cookies()
        cookie_dic = {}
        for cookie in cookies:
            if 'name' in cookie and 'value' in cookie:
                cookie_dic[cookie['name']] = cookie['value']
            with open('cookie_dict'+str(qq[2])+'.txt', 'w') as f:
                json.dump(cookie_dic, f)
def start():
    conf = configparser.ConfigParser()
    conf.read('config.ini')
    qqs = []
    for i in range(6):
        qqs.append([conf.get('qq','name'+str(i)),conf.get('qq','pwd'+str(i)),i])
    create_cookie(qqs)
if __name__ == '__main__':
    start()