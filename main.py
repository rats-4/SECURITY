import bcrypt
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask_cors import CORS
import user_management as dbHandler

# Code snippet for logging a message
# app.logger.critical("message")

app = Flask(__name__)
# Enable CORS to allow cross-origin requests (needed for CSRF demo in Codespaces)
CORS(app)


@app.route("/success.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def addFeedback():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        feedback = request.form["feedback"]
        dbHandler.insertFeedback(feedback)
        dbHandler.listFeedback()
        return render_template("/success.html", state=True, value="Back")
    else:
        dbHandler.listFeedback()
        return render_template("/success.html", state=True, value="Back")


@app.route("/signup.html", methods=["POST", "GET"])
def signup():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        oldpassword = request.form["password"]
        password = bcrypt.hashpw(oldpassword.encode(), bcrypt.gensalt()).decode('utf-8')
        DoB = request.form["dob"]
        dbHandler.insertUser(username, password, DoB)
        return render_template("/index.html")
    else:
        return render_template("/signup.html")

@app.route("/index.html", methods=["POST", "GET"])
@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    # Pass message to front end
    elif request.method == "GET":
        msg = request.args.get("msg", "")
        return render_template("/index.html", msg=msg)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Retrieve hashed password from the database
        hashed_password = dbHandler.retrieveUser(username)

        # Check if the hashed password exists and verify it
        if hashed_password and bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            dbHandler.listFeedback()
            return render_template("/success.html", value=username, state=True)
        else:
            return render_template("/index.html", error="Invalid credentials.")
    
    else:
        return render_template("/index.html")



if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5000)
