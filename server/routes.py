import os
import secrets
from flask import Response
from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from dotenv import load_dotenv
import openai
from server import app, bcrypt, db,mail
import json
# IMPORTING THE CORS APP
from flask_cors import CORS, cross_origin
from server.forms import RegistrationForms, LoginForms, UpdateAccountForms, PostForms, UserInputForms, ResetPasswordForm, RequestResetForm
from server.models import User, Testimonial, IncomeExpenses, Food, Log
from datetime import datetime
from flask_mail import Message

app.app_context().push()
db.create_all()


load_dotenv()
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")



@app.route("/")
def home():
    posts = Testimonial.query.all()
    return render_template('layout.html', posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForms()
    # CHECKS IF FORM IS VALID ON SUBMISSION
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! you are now able to login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForms()
    # CHECKS IF FORM IS VALID ON SUBMISSION
    if form.validate_on_submit():
        user = User.query.filter_by(email= form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Log in unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/about")
def about():
    return render_template("about.html", title='About')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    # generate a random hex for the image
    random_hex = secrets.token_hex(8)
    # get the file extension of the image
    f_name, f_ext = os.path.splitext(form_picture.filename)

    picture_name = random_hex + f_ext
    picture_location = os.path.join(app.root_path, 'static/images', picture_name)
    form_picture.save(picture_location)

    # RESIZE IMAGE?

    return picture_name

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForms()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='images/'+current_user.image_file)
    return render_template('account.html', title='Account', image_file = image_file, form= form)

# CREATING OUR AI CHATBOT USING THE CHATGPT API
@app.route("/ai", methods=["GET", "POST"])
@login_required
def ai():
    if request.method == "POST":
        user_input = request.form["user_input"]
        openai.api_key = os.getenv("API_TOKEN")
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=user_input,
            max_tokens=2040,
            temperature=0
        )
        result = response["choices"][0]["text"]
        return (result)
    return render_template('chat.html', title = 'AI')


@app.route("/post",methods=["GET", "POST"])
@login_required
def community():
    form = PostForms()
    if form.validate_on_submit():
        post = Testimonial(title = form.title.data, content = form.content.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title = 'New Post', form = form)


# FOR OUR WEIGHT TRACKER SECTION
@app.route('/tracker_index')
def tracker_index():
    entries = IncomeExpenses.query.order_by(IncomeExpenses.data.desc()).all()
    return render_template('tracker_index.html', entries=entries)

@app.route('/tracker', methods=["GET", "POST"])
@login_required
def tracker():
    form = UserInputForms()
    if form.validate_on_submit():
        entry = IncomeExpenses(type = form.type.data, amount=form.amount.data,
        category = form.category.data)
        db.session.add(entry)
        db.session.commit()
        flash("Entry added successfully", 'success')
        return redirect(url_for('tracker_index'))
    return render_template('add.html', form = form, title = 'Tracker')

@app.route("/delete/<int:entry_id>")
def delete(entry_id):
    entry = IncomeExpenses.query.get_or_404(int(entry_id))
    db.session.delete(entry)
    db.session.commit()
    flash("Deleted Successfully", 'success')
    return redirect(url_for('tracker_index'))

@app.route('/dashboard')
def dashboard():
    income_vs_expenses = db.session.query(db.func.sum(IncomeExpenses.amount),
    IncomeExpenses.type).group_by(IncomeExpenses.type).order_by(IncomeExpenses.type).all()

    dates = db.session.query(db.func.sum(IncomeExpenses.amount), IncomeExpenses.data).group_by(IncomeExpenses.data).group_by(IncomeExpenses.data).all()

    income_expense = []
    for total_amount,_ in income_vs_expenses:
        income_expense.append(total_amount)

    over_time_expenditure = []
    dates_labels = []
    for amount, date in dates:
        over_time_expenditure.append(amount)
        dates_labels.append(date.strftime('%m/%d/%Y'))

    return render_template('dashboard.html',
    income_vs_expenses = json.dumps(income_expense),
    over_time_expenditure = json.dumps(over_time_expenditure),
    dates_labels = json.dumps(dates_labels))    

