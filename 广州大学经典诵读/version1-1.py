# *-* coding:utf-8 *-*
import smtplib # 实现发送邮件消息
import requests  # 有时"pip"不是最新版的,会导致无法安装
from email.mime.text import MIMEText

# 微信账户唯一标识
wx_key = 'V3WV3zlqVbcmN2%2Ff2VBdatmXnD4oo3mdyc%2Bbz3Od7qkstwLVvEr10mtnUJQTOEM3'
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
        
        【总积分】: {6} / 1500 

    """,
    "Fail_Content": """
    【前言】:1.打卡结果请以实际情况为准;    2.如果有BUG，请及时反馈给我。
    
        今日未能自动打卡，请及时联系作者。
    """,
    "Sender": "894104315@qq.com",
    "Receivers": ["894104315@qq.com"]
}


def main():
    # 测试登录状态
    testLogin()
    # 签到
    SignIn()
    # 赏析古文
    for i in range(1, 6):
        AppreciatePoem(i)
    # 获取榜单
    credit_obj = GetCreditList()
    # 邮件提醒
    MainReminder(credit_obj)


# 测试登录
def testLogin():
    request_body = 'route=user_status&key=' + wx_key
    requests.post(url=des_url, headers=request_header, data=request_body, timeout=3).json()


# 签到
def SignIn():
    request_body = 'route=signin&key=' + wx_key
    requests.post(url=des_url, headers=request_header, data=request_body, timeout=3).json()


# 赏析古文
def AppreciatePoem(type):
    request_body = 'route=classic_time&addtime=90&type=' + str(type) + '&key=' + wx_key
    requests.post(url=des_url, headers=request_header, data=request_body, timeout=3).json()


# 获取榜单
def GetCreditList():
    # 请求所有积分信息
    request_all_credits_body = 'route=user_info&key=' + wx_key
    all_credits = requests.post(url=des_url, headers=request_header, data=request_all_credits_body, timeout=3).json()
    # 请求部分积分信息
    request_item_credits_body = 'route=get_daily_credit&key=' + wx_key
    item_credits = requests.post(url=des_url, headers=request_header, data=request_item_credits_body, timeout=3).json()
    if not all([all_credits["status"], item_credits["status"]]):
        return {"status": 0}
    # 筛选数据
    details = item_credits["result"]
    credit_obj = {
        "status": 1,
        "daily_sign_in": details["daily_sign_credit"],
        "poem_appreciation": details["time1"],
        "word_appreciation": details["time2"],
        "song_appreciation": details["time3"],
        "prose_appreciation": details["time4"],
        "ancient_writing_appreciation": details["time5"],
        "total_credits": all_credits["re"]["credits"]
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
            credit_obj["ancient_writing_appreciation"], credit_obj["total_credits"]
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

