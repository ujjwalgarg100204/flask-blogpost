import os
from datetime import datetime

import jinja_partials
from dotenv import load_dotenv
from flask import Flask, render_template, request as req
from flask_assets import Bundle, Environment
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class BlogPost(db.Model):
    id: int = db.Column("id", db.Integer, primary_key=True)
    title: str = db.Column(db.String)
    content: str = db.Column(db.String)

    date_created: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"BlogPost(id={self.id!r}, title={self.title!r})"


with app.app_context():
    db.create_all()

jinja_partials.register_extensions(app)

assets = Environment(app)
css = Bundle("src/main.css", output="dist/main.css")
js = Bundle("src/*.js", output="dist/main.js")

assets.register("css", css)
assets.register("js", js)
css.build()
js.build()


@app.route("/", methods=["GET", "POST"])
def home():
    match req.method:
        case "POST":
            blog = BlogPost(title=req.form["title"], content=req.form["content"])
            db.session.add(blog)
            db.session.commit()
            return jinja_partials.render_partial("blog/blog_card.html", blog=blog)

        case "GET":
            blogs: list[BlogPost] = db.session.execute(db.select(BlogPost).order_by(BlogPost.id)).scalars()
            return render_template("home/index.html", blogs=blogs)


@app.route('/blog/<int:blog_id>')
def view_post(blog_id: int):
    blog: BlogPost = db.get_or_404(BlogPost, blog_id)
    return render_template('blog/view_blog.html', blog=blog)
