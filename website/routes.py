from flask import render_template, url_for, flash, redirect, request, jsonify
from website import predictor
from website.models import Price, User
from website.forms import RegistrationForm, LoginForm
from website import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
import pickle
from website.predictor import generate_features, clip_prediction
from collections import defaultdict
import numpy as np
import pandas as pd

from joblib import load
sc=load('website/std_scaler.bin')
pf=load('website/poly_features.bin')
model = pickle.load(open('website/predictor.pkl','rb'))



@app.route("/add-price/", methods=["GET", "POST"])
@login_required
def home():
    if (request.method == "POST") and ('open' in request.form):
        open    = request.form["open"]
        low    = request.form["low"]
        high    = request.form["high"]
        market_cap    = request.form["market_cap"]
        market_cap_global    = request.form["market_cap_global"]
        percent_change_24h    = request.form["percent_change_24h"]

        cols=['open','low', 'high', 'market_cap', 'market_cap_global', 'percent_change_24h']
        feats = [x for x in request.form.values()]
        feats = [np.array(feats)]
        tdf=pd.DataFrame(feats, columns=cols)
        for col in cols:
            tdf[col]=tdf[col].astype('float')
        final_features = generate_features(tdf[cols])
        train_cols =['open', 'predmeanmo', 'market_cap_global', 'e','percent_change_24h' ,'p24' ,'ho' ,'mo' ,'mid', 'market_cap', 'predmr' ,'mr'] 
        tdf['pred'] = model.predict(sc.transform(pf.transform(final_features[train_cols])))
        tdf=clip_prediction(tdf)
        close = tdf.pred
        print(close)
        new_price = Price(open=open,low=low, high=high, market_cap=market_cap,
         market_cap_global=market_cap_global, percent_change_24h=percent_change_24h, close=close)
        db.session.add(new_price)
        db.session.commit()
        prices    = Price.query.order_by(Price.date_created).all()
        x = "predicted close price is {}".format(close[0])
    else:
        x = " "
        prices    = Price.query.order_by(Price.date_created).all()
    return render_template("add-price.html",prices=prices,prediction=x )

@app.route("/delete/<int:price_id>")
@login_required
def delete_price(price_id):
    price = Price.query.get(price_id)

    if price:
        db.session.delete(price)
        db.session.commit()

        flash("The record has been deleted.", 'success')
        return redirect(url_for("home"))
    else:
        flash(f"Sorry a record with that id does not exist.", "danger")
        return redirect(url_for("home"))


@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        user = User(email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash("Your account has been created!", 'success')
        return redirect(url_for("login"))

    return render_template("sign-up.html", title="Sign Up", form=form)


@app.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")

            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash(f"Login unsuccessful, please check email and password", "danger")

    return render_template("login.html", title="Login", form=form)





@app.route("/dub-prices/", methods=["POST", "GET"])
def getFDublicate():
    price = request.form["price"]
    prices = Price.query.\
        filter(Price.price_id == price).\
        all()
    print(prices)
    if prices:
        return {"output": False}
    else:
        return {"output": True}


@app.route('/predict_api',methods=['POST'])
def predict_api():
    '''
    For direct API calls trought request
    '''
    data = request.get_json(force=True)
    prediction = predictor.predict([np.array(list(data.values()))])

    output = prediction[0]
    return jsonify(output)



@app.route("/logout")
def logout():
    logout_user()

    return redirect(url_for("home"))
