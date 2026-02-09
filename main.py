import bcrypt
import pyotp
import qrcode
import os
import base64
from io import BytesIO
from flask import Flask, render_template, request, redirect
from flask_cors import CORS
import user_management as dbHandler

app = Flask(__name__)
app.secret_key = 'my_secret_key'
CORS(app)

@app.route("/success.html", methods=["POST", "GET"])
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
        password = bcrypt.hashpw(oldpassword.encode("utf-8"), bcrypt.gensalt())
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
    elif request.method == "GET":
        msg = request.args.get("msg", "")
        return render_template("/index.html", msg=msg)

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = dbHandler.retrieveUser(username)

        if hashed_password and bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return redirect(f"/enable_2fa?username={username}")  # Redirect to 2FA setup
            
        else:
            return render_template("/index.html", error="Invalid credentials.")
    
    return render_template("/index.html")

@app.route("/enable_2fa", methods=["GET"])
def enable_2fa():
    username = request.args.get("username")
    user_secret = pyotp.random_base32()  # Generate TOTP Secret
    totp = pyotp.TOTP(user_secret)
    otp_uri = totp.provisioning_uri(name=username, issuer_name="YourAppName")
    qr_code = qrcode.make(otp_uri)

    stream = BytesIO()
    qr_code.save(stream, format="PNG")
    qr_code_b64 = base64.b64encode(stream.getvalue()).decode('utf-8')

    # Render the 2FA setup page
    return render_template("/2FA.html", value=username, state=True, qr_code_data=qr_code_b64, user_secret=user_secret)

@app.route("/verify_otp", methods=["POST"])
def verify_otp():
    username = request.form["username"]
    otp_input = request.form["otp"]
    user_secret = request.form["user_secret"]

    totp = pyotp.TOTP(user_secret)
    if totp.verify(otp_input):
        return render_template('/success.html')  # Replace with your success handling
    else:
        return "Invalid OTP. Please try again.", 401

if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5000)
