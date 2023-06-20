from server import db, login_manager,app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# THIS IS THE DATABASE OF THE USER
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.png')
    password = db.Column(db.String(20), nullable=False)
    post = db.relationship('Testimonial', backref='author', lazy=True)

    # FOR OUR RESET EMAIL VALIDATION
    def reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod  # ESSENTIALLY WE'RE JUST TELLING THE INTERPRETER NOT TO EXPECT SELF AS A PARAMETER ONLY THE TOKEN
    def verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    # THIS REPRESENTS HOW WE WANT OUR USER DATA TO BE REPRESENTED

    def __repr__(self):
        return f"User('{self.username}', '{self.email}','{self.image_file}')"

# THIS IS THE DATABASE FOR OUR TESTIOMONIAL SECTION
class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    time_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # THIS REPRESENTS HOW WE WANT OUR USER DATA TO BE REPRESENTED
    def __repr__(self):
        return f"Testimonial('{self.title}','{self.time_posted})"


# THIS IS THE DATABASE WE'LL USE TO TRACK WEIGHT GAIN AND WEIGHT LOSS
class IncomeExpenses(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(30), default = 'income', nullable = False)
    category = db.Column(db.String(30), nullable = False, default= 'rent')
    data = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    amount = db.Column(db.Integer, nullable = False)

    def __str__(self):
        return self.id

# DATABASE FOR OUR FOOD TRACKER

log_food = db.Table('log_food',
    db.Column('log_id',db.Integer,db.ForeignKey('log.id'), primary_key = True),
    db.Column('food_id',db.Integer,db.ForeignKey('food.id'), primary_key=True)
)

class Food(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(50), unique = True, nullable = False)
    protiens = db.Column(db.Integer, nullable = False)
    carbs = db.Column(db.Integer, nullable = False)
    fats = db.Column(db.Integer, nullable = False)

    # calculation for calories
    @property
    def calories(self):
        return self.protiens * 4 + self.carbs * 4 + self.fats * 9


class Log(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    date = db.Column(db.Date, nullable = False)
    foods = db.relationship('Food', secondary = log_food, lazy = 'dynamic')