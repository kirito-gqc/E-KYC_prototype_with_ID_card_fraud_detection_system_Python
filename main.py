# -Programmer Name: Gan Qian Chao TP055444
# -Program Name : Flask main function (IDFD System + eKYC prototype functions)
# -Description : Use for running flask application and perform functionality in the application
# -First Written on: 20 Feb 2023
# -Editted on: 16 April 2023

from flask import Flask,render_template, request, redirect, flash, session
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import numpy as np
from werkzeug.utils import secure_filename
import os
import shutil
import random
from preprocess import check_bad_quality
from graphical_landmark_processing import detect_landmarks,get_related_files,classify_landmark,match_face
from textual_landmark_processing import text_verification
from datetime import datetime,date

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
 
app = Flask(__name__, static_url_path='/static')
#secret key
app.secret_key = "kirito_asuna"
#SQL config 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ekyc'
#Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'qianchaogan@gmail.com'
app.config['MAIL_PASSWORD'] = 'kghwnhbconpikpdf'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


#Allow jpg, jpeg and png only
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#connect mysql
mysql = MySQL(app)
#connect Mail
mail = Mail(app)
UPLOAD_FOLDER = 'static/uploads'
login_attempt = 5
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#home page
@app.route('/')
def home():
    return render_template('home.html')

#user login
@app.route('/user')
def user():
    if 'account' not in session:
        return render_template('user_login.html')
    elif 'loginsession' in session:
        return render_template('user_login.html')
    else:
        print('wrong')
        session.clear()
        return render_template('user_login.html')

#admin login
@app.route('/admin')
def admin():
    if 'account' not in session:
        return render_template('admin_login.html')
    else:
        session.clear()
        return render_template('admin_login.html')

@app.route('/logout')
def logout():
   # Remove session data, this will log the user out
   session.clear()
   # Redirect to login page
   return render_template('home.html')

#account_register(Register Step 1)
@app.route('/account', methods =  ['POST', 'GET'])
def account():
    #redirect to account_register.html
    if request.method == 'GET':
        if 'account' not in session:
            return render_template('account_register.html')
        else:
            account = session['account']
            account_list = account['account']
            username = account_list[0]
            email = account_list[1]
            password = account_list[2]
            return render_template('account_register.html', username = username, email = email, password = password)
    #check register account detail
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        # Check if username and email exists using MySQL
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
        username_exist = cursor.fetchone()
        mysql.connection.commit()
        cursor.execute('SELECT * FROM account WHERE email = %s', (email,))
        email_exist = cursor.fetchone()
        mysql.connection.commit()
        cursor.close()
        if username_exist:
            flash("Existing username is found! Please use another username.")
            return redirect(request.url)
        if email_exist:
            flash('Existing email is found! Please use another email.')
            return redirect(request.url)        
        if (password == cpassword):
            account_dict = {}
            account_dict['account'] = [username,email,password]  
            if 'account' not in session:
                session['account'] = account_dict   
                return render_template('id_register.html')
            else:
                account = session['account']
                account.update(account_dict)
                session['account'] = account
                if 'id' in account:
                    id_list = account['id']
                    surname = id_list[0]
                    given_name = id_list[1]
                    id_num = id_list[2]
                    gender = id_list[3]
                    birth_date = id_list[4]
                    granted_date = id_list[5]
                    expired_date = id_list[6]
                    area_code = id_list[7]
                    return render_template('id_register.html', surname = surname, given_name = given_name, id_num = id_num, gender = gender, birth_date = birth_date, granted_date = granted_date, expired_date = expired_date, area_code = area_code)
                else:
                    return render_template('id_register.html')
            
        else:
            flash("Password not matched")
            return redirect(request.url)
def get_account():
    return account()

