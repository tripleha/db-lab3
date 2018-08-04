# -*- coding: UTF-8 -*-


import time
from datetime import datetime
import base64
import traceback

from flask import Flask
from flask import request, redirect, url_for
from flask import render_template

from flask_wtf.csrf import CSRFProtect

from FormClass import (
    SignupForm, 
    LoginForm, 
    GoodsForm, 
    PlaceForm, 
    StandardForm, 
    PartyForm, 
    GuestForm, 
    ShoppingForm,
    ReviewForm
)
from DBTools import DBTools


worker = DBTools()
worker.setup_tables()


admin_id = "mengxiaoji"
admin_pwd = "meng835542226"
check_token = base64.b64encode(bytes(admin_id + admin_pwd, encoding="ascii")).decode("ascii")


my_app = Flask(__name__)

my_app.config.update(
    SECRET_KEY="meng13645958845@"
)

csrf = CSRFProtect(my_app)


@my_app.route("/", methods=["GET"])
def home():
    try:
        user_id_t = str(request.cookies["user_id"])
        session_id_t = int(request.cookies["session_id"])
        user_info = worker.get_user_info(user_id_t, session_id_t)
        if user_info is not None:
            return render_template("home.html", user_name=user_info["user_name"])
    except:
        print(traceback.format_exc())
    return redirect(url_for("login_page"))


@my_app.route("/error/<error_message>")
def error_page(error_message):
    return render_template("error.html", error_message=error_message)


@my_app.route("/admin")
def admin_home():
    try:
        admin_token = request.cookies["a_token"]
        if admin_token == check_token:
            return render_template("admin.html")
    except:
        print(traceback.format_exc())
    return redirect(url_for("home"))


@my_app.route("/admin/error/<error_message>")
def admin_error_page(error_message):
    try:
        admin_token = request.cookies["a_token"]
        if admin_token == check_token:
            return render_template("admin_error.html", error_message=error_message)
    except:
        print(traceback.format_exc())
    return redirect(url_for("home"))


@my_app.route("/login", methods=["GET"])
def login_page():
    login_form = LoginForm(request.form)
    return render_template("login.html", form=login_form)


@my_app.route("/signup", methods=["GET"])
def signup_page():
    signup_form = SignupForm(request.form)
    return render_template("signup.html", form=signup_form)


@my_app.route("/do_signup", methods=["POST"])
def do_signup():
    try:
        signup_form = SignupForm(request.form)
        if signup_form.validate():
            user_id_t = signup_form.user_id.data
            user_pwd_t = signup_form.user_pwd.data
            user_name_t = signup_form.user_name.data
            phone_t = signup_form.phone.data
            if user_id_t == admin_id and user_pwd_t == admin_pwd:
                return redirect(url_for("error_page", error_message="注册失败"))
            insert_user_t = worker.add_user(
                user_id_t,
                user_pwd_t,
                user_name_t,
                phone_t
            )
            if insert_user_t > 0:
                return redirect(url_for("login_page"))
    except:
        print(traceback.format_exc())
    return redirect(url_for("error_page", error_message="注册失败"))


@my_app.route("/do_login", methods=["POST"])
def do_login():
    try:
        login_form = LoginForm(request.form)
        user_id_t = login_form.user_id.data
        user_pwd_t = login_form.user_pwd.data
        if user_id_t == admin_id and user_pwd_t == admin_pwd:
            redirect_to_admin = redirect(url_for("admin_home"))
            resp = my_app.make_response(redirect_to_admin)
            resp.set_cookie("a_token", value=check_token)
            return resp
        if login_form.validate():
            insert_session_t = worker.add_session(user_id_t, user_pwd_t)
            if insert_session_t > 0:
                redirect_to_home = redirect(url_for("home"))
                resp = my_app.make_response(redirect_to_home)
                resp.set_cookie("user_id", value=user_id_t)
                resp.set_cookie("session_id", value=str(insert_session_t))
                return resp
    except:
        print(traceback.format_exc())
    return redirect(url_for("error_page", error_message="登录失败"))


