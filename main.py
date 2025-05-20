import mysql.connector
import random
from tkinter import *
from tkinter import messagebox
from datetime import datetime
from tkinter import ttk
import tkinter as tk
import os

# 数据库连接
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="taxi"
    )


# 用户注册
def user_register():
    user_name = user_name_entry.get()
    user_phone = user_phone_entry.get()
    user_password = user_password_entry.get()
    user_balance = 0.0
    db = connect_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO User (name, phone_number, password, register_time, balance) VALUES (%s, %s, %s, %s, %s)",
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

    if not all([driver_name, driver_phone, driver_password, driver_plate, driver_vehicle_type]):
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


# 管理员主界面
def admin_main_window():
    admin_window = Toplevel()
    admin_window.title("次次打车管理系统")
    admin_window.geometry("1000x600")
    set_window_icon(admin_window)

    notebook = ttk.Notebook(admin_window)
    notebook.pack(fill=BOTH, expand=True)

    # 用户管理标签页
    user_frame = Frame(notebook)
    notebook.add(user_frame, text="用户管理")

    # 司机管理标签页
    driver_frame = Frame(notebook)
    notebook.add(driver_frame, text="司机管理")

    # 用户管理内容
    def load_users():
        tree.delete(*tree.get_children())
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT user_id, name, phone_number, balance FROM User")
        for user in cursor.fetchall():
            tree.insert("", "end", values=user)
        cursor.close()
        db.close()

    columns = ("ID", "姓名", "手机号", "余额")
    tree = ttk.Treeview(user_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill=BOTH, expand=True)

    Label(user_frame, text="新余额:").pack()
    balance_entry = Entry(user_frame)
    balance_entry.pack()
    Button(user_frame, text="更新余额", command=lambda: update_balance(tree, balance_entry)).pack()
    Button(user_frame, text="刷新数据", command=load_users).pack()

    # 司机管理内容
    def load_drivers():
        driver_tree.delete(*driver_tree.get_children())
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT driver_id, name, phone_number, plate_number, vehicle_type, register_time FROM Driver")
        for driver in cursor.fetchall():
            driver_tree.insert("", "end", values=driver)
        cursor.close()
        db.close()

    driver_columns = ("ID", "姓名", "手机号", "车牌号", "车型", "注册时间")
    driver_tree = ttk.Treeview(driver_frame, columns=driver_columns, show="headings")
    for col in driver_columns:
        driver_tree.heading(col, text=col)
    driver_tree.pack(fill=BOTH, expand=True)
    Button(driver_frame, text="刷新数据", command=load_drivers).pack()

    load_users()
    load_drivers()


def update_balance(tree, entry):
    selected = tree.selection()
    if not selected:
        messagebox.showerror("错误", "请选择用户")
        return
    try:
        new_balance = float(entry.get())
        user_id = tree.item(selected[0], "values")[0]
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("UPDATE User SET balance = %s WHERE user_id = %s", (new_balance, user_id))
        db.commit()
        messagebox.showinfo("成功", "余额已更新")
        cursor.close()
        db.close()
    except ValueError:
        messagebox.showerror("错误", "请输入有效数字")
    except mysql.connector.Error as err:
        messagebox.showerror("错误", f"更新失败: {err}")


# 用户登录
def user_login():
    phone = user_phone_entry.get()
    password = user_password_entry.get()

    if phone == "admin" and password == "admin":
        admin_main_window()
        login_window.destroy()
        return

    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT user_id, name, balance FROM User WHERE phone_number = %s AND password = %s",
                   (phone, password))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user:
        messagebox.showinfo("登录成功", f"欢迎 {user[1]}！")
        login_window.destroy()
        user_main_window(user)
    else:
        messagebox.showerror("登录失败", "手机号或密码错误")


# 用户主界面
def user_main_window(user):
    user_window = Toplevel()
    user_window.title("次次打车-用户中心")
    user_window.geometry("400x300")
    set_window_icon(user_window)

    def refresh_balance():
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT balance FROM User WHERE user_id = %s", (user[0],))
        new_balance = cursor.fetchone()[0]
        balance_label.config(text=f"余额: {new_balance}")
        cursor.close()
        db.close()

    Label(user_window, text=f"欢迎 {user[1]}！").pack(pady=10)
    balance_label = Label(user_window, text=f"余额: {user[2]}")
    balance_label.pack()

    # 功能按钮
    btn_frame = Frame(user_window)
    btn_frame.pack(pady=10)

    Button(btn_frame, text="叫车", command=lambda: order_ride(user, refresh_balance)).pack(side=LEFT, padx=5)
    Button(btn_frame, text="历史订单", command=lambda: show_order_history(user)).pack(side=LEFT, padx=5)
    Button(btn_frame, text="充值余额", command=lambda: show_recharge(user, refresh_balance)).pack(side=LEFT, padx=5)


