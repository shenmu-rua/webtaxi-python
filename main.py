import mysql.connector
import random
from tkinter import *
from tkinter import messagebox
from datetime import datetime
from tkinter import ttk

# 数据库连接
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # 替换为你的 MySQL 用户名
        password="admin",  # 替换为你的 MySQL 密码
        database="taxi"  # 替换为你的数据库名称
    )

# 用户注册
def user_register():
    user_name = user_name_entry.get()
    user_phone = user_phone_entry.get()
    user_password = user_password_entry.get()
    user_balance = 0.0  # 初始余额为0
    user_password = user_password_entry.get()
    db = connect_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO User (name, phone_number, password, register_time, balance) VALUES (%s, %s, %s, %s, %s)",
                       (user_name, user_phone, user_password, datetime.now(), user_balance))
        db.commit()
        messagebox.showinfo("注册成功", "用户注册成功！")
        register_window.destroy()
    except mysql.connector.Error as err:
        messagebox.showerror("注册失败", f"注册失败: {err}")
    finally:
        cursor.close()
        db.close()

# 司机注册
def driver_register():
    driver_name = driver_name_entry.get()
    driver_phone = driver_phone_entry.get()
    driver_password = driver_password_entry.get()
    driver_plate = driver_plate_entry.get()
    driver_vehicle_type = driver_vehicle_type_entry.get()

    if not driver_name or not driver_phone or not driver_password or not driver_plate or not driver_vehicle_type:
        messagebox.showerror("注册失败", "所有字段均为必填项")
        return

    db = connect_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO Driver (name, phone_number, driver_password, plate_number, vehicle_type, register_time) VALUES (%s, %s, %s, %s, %s, %s)",
            (driver_name, driver_phone, driver_password, driver_plate, driver_vehicle_type, datetime.now())
        )
        db.commit()
        messagebox.showinfo("注册成功", "司机注册成功！")
        register_window.destroy()
    except mysql.connector.Error as err:
        messagebox.showerror("注册失败", f"注册失败: {err}")
    finally:
        cursor.close()
        db.close()
# 管理员登录
from tkinter import ttk  # 导入 ttk 模块以使用 Treeview

# 管理员登录
def admin_main_window():
    admin_window = Toplevel()
    admin_window.title("管理员主界面")
    admin_window.geometry("800x400")

    Label(admin_window, text="欢迎管理员！").pack()

    # 显示用户列表
    def load_users():
        for row in tree.get_children():
            tree.delete(row)  # 清空现有数据
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT user_id, name, phone_number, balance FROM User")
        users = cursor.fetchall()
        for user in users:
            tree.insert("", "end", values=(user[0], user[1], user[2], user[3]))
        cursor.close()
        db.close()

    def update_balance():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("错误", "请先选择一个用户")
            return
        user_id = tree.item(selected_item[0], "values")[0]
        new_balance = balance_entry.get()
        if not new_balance.isdigit():
            messagebox.showerror("错误", "请输入有效的余额")
            return
        db = connect_db()
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE User SET balance = %s WHERE user_id = %s", (float(new_balance), user_id))
            db.commit()
            messagebox.showinfo("成功", "余额已更新")
            load_users()  # 更新用户列表
        except mysql.connector.Error as err:
            messagebox.showerror("错误", f"更新失败: {err}")
        finally:
            cursor.close()
            db.close()

    # 用户列表表格
    columns = ("ID", "姓名", "手机号", "余额")
    tree = ttk.Treeview(admin_window, columns=columns, show="headings")
    tree.heading("ID", text="用户ID")
    tree.heading("姓名", text="姓名")
    tree.heading("手机号", text="手机号")
    tree.heading("余额", text="余额")
    tree.pack(fill=BOTH, expand=True)

    # 修改余额部分
    Label(admin_window, text="新余额:").pack(pady=5)
    balance_entry = Entry(admin_window)
    balance_entry.pack(pady=5)
    Button(admin_window, text="更新余额", command=update_balance).pack(pady=5)

    # 加载用户数据
    load_users()

# 用户登录
def user_login():
    user_phone = user_phone_entry.get()
    user_password = user_password_entry.get()

    # 检查是否为管理员登录
    if user_phone == "admin" and user_password == "admin":
        messagebox.showinfo("登录成功", "欢迎管理员！")
        login_window.destroy()
        admin_main_window()
        return

    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT user_id, name, balance FROM User WHERE phone_number = %s AND password = %s", (user_phone, user_password))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    if user:
        messagebox.showinfo("登录成功", f"欢迎 {user[1]}！")
        login_window.destroy()
        user_main_window(user)
    else:
        messagebox.showerror("登录失败", "手机号或密码错误")

