# 使用SQLite作为数据库，功能完全
# 没有对数据进行分表等操作，未考虑数据库的性能问题

import os
import re
import time
import math
import sqlite3
import urllib
import requests
import selenium.common
from flask import Flask, jsonify, request
from msedge.selenium_tools import Edge, EdgeOptions

app = Flask(__name__)
# 基础配置
app.secret_key = "@$#~b&sad_/"  # 设置会话加密密钥(自己设置)


# 非路由函数
def getUserCookie(username, password):
    # 设置后台属性
    edge_options = EdgeOptions()
    edge_options.use_chromium = True
    edge_options.headless = True  # 开启静默模式
    # 驱动浏览器
    driver = Edge(executable_path="D:\Microsoft Edge Driver\edgedriver_win64\MicrosoftWebDriver.exe", options=edge_options)
    # 进入登录页面
    driver.get("https://newcas.gzhu.edu.cn/cas/login?service=https%3A%2F%2Fnewmy.gzhu.edu.cn%2Fup%2F")  # 打开登录页面
    driver.maximize_window()  # 最大化窗口
    username_input_tag = driver.find_element_by_id("un")  # 获得用户名输入框
    password_input_tag = driver.find_element_by_id("pd")  # 获取密码输入框
    login_tag = driver.find_element_by_id("index_login_btn")  # 获取登录按钮
    username_input_tag.send_keys(username)  # 输入用户名
    password_input_tag.send_keys(password)  # 输入密码
    login_tag.click()  # 点击登录按钮
    # 进入了个人界面
    time.sleep(1)  # 记得睡一下,不然页面加载不出来
    driver.execute_script("document.documentElement.scrollTop=500")  # 滑动滚动条保证元素可见
    office_system = driver.find_element_by_xpath('//a [@title="教务系统"]')  # 找到属于教务系统的标签
    office_system.click()  # 点击教务系统
    # 进入广州大学教学综合信息服务平台
    # 经过观察,该页面的Cookie与课表页面的Cookie相同,于是只要拿到Cookie即可
    windows = driver.window_handles  # 获取所有窗口句柄
    driver.switch_to.window(windows[1])  # 切换窗口句柄(虽然表面上是新页面,但是实际上还在另一个页面上,获取的Cookie是错的)
    SF_cookie_18_cookie = driver.get_cookie(name="SF_cookie_18")
    JSESSIONID_cookie = driver.get_cookie(name="JSESSIONID")
    # 拼接Cookie
    Cookie = JSESSIONID_cookie["name"] + "=" + JSESSIONID_cookie["value"] + "; " + SF_cookie_18_cookie["name"] + "=" + SF_cookie_18_cookie["value"]
    # driver.quit()
    return Cookie


def requestTimetable(username, cookie):
    base_url = "http://jwxt.gzhu.edu.cn/jwglxt/kbcx/xskbcx_cxXsKb.html?"
    request_header = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38"
    }
    request_params = {"gnmkdm": "N253508", "su": username}
    request_data = bytes(urllib.parse.urlencode({"xnm": "2021", "xqm": "3"}), encoding="utf-8")
    response = requests.post(base_url+urllib.parse.urlencode(request_params),
                             headers=request_header,
                             data=request_data).json()
    return response


def normalizeTimetable(html):
    normalized_course = []
    # 用于转化
    day = {"星期一": "Monday", "星期二": "Tuesday",
                     "星期三": "Wednesday", "星期四": "Thursday",
                     "星期五": "Friday", "星期六": "Saturaday",
                     "星期日": "Sunday"}
    time = {"1-2节": ["08:30", "10:05"], "3-4节": ["10:25", "12:00"],
            "5-6节": ["13:50", "15:25"], "5-7节": ["13:50", "17:45"],
            "7-8节": ["15:45", "17:20"], "9-10节": ["18:20", "19:50"],
            "9-11节": ["18:20", "20:45"]}
    course_list = html["kbList"]
    # 处理数据
    for item in course_list:
        translate_day = day[item["xqjmc"]]
        translate_time = time[item["jc"]]
        course = {
            "name": item["kcmc"],
            "day": translate_day,
            "start_time": translate_time[0],
            "end_time": translate_time[1],
            "duration": item["zcd"],
            "classroom": item["cdmc"].replace("#", ""),
            "lecturer": item["xm"],
            "remark": item["skfsmc"]
        }
        # 加入列表
        normalized_course.append(course)
    return normalized_course