# 订单功能
def order_ride(user, refresh_callback):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT driver_id, name, phone_number, plate_number, vehicle_type FROM Driver")
    drivers = cursor.fetchall()

    if not drivers:
        messagebox.showerror("错误", "没有可用司机")
        return

    driver = random.choice(drivers)
    cost = random.randint(20, 100)

    try:
        cursor.execute(
            "INSERT INTO need (user_id, driver_id, order_time, cost) VALUES (%s, %s, %s, %s)",
            (user[0], driver[0], datetime.now(), cost)
        )
        order_id = cursor.lastrowid
        db.commit()
    except mysql.connector.Error as err:
        messagebox.showerror("错误", f"创建订单失败: {err}")
        return

    # 订单窗口
    order_win = Toplevel()
    order_win.title("订单详情")
    set_window_icon(order_win)

    info = [
        f"司机姓名: {driver[1]}",
        f"联系电话: {driver[2]}",
        f"车牌号码: {driver[3]}",
        f"车辆类型: {driver[4]}",
        f"订单金额: {cost}元"
    ]

    for text in info:
        Label(order_win, text=text).pack(padx=20, pady=5)

    def complete_order():
        if user[2] < cost:
            messagebox.showerror("错误", "余额不足")
            return

        try:
            cursor.execute(
                "UPDATE need SET complete_time = %s WHERE order_id = %s",
                (datetime.now(), order_id)
            )
            cursor.execute(
                "UPDATE User SET balance = balance - %s WHERE user_id = %s",
                (cost, user[0])
            )
            db.commit()
            messagebox.showinfo("成功", "订单已完成")
            order_win.destroy()
            refresh_callback()
            ask_rating(order_id)
        except mysql.connector.Error as err:
            messagebox.showerror("错误", f"更新失败: {err}")
        finally:
            cursor.close()
            db.close()

    Button(order_win, text="确认到达", command=complete_order).pack(pady=10)


def ask_rating(order_id):
    rate_win = Toplevel()
    rate_win.title("服务评分")
    set_window_icon(rate_win)

    Label(rate_win, text="请为本次服务评分（1-5分）:").pack()
    rating = IntVar()
    for i in range(1, 6):
        Radiobutton(rate_win, text=str(i), variable=rating, value=i).pack()

    def submit():
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE need SET rating = %s WHERE order_id = %s",
            (rating.get(), order_id)
        )
        db.commit()
        messagebox.showinfo("感谢", "评分已提交！")
        rate_win.destroy()
        cursor.close()
        db.close()

    Button(rate_win, text="提交", command=submit).pack()


def show_order_history(user):
    history_win = Toplevel()
    history_win.title("历史订单")
    set_window_icon(history_win)

    columns = ("订单ID", "司机ID", "下单时间", "完成时间", "金额", "评分")
    tree = ttk.Treeview(history_win, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill=BOTH, expand=True)

    def load_history():
        tree.delete(*tree.get_children())
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT order_id, driver_id, order_time, complete_time, cost, rating
            FROM need
            WHERE user_id = %s
            ORDER BY order_time DESC
        """, (user[0],))
        for order in cursor.fetchall():
            tree.insert("", "end", values=order)
        cursor.close()
        db.close()
        # 自动刷新
        history_win.after(5000, load_history)

    load_history()


def show_recharge(user, refresh_callback):
    recharge_win = Toplevel()
    recharge_win.title("余额充值")
    set_window_icon(recharge_win)

    Label(recharge_win, text="充值金额:").pack()
    amount_entry = Entry(recharge_win)
    amount_entry.pack()

    def confirm():
        try:
            amount = float(amount_entry.get())
            if amount <= 0:
                raise ValueError

            db = connect_db()
            cursor = db.cursor()
            cursor.execute(
                "UPDATE User SET balance = balance + %s WHERE user_id = %s",
                (amount, user[0])
            )
            db.commit()
            messagebox.showinfo("成功", f"已充值{amount}元")
            refresh_callback()
            recharge_win.destroy()
        except ValueError:
            messagebox.showerror("错误", "请输入有效金额")
        finally:
            cursor.close()
            db.close()

    Button(recharge_win, text="确认充值", command=confirm).pack()


# 司机登录
def driver_login():
    phone = driver_phone_entry.get()
    password = driver_password_entry.get()

    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT driver_id, name FROM Driver WHERE phone_number = %s AND driver_password = %s",
                   (phone, password))
    driver = cursor.fetchone()
    cursor.close()
    db.close()

    if driver:
        messagebox.showinfo("登录成功", f"欢迎 {driver[1]}！")
        login_window.destroy()
        driver_main_window(driver)
    else:
        messagebox.showerror("登录失败", "手机号或密码错误")


# 司机主界面
def driver_main_window(driver):
    driver_win = Toplevel()
    driver_win.title("次次打车-司机端")
    driver_win.geometry("1000x500")
    set_window_icon(driver_win)

    # 欢迎标签
    Label(driver_win, text=f"欢迎司机 {driver[1]}！", font=("Arial", 14)).pack(pady=10)

    # 当前订单状态
    status_label = Label(driver_win, text="当前订单状态：无进行中订单")
    status_label.pack(pady=10)

    # 订单历史
    columns = ("订单ID", "用户ID", "下单时间", "完成时间", "金额", "评分")
    tree = ttk.Treeview(driver_win, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill=BOTH, expand=True)

    def load_orders():
        tree.delete(*tree.get_children())
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT order_id, user_id, order_time, complete_time, cost, rating
            FROM need
            WHERE driver_id = %s
            ORDER BY order_time DESC
        """, (driver[0],))
        for order in cursor.fetchall():
            tree.insert("", "end", values=order)

        # 更新当前订单状态，显示订单号和用户ID
        cursor.execute("""
            SELECT order_id, user_id FROM need
            WHERE driver_id = %s AND complete_time IS NULL
            ORDER BY order_time DESC
            LIMIT 1
        """, (driver[0],))
        current = cursor.fetchone()
        if current:
            status_label.config(text=f"当前有进行中订单：订单ID {current[0]}，用户ID {current[1]}")
        else:
            status_label.config(text="当前订单状态：无进行中订单")

        cursor.close()
        db.close()
        # 自动刷新
        driver_win.after(5000, load_orders)

    load_orders()