@my_app.route("/user_info", methods=["GET"])
def user_info():
    try:
        signup_form = SignupForm(request.form)
        user_id_t = str(request.cookies["user_id"])
        session_id_t = int(request.cookies["session_id"])
        user_info = worker.get_user_info(user_id_t, session_id_t)
        if user_info is not None:
            return render_template("userinfo.html", user_info=user_info, form=signup_form)
    except:
        print(traceback.format_exc())
    return redirect(url_for("login_page"))


@my_app.route("/do_user_info", methods=["POST"])
def change_user_info():
    try:
        signup_form = SignupForm(request.form)
        if signup_form.validate():
            user_id_t = str(request.cookies["user_id"])
            session_id_t = int(request.cookies["session_id"])
            user_pwd_t = signup_form.user_pwd.data
            user_name_t = signup_form.user_name.data
            phone_t = signup_form.phone.data
            if worker.change_user_info(user_id_t, session_id_t, user_pwd_t, user_name_t, phone_t) > 0:
                return redirect(url_for("user_info"))
    except:
        print(traceback.format_exc())
    return redirect(url_for("error_page", error_message="更新失败"))


@my_app.route("/admin/add_goods", methods=["GET"])
def add_goods():
    try:
        admin_token = request.cookies["a_token"]
        if admin_token == check_token:
            goods_form = GoodsForm(request.form)
            get_list = worker.get_goods_list()
            return render_template("add_goods.html", form=goods_form, goods_list=get_list)
    except:
        print(traceback.format_exc())
    return redirect(url_for("home"))


@my_app.route("/admin/do_add_goods", methods=["POST"])
def do_add_goods():
    try:
        admin_token = request.cookies["a_token"]
        if admin_token == check_token:
            goods_form = GoodsForm(request.form)
            goods_name = goods_form.goods_name.data
            goods_price = goods_form.goods_price.data
            if worker.add_goods(goods_name, goods_price) > 0:
                return redirect(url_for("add_goods"))
    except:
        print(traceback.format_exc())
    return redirect(url_for("admin_error_page", error_message="添加失败"))


@my_app.route("/admin/delete_goods/<int:goods_id>")
def delete_goods(goods_id):
    try:
        admin_token = request.cookies["a_token"]
        if admin_token == check_token:
            worker.delete_goods(goods_id)
    except:
        print(traceback.format_exc())
    return redirect(url_for("add_goods"))


@my_app.route("/admin/add_place", methods=["GET"])
def add_place():
    try:
        admin_token = request.cookies["a_token"]
        if admin_token == check_token:
            place_form = PlaceForm(request.form)
            get_list = worker.get_place_list()
            return render_template("add_place.html", form=place_form, place_list=get_list)
    except:
        print(traceback.format_exc())
    return redirect(url_for("home"))


@my_app.route("/admin/do_add_place", methods=["POST"])
def do_add_place():
    try:
        admin_token = request.cookies["a_token"]
        if admin_token == check_token:
            place_form = PlaceForm(request.form)
            place_loc = place_form.place_loc.data
            place_price = place_form.place_price.data
            if worker.add_place(place_loc, place_price) > 0:
                return redirect(url_for("add_place"))
    except:
        print(traceback.format_exc())
    return redirect(url_for("admin_error_page", error_message="添加失败"))


@my_app.route("/admin/delete_place/<int:place_id>")
def delete_place(place_id):
    try:
        admin_token = request.cookies["a_token"]
        if admin_token == check_token:
            worker.delete_place(place_id)
    except:
        print(traceback.format_exc())
    return redirect(url_for("add_place"))


@my_app.route("/admin/add_standard", methods=["GET"])
def add_standard():
    try:
        admin_token = request.cookies["a_token"]
        if admin_token == check_token:
            standard_form = StandardForm(request.form)
            get_list = worker.get_standard_list()
            return render_template("add_standard.html", form=standard_form, standard_list=get_list)
    except:
        print(traceback.format_exc())
    return redirect(url_for("home"))


