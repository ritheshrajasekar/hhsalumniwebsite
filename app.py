from flask import Flask, render_template, url_for, request, redirect, flash, session
import flask
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
PER_PAGE = 5

search_input = None
user_page = 1

admin_search_input = None
admin_path_search = 0
admin_user_page = 1

class Entry(db.Model):
 id = db.Column(db.Integer, primary_key=True)
 first_name = db.Column(db.String(100))
 last_name = db.Column(db.String(100))
 full_name = db.Column(db.String(100))
 college_name = db.Column(db.String(100))
 email = db.Column(db.String(150), unique=True)
 job_sector = db.Column(db.String(150))
 blurb = db.Column(db.String(1000))
 profile_pic = db.Column(db.String(100))
 graduation_year = db.Column(db.String(20))
 approval_status = db.Column(db.String(20))

def create_database(app):
    if not path.exists(DB_NAME):
        db.create_all(app=app)
        print('Created Successfully Database!')

create_database(app)

@app.route('/', methods=['GET', 'POST'])
def index():
 global search_input
 global user_page
 session.pop('user', None)
 s3 = boto3.resource('s3')
 if request.method == 'POST':
   if request.form.get('searchHidden') != None:
    search_input = "%{}%".format(request.form.get('search')).strip()
    search_entries = Entry.query.filter((Entry.first_name.like(search_input)) | (Entry.last_name.like(search_input)) | (Entry.full_name.like(search_input)) | (Entry.college_name.like(search_input)) | (Entry.email.like(search_input)) | (Entry.job_sector.like(search_input)) | (Entry.blurb.like(search_input)) | (Entry.graduation_year.like(search_input))).filter(Entry.approval_status == "approved")
    count = search_entries.count()
    user_page = 1
    user_search_entries = search_entries.paginate(page=user_page, per_page=PER_PAGE)
    return render_template('index.html', entries=user_search_entries, s3=s3, bucket=BUCKET, search=True, count=count)
   elif request.form.get('pagePrevious') != None:
    user_page = request.form.get('pagePrevious')
   elif request.form.get('pageNext') != None:
    user_page = request.form.get('pageNext')
   search_entries = Entry.query.filter((Entry.first_name.like(search_input)) | (Entry.last_name.like(search_input)) | (Entry.full_name.like(search_input)) | (Entry.college_name.like(search_input)) | (Entry.email.like(search_input)) | (Entry.job_sector.like(search_input)) | (Entry.blurb.like(search_input)) | (Entry.graduation_year.like(search_input))).filter(Entry.approval_status == "approved")
   count = search_entries.count()
   user_search_entries = search_entries.paginate(page=int(user_page), per_page=PER_PAGE)
   return render_template('index.html', entries=user_search_entries, s3=s3, bucket=BUCKET, search=True, count=count)
 return render_template('index.html', entries=[], s3=s3, bucket=BUCKET, search=False, count=0)