# 司机登录
def driver_login():
    driver_phone = driver_phone_entry.get()
    driver_password = driver_password_entry.get()  # 从输入框获取密码

    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT driver_id, name FROM Driver WHERE phone_number = %s AND driver_password = %s", 
                   (driver_phone, driver_password))  # 修正字段名为 driver_password
    driver = cursor.fetchone()
    cursor.close()
    db.close()

    if driver:
        messagebox.showinfo("登录成功", f"欢迎 {driver[1]}！")
        login_window.destroy()
        driver_main_window(driver)
    else:
        messagebox.showerror("登录失败", "手机号或密码错误")  # 提示信息更准确
        

# 用户主界面
def user_main_window(user):
    user_window = Toplevel()
    user_window.title("用户主界面")
    user_window.geometry("300x200")

    balance_label = Label(user_window, text=f"余额: {user[2]}")
    balance_label.pack()

    def refresh_balance():
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT balance FROM User WHERE user_id = %s", (user[0],))
        updated_balance = cursor.fetchone()[0]
        cursor.close()
        db.close()
        balance_label.config(text=f"余额: {updated_balance}")
        user[2] = updated_balance  # 更新用户余额

    Label(user_window, text=f"欢迎 {user[1]}！").pack()

    def order_ride():
        db = connect_db()
        cursor = db.cursor()

        # 随机选择司机
        cursor.execute("SELECT driver_id, name, phone_number, plate_number, vehicle_type FROM Driver")
        drivers = cursor.fetchall()
        if not drivers:
            messagebox.showerror("叫车失败", "当前没有可用司机")
            cursor.close()
            db.close()
            return

        selected_driver = random.choice(drivers)  # 随机选择一个司机
        driver_id, driver_name, driver_phone, driver_plate, driver_vehicle_type = selected_driver

        # 随机生成订单金额
        order_cost = random.randint(1, 100)

        # 创建订单（不扣除余额）
        try:
            cursor.execute(
                "INSERT INTO need (user_id, driver_id, order_time, cost) VALUES (%s, %s, %s, %s)",
                (user[0], driver_id, datetime.now(), order_cost)
            )
            db.commit()
            order_id = cursor.lastrowid  # 获取刚插入订单的 ID
        except mysql.connector.Error as err:
            messagebox.showerror("叫车失败", f"订单创建失败: {err}")
            cursor.close()
            db.close()
            return

        cursor.close()
        db.close()

        # 弹出订单详情界面
        ride_window = Toplevel()
        ride_window.title("订单详情")
        ride_window.geometry("300x300")

        Label(ride_window, text="订单已创建！").pack(pady=10)
        Label(ride_window, text=f"司机姓名: {driver_name}").pack(pady=5)
        Label(ride_window, text=f"司机电话: {driver_phone}").pack(pady=5)
        Label(ride_window, text=f"车牌号: {driver_plate}").pack(pady=5)
        Label(ride_window, text=f"车辆类型: {driver_vehicle_type}").pack(pady=5)
        Label(ride_window, text=f"订单金额: {order_cost} 元").pack(pady=10)

        # 到达按钮逻辑
        def complete_order():
            db = connect_db()
            cursor = db.cursor()

            # 检查用户余额是否足够
            if user[2] < order_cost:
                messagebox.showerror("订单失败", "余额不足，请充值")
                cursor.close()
                db.close()
                return

            try:
                # 更新订单完成时间
                cursor.execute(
                    "UPDATE need SET complete_time = %s WHERE order_id = %s",
                    (datetime.now(), order_id)
                )
                # 扣除用户余额
                cursor.execute(
                    "UPDATE User SET balance = balance - %s WHERE user_id = %s",
                    (order_cost, user[0])
                )
                db.commit()
                messagebox.showinfo("订单完成", "订单已完成，余额已扣除")
                ride_window.destroy()
                refresh_balance()  # 更新余额显示
            except mysql.connector.Error as err:
                messagebox.showerror("订单失败", f"更新失败: {err}")
            finally:
                cursor.close()
                db.close()

        Button(ride_window, text="到达", command=complete_order).pack(pady=20)

    Button(user_window, text="叫车", command=order_ride).pack()
# 司机主界面
def driver_main_window(driver):
    driver_window = Toplevel()
    driver_window.title("司机主界面")
    driver_window.geometry("1000x400")

    Label(driver_window, text=f"欢迎 {driver[1]}！").pack(pady=10)

    # 显示订单历史
    def load_order_history():
        for row in tree.get_children():
            tree.delete(row)  # 清空现有数据
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT order_id, user_id, order_time, complete_time, cost FROM need WHERE driver_id = %s AND complete_time IS NOT NULL",
            (driver[0],)
        )
        orders = cursor.fetchall()
        for order in orders:
            tree.insert("", "end", values=(order[0], order[1], order[2], order[3], order[4]))
        cursor.close()
        db.close()

    # 订单历史表格
    columns = ("订单ID", "用户ID", "下单时间", "完成时间", "金额")
    tree = ttk.Treeview(driver_window, columns=columns, show="headings")
    tree.heading("订单ID", text="订单ID")
    tree.heading("用户ID", text="用户ID")
    tree.heading("下单时间", text="下单时间")
    tree.heading("完成时间", text="完成时间")
    tree.heading("金额", text="金额")
    tree.pack(fill=BOTH, expand=True, pady=10)

    # 加载订单历史
    load_order_history()

