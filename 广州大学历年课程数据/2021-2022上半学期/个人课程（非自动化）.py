import requests
import urllib.request
import urllib.error
import xlwt
import sqlite3

# 课程数据
courses = []


def main():
    # 准备工作
    excel_save_path = u"广州大学课程数据.xls"
    database_save_path = u"广州大学课程数据.db"
    initializeDatabase(database_save_path)  # 初始化数据库
    # 获取数据
    html = requestURL()
    print(html)
    # 处理数据
    analyzeData(html)
    # 保存Excel
    saveAsExcel(excel_save_path)
    # 保存数据库
    saveAsDatabase(database_save_path)


# 请求数据
def requestURL():
    base_url = "http://jwxt.gzhu.edu.cn/jwglxt/kbcx/xskbcx_cxXsKb.html?"
    request_header = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",  # 这个在请求"ajax"包时起到决定作用
        "Cookie": "JSESSIONID=DAAAADD38C630FD65845F1474160DDC8; SF_cookie_18=63297385",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38"
    }
    request_params = {"gnmkdm": "N253508", "su": "2006300072"}
    # 对于"requests"库,是否变成字节流无所谓
    request_data = bytes(urllib.parse.urlencode({"xnm": "2021", "xqm": "3"}), encoding="utf-8")
    response = requests.post(base_url+urllib.parse.urlencode(request_params),
                             headers=request_header,
                             data=request_data).json()
    return response


# 处理数据
def analyzeData(html):
    course_list = html["kbList"]
    # 处理数据
    for item in course_list:
        course = {
            # 字典使用"[]"访问属性,对象使用"."访问属性
            "name": item["kcmc"],
            "time": item["xqjmc"]+item["jc"],
            "duration": item["zcd"],
            "classroom": item["cdmc"].replace("#", ""),
            "lecturer": item["xm"]
        }
        print(course)
        # 加入列表
        courses.append(course)


# 保存至Excel
def saveAsExcel(save_path):
    work_book = xlwt.Workbook(encoding="utf-8", style_compression=0)
    work_sheet = work_book.add_sheet("广州大学课程数据", cell_overwrite_ok=True)
    head = ("课程名称", "上课时间", "周数", "上课地点", "授课老师")
    # 写入信息
    for line in range(0, len(courses)):
        for column in range(0, 5):
            # 写入表头
            if line == 0:
                work_sheet.write(line, column * 2, head[column])
        # 写入对应的信息
        work_sheet.write(line+1, 0, courses[line]["name"])
        work_sheet.write(line+1, 2, courses[line]["time"])
        work_sheet.write(line+1, 4, courses[line]["duration"])
        work_sheet.write(line+1, 6, courses[line]["classroom"])
        work_sheet.write(line+1, 8, courses[line]["lecturer"])
    work_book.save(save_path)


# 初始化数据库
def initializeDatabase(database_save_path):
    database = sqlite3.connect(database_save_path)
    cursor = database.cursor()
    # 注意检查数据库是否存在
    sql_operation = """
        create table IF NOT EXISTS 广州大学课程数据
            (id INTEGER not null
                primary key autoincrement,
            name text not null,
            time text not null,
            duration text not null,
            classroom text not null,
            lecturer text not null
            )
    """
    cursor.execute(sql_operation)
    database.commit()
    database.close()


# 保存至数据库
def saveAsDatabase(database_save_path):
    database = sqlite3.connect(database_save_path)
    cursor = database.cursor()
    for course in courses:
        sql_operation = """
            insert into 广州大学课程数据 (name, time, duration, classroom, lecturer)
                values ("{0}", "{1}", "{2}", "{3}", "{4}")
        """.format(course["name"], course["time"], course["duration"], course["classroom"], course["lecturer"])
        cursor.execute(sql_operation)
        database.commit()
    database.close()


if __name__ == "__main__":
    main()
