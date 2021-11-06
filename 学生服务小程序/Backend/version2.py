# 使用MySQL作为数据库，仅对主要功能进行了优化
# 数据库进行了分表，同时进一步实现了关键词查询的功能

import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)
# 数据库
mysql_account = {"user": "root", "password": "cytzero3434"}


@app.route('/')
def helloWorld():
    return "Hello World!"


@app.before_request
def createDatabase():
    database = pymysql.connect(user=mysql_account["user"], password=mysql_account["password"],
                               database="school_service")
    cursor = database.cursor()
    # 维修信息库
    create_repairing_table = """
        CREATE TABLE IF NOT EXISTS repairing_warehouse
        (
        ID INTEGER auto_increment,
        TIME TIMESTAMP default current_timestamp,
        USERNAME VARCHAR(20) not null,
        NAME VARCHAR(20) not null,
        PHONE VARCHAR(20) not null,
        DORM VARCHAR(20) not null,
        DETAILS TEXT not null,
        primary key (ID)
        )CHARSET=utf8mb4;
    """
    create_repaired_table = """
        CREATE TABLE IF NOT EXISTS repaired_warehouse
        (
        ID INTEGER unique not null,
        START TIMESTAMP not null,
        END TIMESTAMP default current_timestamp,
        WORKER VARCHAR(20) not null,
        USERNAME VARCHAR(20) not null,
        NAME VARCHAR(20) not null,
        PHONE VARCHAR(20) not null,
        DORM VARCHAR(20) not null,
        DETAILS TEXT not null
        )CHARSET=utf8mb4;
    """
    cursor.execute(create_repairing_table)
    cursor.execute(create_repaired_table)
    database.commit()
    database.close()


@app.route('/create/repair', methods=["POST"])
def createRepairInfo():
    database = pymysql.connect(user=mysql_account["user"], password=mysql_account["password"],
                               database="school_service")
    cursor = database.cursor()
    # 获取表单
    print(request.json)
    username = request.json.get("username")
    repair_info = request.json.get("repair_info")
    print(repair_info)
    name = repair_info["name"]
    phone = repair_info["phone"]
    dorm = repair_info["dorm"]
    details = repair_info["details"]
    # 检查数据
    if not all([username, name, phone, dorm, details]):
        return jsonify(dict(status=400, message="缺少请求参数"))
    # 插入数据(向"emoji"等数据插入时需要注意编码格式为"utf8mb4",同时在数据表中显示的是"?",但实际上输出是正确的)
    insert_repairInfo = """
        INSERT INTO repairing_warehouse
        (USERNAME, NAME, PHONE, DORM, DETAILS)
        VALUES
        ("{0}", "{1}", "{2}", "{3}", "{4}");
    """.format(username, name, phone, dorm, details)
    cursor.execute(insert_repairInfo)
    database.commit()
    database.close()
    return jsonify(dict(status=200, message="提交成功"))


@app.route('/retrieve/repair/waiting', methods=["GET"])
def retrieveWaitingRepairInfo():
    database = pymysql.connect(user=mysql_account["user"], password=mysql_account["password"],
                               database="school_service")
    cursor = database.cursor()
    # 获取用户名
    username = request.args.get("username")
    if username is None:
        return jsonify(dict(status=400, message="缺少请求参数"))
    # 检索用户信息
    retrieve_repairInfo = """
        SELECT * FROM repairing_warehouse where USERNAME = "{0}"
    """.format(username)
    cursor.execute(retrieve_repairInfo)
    # 手动转化为字典格式
    repairInfo = []
    query_result = cursor.fetchall()
    for query_item in query_result:
        query_item = {
            "id": query_item[0],
            "time": query_item[1].strftime("%Y-%m-%d %H:%M:%S"),
            "name": query_item[3],
            "phone": query_item[4],
            "dorm": query_item[5],
            "details": query_item[6]
        }
        repairInfo.append(query_item)
    return jsonify(dict(status=200, message="查询成功", details=repairInfo))