# 注册界面
    global register_window, user_name_entry, user_phone_entry, user_password_entry, driver_name_entry, driver_phone_entry, driver_password_entry, driver_plate_entry, driver_vehicle_type_entry
    global register_window, user_name_entry, user_phone_entry, user_password_entry, driver_name_entry, driver_phone_entry, driver_plate_entry, driver_vehicle_type_entry
    register_window = Toplevel()
    register_window.title("注册")
    register_window.geometry("300x400")

    # 用户注册
    Label(register_window, text="用户注册").pack()
    Label(register_window, text="姓名:").pack()
    user_name_entry = Entry(register_window)
    user_name_entry.pack()
    Label(register_window, text="手机号:").pack()
    user_phone_entry = Entry(register_window)
    user_phone_entry.pack()
    Label(register_window, text="密码:").pack()
    user_password_entry = Entry(register_window, show="*")
    user_password_entry.pack()
    Button(register_window, text="注册", command=user_register).pack()

    # 司机注册
    Label(register_window, text="司机注册").pack()
    Label(register_window, text="姓名:").pack()
    driver_name_entry = Entry(register_window)
    driver_name_entry.pack()
    Label(register_window, text="手机号:").pack()
    driver_phone_entry = Entry(register_window)
    Label(register_window, text="密码:").pack()
    driver_password_entry = Entry(register_window, show="*")
    driver_password_entry.pack()
    Label(register_window, text="车牌号:").pack()
    Label(register_window, text="车牌号:").pack()
    driver_plate_entry = Entry(register_window)
    driver_plate_entry.pack()
    Label(register_window, text="车型:").pack()
    driver_vehicle_type_entry = Entry(register_window)
    driver_vehicle_type_entry.pack()
    Button(register_window, text="注册", command=driver_register).pack()

# 注册界面
def show_register():
    global register_window, user_name_entry, user_phone_entry, user_password_entry, driver_name_entry, driver_phone_entry, driver_password_entry, driver_plate_entry, driver_vehicle_type_entry
    register_window = Toplevel()
    register_window.title("注册")
    register_window.geometry("300x500")

    # 用户注册
    Label(register_window, text="用户注册").pack()
    Label(register_window, text="姓名:").pack()
    user_name_entry = Entry(register_window)
    user_name_entry.pack()
    Label(register_window, text="手机号:").pack()
    user_phone_entry = Entry(register_window)
    user_phone_entry.pack()
    Label(register_window, text="密码:").pack()
    user_password_entry = Entry(register_window, show="*")
    user_password_entry.pack()
    Button(register_window, text="注册", command=user_register).pack()

    # 司机注册
    Label(register_window, text="司机注册").pack()
    Label(register_window, text="姓名:").pack()
    driver_name_entry = Entry(register_window)
    driver_name_entry.pack()
    Label(register_window, text="手机号:").pack()
    driver_phone_entry = Entry(register_window)
    driver_phone_entry.pack()
    Label(register_window, text="密码:").pack()
    driver_password_entry = Entry(register_window, show="*")
    driver_password_entry.pack()
    Label(register_window, text="车牌号:").pack()
    driver_plate_entry = Entry(register_window)
    driver_plate_entry.pack()
    Label(register_window, text="车型:").pack()
    driver_vehicle_type_entry = Entry(register_window)
    driver_vehicle_type_entry.pack()
    Button(register_window, text="注册", command=driver_register).pack()

# 登录界面
def show_login():
    global login_window, user_phone_entry, user_password_entry, driver_phone_entry, driver_password_entry  # 添加 driver_password_entry
    login_window = Toplevel()
    login_window.title("登录")
    login_window.geometry("300x300")

    # 用户登录
    Label(login_window, text="用户登录").pack()
    Label(login_window, text="手机号:").pack()
    user_phone_entry = Entry(login_window)
    user_phone_entry.pack()
    Label(login_window, text="密码:").pack()
    user_password_entry = Entry(login_window, show="*")
    user_password_entry.pack()
    Button(login_window, text="登录", command=user_login).pack()

    # 司机登录
    Label(login_window, text="司机登录").pack()
    Label(login_window, text="手机号:").pack()
    driver_phone_entry = Entry(login_window)
    driver_phone_entry.pack()
    Label(login_window, text="密码:").pack()
    driver_password_entry = Entry(login_window, show="*")  # 确保 driver_password_entry 被定义
    driver_password_entry.pack()
    Button(login_window, text="登录", command=driver_login).pack()

# 主界面
def main_window():
    main_window = Tk()
    main_window.title("网约车系统")
    main_window.geometry("300x200")

    Button(main_window, text="登录", command=show_login).pack(pady=20)
    Button(main_window, text="注册", command=show_register).pack(pady=20)

    main_window.mainloop()

if __name__ == "__main__":
    main_window()