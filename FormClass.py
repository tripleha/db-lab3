# -*- coding: UTF-8 -*-


from wtforms import Form
from wtforms import TextField
from wtforms.validators import Length, Required


class SignupForm(Form):
    user_id = TextField("user_id", [Length(min=4, max=12), Required()])
    user_pwd = TextField("user_pwd", [Length(min=6, max=12), Required()])
    user_name = TextField("user_name", [Length(min=2, max=20), Required()])
    phone = TextField("phone", [Length(min=11, max=11), Required()])


class LoginForm(Form):
    user_id = TextField("user_id", [Length(min=4, max=12), Required()])
    user_pwd = TextField("user_pwd", [Length(min=6, max=12), Required()])


class GoodsForm(Form):
    goods_name = TextField("goods_name", [Length(min=1, max=100), Required()])
    goods_price = TextField("goods_price", [Length(min=1, max=10), Required()])


class PlaceForm(Form):
    place_loc = TextField("place_loc", [Length(min=1, max=100), Required()])
    place_price = TextField("place_price", [Length(min=1, max=10), Required()])


class StandardForm(Form):
    waiter_count = TextField("waiter_count", [Length(min=1, max=10), Required()])
    table_count = TextField("table_count", [Length(min=1, max=10), Required()])
    chair_count = TextField("chair_count", [Length(min=1, max=10), Required()])
    standard_price = TextField("standard_price", [Length(min=1, max=10), Required()])


class PartyForm(Form):
    begin = TextField("begin", [Length(min=19, max=19), Required()])
    end = TextField("end", [Length(min=19, max=19), Required()])
    shopping_end = TextField("shopping_end", [Length(min=19, max=19), Required()])
    place_id = TextField("place_id", [Length(min=1, max=10), Required()])
    standard_id = TextField("standard_id", [Length(min=1, max=10), Required()])


class GuestForm(Form):
    guest_nike = TextField("guest_nike", [Length(min=2, max=20), Required()])
    guest_phone = TextField("guest_phone", [Length(min=11, max=11), Required()])


class ShoppingForm(Form):
    goods_id = TextField("goods_id", [Length(min=1, max=10), Required()])
    goods_count = TextField("goods_count", [Length(min=1, max=10), Required()])


class ReviewForm(Form):
    review = TextField("review", [Length(min=1, max=100), Required()])


if __name__ == "__main__":
    pass