# FOR OUR FOOD TRACKER SECTION

@app.route('/indexx')
@login_required
def indexx():
    logs = Log.query.order_by(Log.date.desc()).all()

    log_dates = []

    for log in logs:
        protiens = 0
        carbs = 0
        fats = 0
        calories = 0

        for food in log.foods:
            protiens += food.protiens
            carbs += food.carbs
            fats += food.fats
            calories += food.calories

        log_dates.append({
            'log_date': log,
            'protiens': protiens,
            'carbs': carbs,
            'fats': fats,
            'calories': calories

        })

    return render_template('indexx.html', log_dates = log_dates, title='Food Tracker')


@app.route('/create_log', methods = ['POST'])
def create_log():
    date = request.form.get('date')
    log= Log(date=datetime.strptime(date, '%Y-%m-%d'))

    db.session.add(log)
    db.session.commit()
    return redirect(url_for('view', log_id = log.id))

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == "POST":
        food_name = request.form.get('food-name')
        protiens = request.form.get('protein')
        carbs = request.form.get('carbohydrates')
        fats = request.form.get('fat')

        food_id = request.form.get('food-id')
        if food_id:
            food = Food.query.get_or_404(food_id)
            food.name = food_name
            food.protiens = protiens
            food.carbs = carbs
            food.fats = fats
        else:
            new_food = Food(
                name = food_name, 
                protiens = protiens, 
                carbs = carbs, 
                fats = fats
            )
            db.session.add(new_food)
        db.session.commit()
        return redirect(url_for('add'))

    foods = Food.query.all()
    return render_template('addd.html', foods = foods, food=None, title='Food Tracker')

@app.route('/delete_food/<int:food_id>')
def delete_food(food_id):
    food = Food.query.get_or_404(food_id)
    db.session.delete(food)
    db.session.commit()

    return redirect(url_for('add'))


@app.route('/edit_food/<int:food_id>')
def edit_food(food_id):
    food = Food.query.get(food_id)
    foods = Food.query.all()
    return render_template('addd.html', food = food, foods = foods)


@app.route('/view/<int:log_id>')
def view(log_id):
    log = Log.query.get_or_404(log_id)
    foods = Food.query.all()
    totals = {
        'protiens': 0,
        'carbs' : 0,
        'fats' : 0,
        'calories': 0
    }

    for food in log.foods:
        totals['protiens'] += food.protiens
        totals['carbs'] += food.carbs
        totals['fats'] += food.fats
        totals['calories'] += food.calories
    
    return render_template('view.html', foods = foods, log=log, totals=totals, title='Food Tracker')


@app.route('/add_food_to_log/<int:log_id>', methods = ['POST'])
def add_food_to_log(log_id):
    log = Log.query.get_or_404(log_id)

    selected_food = request.form.get('food-select')

    food = Food.query.get(int(selected_food))

    log.foods.append(food)
    db.session.commit()

    return redirect(url_for('view', log_id=log_id))


@app.route('/remove_food_from_log/<int:log_id>/<int:food_id>')
def remove_food_from_log(log_id, food_id):
    log = Log.query.get(log_id)
    food = Food.query.get(food_id)

    log.foods.remove(food)
    db.session.commit()

    return redirect(url_for('view',log_id = log_id))

# FOR OUR RESET PASSWORD SECTION

def send_reset_email(user):
    token = user.reset_token()
    msg = Message('Reset Password Request', sender = 'noreply@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request, please ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route('/reset_password', methods=['GET','POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash('A email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', form=form,title='Reset Password')


@app.route('/reset_token/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_token(token)
    if user is None:
        flash('This is an invalid or Expired token', 'warning')
        return redirect(url_for('reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash('Your password has been changed.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', form=form,title='Reset Password')