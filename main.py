# Imports
import os
from flask import Flask, flash, request, redirect, render_template, send_file
from werkzeug.utils import secure_filename
from fileHandling import fileContents, writeToFile
import time
import shutil
import os
from redvid import Downloader


# Run Program
app=Flask(__name__)

# Set up file size
app.secret_key = "abc"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Set up vars
path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')
OUTPUT_FOLDER = os.path.join(path, 'output')
VIDEO_FOLDER = os.path.join(path, 'vids')
ts = ""

def genFolders():
	try:
		if not os.path.isdir(UPLOAD_FOLDER):
			os.mkdir(UPLOAD_FOLDER)

		if not os.path.isdir(OUTPUT_FOLDER):
			os.mkdir(OUTPUT_FOLDER)

		if not os.path.isdir(VIDEO_FOLDER):
			os.mkdir(VIDEO_FOLDER)
	except:
		print("File remove error")

# Set up configs
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['VIDEO_FOLDER'] = VIDEO_FOLDER

# TXT file only
ALLOWED_EXTENSIONS = set(['txt'])

# Reddit
def download(url, ts):
    try:
        reddit = Downloader(max_q=True)
        reddit.url = str(url)
        reddit.path = os.path.join(VIDEO_FOLDER, ts)
        parsed1 = reddit.url.split('comments/')
        parsed2 = parsed1[1][7:-1]
        print("filename: " + parsed2)

        reddit.download()
        os.rename(reddit.file_name,reddit.path + parsed2+'.mp4')
    except:
        print('error')

def runDownload(url, ts):
    try:
        f = open(url, "r")
        listItems = f.read().splitlines()
    except:
        print('fileread error, check permissions and make sure the file "url.txt" exists')
        exit()
    try:
        index = 0
        for index, i in enumerate(listItems): 
            download(listItems[index], ts)
    except:
        print('index error')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# HTML Page
@app.route('/')
def upload_form():
	return render_template('upload.html')

# Process file input
@app.route('/', methods=['POST'])
def upload_file():
	genFolders()
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# Make sure file exists
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		# If file is file
		if file and allowed_file(file.filename):
			# Get timestamp
			ts = str(time.time())
			# Mkdir
			video_dir = os.path.join(VIDEO_FOLDER, ts)
			os.mkdir(video_dir)
			# Set filename
			filename = secure_filename(ts)
			# Establish dir path
			path = app.config['UPLOAD_FOLDER']
			# Establish path to file
			pathToFile = os.path.join(path, filename)
			# Save the file
			file.save(pathToFile)
			# Run command for reddit
			runDownload(pathToFile, ts)
			# Zip files together
			shutil.make_archive(os.path.join(OUTPUT_FOLDER, ts), 'zip', video_dir)

			# Download file page
			return redirect('/download?filename='+ts+'.zip')
		else:
			flash('Only allowed file type is txt')
			return redirect(request.url)

@app.route("/download")
def download_page (path = None):
	filename = request.args.get('filename')
	path = os.path.join(OUTPUT_FOLDER, filename)
	return send_file(path, as_attachment=True)
 

if __name__ == "__main__":
    app.run(host = '0.0.0.0',port = 80808, debug = True, threaded=True)