#id_register(Register Step 2)        
@app.route('/register', methods =  ['POST', 'GET'])
def register():
    #get to id_register.html
    if request.method == 'GET':
        if 'account' not in session:
            flash('Please do the step 1 before doing step 2')
            return render_template('account_register.html')
        else:
            account = session['account']
            if 'id' in account:
                id_list = account['id']
                surname = id_list[0]
                given_name = id_list[1]
                id_num = id_list[2]
                gender = id_list[3]
                birth_date = id_list[4]
                granted_date = id_list[5]
                expired_date = id_list[6]
                area_code = id_list[7]
                print(account)
                return render_template('id_register.html', surname = surname, given_name = given_name, id_num = id_num, gender = gender, birth_date = birth_date, granted_date = granted_date, expired_date = expired_date, area_code = area_code)
            else:
                print(account)
                print('wrong')
                return render_template('id_register.html')
    #register entered id details
    if request.method == 'POST':
        surname = request.form['surname']
        given_name = request.form['given_name']
        id_num = request.form['id_num']
        gender = request.form['gender']
        birth_date = request.form['birth_date']
        granted_date = request.form['granted_date']
        expired_date = request.form['expired_date']
        area_code = request.form['area_code']
        id_dict = {}
        id_dict['id'] = [surname, given_name, id_num, gender, birth_date, granted_date, expired_date,area_code]
        if 'account' not in session:
            flash('Please do the step 1 before doing step 2')
            return render_template('account_register.html')
        else:
            #Check id number existing
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM user WHERE id_num = %s', (id_num,))
            id_exist = cursor.fetchone()
            mysql.connection.commit()
            if id_exist:
                flash('The information entered for ID card already registered! Please register with a new ID card.')
                return redirect(request.url)
            #Record id details and proceed to card_img_register.html
            account = session['account']
            account.update(id_dict)
            session['account'] = account
            return render_template('card_img_register.html')

#Login function (User)
@app.route('/user/login', methods = ['POST', 'GET'])
def user_login():
    if request.method == 'POST':
        if 'loginsession' not in session:
            session['loginsession'] = 0
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM account WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # print(account)
        mysql.connection.commit()
        cursor.close()
        # If account exists in accounts table in out database
        if account:
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            id = account[0]
            email = account[2]
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT block_time FROM block WHERE account_id = %s ORDER BY block_time DESC LIMIT 1', (id,))
            # Fetch one record and return result
            if cursor.rowcount > 0:
                block = cursor.fetchone()
            else:
                block = False
            # print(account)
            mysql.connection.commit()
            cursor.close() 
            #get current time
            if block:
                block_time = block[0]
                current_dt = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
                # block_dt = datetime.strptime(block_time, "%Y-%m-%d %H:%M:%S")
                time_pass = current_dt-block_time
                total_seconds = time_pass.total_seconds()
                print("Time passed:", time_pass)
                if total_seconds < 600:
                    left_time = 600-total_seconds
                    # calculate the number of minutes and seconds
                    minutes, seconds = divmod(int(left_time), 60)
                    flash('This account is blocked due to the login attempt is used out. Please wait for '+str(minutes)+ ' minute(s) and '+str(seconds)+' second(s)')
                    return render_template('user_login.html')
                else:
                    # Create session data, we can access this data in other routes
                    session['loggedin'] = True
                    session['id'] = account[0]
                    session['username'] = account[1]
                    session['email'] = account[2]
                    return render_template('user_upload.html',username = username)
            else:
                 # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[1]
                session['email'] = account[2]              
                return render_template('user_upload.html',username = username)    
        else:                
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password!')
            return render_template('user_login.html')

