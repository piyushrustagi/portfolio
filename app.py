from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user # type: ignore

app = Flask(__name__)
import sqlite3
DATABASE = "personal_site.db"

def get_db_connection():
 conn = sqlite3.connect(DATABASE)
 conn.row_factory = sqlite3.Row # so we can treat rows like dictionaries
 return conn

# Initialize database (create table if not exists)
conn = get_db_connection()
conn.execute("""
CREATE TABLE IF NOT EXISTS posts (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL,
content TEXT NOT NULL,
created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()
conn.close()

# Set a secret key for session management
app.secret_key = '7981a5f680f9431722c9f405f52b461e645ef00190fd2ec9182631f9026c91bd'

# Homepage route
@app.route("/")
def home():
    projects = [
        {"title": "Project One", "desc": "Description of project one..."},
        {"title": "Project Two", "desc": "Description of project two..."}
    ]
    return render_template("home.html", projects=projects)

# Blog page route (Displays posts)
@app.route("/blog")
def blog():
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM posts ORDER BY created DESC").fetchall()
    conn.close()
    return render_template("blog.html", posts=posts)

# Contact form route (Handles both GET and POST)
@app.route("/contact", methods=["GET", "POST"])
def contact():
    print("Contact route accessed.")  # Debugging Step 1
    if request.method == "POST":
        # Debugging: Print request method to verify it's reaching this block
        print(f"Request Method: {request.method}") # Should print "POST" when form submits
        
        # Get form data
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        
         # Store the message in the database
         # Check if all fields are filled
        if name and email and message:
            # Insert the message into the database
            conn = get_db_connection()
            conn.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
                         (name, email, message))
            conn.commit()
            conn.close()

        # Simulate handling the form by printing the data to the console
        print(f"Received message from {name} ({email}): {message}")
        
        # Flash success message
        if name and email and message:
          flash("Thank you for reaching out! I will get back to you soon.", "success")
        else:
          flash("Please fill in all fields.", "danger")

        # Redirect back to home after processing the form
        return redirect(url_for("home"))
    
    # If the method is GET (user visits /contact), show the contact form
    return render_template("contact.html")



@app.route("/init_post")
def init_post():
    conn = get_db_connection()
    conn.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
                 ("My First Blog Post", "This is a sample blog post about my project."))
    conn.commit()
    conn.close()
    return "Initial post added."

# Admin Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Simple check for username and password (replace with a secure check in a real app)
        if username == "admin" and password == "admin123":  
            session['logged_in'] = True  # Store the session flag
            flash("Login successful!", "success")
            return redirect(url_for("new_post"))  # Redirect to the post creation page
        else:
            flash("Invalid credentials, please try again.", "danger")
    
    return render_template("login.html")

# Route to logout
@app.route("/logout")
def logout():
    session.pop('logged_in', None)  # Remove the session flag
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))

@app.route("/admin")
def admin():
    if 'logged_in' not in session:
        flash("Please log in to access the admin panel.", "danger")
        return redirect(url_for('login'))  # Redirect to login page if not logged in

    return render_template("admin.html")  # Render the admin panel template

@app.route("/admin/messages")
def admin_messages():
    if 'logged_in' not in session:
        flash("Please log in to access the admin panel.", "danger")
        return redirect(url_for('login'))  # Redirect to login page if not logged in

     # Fetch all messages from the database
    conn = get_db_connection()
    messages = conn.execute("SELECT * FROM messages ORDER BY created DESC").fetchall()
    conn.close()

    return render_template("messages.html", messages=messages)

# Route to add a new post (only accessible when logged in)
@app.route("/new_post", methods=["GET", "POST"])
def new_post():
    if not session.get('logged_in'):  # Check if the user is logged in
        flash("Please log in to add a post.", "danger")
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        if not title or not content:
            flash("Title and content are required!", "danger")
        else:
            conn = get_db_connection()
            conn.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
            conn.commit()
            conn.close()
            flash("New post added successfully.", "success")
            return redirect(url_for('blog'))

    return render_template("new_post.html")  # Renders the form page


from datetime import datetime

@app.template_filter('datetimeformat')
def datetimeformat(value, format="%B %d, %Y"):
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime(format)

# Main entry point
if __name__ == "__main__":
    app.run(debug=True)




