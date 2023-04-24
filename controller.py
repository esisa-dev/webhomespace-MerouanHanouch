import crypt
from pathlib import Path
import shutil
from flask import(
    Flask,
    request,
    render_template,
    redirect,
    session,
    abort,
    send_file,
    make_response
)

import os
import datetime as dt
from werkzeug.security import safe_join

app = Flask(__name__)


@app.route('/button-click', methods=['POST'])
def handle_button_click():
    button_name = request.form['button_name']
    result = ""
    if button_name == "Files":
        Fsize = os.popen(f"find {userF} -type f | wc -l").read()
        result = f"Number of files: {Fsize}"
    elif button_name == "Dirs":
        Fdirs = os.popen(f"fin {userF} -type d | wc -l").read()
        result = f"Number of directories: {Fdirs}"
    elif button_name == "Space":
        Fspace = os.popen(f"du -sh {userF}").read()
        result = f"Disk space Ocuped: {Fspace}"
    return render_template('userHome.html', result=result)

@app.route('/download_all')
def download_all():
# Path of the directory to download
    dir_path = userF

    # Create a ZIP archive of the directory
    zip_path = '/tmp/archive.zip'
    shutil.make_archive(zip_path, 'zip', dir_path)

    # Send the ZIP archive as a file attachment
    with open(zip_path, 'rb') as f:
        response = make_response(f.read())
        response.headers['Content-Type'] = 'application/zip'
        response.headers['Content-Disposition'] = 'attachment; filename=archive.zip'

    return response



def FormatTimeToString(sec : float) -> str:
    tObj = dt.datetime.fromtimestamp(sec)
    tStr = dt.datetime.strftime(tObj,"%Y-%m-%d %H:%M:%S")
    return tStr

def get_hashed_password(username):
    with open('/etc/shadow', 'r') as f:
        for line in f:
            fields = line.strip().split(':')
            if fields[0] == username:
                return fields[1]

def authenticate(username, password):
    hashed_password = get_hashed_password(username)
    if hashed_password is None:
        return False
    return crypt.crypt(password, hashed_password) == hashed_password , crypt.crypt(password, hashed_password)
                                  




@app.route('/')
def index():
    return render_template('signin.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['passwd']
    print(username,password)

    global userF
    userF = '/home/' + username

    print(authenticate(username,password))
    print(print(get_hashed_password(username)))
    if authenticate(username,password):
        return redirect('/reports/')
    else:
        return abort(404)


    


@app.route('/reports/', defaults={'reqPath':""})
@app.route('/reports/<path:reqPath>')
def user_folder(reqPath=""):

    absPath = safe_join(userF,reqPath)
    print(absPath)

    if not os.path.exists(absPath):
        print(absPath)
        print('error')
        return abort(404)
    
    if os.path.isfile(absPath):
        return send_file(absPath)

    def ObjFromScan(x):
        if os.path.isdir(x.path):
            Icon = "fa fa-folder"
        else:
            Icon = "fa fa-file-o"
        file_state = x.stat()
        file_size = file_state.st_size
        file_time = FormatTimeToString(file_state.st_mtime)
        print(x.path)
        print(userF)
        print(os.path.relpath(x.path,userF))
        return {"name":x.name, "size":file_size, "mTime":file_time, "Icon":Icon, "Flink":os.path.relpath(x.path,userF)}

    fileName = [ObjFromScan(x) for x in os.scandir(absPath)]
    parentPath = os.path.relpath(Path(absPath).parents[0],userF)
    

    return render_template('userHome.html', files=fileName, parentPath=parentPath)





if (__name__ == '__main__'):
    app.secret_key = os.urandom(12)
    app.run(host="0.0.0.0")