@app.route('/administrator', methods=['GET', 'POST'])
def administrator():
 global admin_search_input
 global admin_path_search
 global admin_user_page
 if flask.g.user:  
  s3 = boto3.resource('s3')
  if request.method == 'POST':
    if request.form.get('approve') != None:
      entry = Entry.query.get_or_404(request.form.get('approve'))
      entry.approval_status = "approved"
      db.session.commit()
      flash('Approved Entry', category='success')
      if admin_path_search == 1:
        search_entries = Entry.query.filter((Entry.first_name.like(admin_search_input)) | (Entry.last_name.like(admin_search_input)) | (Entry.full_name.like(admin_search_input)) | (Entry.college_name.like(admin_search_input)) | (Entry.email.like(admin_search_input)) | (Entry.job_sector.like(admin_search_input)) | (Entry.blurb.like(admin_search_input)) | (Entry.graduation_year.like(admin_search_input)))
        count = search_entries.count()
        admin_search_entries = search_entries.paginate(page=admin_user_page, per_page=PER_PAGE)
        return render_template('administrator.html', entries=admin_search_entries, s3=s3, bucket=BUCKET, search=True, count=count)
      else:
        admin_user_page = 1
        unapproved_entries = Entry.query.filter(Entry.approval_status == "pending")
        count = unapproved_entries.count()
        admin_search_entries = unapproved_entries.paginate(page=admin_user_page, per_page=PER_PAGE)
        return render_template('administrator.html', entries=admin_search_entries, s3=s3, bucket=BUCKET, search=False, count=count)
    elif request.form.get('delete') != None:
      entry = Entry.query.get_or_404(request.form.get('delete'))
      db.session.delete(entry)
      db.session.commit()
      flash('Deleted Entry', category='success')
      if admin_path_search == 1:
        admin_user_page = 1
        search_entries = Entry.query.filter((Entry.first_name.like(admin_search_input)) | (Entry.last_name.like(admin_search_input)) | (Entry.full_name.like(admin_search_input)) | (Entry.college_name.like(admin_search_input)) | (Entry.email.like(admin_search_input)) | (Entry.job_sector.like(admin_search_input)) | (Entry.blurb.like(admin_search_input)) | (Entry.graduation_year.like(admin_search_input)))
        count = search_entries.count()
        admin_search_entries = search_entries.paginate(page=admin_user_page, per_page=PER_PAGE)
        return render_template('administrator.html', entries=admin_search_entries, s3=s3, bucket=BUCKET, search=True, count=count)
      else:
        admin_user_page = 1
        unapproved_entries = Entry.query.filter(Entry.approval_status == "pending")
        count = unapproved_entries.count()
        admin_search_entries = unapproved_entries.paginate(page=admin_user_page, per_page=PER_PAGE)
        return render_template('administrator.html', entries=admin_search_entries, s3=s3, bucket=BUCKET, search=False, count=count)
    elif request.form.get('check_unapproved') != None:
      pass
    elif request.form.get('pagePrevious') != None:
      print("hello savior")
      print(request.form.get('pagePrevious'))
      admin_user_page = int(request.form.get('pagePrevious'))
      if admin_path_search == 1:
        search_entries = Entry.query.filter((Entry.first_name.like(admin_search_input)) | (Entry.last_name.like(admin_search_input)) | (Entry.full_name.like(admin_search_input)) | (Entry.college_name.like(admin_search_input)) | (Entry.email.like(admin_search_input)) | (Entry.job_sector.like(admin_search_input)) | (Entry.blurb.like(admin_search_input)) | (Entry.graduation_year.like(admin_search_input)))
        count = search_entries.count()
        admin_search_entries = search_entries.paginate(page=admin_user_page, per_page=PER_PAGE)
        print("print hello world 1")
        return render_template('administrator.html', entries=admin_search_entries, s3=s3, bucket=BUCKET, search=True, count=count)
      else:
        unapproved_entries = Entry.query.filter(Entry.approval_status == "pending")
        count = unapproved_entries.count()
        admin_search_entries = unapproved_entries.paginate(page=admin_user_page, per_page=PER_PAGE)
        print("print hello world 2")
        return render_template('administrator.html', entries=admin_search_entries, s3=s3, bucket=BUCKET, search=False, count=count)
    elif request.form.get('pageNext') != None:
      print(request.form.get('pageNext'))
      admin_user_page = int(request.form.get('pageNext'))
      print("hello savior 2")
      if admin_path_search == 1:
        search_entries = Entry.query.filter((Entry.first_name.like(admin_search_input)) | (Entry.last_name.like(admin_search_input)) | (Entry.full_name.like(admin_search_input)) | (Entry.college_name.like(admin_search_input)) | (Entry.email.like(admin_search_input)) | (Entry.job_sector.like(admin_search_input)) | (Entry.blurb.like(admin_search_input)) | (Entry.graduation_year.like(admin_search_input)))
        count = search_entries.count()
        admin_search_entries = search_entries.paginate(page=admin_user_page, per_page=PER_PAGE)
        print("print hello world 3")
        return render_template('administrator.html', entries=admin_search_entries, s3=s3, bucket=BUCKET, search=True, count=count)
      else:
        unapproved_entries = Entry.query.filter(Entry.approval_status == "pending")
        count = unapproved_entries.count()
        admin_search_entries = unapproved_entries.paginate(page=admin_user_page, per_page=PER_PAGE)
        print("print hello world 4")
        return render_template('administrator.html', entries=admin_search_entries, s3=s3, bucket=BUCKET, search=False, count=count)

    # make sure delete and approve allows them to see rest of entries when done  
    else:
      admin_path_search = 1
      admin_search_input = request.form.get('search').strip()
      search_entries = Entry.query.filter((Entry.first_name.like(admin_search_input)) | (Entry.last_name.like(admin_search_input)) | (Entry.full_name.like(admin_search_input)) | (Entry.college_name.like(admin_search_input)) | (Entry.email.like(admin_search_input)) | (Entry.job_sector.like(admin_search_input)) | (Entry.blurb.like(admin_search_input)) | (Entry.graduation_year.like(admin_search_input)))
      count = search_entries.count()
      admin_user_page = 1
      admin_search_entries = search_entries.paginate(page=admin_user_page, per_page=PER_PAGE)
      return render_template('administrator.html', entries=admin_search_entries, s3=s3, bucket=BUCKET, search=True, count=count)
  admin_path_search = 0
  admin_user_page = 1
  unapproved_entries = Entry.query.filter(Entry.approval_status == "pending")
  count = unapproved_entries.count()
  admin_search_entries = unapproved_entries.paginate(page=admin_user_page, per_page=PER_PAGE)
  return render_template('administrator.html', entries=admin_search_entries, s3=s3, bucket=BUCKET, search=False, count=count)
 return redirect(url_for('administrator_login'))