def queryOutlineSportsCourses(name, classroom):
    database = sqlite3.connect(u"广州大学选修数据.db")
    cursor = database.cursor()
    query_operation = """select rowid, * from 广州大学体育课程 where 1=1 """
    if name is not None:
        query_operation = query_operation + "and name = '" + name + "' "
    if classroom is not None and classroom != "教学楼":
        query_operation = query_operation + "and classroom like '%" + classroom + "%' "
    # 排除法
    if classroom is not None and classroom == "教学楼":
        query_operation = query_operation + "and classroom not like '%北区%' and classroom not like '%东区%'"
    query_result = cursor.execute(query_operation).fetchall()
    return query_result


def queryInlineSportsCourses(course_name, classroom):
    database = sqlite3.connect(u"广州大学选修数据.db")
    cursor = database.cursor()
    courses = []
    query_operation = """select rowid, * from 广州大学体育课程 where name = '""" + course_name + "' "
    if classroom is not None and classroom != "教学楼":
        query_operation = query_operation + "and classroom like '%" + classroom + "%' "
    if classroom is not None and classroom == "教学楼":
        query_operation = query_operation + "and classroom not like '%北区%' and classroom not like '%东区%'"
    query_result = cursor.execute(query_operation).fetchall()
    for query_item in query_result:
        id = query_item[0]
        teacher = query_item[3]
        contact = query_item[5]
        time = query_item[6]
        classroom = query_item[7]
        course_item = {"id": id, "teacher": teacher, "contact": contact, "time": time, "classroom": classroom}
        courses.append(course_item)
    return courses


def queryOutlineGeneralCourses(credit, day, type):
    database = sqlite3.connect(u"广州大学选修数据.db")
    cursor = database.cursor()
    query_operation = """select rowid, * from 广州大学通识选修课程 where 1=1 """
    if credit is not None:
        query_operation = query_operation + "and credit = '" + credit + "' "
    if day is not None:
        query_operation = query_operation + "and time like '%" + day + "%' "
    if type is not None:
        query_operation = query_operation + "and type = '" + type + "' "
    query_result = cursor.execute(query_operation).fetchall()
    return query_result


def queryInlineGeneralCourses(id, day):
    database = sqlite3.connect(u"广州大学选修数据.db")
    cursor = database.cursor()
    courses = []
    query_operation = """select rowid, * from 广州大学通识选修课程 """ + "where id = '" + id + "' "
    if day is not None:
        query_operation = query_operation + "and time like '%" + day + "%' "
    query_result = cursor.execute(query_operation).fetchall()
    # 查询具体开设班级
    for query_item in query_result:
        id = query_item[0]
        teacher = re.sub(" ", "", query_item[3])
        time = re.sub(" ", "\n", query_item[5])
        classroom = re.sub("<br/>", "\n", query_item[8]).replace("#", "")
        mode = query_item[6]
        remark = query_item[10] or "暂无"
        course_item = {"id": id, "teacher": teacher, "time": time, "classroom": classroom, "mode": mode, "remark": remark}
        courses.append(course_item)
    return courses


@app.before_first_request
def create_database():
    database = sqlite3.connect(u"校园服务.db")
    cursor = database.cursor()
    # 轮播图库
    swiper_table = """
        create table IF NOT EXISTS 首页轮播图库
        (id INTEGER not null primary key autoincrement,
        name text not null unique,
        path text not null unique,
        active NUMERIC not null default TRUE
        )
    """
    # 图标图库
    icon_table = """
        create table IF NOT EXISTS 图标库
        (id INTEGER not null primary key autoincrement,
        name text not null unique,
        path text not null unique,
        active NUMERIC not null default TRUE
        )
    """
    # 报修信息库
    repairInfo_table = """
        create table IF NOT EXISTS 维修信息库
        (id INTEGER not null primary key autoincrement,
        time TIMESTAMP not null default current_timestamp,
        poster text not null,
        name text not null,
        phone text not null,
        dorm text not null,
        details text not null,
        active NUMERIC not null default TRUE 
        )
    """
    # 意见反馈库
    feedback_table = """
        create table IF NOT EXISTS 意见反馈库
        (id INTEGER not null primary key autoincrement,
        time TIMESTAMP not null default current_timestamp,
        poster text not null,
        content text not null,
        image text,
        type text not null
        )
    """
    cursor.execute(swiper_table)
    cursor.execute(icon_table)
    cursor.execute(repairInfo_table)
    cursor.execute(feedback_table)
    database.commit()


