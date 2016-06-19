# -*- coding:utf-8 -*-
import urllib
import urllib2
import cookielib
import re
import getpass
# import lxml
# from bs4 import BeautifulSoup


class NcepuSpider:
    """docstring for """
    def __init__(self, stuid,pwd):
        self.login_url = 'http://202.206.208.84:7777/pls/wwwbks/bks_login2.login?'  # 登录的url
        self.result_url = 'http://202.206.208.84:7777/pls/wwwbks/bkscjcx.jxjh'  # 获取成绩页面的url
        # 创建opener
        self.cookie = cookielib.CookieJar()
        self.opener= urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        # 构造url请求数据
        self.postdata = urllib.urlencode({'stuid':stuid, 'pwd':pwd, })
        self.headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36'
        }
        # 课程信息存储列表
        self.data = list()

        self.credits = 0  # 学分和
        self.sum = 0  # 绩点和
        self.GPA = 0  # 学分绩

    def login(self):
        '''登录'''
        req = urllib2.Request(url = self.login_url,data =self.postdata,headers=self.headers)
        try:
            response = self.opener.open(req)
        except Exception, e:
            if hasattr(e,'code'):
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ',e.code
            elif hasattr(e,'reason'):
                print 'We failed to reach a server.'
                print 'Reason',e,reason

        if re.search(re.compile(u'错误的学号或密码'),response.read().decode('gb18030')):
            print u'你输入了错误的学号或密码，不能登录！'
            exit()

    def spider(self):

        '''登录,获取课程信息,计算学分绩'''
        self.login()  # 登录
        self.get_course_info()  # 获取课程信息

        self.calculate_GPA()  # 计算学分绩
        print 'The total point is: ', self.sum
        print 'The total credits is: ', self.credits
        print 'GPA = ', self.GPA

    def get_course_info(self):
        '''获得课程信息'''
        try:
            result = self.opener.open(self.result_url).read().decode('gb18030')
        except Exception, e:
            print 'Sorry,there have an error...'
            exit()
        # 处理课程页面,提取所需数据
        self.process_info(result)

    def process_info(self,result):
        '''处理课程页面,提取所需数据'''

        # 获得每个课程的列表源代码
        pattern_str = r'<tr>[\s\S]*?</tr>'
        pattern_course = re.compile(pattern_str)
        courses = re.findall(pattern_course,result)
        # 获取每个课程的各项数据
        pattern = re.compile(r'>([^<]*)</td')
        for course in courses:
            items = re.findall(pattern,course)
            #if not len(items) in range(5,11):continue

            # 显示每门课程的详细信息
            # for item in items:
            #     print u"%-10s" %(item),
            # print '|',len(items)
            # print '--------------------------------------------------------------------------------------------------'

            # 构造数据字典，添加到数据列表
            if len(items) == 8:
                for term,course_id,course_name,credit,not_important,not_important1,not_important2,score in [tuple(items)]:
                    dic = {
                        'term':term,
                        'course_id':course_id,
                        'course_name':course_name,
                        'credit':credit,
                        'score':score
                    }
                    self.data.append(dic)
            elif len(items) == 10:
                for term,course_id,course_name,credit,hours,attr,type_of_test,score,moudle,requset in [tuple(items)]:
                    dic = {
                        'term':term,
                        'course_id':course_id,
                        'course_name':course_name,
                        'credit':credit,
                        'score':score,
                        'moudle':moudle,
                        'requset':requset
                    }
                    self.data.append(dic)

            # 打印数据字典内容
            # for i in  self.data:
            #     print i

    def calculate_GPA(self):
        '''计算学分和，绩点和，学分绩'''
        map_of_score = {u'通过': 60, u'中': 70, u'良': 80, u'优': 90}  # 把课程的评测结果量化
        other_of_score = ['&nbsp;', u'不及格', u'不通过']  # 不计入学分绩的条件
        for Course in self.data:
            if Course['score'] in map_of_score:
                self.sum += float(Course['credit']) * map_of_score[Course['score']]
                self.credits += float(Course['credit'])
                continue
            if Course['score'] in other_of_score: continue
            self.sum += float(Course['credit']) * float(Course['score'])
            self.credits += float(Course['credit'])
        self.GPA = float(self.sum/self.credits)

if __name__ == '__main__':
    stuid = raw_input('Please input your id:')
    pwd = getpass.getpass('Please input your password: ')
    mySpider = NcepuSpider(stuid,pwd)
    mySpider.spider()

