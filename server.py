import os
import uuid

from generator import generate_model, generate_new, save
from flask import Flask, flash, request, redirect, url_for
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def serveRoot():
    if request.method == "POST":
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and file.filename.endswith('.mid'):
            fileId = str(uuid.uuid4())
            filename = fileId + '.mid'
            path = os.path.join('./uploads', fileId + '.mid')
            output = os.path.join('./uploads', fileId + '_out.mid')
            file.save(path)

            model = generate_model(path)
            song = generate_new(model)
            save(song, output)
            return redirect("/uploaded?file=" + fileId)
    else:
        return """<style>
            body {
                font: normal normal normal 14px/1.4em avenir-lt-w01_35-light1475496,sans-serif;
                text-align: center;
            }
            #upload, #submit {
                display: none;
            }
            .button {
                padding: 10 40px;
                border: 2px solid rgba(145, 145, 145, 1);
                color: #919191;
                display: inline-block;
                cursor: pointer;
                transition: 0.3s;
            }
            .button:hover {
                color: #ffffff;
                background: rgba(145, 145, 145, 1);
            }
            .button.disabled {
                color: #ffffff;
                background: rgba(145, 145, 145, 1);
                pointer-events: none;
                cursor: initial;
            }
            #selectedFile {
                display: inline-block;
                padding: 10px 0;
            }
        </style>
        <form method="post" enctype="multipart/form-data">
            <label id="uploadLabel" class="button">
                <input id="upload" accept=".mid" type="file" name="file">
                <span id="uploadText">Select File</span><br />
            </label><br />
            <span id="selectedFile">Please select a file to process.</span><br />
            <label id="submitLabel" class="button disabled">
                <input id="submit" type="submit" value="Process">
                <span id="submitText">Process</span><br />
            </label>
        </form>
        <script>
            document.getElementById("upload").onchange = function(event) {
                let files = document.getElementById("upload").files;
                let fileName = "Please select a file to process.";
                if (files.length > 0) {
                    fileName = document.getElementById("upload").files[0].name;
                    document.getElementById("selectedFile").textContent = fileName;
                    document.getElementById("submitLabel").classList.remove("disabled");
                } else {
                    document.getElementById("submitLabel").classList.add("disabled");
                }
            };
        </script>
        """

@app.route("/uploaded")
def serveUpdated():
    return "<span style=\"display:inline-block;width:100%;text-align:center;font:normal normal normal 14px/1.4em avenir-lt-w01_35-light1475496,sans-serif;\">Your file has been uploaded!</span>"