@app.route('/', methods=["GET"])
def helloWorld():
    return "Hello World!"


@app.route('/add/icon', methods=["POST"])
def addIcon():
    database = sqlite3.connect(u"校园服务.db")
    cursor = database.cursor()
    # 获取传入数据
    icons = request.get_json()
    for icon_item in icons:
        if "name" in icon_item and "path" in icon_item:
            name = icon_item["name"]
            path = icon_item["path"]
            add_operation = """
                insert into 图标库 (name, path)
                    values ("{0}", "{1}")
            """.format(name, path)
            try:
                cursor.execute(add_operation)
            except sqlite3.OperationalError:
                return jsonify(dict(status=500, message="无法完成该请求"))
            except sqlite3.IntegrityError:
                return jsonify(dict(status=400, message="已存在图标的相关信息"))
        else:
            return jsonify(dict(status=400, message="无法获取图标信息"))
    database.commit()
    return jsonify(dict(status=200, message="添加成功"))


@app.route('/del/icon', methods=["DELETE"])
def deleteIcon():
    database = sqlite3.connect(u"校园服务.db")
    cursor = database.cursor()
    # 由于无论删除是否存在的数据,数据库都会返回成功,因此先查询是否存在
    query_operation = """select * from 图标库"""
    query_result = cursor.execute(query_operation).fetchall()
    # 获取参数
    delete_icons = request.get_json()
    for icon_item in delete_icons:
        if "id" in icon_item:
            id = icon_item["id"]
            # 查询对应的图片
            for query_item in query_result:
                if query_item[0] == id:
                    delete_operation = """delete from 图标库 where id = ({0})""".format(id)
                    cursor.execute(delete_operation)
                    break
            else:
                return jsonify(dict(status=404, message="无法找到目标图标"))
        else:
            jsonify(dict(status=400, message="无法获取图标信息"))
    else:
        database.commit()
        return jsonify(dict(status=200, message="删除成功"))


@app.route('/update/icon', methods=["POST"])
def updateIcon():
    database = sqlite3.connect(u"校园服务.db")
    cursor = database.cursor()
    # 查询
    query_operation = """select * from 图标库"""
    query_result = cursor.execute(query_operation).fetchall()
    # 获取参数
    modify_icon = request.get_json()
    if "id" in modify_icon and "name" in modify_icon and "path" in modify_icon and "active" in modify_icon:
        id = modify_icon["id"]
        name = modify_icon["name"]
        path = modify_icon["path"]
        active = modify_icon["active"]
        for query_item in query_result:
            if query_item[0] == id:
                # 获取需要改变的参数
                update_operation = """
                    update 图标库 set name = ("{1}"), path = ("{2}"), active = ({3}) where id = ("{0}")
                """.format(id, name, path, active)
                try:
                    cursor.execute(update_operation)
                    break
                except sqlite3.IntegrityError:
                    return jsonify(dict(status=400, message="已存在图标相关信息"))
        else:
            return jsonify(dict(status=404, message="无法找到目标图标"))
    else:
        return jsonify(dict(status=400, message="无法获取图标信息"))
    database.commit()
    return jsonify(dict(status=200, message="修改成功"))


@app.route('/get/icon', methods=["GET"])
def getIcon():
    database = sqlite3.connect(u"校园服务.db")
    cursor = database.cursor()
    icons = []
    # 返回"active"图片
    get_operation = """select * from 图标库"""
    query_result = cursor.execute(get_operation).fetchall()
    # 数据处理
    for query_item in query_result:
        if query_item[3] == 1:
            image = {"id": query_item[0], "name": query_item[1], "path": query_item[2]}
            icons.append(image)
    return jsonify(dict(status=200, message="获取成功", details=icons))


@app.route('/add/swiper-image', methods=["POST"])
def addSwiperImage():
    database = sqlite3.connect(u"校园服务.db")
    cursor = database.cursor()
    # 获取传入数据
    swiper_image = request.get_json()
    for image_item in swiper_image:
        # 判断"name","path"属性是否完整
        if "name" in image_item and "path" in image_item:
            name = image_item["name"]
            path = image_item["path"]
            add_operation = """
                insert into 首页轮播图库 (name, path)
                    values ("{0}", "{1}")
            """.format(name, path)
            try:
                cursor.execute(add_operation)
            except sqlite3.OperationalError:
                return jsonify(dict(status=500, message="无法完成该请求"))
            except sqlite3.IntegrityError:
                return jsonify(dict(status=400, message="已存在图片的相关信息"))
        else:
            return jsonify(dict(status=400, message="无法获取图片信息"))
    database.commit()
    return jsonify(dict(status=200, message="添加成功"))