@app.route('/user/upload', methods = ['POST', 'GET'])
def upload_verify():
    username = session['username']
    if request.method == 'GET':
        if 'loggedin' not in session:
            flash('Please do login process before upload image')
            return render_template('user_login.html')
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file is uploaded')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Filename is empty')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            id = session['id']
            filename = secure_filename(file.filename)
            temp_file = os.path.join(app.config['UPLOAD_FOLDER'],'temp', filename)
            file.save(temp_file)
            #Bad quality image detection (glare, blur, tilt)
            blur,glare,tilt = check_bad_quality(temp_file)
            if blur==1:
                flash("Image is blur")
                os.remove(temp_file)
                return redirect(request.url)
            elif glare==1:
                flash("Image is glare")
                os.remove(temp_file)
                return redirect(request.url)
            elif tilt ==1:
                flash("Image is tilt")
                os.remove(temp_file)
                return redirect(request.url)
            else:
                idfd = request.form['idfd']
                if idfd == "Yes":
                    session['verify'] = filename 
                    return render_template('idfd_verification.html', image_name = filename, result = '')

                else:
                    file_path = temp_file
                    registered_path = os.path.join(app.config['UPLOAD_FOLDER'], username)
                    registered = os.listdir(registered_path)[0]
                    registered_filename = os.path.join(registered_path, registered)
                    #detect landmark in card(must have face, face_landmark_1, face_landmark_2 and signature)
                    myresult,replace = detect_landmarks(file_path)
                    required_keys = [0, 1, 2, 3]
                    label = ['face','face_landmark_1','face_landmark_2','signature']
                    for key in required_keys:
                        if key not in myresult:
                            missing = label[key]
                            os.remove(file_path)
                            flash(f"Error: {missing} is missing from the result. Please reupload another image")
                            return render_template('user_upload.html',username=username)
                    else:
                        #Landmark classification (Identify fraud)
                        prediction,landmark = get_related_files(file_path,replace)
                        face_fraud, landmark_1_fraud, landmark_2_fraud, signature_fraud = classify_landmark(landmark)
                        if any([face_fraud, landmark_1_fraud, landmark_2_fraud, signature_fraud]):
                            fraud_verification = False
                        else:
                            fraud_verification = True
                        #face_matching    
                        match = match_face(registered_filename, landmark)
                        cursor = mysql.connection.cursor()
                        cursor.execute('SELECT surname,given_name,id_num,gender, birth_date, granted_date, expired_date, area_code FROM user WHERE account_id = %s', (id,))
                        # Fetch one record and return result
                        id_detail = cursor.fetchone()
                        mysql.connection.commit()
                        cursor.close()
                        id_list = []
                        for element in id_detail:
                            if isinstance(element, date):
                                id_list.append(element.strftime('%Y-%m-%d'))
                            else:
                                id_list.append(str(element))
                        #text verification
                        surname_fraud, given_name_fraud, id_num_fraud, birth_date_fraud, granted_date_fraud, expired_date_fraud, area_code_fraud = text_verification(file_path,id_list)
                        if not all ([surname_fraud, given_name_fraud, id_num_fraud, birth_date_fraud, granted_date_fraud, expired_date_fraud, area_code_fraud]):
                            verification_text = False
                        else:
                            verification_text = True
                        #All verification must be True
                        if not all ([fraud_verification,match,verification_text]):
                            session['verification'] = 'fail'
                        else:
                            session['verification'] = 'pass'    
                            
                    #verification start        
                    verification = session['verification']
                    id = session['id']
                    email = session['email']
                    if verification == 'pass':                
                        os.remove(temp_file)
                        #generate otp randomly
                        otp = generate_otp()
                        session['otp'] = otp
                        #send smtp email
                        msg = Message('IDFD OTP Verification', sender='qianchaogan@gmail.com', recipients=[email])
                        msg.body = "Hi user " +username+ "! Your OTP for this login attempt is: " + otp
                        mail.send(msg)
                        flash('IDFD verification passed, an otp had been sent to your registered email: '+ email)
                        return render_template('otp_login.html')
                    else:
                        os.remove(temp_file)
                        #record access attempt, if pass 5 times, block access
                        session['loginsession']+=1
                        session.pop('verification', None)
                        left_attempt = login_attempt - session['loginsession']
                        if left_attempt > 1:
                            flash('IDFD verification failed! You still have '+str(left_attempt)+' attempt(s)')
                            return render_template('user_upload.html',username= username)
                        elif left_attempt == 1:
                            flash('IDFD verification failed! This is your last attempt, the account will be block for 10 minutes if used out login attempt')
                            return render_template('user_upload.html',username= username)
                        else:
                            now = datetime.now()
                            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
                            cursor = mysql.connection.cursor()
                            cursor.execute("INSERT INTO block (block_time, account_id) VALUES(%s,%s)",[current_time,id])
                            mysql.connection.commit()    
                            msg = Message('Blocked Account', sender='qianchaogan@gmail.com', recipients=[email])
                            msg.body = "Hi user " +username+ "! The IDFD system in eKYC website had detected your account contains multiple fail access due to possible fraud detected or other suspicious activities in eKYC login process.\nYour account will be block for 10 minutes starting from "+current_time+ ".Please contact our administrator at qianchaogan@gmail.com if there is any query about the eKYC process. Thanks for your consideration" 
                            mail.send(msg)
                            flash('This account is blocked due to the login attempt is used out. Please wait for 10 minutes to able to reaccess the account') 
                            session.clear()
                            return render_template('user_login.html')    
                        
        else:
            #If not upload image, sent error message
            flash('Please submit image in jpg, jpeg and png')
            return redirect(request.url)    

    # If no valid image file was uploaded, show the file upload form:
    return render_template('user_upload.html', username = username)

