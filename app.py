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
   search_entries += Entry.query.filter(Entry.first_name.like(search_input))
   search_entries += Entry.query.filter(Entry.last_name.like(search_input))
   print("search entries")
   print(search_entries)
   #print(search_input)

   #qry = db.Query(Entry).filter(str(Entry.first_name).lower().contains(search_input.lower()))
  #  qry = db.Query(Entry).filter(search_input.lower() in str(Entry.first_name).lower())
  #  print("rithesh hello" + str(qry))

  #  for entry in qry.all():
  #    search_entries.append(entry)
   #qry = db.Query(Entry).filter(str(Entry.last_name).lower().contains(search_input.lower()))
  #  qry = db.Query(Entry).filter(search_input.lower() in str(Entry.last_name).lower())
  #  for entry in qry.all():
  #    search_entries.append(entry)
  #  print(search_entries)
   return render_template('index.html', entries=search_entries, s3=s3, bucket=BUCKET)
  
 return render_template('index.html', entries=[], s3=s3, bucket=BUCKET)

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
  
    #add handling when it is intially NoneType with 0 entries
    #print("rithesh:" + str(last_id))
    current_id = last_id + 1
    profile_pic_path = str(current_id) + "_" + profile_picture_file.filename 
    s3.Bucket(BUCKET).put_object(Key=profile_pic_path, Body=profile_picture_file)

    #profile_pic_path = path.join(app.config['UPLOAD_FOLDER'], profile_picture_file.filename)
    #profile_picture_file.save(profile_pic_path) 
  
  college_name_input = ""
  if request.form.get('collegeName') != "":
    college_name_input = request.form.get('collegeName')
  else:
    college_name_input = 'none'
  
  
  #try:
  entry = Entry.query.filter_by(email=email_input).first()
  if entry:
    flash('Email already exists', category='error')
    print("email already used error")
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