@app.route('/del/swiper-image', methods=["DELETE"])
def deleteSwiperImage():
    database = sqlite3.connect(u"校园服务.db")
    cursor = database.cursor()
    # 由于无论删除是否存在的数据,数据库都会返回成功,因此先查询是否存在
    query_operation = """select * from 首页轮播图库"""
    query_result = cursor.execute(query_operation).fetchall()
    # 获取参数
    delete_image = request.get_json()
    for image_item in delete_image:
        if "id" in image_item:
            id = image_item["id"]
            # 查询对应的图片
            for query_item in query_result:
                if query_item[0] == id:
                    delete_operation = """delete from 首页轮播图库 where id = ({0})""".format(id)
                    cursor.execute(delete_operation)
                    break
            else:
                return jsonify(dict(status=404, message="无法找到目标图片"))
        else:
            jsonify(dict(status=400, message="无法获取图片信息"))
    else:
        database.commit()
        return jsonify(dict(status=200, message="删除成功"))


@app.route('/update/swiper-image', methods=["POST"])
def updateSwiperImage():
    database = sqlite3.connect(u"校园服务.db")
    cursor = database.cursor()
    # 查询
    query_operation = """select * from 首页轮播图库"""
    query_result = cursor.execute(query_operation).fetchall()
    # 获取参数
    modify_image = request.get_json()
    if "id" in modify_image and "name" in modify_image and "path" in modify_image and "active" in modify_image:
        id = modify_image["id"]
        name = modify_image["name"]
        path = modify_image["path"]
        active = modify_image["active"]
        for query_item in query_result:
            if query_item[0] == id:
                # 获取需要改变的参数
                update_operation = """
                    update 首页轮播图库 set name = ("{1}"), path = ("{2}"), active = ({3}) where id = ("{0}")
                """.format(id, name, path, active)
                try:
                    cursor.execute(update_operation)
                    break
                except sqlite3.IntegrityError:
                    return jsonify(dict(status=400, message="已存在图片相关信息"))
        else:
            return jsonify(dict(status=404, message="无法找到目标图片"))
    else:
        return jsonify(dict(status=400, message="无法获取图片信息"))
    database.commit()
    return jsonify(dict(status=200, message="修改成功"))


@app.route('/get/swiper-image', methods=["GET"])
def getSwiperImage():
    database = sqlite3.connect(u"校园服务.db")
    cursor = database.cursor()
    swiper_images = []
    # 返回"active"图片
    get_operation = """select * from 首页轮播图库"""
    query_result = cursor.execute(get_operation).fetchall()  # 获取查询结果,返回的是数组,每个元素又是元组
    # 数据处理
    for query_item in query_result:
        if query_item[3] == 1:
            image = {"id": query_item[0], "name": query_item[1], "path": query_item[2]}
            swiper_images.append(image)
    return jsonify(dict(status=200, message="获取成功", details=swiper_images))


@app.route('/add/repair-Information', methods=["POST"])
def addRepairInformation():
    database = sqlite3.connect(u"校园服务.db")
    cursor = database.cursor()
    # 获取表单
    repair_information = request.get_json()
    if ("poster" in repair_information
            and "name" in repair_information
            and "phone" in repair_information
            and "dorm" in repair_information
            and "details" in repair_information):
        poster = repair_information["poster"]
        name = repair_information["name"]
        phone = repair_information["phone"]
        dorm = repair_information["dorm"]
        details = repair_information["details"]
        add_operation = """
            insert into 维修信息库 (poster, name, phone, dorm, details)
                values ("{0}", "{1}", "{2}", "{3}", "{4}")
        """.format(poster, name, phone, dorm, details)
        try:
            cursor.execute(add_operation)
            database.commit()
            return jsonify(dict(status=200, message="提交成功"))
        except sqlite3.OperationalError:
            return jsonify(dict(status=500, message="无法完成该请求"))
        except sqlite3.IntegrityError:
            return jsonify(dict(status=400, message="已存在维修的相关信息"))
    else:
        return jsonify(dict(status=400, message="无法获取维修信息"))


