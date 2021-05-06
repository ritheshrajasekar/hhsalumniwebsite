from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from os import path
import boto3
from botocore.client import Config


app = Flask(__name__)
DB_NAME = "database.db"
UPLOAD_FOLDER = './static/images/profile_pics'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['SECRET_KEY'] = 'secret password key phrase here'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

#s3 = boto3.client('s3', aws_access_key_id="AKIA6BDN2SIRY3HW2J4T", aws_secret_access_key="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")

BUCKET = "hhs.alumni"

current_id = 0

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

@app.route('/')
def index():
 return render_template('index.html')

@app.route('/addinfo', methods=['GET', 'POST'])
def add_info():
 global current_id
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
  if profile_picture_file.filename == "":
    profile_pic_path = "none"
  else:
    s3 = boto3.resource('s3', aws_access_key_id="AKIA6BDN2SIRY3HW2J4T", aws_secret_access_key="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")
    s3.Bucket(BUCKET).put_object(Key=profile_picture_file.filename, Body=profile_picture_file)

    #profile_pic_path = path.join(app.config['UPLOAD_FOLDER'], profile_picture_file.filename)
    #profile_picture_file.save(profile_pic_path) 
  
  college_name_input = ""
  if request.form.get('collegeName') != "":
    college_name_input = request.form.get('collegeName')
  else:
    college_name_input = 'none'
  
  #new_entry = Entry(first_name=first_name_input, last_name=last_name_input, email=email_input, college_name=college_name_input, job_sector=job_sector_input, blurb=blurb_input, profile_pic=profile_pic_path, approval_status=approval_status_input)
  current_id += 1
  #print("currentId: " + str(current_id))
  
 return render_template('addinfo.html')



if __name__ == "__main__":
 app.run(debug=True)