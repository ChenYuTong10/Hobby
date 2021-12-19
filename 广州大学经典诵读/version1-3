# *-* coding:utf-8 *-*
import re
import smtplib  # 实现发送邮件消息
import requests  # 有时"pip"不是最新版的,会导致无法安装
from email.mime.text import MIMEText

# 微信账户唯一标识
wx_key = 'Ag1FclhrCqKH7HEGO8y8CKR%2BNQnd5907rLRLgFjtsu%2BfZUdfIiNE9xS%2FSz%2Fi%2F%2BJj'
# 请求相关
des_url = "https://jdsd.gzhu.edu.cn/coctl_gzhu/index_wx.php"
request_header = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept-Encoding": "gzip,compress,br,deflate",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.15(0x18000f2a) NetType/WIFI Language/zh_CN"
}
# 邮箱配置
mailbox_config = {
    "Host": "smtp.qq.com",
    "Username": "894104315",
    "Password": "pmnahccazdgibfef"
}
mail_config = {
    "Subject": u"广州大学经典诵读自动打卡结果",
    "Success_Content": """
        广州大学经典诵读自动打卡结果:
            1.每日签到: {0} / 2;
            2.唐诗鉴赏: {1} / 2;
            3.宋词鉴赏: {2} / 2;
            4.元曲鉴赏: {3} / 2;
            5.诗赋鉴赏: {4} / 2;
            6.古文鉴赏: {5} / 2;
            7.每日一练: {6} / 9;

        【总积分】: {7} / 1500 
    """,
    "Fail_Content": """
        今日未能自动打卡，请及时处理。

    """,
    "Sender": "894104315@qq.com",
    "Receivers": ["894104315@qq.com"]
}

# 正则表达式
total_credits_pattern = re.compile(r'.*?"credits":"(.*?)".*?')
daily_sign_credit_pattern = re.compile(r'.*?"daily_sign_credit":"(.*?)".*?')
poem_appreciation_pattern = re.compile(r'.*?"time1":(.*?),.*?')
word_appreciation_pattern = re.compile(r'.*?"time2":(.*?),.*?')
song_appreciation_pattern = re.compile(r'.*?"time3":(.*?),.*?')
prose_appreciation_pattern = re.compile(r'.*?"time4":(.*?),.*?')
ancient_writing_appreciation_pattern = re.compile(r'.*?"time5":(.*?),.*?')
daily_practice_pattern = re.compile(r'.*?"daily_train_credit":"(.*?)".*?')


def main():
    # 测试登录状态
    testLogin()
    # 签到
    SignIn()
    # 赏析古文
    for i in range(1, 6):
        AppreciatePoem(i)
    # 每日一练
    for i in range(1, 4):
        DailyPractice()
    # 获取榜单
    credit_obj = GetCreditList()
    # # 邮件提醒
    MainReminder(credit_obj)


# 测试登录
def testLogin():
    request_body = 'route=user_status&key=' + wx_key
    requests.post(url=des_url, headers=request_header, data=request_body, timeout=3)


# 签到
def SignIn():
    request_body = 'route=signin&key=' + wx_key
    requests.post(url=des_url, headers=request_header, data=request_body, timeout=3)


# 赏析古文
def AppreciatePoem(type):
    request_body = 'route=classic_time&addtime=90&type=' + str(type) + '&key=' + wx_key
    requests.post(url=des_url, headers=request_header, data=request_body, timeout=3)


# 每日一练
def DailyPractice():
    request_body = 'route=train_finish&train_id=3111087&train_result=%5B%5B%22vZiFNvMf8EQrUQjxt5nNjA%3D%3D%22%2C%221%22%5D%2C%5B%222u63JYohfBX9IhLPtRg5YA%3D%3D%22%2C%221%22%5D%2C%5B%22CzvOZXZOWB%2Fdia6MkA9edQ%3D%3D%22%2C%221%22%5D%2C%5B%22itO8HROTsz5M%2FLLBAJ8cjA%3D%3D%22%2C%221%22%5D%2C%5B%229Y0t88DciWkqx4dvdJA3iQ%3D%3D%22%2C%221%22%5D%5D&key=Ag1FclhrCqKH7HEGO8y8CKR%2BNQnd5907rLRLgFjtsu%2BfZUdfIiNE9xS%2FSz%2Fi%2F%2BJj'
    requests.post(url=des_url, headers=request_header, data=request_body, timeout=3)


# 获取榜单
def GetCreditList():
    # 请求所有积分信息
    request_all_credits_body = 'route=user_info&key=' + wx_key
    all_credits = requests.post(url=des_url, headers=request_header, data=request_all_credits_body, timeout=3).text
    # 请求部分积分信息
    request_item_credits_body = 'route=get_daily_credit&key=' + wx_key
    item_credits = requests.post(url=des_url, headers=request_header, data=request_item_credits_body, timeout=3).text
    # 筛选数据
    credit_obj = {
        "status": 1,
        "daily_sign_in": re.findall(daily_sign_credit_pattern, item_credits)[0],
        "poem_appreciation": re.findall(poem_appreciation_pattern, item_credits)[0],
        "word_appreciation": re.findall(word_appreciation_pattern, item_credits)[0],
        "song_appreciation": re.findall(song_appreciation_pattern, item_credits)[0],
        "prose_appreciation": re.findall(prose_appreciation_pattern, item_credits)[0],
        "ancient_writing_appreciation": re.findall(ancient_writing_appreciation_pattern, item_credits)[0],
        "daily_practice": re.findall(daily_practice_pattern, item_credits)[0],
        "total_credits": re.findall(total_credits_pattern, all_credits)[0]
    }
    return credit_obj


# 邮件提醒
def MainReminder(credit_obj):
    # "order"为收件人的序号
    # 邮件配置
    if credit_obj["status"]:
        content = mail_config["Success_Content"].format(
            credit_obj["daily_sign_in"], credit_obj["poem_appreciation"], credit_obj["word_appreciation"],
            credit_obj["song_appreciation"], credit_obj["prose_appreciation"],
            credit_obj["ancient_writing_appreciation"], credit_obj["daily_practice"], credit_obj["total_credits"]
        )
    else:
        content = mail_config["Fail_Content"]
    message = MIMEText(content, 'plain', 'utf-8')
    message["Subject"] = mail_config["Subject"]
    message["From"] = mail_config["Sender"]
    message["To"] = mail_config["Receivers"][0]
    # 发送邮件
    smtpEvent = smtplib.SMTP_SSL(mailbox_config["Host"])
    smtpEvent.login(mailbox_config["Username"], mailbox_config["Password"])
    smtpEvent.sendmail(mail_config["Sender"], mail_config["Receivers"][0], message.as_string())
    # 退出
    smtpEvent.quit()


if __name__ == "__main__":
    main()