@app.route('/del/repair-Information', methods=["DELETE"])
def deleteRepairInformation():
    database = sqlite3.connect(u"校园服务.db")
    cursor = database.cursor()
    query_operation = """select * from 维修信息库"""
    query_result = cursor.execute(query_operation).fetchall()
    # 获取信息
    id = int(request.args.get("id"))  # 传进来的是"str"类型
    if id is None:
        return jsonify(dict(status=400, message="无法获取维修信息"))
    else:
        for query_item in query_result:
            if query_item[0] == id:
                delete_operation = """delete from 维修信息库 where id = ({0})""".format(id)
                cursor.execute(delete_operation)
                database.commit()
                return jsonify(dict(status=200, message="删除成功"))
        else:
            return jsonify(dict(status=400, message="无法找到目标信息"))


@app.route('/update/repair-Information', methods=["POST"])
def updateRepairInformation():
    database = sqlite3.connect(u"校园服务.db")
    cursor = database.cursor()
    query_operation = """select * from 维修信息库"""
    query_result = cursor.execute(query_operation).fetchall()
    # 获取表单
    repair_information = request.get_json()
    if ("id" in repair_information
            and "name" in repair_information
            and "phone" in repair_information
            and "dorm" in repair_information
            and "details" in repair_information):
        id = repair_information["id"]
        name = repair_information["name"]
        phone = repair_information["phone"]
        dorm = repair_information["dorm"]
        details = repair_information["details"]
        for query_item in query_result:
            if query_item[0] == id:
                update_operation = """
                    update 维修信息库 set name = ("{1}"), phone = ("{2}"), dorm = ("{3}"), details = ("{4}") where id = ("{0}")
                """.format(id, name, phone, dorm, details)
                cursor.execute(update_operation)
                database.commit()
                return jsonify(dict(status=200, message="修改成功"))
        else:
            return jsonify(dict(status=400, message="无法找到目标信息"))
    else:
        return jsonify(dict(status=400, message="无法获取维修信息"))


@app.route('/get/repair-Information/unrepaired', methods=["GET"])
def getUnrepairedInformation():
    database = sqlite3.connect(u"校园服务.db")
    cursor = database.cursor()
    query_operation = """select * from 维修信息库"""
    query_result = cursor.execute(query_operation).fetchall()
    history_record_list = []
    # 获取参数
    username = request.args.get("username")
    if not username:
        return jsonify(dict(status=400, message="无法获取用户信息"))
    # 开始查找
    for query_item in query_result:
        if query_item[2] == username and query_item[7] == 1:
            history_record_item = {
                "id": query_item[0],
                "time": query_item[1],
                "name": query_item[3],
                "phone": query_item[4],
                "dorm": query_item[5],
                "details": query_item[6]
            }
            history_record_list.append(history_record_item)
    return jsonify(dict(status=200, message="获取成功", details=history_record_list))


@app.route('/get/repair-Information/repaired', methods=["GET"])
def getRepairedInformation():
    database = sqlite3.connect(u"校园服务.db")
    cursor = database.cursor()
    query_operation = """select * from 维修信息库"""
    query_result = cursor.execute(query_operation).fetchall()
    history_record_list = []
    history_record_item = {}
    # 获取参数
    username = request.args.get("username")
    if not username:
        return jsonify(dict(status=400, message="无法获取用户信息"))
    # 开始查找
    for query_item in query_result:
        if query_item[2] == username and query_item[7] == 0:
            history_record_item = {
                "id": query_item[0],
                "time": query_item[1],
                "name": query_item[3],
                "phone": query_item[4],
                "dorm": query_item[5],
                "details": query_item[6]
            }
            history_record_list.append(history_record_item)
    return jsonify(dict(status=200, message="获取成功", details=history_record_list))


@app.route('/add/feedback', methods=["POST"])
def addFeedback():
    database = sqlite3.connect(u"校园服务.db")
    cursor = database.cursor()
    basic_path = "D:\微信\微信小程序\项目\用户上传图片/"
    time_now = time.strftime("%Y-%m-%d", time.localtime())
    # 获取上传数据和图片("form-data"类型惹不起)
    feedback_information = request.form
    feedback_image = request.files.get("feedback_image")
    if ("poster" in feedback_information
            and feedback_information["poster"] is not None
            and "content" in feedback_information
            and "type" in feedback_information):
        poster = feedback_information["poster"]
        content = feedback_information["content"]
        type = feedback_information["type"]
        # 图片处理
        feedback_image_folder = basic_path + time_now + " " + poster  # 使用时间和用户名组合创建文件夹
        if not os.path.exists(feedback_image_folder):
            os.mkdir(feedback_image_folder)
        feedback_image.save(feedback_image_folder + "\\" + feedback_image.filename)  # 注意要加文件名
        # 加入数据库
        add_operation = """
            insert into 意见反馈库 (poster, content, image, type)
                values ("{0}", "{1}", "{2}", "{3}")
        """.format(poster, content, feedback_image.filename, type)
        try:
            cursor.execute(add_operation)
        except sqlite3.OperationalError:
            return jsonify(dict(status=500, message="无法完成该请求"))
    else:
        return jsonify(dict(status=400, message="无法获得反馈信息"))
    database.commit()
    return jsonify(dict(status=200, message="反馈成功"))