#generate otp function
def generate_otp():
    final_otp = ''
    otp_size = 6
    for i in range(otp_size):
        final_otp = final_otp + str(random.randint(0,9))
    return final_otp

#IDFD verification process (IDFD verification login process)
@app.route('/user/verify', methods = ['POST','GET'])
def verify():
    #redirect to idfd_verification.html
    if request.method == 'GET':
        if 'verify' not in session:
            flash('Please restart the process from login account')
            return render_template('user_login.html')
        else:
            id = session['id']
            card = session['verify']
            username = session['username']
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp',secure_filename(card))
            registered_path = os.path.join(app.config['UPLOAD_FOLDER'], username)
            registered = os.listdir(registered_path)[0]
            registered_filename = os.path.join(registered_path, registered)
            #start verification
            myresult,replace = detect_landmarks(file_path)
            required_keys = [0, 1, 2, 3]
            label = ['face','face_landmark_1','face_landmark_2','signature']
            for key in required_keys:
                if key not in myresult:
                    missing = label[key]
                    os.remove(file_path)
                    flash(f"Error: {missing} is missing from myresult")
                    return render_template('user_upload.html',username=username)
            else:
                face = myresult[0]
                landmark_1 = myresult[1]
                landmark_2 = myresult[2]
                signature = myresult[3]
                prediction,landmark = get_related_files(file_path,replace)
                predict_folder = prediction.split('\\')[-1]
                face_fraud, landmark_1_fraud, landmark_2_fraud, signature_fraud = classify_landmark(landmark)
                if any([face_fraud, landmark_1_fraud, landmark_2_fraud, signature_fraud]):
                    fraud_verification = False
                else:
                    fraud_verification = True
                #face matching    
                match = match_face(registered_filename, landmark)
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT surname,given_name,id_num,gender, birth_date, granted_date, expired_date, area_code FROM user WHERE account_id = %s', (id,))
                # Fetch one record and return result
                id_detail = cursor.fetchone()
                mysql.connection.commit()
                cursor.close()
                # convert the first two elements to uppercase
                id_list = []
                for element in id_detail:
                    if isinstance(element, date):
                        id_list.append(element.strftime('%Y-%m-%d'))
                    else:
                        id_list.append(str(element))
        
                surname_fraud, given_name_fraud, id_num_fraud, birth_date_fraud, granted_date_fraud, expired_date_fraud, area_code_fraud = text_verification(file_path,id_list)
                if not all ([surname_fraud, given_name_fraud, id_num_fraud, birth_date_fraud, granted_date_fraud, expired_date_fraud, area_code_fraud]):
                    verification_text = False
                else:
                    verification_text = True
                if not all ([fraud_verification,match,verification_text]):
                        session['verification'] = 'fail'
                else:
                    session['verification'] = 'pass'
                #view result of IDFD verification
                return render_template('idfd_verification.html', image_name = card, result = predict_folder, face = face, landmark_1 = landmark_1,
                                       landmark_2 = landmark_2, signature = signature, face_fraud = face_fraud, landmark_1_fraud = landmark_1_fraud,
                                       landmark_2_fraud = landmark_2_fraud, signature_fraud = signature_fraud,face_match = match, surname_fraud = surname_fraud,
                                       given_name_fraud = given_name_fraud, id_num_fraud = id_num_fraud, birth_date_fraud = birth_date_fraud,
                                       granted_date_fraud = granted_date_fraud,expired_date_fraud = expired_date_fraud, area_code_fraud = area_code_fraud)       
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'verification' not in session:
            flash('Please start IDFD before continue')
            card = session['verify']
            return render_template('idfd_verification.html',image_name = card, result = '')
        else:
            verification = session['verification']
            card = session['verify']
            username = session['username']
            temp_file = os.path.join(app.config['UPLOAD_FOLDER'],'temp', secure_filename(card))
            if verification == 'pass':
                os.remove(temp_file)
                email = session['email']
                username = session['username']
                otp = generate_otp()
                session['otp'] = otp
                msg = Message('IDFD OTP Verification', sender='qianchaogan@gmail.com', recipients=[email])
                msg.body = "Hi user " +username+ "! Your OTP for this login attempt is: " + otp
                mail.send(msg)
                flash('IDFD verification passed, an otp had been sent to your registered email: '+ email)
                return render_template('otp_login.html')
            else:
                os.remove(temp_file)
                session['loginsession']+=1
                session.pop('verification',None)
                left_attempt = login_attempt - session['loginsession']
                if left_attempt > 1:
                    flash('IDFD verification failed! You still have '+str(left_attempt)+' attempt(s)')
                    return render_template('user_upload.html',username= username)
                elif left_attempt == 1:
                    flash('IDFD verification failed! This is your last attempt, the account will be block for 10 minutes if used out login attempt')
                    return render_template('user_upload.html',username= username)
                else:
                    id = session['id']
                    username = session['username']
                    now = datetime.now()
                    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
                    cursor = mysql.connection.cursor()
                    cursor.execute("INSERT INTO block (block_time, account_id) VALUES(%s,%s)",[current_time,id])
                    mysql.connection.commit()    
                    msg = Message('Blocked Account', sender='qianchaogan@gmail.com', recipients=[email])
                    msg.body = "Hi user " +username+ "! The IDFD system in eKYC website had detected your account contains multiple fail access due to possible fraud detected or other suspicious activities in eKYC login process.\nYour account will be block for 10 minutes starting from "+current_time+ ".Please contact our administrator at qianchaogan@gmail.com if there is any query about the eKYC process. Thanks for your consideration" 
                    mail.send(msg)
                    session.clear()
                    flash('This account is blocked due to the login attempt is used out. Please wait for 10 minutes to able to reaccess the account') 
                    return render_template('user_login.html')  
                
