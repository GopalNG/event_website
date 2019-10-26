from flask import Flask,render_template, url_for, flash, redirect, session,logging,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
import json
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

from models import User,Events,Attendees,PrivateJoinReq

class GmailHandler:

    def __init__(self, gmail):
        self.gmail = gmail
        self.password = "vvaefbxpkfyjotvv"

    def send_mail(self, receivers, subject, text):

        if not isinstance(receivers, list):
            receivers = [receivers]

        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(self.gmail, self.password)

        for receiver in receivers:
            msg = MIMEText(text)
            msg['Subject'] = subject
            msg['From'] = self.gmail
            msg['To'] = receiver
            smtp.sendmail(self.gmail, receiver, str(msg))
        smtp.quit()
        return True

@app.route('/')
def home():
    data = Events.query.all()
    return render_template("index.html",events=data,title="Home")

@app.route('/login',methods=["GET","POST"])
def user_login():
    if request.method == "POST":
        uemail = request.form["uname"]
        upass = request.form["passw"]
        login = User.query.filter_by(email=uemail,password=upass).first()
        if login is not None:
            session['email'] = uemail
            print(session['email'])
            return redirect(url_for("home"))
    return render_template("login.html")

@app.route('/register',methods=["GET","POST"])
def user_register():
    if request.method == "POST":
        uname = request.form.get("uname")
        mail = request.form.get("mail")
        passw = request.form.get("passw")
        try:
            user = User(username=uname,email=mail,password=passw)
            db.session.add(user)
            db.session.commit()
            flash("User Login Success")
            return redirect(url_for("user_login"))
        except Exception as error:
            print(error)
    return render_template("register.html")

@app.route('/logout')
def user_logout():
    if session.get('email'):
        session.pop('email', None)
        flash("Logged Out Success")
        return redirect(url_for('home'))
    return redirect(url_for('user_login'))

@app.route('/createevent',methods=["GET","POST"])
def create_event():
    if session.get('email'):
        print(session.get('email'))
        if request.method == "GET":
            eventtype = ['select one','Public','Private']
            return render_template("create_event.html",title="Create Event",eventtype=eventtype)
        else:
            etitle = request.form.get("title")
            econtent = request.form.get("content")
            ecity = request.form.get("city")
            estate = request.form.get("state")
            elocation = request.form.get("location")
            mailid = session.get('email')
            euser_id = db.session.query(User.id).filter_by(email=mailid).first()
            eventtype = request.form.get("etype")
            print("EEEEE :: {}".format(eventtype))
            print("D::::"+str(datetime.utcnow))

            etime = request.form.get("time")
            f = "%Y-%m-%dT%H:%M"
            formated_time = datetime.strptime(etime,f)
            print(euser_id , mailid,etime,formated_time)
            try:
                event = Events(title=etitle,content=econtent,event_type=eventtype,user_id=euser_id[0],city=ecity,state=estate,location=elocation,date_posted=formated_time)
                print(etitle, econtent,ecity,estate,elocation,euser_id)
                db.session.add(event)
                db.session.commit()
                flash("Created Event Successful")
                return redirect(url_for("home"))
            except Exception as error:
                print(error)
    return redirect(url_for("home"))

@app.route('/join/<event_id>')
def join_event(event_id):
    if session.get('email'):
        umailid = session.get('email')
        rtnvalue = Attendees.query.filter_by(mailid=umailid,event_id=event_id).first()
        if not rtnvalue:
            joinevent = Attendees(mailid=umailid,event_id=event_id)
            db.session.add(joinevent)
            db.session.commit()
            flash('Request success -You Joined event_id : {} and User : {}'.format(event_id,umailid))
            return redirect(url_for('home'))
        flash("AlReady Joined Event {}".format(event_id))
        return redirect(url_for('home'))
    return redirect(url_for('user_login'))

@app.route('/privateeventjoinreq/<eventid>/<emailid>',methods=["GET","POST"])
def join_private_event(eventid,emailid):
    try:
        # get request id with eventid and emailid
        reqid = db.session.query(PrivateJoinReq.id).filter_by(mailid=emailid).first()
        # add to attendees list emailid and event
        if reqid:
            joinevent = Attendees(mailid=emailid,event_id=eventid)
            db.session.add(joinevent)
            db.session.commit()
            # delete request id
            obj = PrivateJoinReq.query.filter_by(id=reqid[0],mailid=emailid).first()
            db.session.delete(obj)
            db.session.commit()
            flash("Joined Event {} for mailid {}".format(eventid,emailid))
            return redirect(url_for('home'))
    except TypeError:
        flash("AlReady Joined or Token Deleted")

@app.route('/joinreqform/<eventid>',methods=["GET","POST"])
def join_req_from(eventid):
    if request.method == "POST":
        email = request.form.get("mail")
        rtnvalue = Attendees.query.filter_by(mailid=email,event_id=eventid).first()
        if not rtnvalue:
            sub_content = 'http://127.0.0.1:5000/privateeventjoinreq/{}/{}'.format(eventid,email)
            rest = GmailHandler("nagubandigopal@gmail.com").send_mail(receivers=[email],subject="click above link to join the event",text=sub_content)
            print(rest)
            if rest:
                joinreq = PrivateJoinReq(mailid=email,event_id=eventid)
                db.session.add(joinreq)
                db.session.commit()
            flash("Request Sent To Your Mail Id : {} for event: {}".format(email,eventid))
            return redirect(url_for('home'))
        flash("AlReady Join In Event Thanks For your Intrest")
    return render_template("join_req_form.html")

if __name__=="__main__":
    app.run(debug=True)