@app.route('/administrator_login', methods=['GET', 'POST'])
def administrator_login():
 if request.method == 'POST':
  session.pop('user', None) 
  user_name = request.form.get('username').lower()
  password = request.form.get('password')
  if user_name == USER_NAME and password == PASSWORD:
    session['user'] = request.form.get('username').lower()
    return redirect(url_for('administrator'))
  else:
    flash('Incorrect username or password', category='error') 
   
 return render_template('administrator_login.html')

@app.route('/about_us', methods=['GET', 'POST'])
def about_us(): 
 return render_template('about_us.html')

@app.route('/help', methods=['GET', 'POST'])
def help(): 
 return render_template('help.html')

@app.before_request
def before_request():
  flask.g.user = None
  if 'user' in session:
    flask.g.user = session['user']
  
@app.route('/addinfo', methods=['GET', 'POST'])
def add_info():
 if request.method == 'POST':
  first_name_input = request.form.get('firstName').strip()
  last_name_input = request.form.get('lastName').strip()
  full_name_input = first_name_input + " " + last_name_input
  email_input = request.form.get('email')
  graduation_year_input = request.form.get('graduationYear')
  blurb_input = request.form.get('blurb').strip()
  approval_status_input = "pending"
  job_sector_list = []
  other_option = False
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
  if request.form.get('other') != None:
    other_option = True
    job_sector_list.append(request.form.get('otherOption'))
  job_sector_input = ""
  for index in range(len(job_sector_list)):
    if index != 0:
      job_sector_input += "/ "
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
    college_name_input = request.form.get('collegeName').strip()
  else:
    college_name_input = 'none'
  
  #add graduation_year into entries
  #check every single input before creating entry and add flashes
  errors = 0
  entry = Entry.query.filter_by(email=email_input).first()
  if entry:
   errors += 1
   flash('Email already exists', category='error')
  if len(first_name_input) < 1 or len(last_name_input) < 1:
   errors += 1
   flash('Invalid Name', category='error')   
  if len(job_sector_input) < 3:
   errors += 1
   flash('Please choose career field', category='error')  
  if len(blurb_input) < 3:
   errors += 1
   flash('Please enter blurb', category='error') 
  elif len(blurb_input) > 400:
   errors += 1
   flash('Blurb must be under 400 characters', category='error')
  if other_option and len(request.form.get('otherOption').strip()) < 1:
   errors += 1
   flash('Enter other career field selected', category='error')          
  if errors == 0:
    new_entry = Entry(first_name=first_name_input, last_name=last_name_input, full_name=full_name_input, email=email_input, college_name=college_name_input, job_sector=job_sector_input, blurb=blurb_input, approval_status=approval_status_input, profile_pic=profile_pic_path, graduation_year=graduation_year_input)

    db.session.add(new_entry)
    print("here3")
    db.session.commit()
    print("here")
    return redirect('/')
    print("here1")

  
 return render_template('addinfo.html')



if __name__ == "__main__":
 app.run(debug=True)