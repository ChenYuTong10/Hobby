import requests
import urllib.request
import urllib.error
import re
import pymysql

# MySQL数据库
mysql_account = {"user": "root", "password": "cytzero3434"}


# 请求头
request_header = {
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Cookie": "JSESSIONID=8E6EDEB4E6D785F93FB44D4D4CDBB425; SF_cookie_18=96032857",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47"
}


# 匹配模板
course_category_template = re.compile("[\u4E00-\u9FA5]+")
teacher_all_template = re.compile(".*?/[\u4E00-\u9FA5]+/[\u4E00-\u9FA5]+")
teacher_id_template = re.compile("[0-9]+")
teacher_name_template = re.compile(".*?/([\u4E00-\u9FA5]+)/.*?")
teacher_post_template = re.compile(".*?/.*?/([\u4E00-\u9FA5]+)")


def main():
    initializeMySQL()
    # 体育课数据
    getSportsCourses()
    # 选修课程数据
    getGeneralCourses()


def requestOutlineCourses(page, kklxdm):
    des_url = "http://jwxt.gzhu.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbPartDisplay.html?gnmkdm=N253512&su=2006300072"
    request_data = bytes(
        urllib.parse.urlencode(
            {"rwlx": "1", "xkly": "1", "bklx_id": "0", "xqh_id": "1", "jg_id": "06", "zyh_id": "0630", "zyfx_id": "wfx",
             "njdm_id": "2020", "bh_id": "200630002", "xbm": "1", "xslbdm": "0", "ccdm": "1", "xsbj": "4294967296",
             "sfkknj": "1", "sfkkzy": "1", "sfznkx": "0", "zdkxms": "0", "sfkxq": "0", "sfkcfx": "0", "kkbk": "0",
             "kkbkdj": "0", "sfkgbcx": "1", "sfrxtgkcxd": "1", "tykczgxdcs": "2", "xkxnm": "2021", "xkxqm": "3",
             "kklxdm": kklxdm, "rlkz": "0", "xkzgbj": "0", "kspage": 1 + page * 10, "jspage": (page + 1) * 10,
             "jxbzb": ""})
        , encoding="utf-8")
    response = requests.post(url=des_url, headers=request_header, data=request_data).json()["tmpList"]
    return response


def requestClassInfo(rwlx, xkly, bklx_id, sfkknj, sfkkzy, kklxdm, course_number, xkkz_id):
    des_url = "http://jwxt.gzhu.edu.cn/jwglxt/xsxk/zzxkyzbjk_cxJxbWithKchZzxkYzb.html?gnmkdm=N253512&su=2006300072"
    request_data = bytes(
        urllib.parse.urlencode(
            # 也可以这么构造字典
            dict(rwlx=rwlx, xkly=xkly, bklx_id=bklx_id, xqh_id="1", jg_id="06", zyh_id="0630", zyfx_id="wfx",
                 njdm_id="2020", bh_id="200630002", xbm="1", xslbdm="0", ccdm="1", xsbj="4294967296", sfkknj=sfkknj,
                 sfkkzy=sfkkzy, sfznkx="0", zdkxms="0", sfkxq="0", sfkcfx="0", kkbk="0", kkbkdj="0", xkxnm="2021",
                 xkxqm="3", rlkz="0", kklxdm=kklxdm, kch_id=course_number, xkkz_id=xkkz_id, cxbj="0", fxbj="0"))
        , encoding="utf-8")
    response = requests.post(url=des_url, headers=request_header, data=request_data).json()
    return response