@app.route('/get/timetable', methods=["POST"])
def getTimetable():
    userInfo = request.get_json()
    if "username" in userInfo and "password" in userInfo:
        username = userInfo["username"]
        password = userInfo["password"]
        try:
            # 获取Cookie
            cookie = getUserCookie(username, password)
            # 请求数据
            html = requestTimetable(username, cookie)
            # 标准化课程表
            timetable = normalizeTimetable(html)
            return jsonify(dict(status=200, message="登录成功", details=timetable))
        except selenium.common.exceptions.NoSuchElementException as e:
            print(e.msg)
            return jsonify(dict(status=400, message="无法获取课程表"))
    else:
        return jsonify(dict(status=400, message="无法获取用户信息"))


@app.route('/get/course-list/sports', methods=["GET"])
def getSportsCourse():
    # 前端为了好看,关键字对不上
    classroom_transform = {"教学楼": "教学楼", "北区运动场": "北区", "东区运动场": "东区"}
    # 获取页码等参数
    page_number = int(request.args.get("page_number"))
    name = request.args.get("name")
    classroom = request.args.get("classroom")
    # 检查参数
    if page_number <= 0:
        return jsonify(dict(status=400, message="无法获取课程信息"))
    if classroom is not None:
        classroom = classroom_transform[classroom]
    # 课程大纲
    outline_courses_result = queryOutlineSportsCourses(name, classroom)
    total_pages = math.ceil(len(outline_courses_result)/15.0)
    outline_courses_result = outline_courses_result[15*(page_number-1)::1]
    # 具体开设课程
    course_name = ""
    courses = []
    for outline_courses_item in outline_courses_result:
        if outline_courses_item[2] == course_name:
            continue
        course_name = outline_courses_item[2]
        inline_courses_result = queryInlineSportsCourses(str(course_name), classroom)
        if not len(inline_courses_result):  # 如果具体没有课,那就去掉
            continue
        # 整合
        course = {
            "isActive": 0,
            "id": outline_courses_item[0],
            "name": outline_courses_item[2],
            "credit": outline_courses_item[8],
            "course_number": len(inline_courses_result),
            "details": inline_courses_result
        }
        courses.append(course)
        if len(courses) >= 15:
            break
    return jsonify(dict(status=200, message="获取成功", total_pages=total_pages, page_number=page_number, details=courses))


@app.route('/get/course-list/general', methods=["GET"])
def getGeneralCourse():
    # 获取页码等参数
    page_number = int(request.args.get("page_number"))
    credit = request.args.get("credit")
    day = request.args.get("day")
    type = request.args.get("type")
    # 检查参数
    if page_number <= 0:
        return jsonify(dict(status=400, message="无法获取课程信息"))
    # 课程大纲
    outline_courses_result = queryOutlineGeneralCourses(credit, day, type)
    total_pages = math.ceil(len(outline_courses_result) / 15.0)  # 计算总页数
    outline_courses_result = outline_courses_result[15 * (page_number - 1)::1]
    # 具体开设课程
    id = 0
    courses = []
    for outline_courses_item in outline_courses_result:
        if outline_courses_item[1] == id:  # 筛选相同的课程
            continue
        id = outline_courses_item[1]
        inline_courses_result = queryInlineGeneralCourses(str(id), day)
        if not len(inline_courses_result):  # 如果具体没有课,那就去掉
            continue
        # 整合
        course = {
            "isActive": 0,
            "id": outline_courses_item[0],
            "name": re.sub(" ", "", outline_courses_item[2]),
            "type": outline_courses_item[7],
            "credit": outline_courses_item[9],
            "course_number": len(inline_courses_result),
            "details": inline_courses_result
        }
        courses.append(course)
        if len(courses) >= 15:
            break
    return jsonify(dict(status=200, message="获取成功", total_pages=total_pages, page_number=page_number, details=courses))


if __name__ == '__main__':
    app.run(host="0.0.0.0")