#OTP verification process (IDFD login process step 3)            
@app.route('/user/otp', methods = ['POST', 'GET'])
def otp():
    if request.method == 'GET':
        if 'loggedin' not in session:
            flash('Please login before get otp')
            return render_template('user_login.html')
    #sent otp email and record access
    if request.method == 'POST':
        otp = request.form['otp']
        if 'otp' in session and session['otp'] == otp:
            del session['otp']
            username = session['username']
            id = session['id']
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO access (access_time, account_id) VALUES(%s,%s)",[current_time,id])
            mysql.connection.commit()
            flash('OTP verified. Welcome to eKYC account, user '+username)
            return render_template('user_index.html', username = username)
        
        else:
            #Block access after 5 time fail access. 
            session['loginsession']+=1
            left_attempt = login_attempt - session['loginsession']
            if left_attempt > 1:
                flash('Incorrect otp! You still have '+str(left_attempt)+' attempt(s)')
                return render_template('otp_login.html')
            elif left_attempt == 1:
                flash('Incorrect otp! This is your last attempt, the account will be block for 10 minutes if used out login attempt')
                return render_template('otp_login.html')
            else:
                id = session['id']
                username = session['username']
                email = session['email']
                now = datetime.now()
                current_time = now.strftime("%Y-%m-%d %H:%M:%S")
                cursor = mysql.connection.cursor()
                cursor.execute("INSERT INTO block (block_time, account_id) VALUES(%s,%s)",[current_time,id])
                mysql.connection.commit()    
                msg = Message('Blocked Account', sender='qianchaogan@gmail.com', recipients=[email])
                msg.body = "Hi user " +username+ "! The IDFD system in eKYC website had detected your account contains multiple fail access due to possible fraud detected or other suspicious activities in eKYC login process.\nYour account will be block for 10 minutes starting from "+current_time+ ".Please contact our administrator at qianchaogan@gmail.com if there is any query about the eKYC process. Thanks for your consideration" 
                mail.send(msg)
                session.clear()                
                flash('This account is blocked due to the login attempt is used out. Please wait for 10 minutes to able to reaccess the account') 
                return render_template('user_login.html')      
    
