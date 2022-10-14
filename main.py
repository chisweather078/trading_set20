from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///trades.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    set_num = db.Column(db.String(80), nullable=False)
    symbol = db.Column(db.String(80), nullable=False)
    buy_sell = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime(80), nullable=False)
    trend = db.Column(db.String(120), nullable=False)
    divergence = db.Column(db.String(120), nullable=False)
    confirmation = db.Column(db.Text, nullable=False)
    outcome = db.Column(db.Float, nullable=True)
    close = db.Column(db.Text, nullable=True)
    deduction = db.Column(db.Text, nullable=True)
    open_image = db.Column(db.String(280), nullable=False)
    close_image = db.Column(db.String(280), nullable=True)


class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_set = db.Column(db.Integer, nullable=False)


db.create_all()

# db.session.add(Counter(current_set=1))
# db.session.commit()


@app.route("/")
def home():
    titles = sorted({trade.set_num for trade in Trade.query.all()})
    trades_dict = {group_num: Trade.query.filter_by(set_num=group_num) for group_num in titles}
    final_dict = {
        key: {"count": value.count(),
              "pnl": round(sum([trade.outcome for trade in list(value)]), 2),
              "winners": len([trade.outcome for trade in list(value) if trade.outcome > 0]),
              "losers": len([trade.outcome for trade in list(value) if trade.outcome < 0])}
        for key, value in trades_dict.items()}
    return render_template("sets.html", trades_group=final_dict)


@app.route("/list/<set_num>")
def my_trades(set_num):
    trades_list = db.session.query(Trade).filter_by(set_num=set_num)
    return render_template("trades.html", trades_list=trades_list)


@app.route("/add", methods=["GET", "POST"])
def add_trade():
    if request.method == "POST":
        if len(Trade.query.all()) % 20 == 0 and len(Trade.query.all()) > 0:
            Counter.query.get(1).current_set += 1

        year, month, day = request.form["date"].split("-")

        if request.form["outcome"]:
            new_trade = Trade(
                set_num="SET " + str(Counter.query.get(1).current_set),
                symbol=request.form["symbol"],
                buy_sell=request.form["buy_sell"],
                date=datetime(int(year), int(month), int(day)),
                trend=request.form["trend"],
                divergence=request.form["divergence"],
                confirmation=request.form["confirmation"],
                outcome=request.form["outcome"],
                close=request.form["close"],
                deduction=request.form["deduction"],
                open_image=request.form["open_image"],
                close_image=request.form["close_image"],
            )
        else:
            new_trade = Trade(
                set_num="SET " + str(Counter.query.get(1).current_set),
                symbol=request.form["symbol"],
                buy_sell=request.form["buy_sell"],
                date=datetime(int(year), int(month), int(day)),
                trend=request.form["trend"],
                divergence=request.form["divergence"],
                confirmation=request.form["confirmation"],
                outcome=0,
                close=request.form["close"],
                deduction=request.form["deduction"],
                open_image=request.form["open_image"],
                close_image=request.form["close_image"],
            )
        db.session.add(new_trade)
        db.session.commit()
        return redirect(url_for("view_trade", trade_id=new_trade.id))
    return render_template("add.html")


@app.route("/update/<int:trade_id>", methods=["GET", "POST"])
def update(trade_id):
    trade_to_update = Trade.query.get(trade_id)
    if request.method == "POST":
        year, month, day = request.form["date"].split("-")
        trade_to_update.symbol = request.form["symbol"]
        trade_to_update.buy_sell = request.form["buy_sell"]
        trade_to_update.date = datetime(int(year), int(month), int(day))
        trade_to_update.trend = request.form["trend"]
        trade_to_update.divergence = request.form["divergence"]
        trade_to_update.confirmation = request.form["confirmation"]
        trade_to_update.outcome = request.form["outcome"]
        trade_to_update.close = request.form["close"]
        trade_to_update.deduction = request.form["deduction"]
        trade_to_update.open_image = request.form["open_image"]
        trade_to_update.close_image = request.form["close_image"]
        db.session.commit()
        return redirect(url_for("view_trade", trade_id=trade_to_update.id))

    return render_template("update.html", trade_to_update=trade_to_update)


@app.route("/view/<int:trade_id>", methods=["GET"])
def view_trade(trade_id):
    trade_to_view = Trade.query.get(trade_id)
    return render_template("view.html", trade_to_view=trade_to_view)


@app.route("/delete/<int:trade_id>")
def delete_trade(trade_id):
    to_delete = Trade.query.get(trade_id)
    db.session.delete(to_delete)
    db.session.commit()
    return redirect(url_for("my_trades", set_num=to_delete.set_num))


if __name__ == "__main__":
    app.run(debug=True)