def getSportsCourses():
    # 课程信息
    superior_courses = []
    junior_classes = []
    # 教师信息
    teachers_information = []
    courses = requestOutlineCourses(0, "06")[0]  # 请求大纲课程数据
    classes = requestClassInfo(3, 0, "6C353C1B57AF6044E053206411AC1698", 0,
                               0, "06", "00121703", "C6075929FE511CBDE0530100007F89E8")  # 获取课程开设班级
    # 将班级信息整合
    for class_item in classes:
        # 整合课程信息
        course = {
            "ID": courses["kch_id"],
            "NAME": courses["kcmc"],
            "ACADEMY": class_item["kkxymc"],
            "CREDIT": courses["xf"]
        }
        superior_courses.append(course)
        class_ = {
            "COURSE_ID": courses["kch_id"],
            "CLASS_ID": courses["kch_id"] + "-" + str(classes.index(class_item) + 1),
            "GROUP_BY": class_item["kcxzmc"],
            "CATEGORY": re.findall(course_category_template, class_item["xkbz"])[0],
            "MODE": class_item["jxms"] if "jxms" in class_item.keys() else "暂无",
            "SITE": class_item["jxdd"] if "jxdd" in class_item.keys() else "暂无",
            "TIME": class_item["sksj"] if "sksj" in class_item.keys() else "暂无"
        }
        junior_classes.append(class_)
        # 整合班级老师信息
        teachers_id = []
        teachers = re.findall(teacher_all_template, class_item["jsxx"])
        for teacher in teachers:
            teacher = {
                "ID": re.findall(teacher_id_template, teacher)[0],
                "NAME": re.findall(teacher_name_template, teacher)[0],
                "POST": re.findall(teacher_post_template, teacher)[0]
            }
            teachers_id.append(teacher["ID"])
            teachers_information.append(teacher)
        else:
            insertSuperiorTable(superior_courses)
            insertJuniorTable(junior_classes)
            insertTeacherTable(teachers_information)
            insertTCRelationTable(teachers_id, class_["CLASS_ID"])  # 老师课程对应信息(即刻插入)


def getGeneralCourses():
    # 课程信息
    superior_courses = []
    junior_classes = []
    # 教师信息
    teachers_information = []
    page = 0
    course_number = ""
    while True:
        courses = requestOutlineCourses(page, "10")  # 请求课程数据
        # 是否获取课程成功
        if len(courses) == 0:
            break
        else:
            page = page + 1
        for course_item in courses:
            # 过滤相同的课程
            if course_number == course_item["kch_id"]:
                continue
            else:
                course_number = course_item["kch_id"]  # 更新课程编码
            classes = requestClassInfo(2, 0, 0, 0, 0, 10, course_number, "C5F7F076576D75F5E053206411AC2648")  # 获取课程开设班级
            # 将班级信息整合
            for class_item in classes:
                # 将课程信息整合
                course = {
                    "ID": course_item["kch_id"],
                    "NAME": course_item["kcmc"],
                    "ACADEMY": class_item["kkxymc"],
                    "CREDIT": course_item["xf"]
                }
                superior_courses.append(course)
                class_ = {
                    "COURSE_ID": course_item["kch_id"],
                    "CLASS_ID": course_item["kch_id"] + "-" + str(classes.index(class_item) + 1),
                    "GROUP_BY": class_item["kcxzmc"],
                    "CATEGORY": class_item["kcgsmc"],
                    "MODE": class_item["jxms"],
                    "SITE": re.sub("<br/>", "\n", class_item["jxdd"]).replace("#", ""),
                    "TIME": re.sub("<br/>", "\n", class_item["sksj"])
                }
                junior_classes.append(class_)
                # 整合班级老师信息
                teachers_id = []
                teachers = re.findall(teacher_all_template, class_item["jsxx"])
                for teacher in teachers:
                    teacher = {
                        "ID": re.findall(teacher_id_template, teacher)[0],
                        "NAME": re.findall(teacher_name_template, teacher)[0],
                        "POST": re.findall(teacher_post_template, teacher)[0]
                    }
                    teachers_id.append(teacher["ID"])
                    teachers_information.append(teacher)
                else:
                    insertSuperiorTable(superior_courses)
                    insertJuniorTable(junior_classes)
                    insertTeacherTable(teachers_information)
                    insertTCRelationTable(teachers_id, class_["CLASS_ID"])  # 老师课程对应信息(即刻插入)