@my_app.route("/admin/do_add_standard", methods=["POST"])
def do_add_standard():
    try:
        admin_token = request.cookies["a_token"]
        if admin_token == check_token:
            standard_form = StandardForm(request.form)
            waiter_count = standard_form.waiter_count.data
            table_count = standard_form.table_count.data
            chair_count = standard_form.chair_count.data
            standard_price = standard_form.standard_price.data
            if worker.add_standard(waiter_count, table_count, chair_count, standard_price) > 0:
                return redirect(url_for("add_standard"))
    except:
        print(traceback.format_exc())
    return redirect(url_for("admin_error_page", error_message="添加失败"))


@my_app.route("/admin/delete_standard/<int:standard_id>")
def delete_standard(standard_id):
    try:
        admin_token = request.cookies["a_token"]
        if admin_token == check_token:
            worker.delete_standard(standard_id)
    except:
        print(traceback.format_exc())
    return redirect(url_for("add_standard"))


@my_app.route("/goods_list", methods=["GET"])
def goods_list():
    try:
        user_id_t = str(request.cookies["user_id"])
        session_id_t = int(request.cookies["session_id"])
        user_info = worker.get_user_info(user_id_t, session_id_t)
        if user_info is not None:
            get_list = worker.get_goods_list()
            if get_list is not None:
                return render_template("show_goods.html", user_name=user_info["user_name"], goods_list=get_list)
            else:
                return redirect(url_for("home"))
    except:
        print(traceback.format_exc())
    return redirect(url_for("login_page"))


@my_app.route("/place_list", methods=["GET"])
def place_list():
    try:
        user_id_t = str(request.cookies["user_id"])
        session_id_t = int(request.cookies["session_id"])
        user_info = worker.get_user_info(user_id_t, session_id_t)
        if user_info is not None:
            get_list = worker.get_place_list()
            if get_list is not None:
                return render_template("show_place.html", user_name=user_info["user_name"], place_list=get_list)
            else:
                return redirect(url_for("home"))
    except:
        print(traceback.format_exc())
    return redirect(url_for("login_page"))


@my_app.route("/standard_list", methods=["GET"])
def standard_list():
    try:
        user_id_t = str(request.cookies["user_id"])
        session_id_t = int(request.cookies["session_id"])
        user_info = worker.get_user_info(user_id_t, session_id_t)
        if user_info is not None:
            get_list = worker.get_standard_list()
            if get_list is not None:
                return render_template("show_standard.html", user_name=user_info["user_name"], standard_list=get_list)
            else:
                return redirect(url_for("home"))
    except:
        print(traceback.format_exc())
    return redirect(url_for("login_page"))


@my_app.route("/add_party", methods=["GET"])
def add_party():
    try:
        party_form = PartyForm(request.form)
        user_id_t = str(request.cookies["user_id"])
        session_id_t = int(request.cookies["session_id"])
        user_info = worker.get_user_info(user_id_t, session_id_t)
        place_list = worker.get_place_list()
        standard_list = worker.get_standard_list()
        if user_info is not None:
            return render_template(
                "add_party.html",
                user_name=user_info["user_name"],
                form=party_form, 
                place_list=place_list, 
                standard_list=standard_list
            )
    except:
        print(traceback.format_exc())
    return redirect(url_for("home"))


