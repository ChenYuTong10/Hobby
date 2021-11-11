import requests
import urllib.request
import urllib.error
import re
import sqlite3

# 请求头
request_header = {
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Cookie": "JSESSIONID=F7878DA7AA0EBDED66C085DE01BF2C47; SF_cookie_18=49731168",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47"
}

# 匹配模板
course_name_template = re.compile("[\u4E00-\u9FA5]+")
course_teacher_template = re.compile(".*?/(.*?)/.*?")
teacher_contact_template = re.compile(".*?([0-9]+)")

# 课程信息
main_courses = []
sports_courses = []
general_courses = []
major_courses = []


def main():
    database_save_path = u"广州大学选修数据.db"
    initializeDatabase(database_save_path)
    # 主修课程
    getMainCourse()
    # 体育课数据
    getSportsCourse()
    # 选修课程数据
    getGeneralCourse()
    # 其他特殊课程
    getMajorCourse()
    # 数据库
    saveAsDatabase(database_save_path)


def requestOutlineCourse(page, kklxdm):
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


def getMainCourse():
    for page in range(0, 100):
        # 请求课程数据
        courses = requestOutlineCourse(page, "01")
        course_number = ""
        for course_item in courses:
            # 过滤相同的课程
            if course_number == course_item["kch_id"]:
                continue
            course_number = course_item["kch_id"]  # 获取课程编码
            classes = requestClassInfo(1, 1, 0, 1, 1, "01", course_number, "C6075929FE3B1CBDE0530100007F89E8")
            # 将班级信息整合
            for class_item in classes:
                class_teachers = re.findall(course_teacher_template, class_item["jsxx"])
                # 将老师名称合并
                teacher = ""
                for teacher_item in class_teachers:
                    teacher = teacher + teacher_item + " "
                # 处理没有备注的情况
                remark = ""
                if "xkbz" in class_item.keys():  # 判断是否存在该"key"
                    remark = class_item["xkbz"]
                course = {
                    "id": course_item["kch_id"],
                    "name": course_item["kcmc"],
                    "teacher": teacher,
                    "academy": class_item["kkxymc"],
                    "time": re.sub("<br/>", " ", class_item["sksj"]),
                    "mode": class_item["jxms"],
                    "classroom": class_item["jxdd"],
                    "credit": course_item["xf"],
                    "remark": remark
                }
                main_courses.append(course)


def getSportsCourse():
    # 请求课程数据
    courses = requestOutlineCourse(0, "06")[0]
    classes = requestClassInfo(3, 0, "6C353C1B57AF6044E053206411AC1698", 0,
                               0, "06", "00121703", "C6075929FE511CBDE0530100007F89E8")  # 获取课程开设班级
    # 将班级信息整合
    for class_item in classes:
        class_teachers = re.findall(course_teacher_template, class_item["jsxx"])[0]
        course = {
            "id": courses["kch_id"],
            "name": re.findall(course_name_template, class_item["xkbz"])[0],
            "teacher": class_teachers,
            "academy": class_item["kkxymc"],
            "contact": re.findall(teacher_contact_template, class_item["xkbz"])[0],
            "time": re.sub("<br/>", " ", class_item["sksj"]),
            "classroom": class_item["jxdd"],
            "credit": courses["xf"]
        }
        sports_courses.append(course)


def getGeneralCourse():
    for page in range(0, 24):
        # 请求课程数据
        courses = requestOutlineCourse(page, 10)
        course_number = ""
        for course_item in courses:
            # 过滤相同的课程
            if course_number == course_item["kch_id"]:
                continue
            course_number = course_item["kch_id"]  # 获取课程编码
            classes = requestClassInfo(2, 0, 0, 0, 0, 10, course_number, "C5F7F076576D75F5E053206411AC2648")  # 获取课程开设班级
            # 将班级信息整合
            for class_item in classes:
                class_teachers = re.findall(course_teacher_template, class_item["jsxx"])
                # 将老师名称合并
                teacher = ""
                for teacher_item in class_teachers:
                    teacher = teacher + teacher_item + " "
                # 处理没有备注的情况
                remark = ""
                if "xkbz" in class_item.keys():  # 判断是否存在该"key"
                    remark = class_item["xkbz"]
                course = {
                    "id": course_item["kch_id"],
                    "name": course_item["kcmc"],
                    "teacher": teacher,
                    "academy": class_item["kkxymc"],
                    "time": re.sub("<br/>", " ", class_item["sksj"]),
                    "mode": class_item["jxms"],
                    "type": class_item["kcgsmc"],
                    "classroom": class_item["jxdd"],
                    "credit": course_item["xf"],
                    "remark": remark
                }
                general_courses.append(course)