#Login function (Admin)
@app.route('/admin/login', methods = ['POST', 'GET'])
def admin_login():
    if request.method =='GET':
        if 'loggedin' not in session:
            flash("You have not login to the admin account")
            return render_template('home.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # print(account)
        mysql.connection.commit()
        cursor.close()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            username = session['username']
            flash('Logged in successfully')
            # Redirect to home page
            return render_template('admin_index.html',username = username)
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password!')
            return render_template('admin_login.html')


#ID image registration (Step 3)+bad_quality removal+ fraud_graphical_landmark_detection + text_verification
@app.route('/id', methods = ['POST', 'GET'])
def upload_image():
    if request.method == 'GET':
        if 'account' not in session:
            flash('Please do the step 1 before doing step 3')
            return render_template('account_register.html')
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file is uploaded')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Filename is empty')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temp_file = os.path.join(app.config['UPLOAD_FOLDER'],'temp', filename)
            file.save(temp_file)
            blur,glare,tilt = check_bad_quality(temp_file)
            if blur==1:
                flash("Image is blur")
                os.remove(temp_file)
                return redirect(request.url)
            elif glare==1:
                flash("Image is glare")
                os.remove(temp_file)
                return redirect(request.url)
            elif tilt ==1:
                flash("Image is tilt")
                os.remove(temp_file)
                return redirect(request.url)
            else:
                idfd = request.form['idfd']
                if idfd == "Yes":
                    card_dict = {}
                    card_dict['card'] = filename
                    if 'account' not in session:
                        session['account'] = card_dict   
                        return render_template('idfd_process.html', image_name = filename, result = '')
                    else:
                        account = session['account']
                        account.update(card_dict)
                        session['account'] = account
                        return render_template('idfd_process.html',image_name = filename, result = '')
                    
                    # os.remove(temp_file)
                else:
                    account = session['account']
                    file_path = temp_file
                    myresult,replace = detect_landmarks(file_path)
                    required_keys = [0, 1, 2, 3]
                    label = ['face','face_landmark_1','face_landmark_2','signature']
                    for key in required_keys:
                        if key not in myresult:
                            missing = label[key]
                            os.remove(file_path)
                            flash(f"Error: {missing} is missing from myresult")
                            return redirect(request.url)
                    else:
                        prediction,landmark = get_related_files(file_path,replace)
                        face_fraud, landmark_1_fraud, landmark_2_fraud, signature_fraud = classify_landmark(landmark)
                        if any([face_fraud, landmark_1_fraud, landmark_2_fraud, signature_fraud]):
                            fraud_verification = False
                        else:
                            fraud_verification = True
                        id = account['id'].copy()
                        surname_found, given_name_found, id_num_found, birth_date_found, granted_date_found, expired_date_found, area_code_found = text_verification(file_path,id)
                        if not all ([surname_found, given_name_found, id_num_found, birth_date_found, granted_date_found, expired_date_found, area_code_found]):
                            verification_text = False
                        else:
                            verification_text = True
                        if not all ([fraud_verification,verification_text]):
                            session['verification'] = 'fail'
                        else:
                            session['verification'] = 'pass'    
                            
                    #verification start        
                    verification = session['verification']
                    if verification == 'pass':                
                        account_list = account['account']
                        id_list = account['id']
                        username = account_list[0]
                        user_folder = os.path.join(app.config['UPLOAD_FOLDER'],username)
                        if not os.path.exists(user_folder):
                            os.makedirs(user_folder)
                        else:
                            os.remove(temp_file)
                            flash("Register fail as you had used the existing username")
                            return redirect("/account",code=302) 
                        cursor = mysql.connection.cursor()
                        cursor.execute("INSERT INTO account (username, email, password) VALUES(%s,%s,%s)",account_list)
                        mysql.connection.commit()
                        # Retrieve the username of the inserted row
                        cursor.execute("SELECT LAST_INSERT_ID()")
                        account_id = cursor.fetchone()[0]
                        id_list.append(account_id)
                        cursor.execute("INSERT INTO user (surname, given_name, id_num, gender, birth_date, granted_date, expired_date, area_code, account_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",id_list)
                        cursor.execute("INSERT INTO id_card (img_name, account_id) VALUES (%s,%s)", [filename,account_id])
                        mysql.connection.commit()
                        cursor.close()
                        shutil.move(temp_file,os.path.join(user_folder, filename))
                        session.clear()
                        flash("Register successfully")
                        return render_template('user_login.html')
                    else:
                        os.remove(temp_file)
                        flash("Register fail due to the id verification not pass. Please check again your id and information given")
                        session.pop('verification',None)
                        return redirect("/account",code=302) 
                        
        else:
            flash('Please submit image in jpg, jpeg and png')
            return redirect(request.url)

    

    # If no valid image file was uploaded, show the file upload form:
    return render_template('card_img_register.html')

