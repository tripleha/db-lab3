# -*- coding: UTF-8 -*-
"""
mysql 数据库操作模块
"""

import re
import time
import traceback

import pymysql.cursors


class DBTools:
    """
    mysql数据库操作工具
    """

    def __init__(self):
        self.host = "127.0.0.1"
        self.user = "root"
        self.password = "meng835542226"
        self.db = "lab3"
        self.charset = "utf8mb4"
        self.cursorclass = pymysql.cursors.DictCursor
        conn = pymysql.connect(
            host=self.host,
            user="root",
            password="meng835542226",
            db="lab3",
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def setup_tables(self):
        """
        读取表定义文件中的sql语句建立相应的表
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return
        else:
            with open("setup_database", "r", encoding="utf-8") as tables_file:
                query = ""
                for line in tables_file:
                    if line.strip():
                        query += line
                    else:
                        try:
                            with conn.cursor() as cursor:
                                cursor.execute(query)
                            conn.commit()
                            query = ""
                        except:
                            print(traceback.format_exc())
                if query.strip():
                    try:
                        with conn.cursor() as cursor:
                            cursor.execute(query)
                        conn.commit()
                    except:
                        print(traceback.format_exc())
        finally:
            conn.close()

    def add_user(self, _user_id, _user_pwd, _user_name, _phone):
        """
        添加一个用户信息到数据库中
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            if len(_user_id) < 4 or len(_user_id) > 12:
                return 0
            if len(_user_pwd) < 6 or len(_user_pwd) > 12:
                return 0
            if len(_user_name) < 2 or len(_user_name) > 20:
                return 0
            if not re.match("^\d{11}$", _phone):
                return 0
            sql = "insert into user (user_id, user_pwd, user_name, phone) values (%s, %s, %s, %s)"
            with conn.cursor() as cursor:
                try:
                    result_t = cursor.execute(sql, [_user_id, _user_pwd, _user_name, _phone])
                    if result_t > 0:
                        conn.commit()
                except:
                    print(traceback.format_exc())
                    result_t = 0
        finally:
            conn.close()
        return result_t

    def add_session(self, _user_id, _user_pwd):
        """
        添加一个用户登录session到数据库中
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            sql_check = "select user_id from user where user_id=%s and user_pwd=%s"
            sql_insert = "insert into session (user_id, valid) values (%s, %s)"
            sql_get_session = "select LAST_INSERT_ID() as session_id"
            with conn.cursor() as cursor:
                try:
                    cursor.execute(sql_check, [_user_id, _user_pwd])
                    user_t = cursor.fetchall()
                    if len(user_t) > 0:
                        result_t = cursor.execute(sql_insert, [_user_id, int((time.time()+3600*24*7)*1000)])
                        if result_t > 0:
                            cursor.execute(sql_get_session)
                            get_session = cursor.fetchall()
                            if len(get_session) > 0:
                                result_t = get_session[0]["session_id"]
                                conn.commit()
                    else:
                        result_t = 0
                except:
                    result_t = 0
        finally:
            conn.close()
        return result_t

    def check_session(self, _user_id, _session_id):
        """
        检查用户登录session是否存在于数据库中并且未过期
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            sql_check = "select session_id from session where session_id=%s and user_id=%s and valid>=%s"
            with conn.cursor() as cursor:
                try:
                    cursor.execute(sql_check, [_session_id, _user_id, int(time.time()*1000)])
                    session_t = cursor.fetchall()
                    result_t = len(session_t)
                except:
                    print(traceback.format_exc())
                    result_t = 0
        finally:
            conn.close()
        return result_t

    def get_user_info(self, _user_id, _session_id):
        """
        从数据库中获取用户信息
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return None
        else:
            session_count = self.check_session(_user_id, _session_id)
            if session_count > 0:
                sql_get_info = "select user_id, user_pwd, user_name, phone from user where user_id=%s"
                with conn.cursor() as cursor:
                    try:
                        cursor.execute(sql_get_info, [_user_id,])
                        user_t = cursor.fetchall()
                        if len(user_t) > 0:
                            result_t = user_t[0]
                        else:
                            result_t = None
                    except:
                        print(traceback.format_exc())
                        result_t = None
            else:
                result_t = None
        finally:
            conn.close()
        return result_t

    def change_user_info(self, _user_id, _session_id, _user_pwd, _user_name, _phone):
        """
        更改用户信息
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            if len(_user_pwd) < 6 or len(_user_pwd) > 12:
                return 0
            if len(_user_name) < 2 or len(_user_name) > 20:
                return 0
            if not re.match("^\d{11}$", _phone):
                return 0
            session_count = self.check_session(_user_id, _session_id)
            if session_count > 0:
                sql_update = "update user set user_pwd=%s, user_name=%s, phone=%s where user_id=%s"
                with conn.cursor() as cursor:
                    try:
                        result_t = cursor.execute(sql_update, [_user_pwd, _user_name, _phone, _user_id])
                        if result_t > 0:
                            conn.commit()
                    except:
                        print(traceback.format_exc())
                        result_t = 0
            else:
                result_t = 0
        finally:
            conn.close()
        return result_t

    def add_goods(self, _goods_name, _goods_price):
        """
        添加一项商品到数据库中
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            sql_insert = "insert into goods (goods_name, goods_price) values (%s, %s)"
            sql_get_id = "select LAST_INSERT_ID() as goods_id"
            with conn.cursor() as cursor:
                try:
                    result_t = cursor.execute(sql_insert, [_goods_name, _goods_price])
                    if result_t > 0:
                        cursor.execute(sql_get_id)
                        get_ids = cursor.fetchall()
                        if len(get_ids) > 0:
                            result_t = get_ids[0]["goods_id"]
                            conn.commit()
                except:
                    result_t = 0
        finally:
            conn.close()
        return result_t

    def delete_goods(self, _goods_id):
        """
        从数据库中删除一项商品
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            sql_delete = "delete from goods where goods_id=%s"
            with conn.cursor() as cursor:
                try:
                    result_t = cursor.execute(sql_delete, [_goods_id,])
                    if result_t > 0:
                        conn.commit()
                except:
                    result_t = 0
        finally:
            conn.close()
        return result_t


    def add_place(self, _place_loc, _place_price):
        """
        添加一个聚会地点到数据库中
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            sql_insert = "insert into place (place_loc, place_price) values (%s, %s)"
            sql_get_id = "select LAST_INSERT_ID() as place_id"
            with conn.cursor() as cursor:
                try:
                    result_t = cursor.execute(sql_insert, [_place_loc, _place_price])
                    if result_t > 0:
                        cursor.execute(sql_get_id)
                        get_ids = cursor.fetchall()
                        if len(get_ids) > 0:
                            result_t = get_ids[0]["place_id"]
                            conn.commit()
                except:
                    result_t = 0
        finally:
            conn.close()
        return result_t

    def delete_place(self, _place_id):
        """
        从数据库中删除一个地点
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            sql_delete = "delete from place where place_id=%s"
            with conn.cursor() as cursor:
                try:
                    result_t = cursor.execute(sql_delete, [_place_id,])
                    if result_t > 0:
                        conn.commit()
                except:
                    result_t = 0
        finally:
            conn.close()
        return result_t

    def add_standard(self, _waiter_count, _table_count, _chair_count, _standard_price):
        """
        添加一个聚会规格到数据库中
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            sql_insert = "insert into standard (waiter_count, table_count, chair_count, standard_price) values (%s, %s, %s, %s)"
            sql_get_id = "select LAST_INSERT_ID() as standard_id"
            with conn.cursor() as cursor:
                try:
                    result_t = cursor.execute(sql_insert, [_waiter_count, _table_count, _chair_count, _standard_price])
                    if result_t > 0:
                        cursor.execute(sql_get_id)
                        get_ids = cursor.fetchall()
                        if len(get_ids) > 0:
                            result_t = get_ids[0]["standard_id"]
                            conn.commit()
                except:
                    result_t = 0
        finally:
            conn.close()
        return result_t

    def delete_standard(self, _standard_id):
        """
        从数据库中删除一个聚会规格
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            sql_delete = "delete from standard where standard_id=%s"
            with conn.cursor() as cursor:
                try:
                    result_t = cursor.execute(sql_delete, [_standard_id,])
                    if result_t > 0:
                        conn.commit()
                except:
                    result_t = 0
        finally:
            conn.close()
        return result_t

    def get_goods_list(self):
        """
        从数据库获取商品列表
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return None
        else:
            sql_get = "select goods_id, goods_name, goods_price from goods"
            with conn.cursor() as cursor:
                try:
                    cursor.execute(sql_get)
                    result_t = cursor.fetchall()
                except:
                    result_t = None
        finally:
            conn.close()
        return result_t

    def get_place_list(self):
        """
        从数据库获取地点列表
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return None
        else:
            sql_get = "select place_id, place_loc, place_price from place"
            with conn.cursor() as cursor:
                try:
                    cursor.execute(sql_get)
                    result_t = cursor.fetchall()
                except:
                    result_t = None
        finally:
            conn.close()
        return result_t

    def get_standard_list(self):
        """
        从数据库获取规格列表
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return None
        else:
            sql_get = "select standard_id, waiter_count, table_count, chair_count, standard_price from standard"
            with conn.cursor() as cursor:
                try:
                    cursor.execute(sql_get)
                    result_t = cursor.fetchall()
                except:
                    result_t = None
        finally:
            conn.close()
        return result_t

    def add_guest(self, _user_id, _session_id, _guest_nike, _guest_phone, _order_id):
        """
        添加一个客人到数据库中
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            session_count = self.check_session(_user_id, _session_id)
            if session_count > 0:
                is_active = self.check_party_active(_order_id)
                if is_active == 1:
                    sql_insert = "insert into guest (guest_nike, guest_phone, order_id) values (%s, %s, %s)"
                    sql_get_id = "select LAST_INSERT_ID() as guest_id"
                    with conn.cursor() as cursor:
                        try:
                            result_t = cursor.execute(sql_insert, [_guest_nike, _guest_phone, _order_id])
                            if result_t > 0:
                                cursor.execute(sql_get_id)
                                get_ids = cursor.fetchall()
                                if len(get_ids) > 0:
                                    result_t = get_ids[0]["guest_id"]
                                    conn.commit()
                        except:
                            result_t = 0
                else:
                    result_t = 0
        finally:
            conn.close()
        return result_t

    def add_shopping_list(self, _user_id, _session_id, _goods_id, _goods_count, _order_id):
        """
        添加一个购物项到数据库中
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            session_count = self.check_session(_user_id, _session_id)
            if session_count > 0:
                is_active = self.check_party_active(_order_id)
                if is_active == 1:
                    sql_insert = "insert into shopping_list (goods_id, goods_count, order_id) values (%s, %s, %s)"
                    sql_get_id = "select LAST_INSERT_ID() as shopping_id"
                    with conn.cursor() as cursor:
                        try:
                            result_t = cursor.execute(sql_insert, [_goods_id, _goods_count, _order_id])
                            if result_t > 0:
                                cursor.execute(sql_get_id)
                                get_ids = cursor.fetchall()
                                if len(get_ids) > 0:
                                    result_t = get_ids[0]["shopping_id"]
                                    conn.commit()
                        except:
                            result_t = 0
                else:
                    result_t = 0
        finally:
            conn.close()
        return result_t

    def get_guests(self, _user_id, _session_id, _order_id):
        """
        从数据库获取客人列表
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return None
        else:
            session_count = self.check_session(_user_id, _session_id)
            if session_count > 0:
                sql_get = "select guest_id, guest_nike, guest_phone, order_id from guest where order_id=%s"
                with conn.cursor() as cursor:
                    try:
                        cursor.execute(sql_get, [_order_id,])
                        result_t = cursor.fetchall()
                    except:
                        result_t = None
        finally:
            conn.close()
        return result_t

    def get_shopping_list(self, _user_id, _session_id, _order_id):
        """
        从数据库获取购物项列表
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return None
        else:
            session_count = self.check_session(_user_id, _session_id)
            if session_count > 0:
                # sql_get = "select shopping_id, shopping_list.goods_id as goods_id, goods_name, goods_price, goods_count \
                #     from shopping_list, goods \
                #     where shopping_list.goods_id=goods.goods_id and order_id=%s \
                #     group by shopping_id, shopping_list.goods_id, goods_name, goods_price, goods_count"
                sql_get = "select distinct * from shopping_list_view where order_id=%s order by shopping_id"
                with conn.cursor() as cursor:
                    try:
                        cursor.execute(sql_get, [_order_id,])
                        result_t = cursor.fetchall()
                    except:
                        result_t = None
        finally:
            conn.close()
        return result_t

    def add_party_order(self, _user_id, _session_id, _begin, _end, _shopping_end, _place_id, _standard_id):
        """
        添加一个聚会项目到数据库
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            session_count = self.check_session(_user_id, _session_id)
            if session_count > 0:
                sql_insert = "insert into party_order \
                    (user_id, active, begin, end, shopping_end, place_id, standard_id) \
                    values (%s, %s, %s, %s, %s, %s, %s)"
                sql_get_id = "select LAST_INSERT_ID() as order_id"
                with conn.cursor() as cursor:
                    try:
                        result_t = cursor.execute(sql_insert, [_user_id, "1", _begin, _end, _shopping_end, _place_id, _standard_id])
                        if result_t > 0:
                            cursor.execute(sql_get_id)
                            get_ids = cursor.fetchall()
                            if len(get_ids) > 0:
                                result_t = get_ids[0]["order_id"]
                                conn.commit()
                    except:
                        result_t = 0
        finally:
            conn.close()
        return result_t

    def get_user_party_orders(self, _user_id, _session_id):
        """
        从数据库获取用户的聚会项目列表
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return None
        else:
            session_count = self.check_session(_user_id, _session_id)
            if session_count > 0:
                sql_get = "select * from party_order where user_id=%s"
                with conn.cursor() as cursor:
                    try:
                        cursor.execute(sql_get, [_user_id,])
                        result_t = cursor.fetchall()
                    except:
                        result_t = None
        finally:
            conn.close()
        return result_t

    def get_one_party_order(self, _user_id, _session_id, _order_id):
        """
        从数据库获取指定聚会项目的全部信息
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return None
        else:
            session_count = self.check_session(_user_id, _session_id)
            if session_count > 0:
                sql_get = "select distinct order_id, active, begin, end, \
                    review, shopping_end, party_order.place_id as place_id, place_loc, place_price, \
                    standard.standard_id as standard_id, waiter_count, table_count, chair_count, standard_price \
                    from party_order, place, standard \
                    where party_order.place_id=place.place_id \
                    and party_order.standard_id=standard.standard_id and order_id=%s and user_id=%s"
                sql_guest_count = "select count(*) as guest_count from guest where order_id=%s"
                sql_shopping_count = "select count(*) as shopping_count from shopping_list where order_id=%s"
                with conn.cursor() as cursor:
                    try:
                        cursor.execute(sql_get, [_order_id, _user_id])
                        result_t = cursor.fetchall()[0]
                        cursor.execute(sql_guest_count, [_order_id,])
                        count_t = cursor.fetchall()[0]
                        result_t["guest_count"] = count_t["guest_count"]
                        cursor.execute(sql_shopping_count, [_order_id,])
                        count_t = cursor.fetchall()[0]
                        result_t["shopping_count"] = count_t["shopping_count"]
                    except:
                        result_t = None
        finally:
            conn.close()
        return result_t

    def check_party_active(self, _order_id):
        """
        检查聚会订单是否已经完成
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            sql_get = "select active from party_order where order_id=%s"
            with conn.cursor() as cursor:
                try:
                    cursor.execute(sql_get, [_order_id,])
                    result_t = int(cursor.fetchall()[0]["active"])
                except:
                    result_t = 0
        finally:
            conn.close()
        return result_t

    def delete_party(self, _user_id, _session_id, _order_id):
        """
        从数据库中删除聚会订单
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            session_count = self.check_session(_user_id, _session_id)
            if session_count > 0:
                sql_delete = "delete from party_order where order_id=%s and user_id=%s"
                with conn.cursor() as cursor:
                    try:
                        result_t = cursor.execute(sql_delete, [_order_id, _user_id])
                        if result_t > 0:
                            conn.commit()
                    except:
                        result_t = 0
        finally:
            conn.close()
        return result_t

    def delete_guest(self, _user_id, _session_id, _order_id, _guest_id):
        """
        从数据库中删除一个客人
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            session_count = self.check_session(_user_id, _session_id)
            if session_count > 0:
                is_active = self.check_party_active(_order_id)
                if is_active == 1:
                    sql_delete = "delete from guest where order_id=%s and guest_id=%s"
                    with conn.cursor() as cursor:
                        try:
                            result_t = cursor.execute(sql_delete, [_order_id, _guest_id])
                            if result_t > 0:
                                conn.commit()
                        except:
                            result_t = 0
                else:
                    result_t = 0
        finally:
            conn.close()
        return result_t

    def delete_shopping(self, _user_id, _session_id, _order_id, _shopping_id):
        """
        从数据库中删除一条购物清单
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            session_count = self.check_session(_user_id, _session_id)
            if session_count > 0:
                is_active = self.check_party_active(_order_id)
                if is_active == 1:
                    sql_delete = "delete from shopping_list where order_id=%s and shopping_id=%s"
                    with conn.cursor() as cursor:
                        try:
                            result_t = cursor.execute(sql_delete, [_order_id, _shopping_id])
                            if result_t > 0:
                                conn.commit()
                        except:
                            result_t = 0
                else:
                    result_t = 0
        finally:
            conn.close()
        return result_t

    def add_party_review(self, _user_id, _session_id, _order_id, _review):
        """
        完成一个聚会并为其填写评价
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=self.cursorclass
            )
        except:
            print("connect fail")
            return 0
        else:
            session_count = self.check_session(_user_id, _session_id)
            if session_count > 0:
                is_active = self.check_party_active(_order_id)
                if is_active == 1:
                    sql_update = "update party_order set active='0', review=%s where order_id=%s and user_id=%s"
                    with conn.cursor() as cursor:
                        try:
                            result_t = cursor.execute(sql_update, [_review, _order_id, _user_id])
                            if result_t > 0:
                                conn.commit()
                        except:
                            print(traceback.format_exc())
                            result_t = 0
                else:
                    result_t = 0
        finally:
            conn.close()
        return result_t


if __name__ == "__main__":
    pass