# 初始化数据库
def initializeMySQL():
    database = pymysql.connect(user=mysql_account["user"], password=mysql_account["password"],
                               database="2021_school_courses")
    cursor = database.cursor()
    create_teachers = """
        CREATE TABLE IF NOT EXISTS teachers
        (
        ID CHAR(10),
        NAME CHAR(10) NOT NULL,
        POST CHAR(20),
        PRIMARY KEY (ID)
        )CHARSET utf8mb4;
    """
    create_superior_courses = """
        CREATE TABLE IF NOT EXISTS superior_courses
        (
        ID CHAR(50),
        NAME CHAR(100) NOT NULL,
        ACADEMY CHAR(50) NOT NULL,
        CREDIT DOUBLE NOT NULL,
        PRIMARY KEY (ID)
        )CHARSET utf8mb4;
    """
    create_junior_classes = """
        CREATE TABLE IF NOT EXISTS junior_classes
        (
        CLASS_ID CHAR(50),
        COURSE_ID CHAR(50) NOT NULL,
        GROUP_BY CHAR(50) NOT NULL,
        CATEGORY CHAR(20) NOT NULL,
        MODE CHAR(20),
        SITE CHAR(50),
        TIME CHAR(100),
        PRIMARY KEY (CLASS_ID),
        CONSTRAINT fk_junior_id FOREIGN KEY(COURSE_ID) REFERENCES superior_courses(ID)
        )CHARSET utf8mb4;
    """
    create_tc_relation = """
        CREATE TABLE IF NOT EXISTS tc_relation
        (
        TEACHER_ID CHAR(10),
        CLASS_ID CHAR(50),
        PRIMARY KEY (TEACHER_ID, CLASS_ID),
        CONSTRAINT fk_teacher_id FOREIGN KEY(TEACHER_ID) REFERENCES teachers(ID),
        CONSTRAINT fk_class_id FOREIGN KEY(CLASS_ID) REFERENCES junior_classes(CLASS_ID)
        )CHARSET utf8mb4;
    """
    cursor.execute(create_teachers)
    cursor.execute(create_superior_courses)
    cursor.execute(create_junior_classes)
    cursor.execute(create_tc_relation)
    database.commit()
    database.close()


# 插入主表数据
def insertSuperiorTable(superior_courses):
    database = pymysql.connect(user=mysql_account["user"], password=mysql_account["password"],
                               database="2021_school_courses")
    cursor = database.cursor()
    for superior_item in superior_courses:
        insert_operation = """
            INSERT IGNORE INTO superior_courses
            SELECT "{0}", "{1}", "{2}", {3} FROM DUAL
            WHERE NOT EXISTS (SELECT 1 FROM superior_courses WHERE ID = "{1}")
        """.format(superior_item["ID"], superior_item["NAME"], superior_item["ACADEMY"], superior_item["CREDIT"])
        cursor.execute(insert_operation)
    database.commit()
    database.close()


# 插入副表数据
def insertJuniorTable(junior_classes):
    database = pymysql.connect(user=mysql_account["user"], password=mysql_account["password"],
                               database="2021_school_courses")
    cursor = database.cursor()
    for class_item in junior_classes:
        insert_operation = """
            INSERT IGNORE INTO junior_classes
            (COURSE_ID, CLASS_ID, GROUP_BY, CATEGORY, MODE, SITE, TIME)
            VALUES 
            ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}")
        """.format(class_item["COURSE_ID"], class_item["CLASS_ID"], class_item["GROUP_BY"],
                   class_item["CATEGORY"], class_item["MODE"], class_item["SITE"], class_item["TIME"])
        cursor.execute(insert_operation)
    database.commit()
    database.close()


# 插入老师数据
def insertTeacherTable(teachers_information):
    database = pymysql.connect(user=mysql_account["user"], password=mysql_account["password"],
                               database="2021_school_courses")
    cursor = database.cursor()
    for teacher in teachers_information:
        insert_operation = """
            INSERT IGNORE INTO teachers
            (ID, NAME, POST)
            VALUES 
            ("{0}", "{1}", "{2}")
        """.format(teacher["ID"], teacher["NAME"], teacher["POST"])
        cursor.execute(insert_operation)
    database.commit()
    database.close()


# 插入老师课程对应数据
def insertTCRelationTable(teachers_id, class_id):
    database = pymysql.connect(user=mysql_account["user"], password=mysql_account["password"],
                               database="2021_school_courses")
    cursor = database.cursor()
    for teacher_id in teachers_id:
        insert_operation = """
            INSERT INTO tc_relation
            (TEACHER_ID, CLASS_ID)
            VALUES
            ("{0}", "{1}")
        """.format(teacher_id, class_id)
        cursor.execute(insert_operation)
    database.commit()
    database.close()


if __name__ == "__main__":
    main()