@my_app.route("/do_add_party", methods=["POST"])
def do_add_party():
    try:
        party_form = PartyForm(request.form)
        if party_form.validate():
            user_id_t = str(request.cookies["user_id"])
            session_id_t = int(request.cookies["session_id"])
            begin = time.mktime(datetime.strptime(party_form.begin.data, "%Y-%m-%d %H:%M:%S").timetuple())
            end = time.mktime(datetime.strptime(party_form.end.data, "%Y-%m-%d %H:%M:%S").timetuple())
            shopping_end = time.mktime(datetime.strptime(party_form.shopping_end.data, "%Y-%m-%d %H:%M:%S").timetuple())
            place_id = int(party_form.place_id.data)
            standard_id = int(party_form.standard_id.data)
            order_t = worker.add_party_order(user_id_t, session_id_t, begin, end, shopping_end, place_id, standard_id)
            if order_t > 0:
                return redirect(url_for("get_one_party", order_id=order_t))
    except:
        print(traceback.format_exc())
    return redirect(url_for("error_page", error_message="添加失败"))


@my_app.route("/party_list", methods=["GET"])
def get_party_list():
    try:
        user_id_t = str(request.cookies["user_id"])
        session_id_t = int(request.cookies["session_id"])
        user_info = worker.get_user_info(user_id_t, session_id_t)
        if user_info is not None:
            get_list = worker.get_user_party_orders(user_id_t, session_id_t)
            if get_list is not None:
                for each in get_list:
                    each["begin"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(each["begin"]))
                    each["end"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(each["end"]))
                    each["shopping_end"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(each["shopping_end"]))
                return render_template("show_party_list.html", user_name=user_info["user_name"], party_list=get_list)
    except:
        print(traceback.format_exc())
    return redirect(url_for("home"))


@my_app.route("/get_one_party/<int:order_id>", methods=["GET"])
def get_one_party(order_id):
    try:
        user_id_t = str(request.cookies["user_id"])
        session_id_t = int(request.cookies["session_id"])
        user_info = worker.get_user_info(user_id_t, session_id_t)
        if user_info is not None:
            get_party_t = worker.get_one_party_order(user_id_t, session_id_t, order_id)
            if get_party_t is not None:
                get_party_t["begin"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(get_party_t["begin"]))
                get_party_t["end"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(get_party_t["end"]))
                get_party_t["shopping_end"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(get_party_t["shopping_end"]))
                return render_template("one_party.html", user_name=user_info["user_name"], party_order=get_party_t)
    except:
        print(traceback.format_exc())
    return redirect(url_for("get_party_list"))


@my_app.route("/get_guests/<int:order_id>", methods=["GET"])
def get_guests(order_id):
    try:
        guest_form = GuestForm(request.form)
        user_id_t = str(request.cookies["user_id"])
        session_id_t = int(request.cookies["session_id"])
        user_info = worker.get_user_info(user_id_t, session_id_t)
        if user_info is not None:
            guest_list = worker.get_guests(user_id_t, session_id_t, order_id)
            get_active = worker.check_party_active(order_id)
            if guest_list is not None:
                return render_template(
                    "add_guest.html", 
                    user_name=user_info["user_name"], 
                    order_id=order_id, 
                    active=get_active,
                    form=guest_form, 
                    guest_list=guest_list
                )
    except:
        print(traceback.format_exc())
    return redirect(url_for("get_one_party", order_id=order_id))


@my_app.route("/get_shopping_list/<int:order_id>", methods=["GET"])
def get_shopping_list(order_id):
    try:
        shopping_form = ShoppingForm(request.form)
        user_id_t = str(request.cookies["user_id"])
        session_id_t = int(request.cookies["session_id"])
        user_info = worker.get_user_info(user_id_t, session_id_t)
        if user_info is not None:
            shopping_list = worker.get_shopping_list(user_id_t, session_id_t, order_id)
            get_active = worker.check_party_active(order_id)
            goods_list = worker.get_goods_list()
            if shopping_list is not None:
                return render_template(
                    "add_shopping_list.html", 
                    user_name=user_info["user_name"], 
                    order_id=order_id, 
                    active=get_active,
                    form=shopping_form, 
                    shopping_list=shopping_list,
                    goods_list=goods_list
                )
    except:
        print(traceback.format_exc())
    return redirect(url_for("get_one_party", order_id=order_id))