@app.route('/retrieve/repair/finished', methods=["GET"])
def retrieveFinishedRepairInfo():
    database = pymysql.connect(user=mysql_account["user"], password=mysql_account["password"],
                               database="school_service")
    cursor = database.cursor()
    # 获取用户名
    username = request.args.get("username")
    if username is None:
        return jsonify(dict(status=400, message="缺少请求参数"))
    # 检索用户信息
    retrieve_repairInfo = """
        SELECT * FROM repaired_warehouse where USERNAME = "{0}"
    """.format(username)
    cursor.execute(retrieve_repairInfo)
    # 手动转化为字典格式
    repairInfo = []
    query_result = cursor.fetchall()
    for query_item in query_result:
        query_item = {
            "id": query_item[0],
            "start": query_item[1].strftime("%Y-%m-%d %H:%M:%S"),
            "end": query_item[2].strftime("%Y-%m-%d %H:%M:%S"),
            "worker": query_item[3],
            "name": query_item[5],
            "phone": query_item[6],
            "dorm": query_item[7],
            "details": query_item[8]
        }
        repairInfo.append(query_item)
    return jsonify(dict(status=200, message="查询成功", details=repairInfo))


@app.route('/update/repair', methods=["POST"])
def updateRepairInfo():
    database = pymysql.connect(user=mysql_account["user"], password=mysql_account["password"],
                               database="school_service")
    cursor = database.cursor()
    # 获取表单
    id = request.json.get("id")
    name = request.json.get("name")
    phone = request.json.get("phone")
    dorm = request.json.get("dorm")
    details = request.json.get("details")
    # 检查数据
    if not all([name, phone, dorm, details]):
        return jsonify(dict(status=400, message="缺省请求参数"))
    # 更新数据库
    update_repairInfo = """
        UPDATE repairing_warehouse SET name = "{0}", phone = "{1}", dorm = "{2}", details = "{3}"
        where id = "{4}"
    """.format(name, phone, dorm, details, id)
    cursor.execute(update_repairInfo)
    database.commit()
    database.close()
    return jsonify(dict(status=200, message="更新成功"))


@app.route('/delete/repair', methods=["DELETE"])
def deleteRepairInfo():
    database = pymysql.connect(user=mysql_account["user"], password=mysql_account["password"],
                               database="school_service")
    cursor = database.cursor()
    # 获取条目id
    id = request.args.get("id")
    if id is None:
        return jsonify(dict(status=400, message="缺少请求参数"))
    # 查询删除条目
    delete_repairInfo = """
        DELETE FROM repairing_warehouse where ID = ("{0}")
    """.format(id)
    cursor.execute(delete_repairInfo)
    database.commit()
    database.close()
    return jsonify(dict(status=200, message="删除成功"))


@app.route('/search/courses', methods=["GET"])
def retrieveCourses():
    database = pymysql.connect(user=mysql_account["user"], password=mysql_account["password"],
                               database="2021_school_courses")
    cursor = database.cursor()
    search_result = []
    # 获取检索参数
    page_number = int(request.args.get("page_number"))
    page_size = int(request.args.get("page_size"))
    keyword = request.args.get("keyword")
    # 查询
    search_operation = """
        SELECT superior_courses.ID, superior_courses.NAME, superior_courses.ACADEMY, superior_courses.CREDIT,
        junior_classes.CATEGORY, junior_classes.GROUP_BY, junior_classes.SITE, junior_classes.TIME,
        teachers.NAME FROM tc_relation
        INNER JOIN teachers ON teachers.ID = tc_relation.TEACHER_ID
        INNER JOIN junior_classes ON junior_classes.CLASS_ID = tc_relation.CLASS_ID
        AND junior_classes.CATEGORY LIKE "%{0}%"
        INNER JOIN superior_courses ON junior_classes.COURSE_ID = superior_courses.ID
        LIMIT {1}, {2};
    """.format(keyword, (page_number - 1) * page_size, page_size)
    cursor.execute(search_operation)
    query_result = cursor.fetchall()
    # 转化为"json"格式
    for query_item in query_result:
        search_item = {
            "id": query_item[0],
            "course_name": query_item[1],
            "academy": query_item[2],
            "category": query_item[3],
            "group_by": query_item[4],
            "site": query_item[5],
            "time": query_item[6],
            "teacher": query_item[7]
        }
        search_result.append(search_item)
    return jsonify(dict(status=200, message="查询成功", details=search_result,
                        page_number=page_number, page_size=page_size))


if __name__ == '__main__':
    app.run(host="0.0.0.0")

