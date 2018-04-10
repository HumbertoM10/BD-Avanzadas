from flask import Flask, render_template, flash, request, redirect, url_for
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from tt import post_tweets, get_JSON
from json import loads

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '\x12t\x0b\xa7\xdf\x8d\x96L\t\xdd\x1a\xe7\xaf\xd1:[\xca\xec)\xef\xf4\x82\x17\xec'

class ReusableForm(Form):
    hash = TextField('key_word:', validators=[validators.required()])

@app.route("/index")
def test():
    return render_template('index2.html')

@app.route("/getTweets/<string:hash>")
def getTweets(hash):
    tweets = get_JSON(hash)
    return redirect(url_for('index'))

@app.route("/", methods=['GET', 'POST'])
def post():
    form = ReusableForm(request.form)

    print (form.errors)
    if request.method == 'POST':
        hash=request.form['hash']
        print (hash)

        if form.validate():
            post_tweets(hash)
            return redirect(url_for('getTweets', hash = hash))
        else:
            flash('All the form fields are required. ')

    return render_template('index2.html', form=form)

if __name__ == "__main__":
    app.run()