@my_app.route("/do_add_guest/<int:order_id>", methods=["POST"])
def do_add_guest(order_id):
    try:
        guest_form = GuestForm(request.form)
        if guest_form.validate():
            user_id_t = str(request.cookies["user_id"])
            session_id_t = int(request.cookies["session_id"])
            guest_nike = guest_form.guest_nike.data
            guest_phone = guest_form.guest_phone.data
            guest_t = worker.add_guest(user_id_t, session_id_t, guest_nike, guest_phone, order_id)
            if guest_t > 0:
                return redirect(url_for("get_guests", order_id=order_id))
    except:
        print(traceback.format_exc())
    return redirect(url_for("error_page", error_message="添加失败"))


@my_app.route("/do_add_shopping/<int:order_id>", methods=["POST"])
def do_add_shopping(order_id):
    try:
        shopping_form = ShoppingForm(request.form)
        if shopping_form.validate():
            user_id_t = str(request.cookies["user_id"])
            session_id_t = int(request.cookies["session_id"])
            goods_id = int(shopping_form.goods_id.data)
            goods_count = int(shopping_form.goods_count.data)
            shopping_t = worker.add_shopping_list(user_id_t, session_id_t, goods_id, goods_count, order_id)
            print(shopping_t)
            if shopping_t > 0:
                return redirect(url_for("get_shopping_list", order_id=order_id))
    except:
        print(traceback.format_exc())
    return redirect(url_for("error_page", error_message="添加失败"))


@my_app.route("/delete_party/<int:order_id>", methods=["GET"])
def delete_party(order_id):
    try:
        user_id_t = str(request.cookies["user_id"])
        session_id_t = int(request.cookies["session_id"])
        party_t = worker.delete_party(user_id_t, session_id_t, order_id)
    except:
        print(traceback.format_exc())
    return redirect(url_for("get_party_list"))


@my_app.route("/delete_guest/<int:order_id>/<int:guest_id>", methods=["GET"])
def delete_guest(order_id, guest_id):
    try:
        user_id_t = str(request.cookies["user_id"])
        session_id_t = int(request.cookies["session_id"])
        worker.delete_guest(user_id_t, session_id_t, order_id, guest_id)
    except:
        print(traceback.format_exc())
    return redirect(url_for("get_guests", order_id=order_id))


@my_app.route("/delete_shopping/<int:order_id>/<int:shopping_id>", methods=["GET"])
def delete_shopping(order_id, shopping_id):
    try:
        user_id_t = str(request.cookies["user_id"])
        session_id_t = int(request.cookies["session_id"])
        worker.delete_shopping(user_id_t, session_id_t, order_id, shopping_id)
    except:
        print(traceback.format_exc())
    return redirect(url_for("get_shopping_list", order_id=order_id))


@my_app.route("/party_done/<int:order_id>", methods=["GET"])
def party_done(order_id):
    try:
        review_form = ReviewForm(request.form)
        user_id_t = str(request.cookies["user_id"])
        session_id_t = int(request.cookies["session_id"])
        user_info = worker.get_user_info(user_id_t, session_id_t)
        if user_info is not None:
            return render_template("done_party.html", user_name=user_info["user_name"], order_id=order_id)
    except:
        print(traceback.format_exc())
    return redirect(url_for("get_one_party", order_id=order_id))


@my_app.route("/do_party_done/<int:order_id>", methods=["POST"])
def do_party_done(order_id):
    try:
        review_form = ReviewForm(request.form)
        if review_form.validate():
            user_id_t = str(request.cookies["user_id"])
            session_id_t = int(request.cookies["session_id"])
            review = review_form.review.data
            if worker.add_party_review(user_id_t, session_id_t, order_id, review) > 0:
                return redirect(url_for("get_one_party", order_id=order_id))
    except:
        print(traceback.format_exc())
    return redirect(url_for("error_page", error_message="提交失败"))



if __name__ == "__main__":
    my_app.run(debug=True)
