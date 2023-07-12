from application import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """
    User class is a table in the site.db
    """
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    commentator = db.relationship('Comments', backref='commentator', lazy=True)


    def __repr__(self):
        """
        How User object will be printed.
        """
        return ('User: ({}, {}, {})'.format(self.username, self.email, self.image_file))


class Post(db.Model):
    """
    Post class is a table in the site.db
    """
    __tablename__ = "post"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comments', backref='for_post', lazy=True)

    def __repr__(self):
        """
        How Post object will be printed.
        """
        return ('Post: ({}, {})'.format(self.title, self.date_posted))
    
class Comments(db.Model):
    """
    Comment class is a table in site.db
    """
    __tablename__ = "comments"
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False, unique=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        """
        How a comment will be printed
        """
        return ('Commment: {}, ({})'.format(self.content, self.date_posted))