def getMajorCourse():
    # 请求课程数据
    courses = requestOutlineCourse(0, 11)
    course_number = ""
    for course_item in courses:
        # 过滤相同的课程
        if course_number == course_item["kch_id"]:
            continue
        course_number = course_item["kch_id"]  # 获取课程编码
        classes = requestClassInfo(2, 0, 0, 0, 0, 11, course_number, "C5F75C671B3F6546E053206411AC9898")  # 获取课程开设班级
        # 将班级信息整合
        for class_item in classes:
            class_teachers = re.findall(course_teacher_template, class_item["jsxx"])
            # 将老师名称合并
            teacher = ""
            for teacher_item in class_teachers:
                teacher = teacher + teacher_item + " "
            # 处理没有备注的情况
            remark = ""
            if "xkbz" in class_item.keys():  # 判断是否存在该"key"
                remark = class_item["xkbz"]
            course = {
                "id": course_item["kch"],
                "name": course_item["kcmc"],
                "teacher": teacher,
                "academy": class_item["kkxymc"],
                "time": re.sub("<br/>", " ", class_item["sksj"]),
                "mode": class_item["jxms"],
                "type": class_item["kcgsmc"],
                "classroom": class_item["jxdd"],
                "credit": course_item["xf"],
                "remark": remark
            }
            major_courses.append(course)


# 初始化数据库
def initializeDatabase(database_save_path):
    database = sqlite3.connect(database_save_path)
    cursor = database.cursor()
    main_operation = """
            create table IF NOT EXISTS 广州大学主修课程
            (id INTEGER not null,
            name text not null,
            teacher text not null,
            academy text not null,
            time text not null,
            mode text not null,
            classroom text,
            credit double not null,
            remark text
            )
    """
    sports_operation = """
        create table IF NOT EXISTS 广州大学体育课程
            (id INTEGER not null,
            name text not null,
            teacher text not null,
            academy text not null,
            contact text not null,
            time text not null,
            classroom text not null,
            credit double not null
            )
    """
    general_operation = """
            create table IF NOT EXISTS 广州大学通识选修课程
            (id INTEGER not null,
            name text not null,
            teacher text not null,
            academy text not null,
            time text not null,
            mode text not null,
            type text not null,
            classroom text,
            credit double not null,
            remark text
            )
    """
    special_operation = """
            create table IF NOT EXISTS 广州大学其他特殊课程
            (id INTEGER not null,
            name text not null,
            teacher text not null,
            academy text not null,
            time text not null,
            mode text not null,
            type text not null,
            classroom text,
            credit double not null,
            remark text
            )
    """
    cursor.execute(main_operation)
    cursor.execute(sports_operation)
    cursor.execute(general_operation)
    cursor.execute(special_operation)
    database.commit()
    database.close()


# 保存数据
def saveAsDatabase(database_save_path):
    database = sqlite3.connect(database_save_path)
    cursor = database.cursor()
    for course in main_courses:
        # 表面看起来500条,实际分页了
        sql_operation = """
            insert into 广州大学主修课程 (id, name, teacher, academy, time, mode, classroom, credit, remark)
                values ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", "{8}")
        """.format(course["id"], course["name"], course["teacher"],
                   course["academy"], course["time"], course["mode"],
                   course["classroom"], course["credit"], course["remark"])
        cursor.execute(sql_operation)
        database.commit()

    for course in sports_courses:
        sql_operation = """
            insert into 广州大学体育课程 (id, name, teacher, academy, contact, time, classroom, credit)
                values ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}")
        """.format(course["id"], course["name"], course["teacher"], course["academy"],
                   course["contact"], course["time"], course["classroom"], course["credit"])
        cursor.execute(sql_operation)
        database.commit()

    for course in general_courses:
        sql_operation = """
            insert into 广州大学通识选修课程 (id, name, teacher, academy, time, mode, type, classroom, credit, remark)
                values ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", "{8}", "{9}")
        """.format(course["id"], course["name"], course["teacher"], course["academy"], course["time"],
                   course["mode"], course["type"], course["classroom"], course["credit"], course["remark"])
        cursor.execute(sql_operation)
        database.commit()

    for course in major_courses:
        sql_operation = """
            insert into 广州大学其他特殊课程 (id, name, teacher, academy, time, mode, type, classroom, credit, remark)
                values ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", "{8}", "{9}")
        """.format(course["id"], course["name"], course["teacher"], course["academy"], course["time"],
                   course["mode"], course["type"], course["classroom"], course["credit"], course["remark"])
        cursor.execute(sql_operation)
        database.commit()
    database.close()


if __name__ == "__main__":
    main()
