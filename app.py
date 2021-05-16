from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from os import path
import boto3
from botocore.client import Config


app = Flask(__name__)
DB_NAME = "database_2.db"
UPLOAD_FOLDER = './static/images/profile_pics'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['SECRET_KEY'] = 'secret password key phrase here'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

#s3 = boto3.client('s3', aws_access_key_id="AKIA6BDN2SIRY3HW2J4T", aws_secret_access_key="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")

BUCKET = "hhs.alumni"
USER_NAME = "hhs"
PASSWORD = "hhs"

class Entry(db.Model):
 id = db.Column(db.Integer, primary_key=True)
 first_name = db.Column(db.String(100))
 last_name = db.Column(db.String(100))
 college_name = db.Column(db.String(100))
 email = db.Column(db.String(150), unique=True)
 job_sector = db.Column(db.String(150))
 blurb = db.Column(db.String(1000))
 profile_pic = db.Column(db.String(100))
 approval_status = db.Column(db.Integer)

def create_database(app):
    if not path.exists(DB_NAME):
        db.create_all(app=app)
        print('Created Successfully Database!')

create_database(app)

@app.route('/', methods=['GET', 'POST'])
def index():
 s3 = boto3.resource('s3')
 if request.method == 'POST':
   search_input = "%{}%".format(request.form.get('search'))
   search_entries = []
   #add additional search filters
   search_entries += Entry.query.filter(Entry.first_name.like(search_input)).filter(Entry.approval_status == "approved")
   search_entries += Entry.query.filter(Entry.last_name.like(search_input)).filter(Entry.approval_status == "approved")
   return render_template('index.html', entries=search_entries, s3=s3, bucket=BUCKET)
  
 return render_template('index.html', entries=[], s3=s3, bucket=BUCKET)

@app.route('/administrator', methods=['GET', 'POST'])
def administrator():
 s3 = boto3.resource('s3')
 if request.method == 'POST':
   if request.form.get('approve') != None:
    entry = Entry.query.get_or_404(request.form.get('approve'))
    entry.approval_status = "approved"
    db.session.commit()
    flash('Approved Entry', category='success')
   elif request.form.get('delete') != None:
    entry = Entry.query.get_or_404(request.form.get('delete'))
    db.session.delete(entry)
    db.session.commit()
    flash('Deleted Entry', category='success')
   elif request.form.get('check_unapproved') != None:
    pass
   else:
    search_input = "%{}%".format(request.form.get('search'))
    search_entries = []
    #add additional search filters
    search_entries += Entry.query.filter(Entry.first_name.like(search_input))
    search_entries += Entry.query.filter(Entry.last_name.like(search_input))
    return render_template('administrator.html', entries=search_entries, s3=s3, bucket=BUCKET)
 unapproved_entries = []
 unapproved_entries += Entry.query.filter(Entry.approval_status == "pending")
 print("hello world 2")
 return render_template('administrator.html', entries=unapproved_entries, s3=s3, bucket=BUCKET)

@app.route('/administrator_login', methods=['GET', 'POST'])
def administrator_login():
 if request.method == 'POST':
  user_name = request.form.get('username').lower()
  password = request.form.get('password')
  if user_name == USER_NAME and password == PASSWORD:
    return redirect('/administrator')
   
 return render_template('administrator_login.html')

@app.route('/addinfo', methods=['GET', 'POST'])
def add_info():
 if request.method == 'POST':
  first_name_input = request.form.get('firstName')
  last_name_input = request.form.get('lastName')
  email_input = request.form.get('email')
  graduation_year_input = request.form.get('graduationYear')
  blurb_input = request.form.get('blurb')
  approval_status_input = "pending"
  job_sector_list = []
  if request.form.get('technology') != None:
    job_sector_list.append(request.form.get('technology'))
  if request.form.get('business') != None:
    job_sector_list.append(request.form.get('business'))
  if request.form.get('healthCare') != None:
    job_sector_list.append(request.form.get('healthCare'))
  if request.form.get('education') != None:
    job_sector_list.append(request.form.get('education'))
  if request.form.get('government') != None:
    job_sector_list.append(request.form.get('government'))
  job_sector_input = ""
  for index in range(len(job_sector_list)):
    if index != 0:
      job_sector_input += "/"
    job_sector_input += job_sector_list[index]

  profile_picture_file = request.files['profilePic']
  profile_pic_path = ""
  last_id = 0
  if profile_picture_file.filename == "":
    profile_pic_path = "none"
  else:
    s3 = boto3.resource('s3', aws_access_key_id="AKIA6BDN2SIRY3HW2J4T", aws_secret_access_key="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", config=Config(signature_version='s3v4'))
    try:
      last_id = Entry.query.order_by(Entry.id.desc()).first().id
    except:
      last_id = 0
  
    current_id = last_id + 1
    profile_pic_path = str(current_id) + "_" + profile_picture_file.filename 
    s3.Bucket(BUCKET).put_object(Key=profile_pic_path, Body=profile_picture_file)

  
  college_name_input = ""
  if request.form.get('collegeName') != "":
    college_name_input = request.form.get('collegeName')
  else:
    college_name_input = 'none'
  
  #add graduation_year into entries
  #check every single input before creating entry and add flashes
  entry = Entry.query.filter_by(email=email_input).first()
  if entry:
    flash('Email already exists', category='error')
  else:
    new_entry = Entry(first_name=first_name_input, last_name=last_name_input, email=email_input, college_name=college_name_input, job_sector=job_sector_input, blurb=blurb_input, approval_status=approval_status_input, profile_pic=profile_pic_path)

    db.session.add(new_entry)
    print("here3")
    db.session.commit()
    print("here")
    return redirect('/')
    print("here1")

  
 return render_template('addinfo.html')



if __name__ == "__main__":
 app.run(debug=True)