# 注册界面
def show_register():
    global register_window
    register_window = Toplevel()
    register_window.title("次次打车-用户注册")
    register_window.geometry("400x600")
    set_window_icon(register_window)

    # 用户注册部分
    Label(register_window, text="用户注册", font=("Arial", 12, "bold")).pack(pady=5)
    Frame(register_window, height=2, bg="black").pack(fill=X)

    fields = ["姓名:", "手机号:", "密码:"]
    entries = []
    for field in fields:
        Label(register_window, text=field).pack()
        entry = Entry(register_window)
        entry.pack()
        entries.append(entry)

    Button(register_window, text="注册用户", command=lambda: user_register()).pack(pady=10)

    # 司机注册部分
    Label(register_window, text="司机注册", font=("Arial", 12, "bold")).pack(pady=5)
    Frame(register_window, height=2, bg="black").pack(fill=X)

    driver_fields = ["姓名:", "手机号:", "密码:", "车牌号:", "车型:"]
    driver_entries = []
    for field in driver_fields:
        Label(register_window, text=field).pack()
        entry = Entry(register_window)
        entry.pack()
        driver_entries.append(entry)

    Button(register_window, text="注册司机", command=lambda: driver_register()).pack(pady=10)

    # 设置全局变量
    global user_name_entry, user_phone_entry, user_password_entry
    global driver_name_entry, driver_phone_entry, driver_password_entry, driver_plate_entry, driver_vehicle_type_entry
    user_name_entry, user_phone_entry, user_password_entry = entries[:3]
    driver_name_entry, driver_phone_entry, driver_password_entry, driver_plate_entry, driver_vehicle_type_entry = driver_entries


# 登录界面
def show_login():
    global login_window
    login_window = Toplevel()
    login_window.title("次次打车-登录")
    login_window.geometry("400x400")
    set_window_icon(login_window)

    # 用户登录
    Label(login_window, text="用户登录", font=("Arial", 12, "bold")).pack(pady=5)
    Frame(login_window, height=2, bg="black").pack(fill=X)

    Label(login_window, text="手机号:").pack()
    global user_phone_entry
    user_phone_entry = Entry(login_window)
    user_phone_entry.pack()

    Label(login_window, text="密码:").pack()
    global user_password_entry
    user_password_entry = Entry(login_window, show="*")
    user_password_entry.pack()

    Button(login_window, text="用户登录", command=user_login).pack(pady=5)

    # 司机登录
    Label(login_window, text="司机登录", font=("Arial", 12, "bold")).pack(pady=5)
    Frame(login_window, height=2, bg="black").pack(fill=X)

    Label(login_window, text="手机号:").pack()
    global driver_phone_entry
    driver_phone_entry = Entry(login_window)
    driver_phone_entry.pack()

    Label(login_window, text="密码:").pack()
    global driver_password_entry
    driver_password_entry = Entry(login_window, show="*")
    driver_password_entry.pack()

    Button(login_window, text="司机登录", command=driver_login).pack(pady=5)


# 主界面
def main_window():
    root = Tk()
    root.title("次次打车出行平台")
    root.geometry("300x200")
    set_window_icon(root)
    Label(root, text="欢迎使用次次打车", font=("Arial", 14)).pack(pady=20)
    Button(root, text="登录", command=show_login, width=15).pack(pady=5)
    Button(root, text="注册", command=show_register, width=15).pack(pady=5)
    root.mainloop()


def set_window_icon(window):
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        window.iconbitmap(icon_path)
    except Exception:
        pass

if __name__ == "__main__":
    main_window()