#IDFD register process (Step 3)
@app.route('/idfd', methods = ['POST','GET'])
def verification():
    if request.method == 'GET':
        if 'account' not in session:
            flash('Please do the step 1 before start IDFD')
            return render_template('account_register.html')
        else:
            account = session['account']
            card = account['card']
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp',secure_filename(card))
            myresult,replace = detect_landmarks(file_path)
            required_keys = [0, 1, 2, 3]
            label = ['face','face_landmark_1','face_landmark_2','signature']
            for key in required_keys:
                if key not in myresult:
                    missing = label[key]
                    os.remove(file_path)
                    flash(f"Error: {missing} is missing from myresult")
                    return render_template('card_img_register.html')
            else:
                face = myresult[0]
                landmark_1 = myresult[1]
                landmark_2 = myresult[2]
                signature = myresult[3]
                prediction,landmark = get_related_files(file_path,replace)
                predict_folder = prediction.split('\\')[-1]
                face_fraud, landmark_1_fraud, landmark_2_fraud, signature_fraud = classify_landmark(landmark)
                if any([face_fraud, landmark_1_fraud, landmark_2_fraud, signature_fraud]):
                    fraud_verification = False
                else:
                    fraud_verification = True
                id = account['id'].copy()
                surname_found, given_name_found, id_num_found, birth_date_found, granted_date_found, expired_date_found, area_code_found = text_verification(file_path,id)
                if not all ([surname_found, given_name_found, id_num_found, birth_date_found, granted_date_found, expired_date_found, area_code_found]):
                    verification_text = False
                else:
                    verification_text = True
                if not all ([fraud_verification,verification_text]):
                    session['verification'] = 'fail'
                else:
                    session['verification'] = 'pass'
                return render_template('idfd_process.html', image_name = card, result = predict_folder, face = face, landmark_1 = landmark_1,
                                    landmark_2 = landmark_2, signature = signature, face_fraud = face_fraud, landmark_1_fraud = landmark_1_fraud,
                                    landmark_2_fraud = landmark_2_fraud, signature_fraud = signature_fraud, surname_found = surname_found,
                                    given_name_found = given_name_found, id_num_found = id_num_found, birth_date_found = birth_date_found,
                                    granted_date_found = granted_date_found, expired_date_found = expired_date_found, area_code_found = area_code_found )       
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'verification' not in session:
            flash('Please start IDFD before continue')
            account = session['account']
            card = account['card']
            return render_template('idfd_process.html',image_name = card, result = '')
        else:
            verification = session['verification']
            account = session['account']
            filename = account['card']
            if verification == 'pass':
                account_list = account['account']
                id_list = account['id']
                username = account_list[0]
                temp_file = os.path.join(app.config['UPLOAD_FOLDER'],'temp', filename)
                user_folder = os.path.join(app.config['UPLOAD_FOLDER'],username)
                if not os.path.exists(user_folder):
                    os.makedirs(user_folder)
                else:
                    os.remove(temp_file)
                    flash("Register fail as you had used the existing username")
                    return redirect("/account",code=302) 
                cursor = mysql.connection.cursor()
                cursor.execute("INSERT INTO account (username, email, password) VALUES(%s,%s,%s)",account_list)
                mysql.connection.commit()
                # Retrieve the username of the inserted row
                cursor.execute("SELECT LAST_INSERT_ID()")
                account_id = cursor.fetchone()[0]
                id_list.append(account_id)
                cursor.execute("INSERT INTO user (surname, given_name, id_num, gender, birth_date, granted_date, expired_date, area_code, account_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",id_list)
                cursor.execute("INSERT INTO id_card (img_name, account_id) VALUES (%s,%s)", [filename,account_id])
                mysql.connection.commit()
                cursor.close()
                shutil.move(temp_file,os.path.join(user_folder, filename))
                session.clear()
                flash("Register successfully")
                return render_template('user_login.html')
            else:
                temp_file = os.path.join(app.config['UPLOAD_FOLDER'],'temp', filename)
                os.remove(temp_file)
                flash("Register fail due to the id verification not pass. Please check again your id and information given")
                session.pop('verification',None)
                return redirect("/account",code=302)              

#view access record(Admin)
@app.route('/access', methods = ['POST','GET'])
def access():
    if request.method == 'GET':
        if 'loggedin' not in session:
            flash("You have not login to the admin account")
            return render_template('home.html')
        else:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT access_id, username, email, access_time FROM account INNER JOIN access ON account.account_id= access.account_id" )
            data = cursor.fetchall()
            mysql.connection.commit() 
            cursor.close()           
            return render_template('eKYC_access.html',data=data)
    if request.method == 'POST':
        search = request.form['search']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT access_id, username, email, access_time FROM account INNER JOIN access ON account.account_id= access.account_id WHERE username LIKE %s OR email LIKE %s OR access_time LIKE %s", ("%"+search+"%","%"+search+"%","%"+search+"%",))
        data = cursor.fetchall()
        mysql.connection.commit()
        return render_template('eKYC_access.html',data=data)         

#Run system    
if __name__ == '__main__':           
    app.run(host='localhost', port=5000, debug=True)