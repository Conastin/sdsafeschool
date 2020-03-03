import requests
from bs4 import BeautifulSoup
import re

sch_id = '187' #这里输入学校id
shouji = '15098748679' #这里输入手机号
mima = 'abc123' #这里输入密码
daan = []

# post登录
session = requests.session()
url_login = 'http://exam.sdsafeschool.gov.cn/m_login.php?adminaction=login' #登陆地址
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
}
data = {
    # 学校id
    'sch_id': sch_id,
    # 手机
    'shouji': shouji,
    # 密码
    'pppp': mima
}
# 登录
session.post(url_login, headers=headers, data=data)

#读取题库
try:
    #读取题库
    f = open("dict.txt", 'r')
    itemdict = eval(f.read())
    f.close()
except FileNotFoundError:
    #无题库文件 开始爬取题库
    timeout = 0
    url_test = 'http://exam.sdsafeschool.gov.cn/m_mokao.php'
    while True:
        webpage = session.get(url_test)
        item = BeautifulSoup(webpage.content, 'html.parser')
        num = 1
        for i in item.find_all(class_='ti'):
            id = 'daan_' + str(num)
            answer = i.find(id=id).text
            title = i.find(class_='title').text
            # 去掉序号的题目加入titles
            if title[2] == ' ':
                if not title[3::] in dict:
                    timeout = 0
                    dict.update({title[3::]: answer})
                    print(title[3::], answer)
                else:
                    timeout += 1
            else:
                if not title[2::] in dict:
                    timeout = 0
                    dict.update({title[2::]: answer})
                    print(title[2::], answer)
                else:
                    timeout += 1
            num += 1
        if timeout > 2500:
            # 存储
            f = open('dict.txt', 'w')
            f.write(str(dict))
            f.close()
            print('保存成功')
            break
#开始考试
headers = {
    'Referer': 'http://exam.sdsafeschool.gov.cn/m_kaoshi_log.php?from_url=m_kaoshi_log.php',
    'Host': 'exam.sdsafeschool.gov.cn',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}
examurl = 'http://exam.sdsafeschool.gov.cn/m_kaoshi.php'
indexurl = 'http://exam.sdsafeschool.gov.cn/m_kaoshi_log.php?from_url=m_kaoshi_log.php'
exampage = session.get(indexurl, headers=headers)
check = BeautifulSoup(exampage.content, 'html.parser')
# print(page.find(class_='tishikuang').text)
if '很遗憾，你没有通过考试。'==check.find(class_='tishikuang').text:
    print('你没机会了')
elif '恭喜，你已通过考试。'==check.find(class_='tishikuang').text[0:10]:
    print('恭喜，你已通过考试。')
else:
    exampage = session.get(examurl, headers=headers)
    page = BeautifulSoup(exampage.content, 'html.parser')
    #获取sa sf di
    sa = re.search("sa:'(.*)'", page.text).group(1)
    sf = re.search("sf:'(.*)'", page.text).group(1)
    di = re.search("di:'(.*)'", page.text).group(1)
    #获取答案
    for i in page.find_all(class_='ti'):
        item = i.find(class_='title').text
        if item[2] == ' ':
            daan.append(itemdict[item[3::]])
        else:
            daan.append(itemdict[item[2::]])
    #格式化答案 ya
    num = 1
    ya = ''
    for i in daan:
        if num==25:
            ya +='"' + i + '"'
        else:
            ya += '"' + i + '",'
        num += 1
    #提交答案
    post_url = 'http://exam.sdsafeschool.gov.cn/m_kaoshi_save.php'
    headers = {
        'Referer': 'http://exam.sdsafeschool.gov.cn/m_kaoshi.php',
        'Host': 'exam.sdsafeschool.gov.cn',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Origin': 'http://exam.sdsafeschool.gov.cn'
    }
    data = {
        'is_jiaojuan': '1',
        'ya': ya,
        'di': di,
        'sa': sa,
        'sf': sf
    }
    res = session.post(post_url, headers=headers, data=data)
    if res.status_code == 200:
        print('已成功')
    else:
        print('失败')
    exampage = session.get(indexurl, headers=headers)
    check = BeautifulSoup(exampage.content, 'html.parser')
    print(check.find(class_='tishikuang').text)