# webtaxi-python
基于python的类网约车实现功能程序-适合期末设计
1.将本地或云端MySQL数据库导入taxi.sql文件
2.在main.py中修改user password (有需要修改host)内容
`def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # 替换为你的 MySQL 用户名
        password="admin",  # 替换为你的 MySQL 密码
        database="taxi"  # 替换为你的数据库名称
    )`
3.完成食用

