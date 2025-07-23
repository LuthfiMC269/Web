from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from dotenv import load_dotenv
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)

# ───── Admin Login Credentials ─────
load_dotenv()
ADMIN_CREDENTIALS = {
    "username": os.getenv("USER_NAME"),
    "password": os.getenv("PASSWORD")
}

# ───── Model BlogPost ─────
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    excerpt = db.Column(db.Text)
    image = db.Column(db.String(200))
    content = db.Column(db.Text)

# ───── Secure Admin Panel ─────
class SecureAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not session.get("admin_logged_in"):
            return redirect(url_for("login"))
        return super().index()

    def is_accessible(self):
        return session.get("admin_logged_in")

class SecureModelView(ModelView):
    def is_accessible(self):
        return session.get("admin_logged_in")

admin = Admin(app, name='Admin Panel', index_view=SecureAdminIndexView(), template_mode='bootstrap4')
admin.add_view(SecureModelView(BlogPost, db.session))

# ───── Routes ─────

GITHUB_USERNAME = os.getenv("GITHUBUSR")

def get_github_projects():
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            repos = sorted(response.json(), key=lambda r: r['stargazers_count'], reverse=True)
            return repos
        else:
            return []
    except:
        return []

@app.route("/")
def index():
    projects = get_github_projects()
    for repo in projects:
        repo['image'] = get_repo_image(repo)
    return render_template("index.html", projects=projects)

@app.route("/blogs")
def blogs():
    posts = BlogPost.query.all()
    return render_template("blogs.html", posts=posts)

@app.route("/blogs/<slug>")
def blog_detail(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    return render_template("blog_detail.html", post=post)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
            session["admin_logged_in"] = True
            return redirect("/admin")
        else:
            flash("Invalid username or password.")
    return render_template("admin_login.html")

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("login"))

def get_repo_image(repo):
    repo_name = repo['name'].lower().replace('_', '-')
    local_image = f"images/repos/{repo_name}.png"
    full_path = os.path.join("static", local_image)

    if os.path.exists(full_path):
        return url_for('static', filename=local_image)
    else:
        username = repo['owner']['login']
        return f"https://opengraph.githubassets.com/1/{username}/{repo['name']}"


if __name__ == "__main__":
    app.run(debug=True)
