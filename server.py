import os
import uuid
from flask import Flask, flash, request, redirect, url_for, send_from_directory, jsonify
from flask_cors import CORS, cross_origin

from generator import generate_model, generate_n_gram, generate_rnn, save
import rnn

rnn = RNN('./01Minuetto1.mid')

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/", methods=["GET", "POST"])
def serve_root():
    if request.method == "POST":
        if 'algo' not in request.form:
            return redirect(request.url)

        if request.form['algo'] == 'n_gram':
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
                file_id = str(uuid.uuid4())
                filename = file_id + '.mid'
                path = os.path.join('./uploads', file_id + '.mid')
                output = os.path.join('./uploads', file_id + '_out.mid')
                info = os.path.join('./uploads', file_id + '.info')
                file.save(path)
                with open(info, 'w') as info_file:
                    info_file.write(file.filename[:-4])

                encoded_midi = EncodedMidi(path)
                model = generate_model(encoded_midi.encoding)
                song = generate_n_gram(model)
                save(song, encoded_midi.ticks_per_beat, output)
                return redirect("https://mg.pantherman594.com/uploaded?file=" + file_id)
            else:
                return redirect(request.url)
        elif request.form['algo'] == 'rnn':
            file_id = str(uuid.uuid4())
            filename = file_id + '.mid'
            path = os.path.join('./uploads', file_id + '.mid')
            output = os.path.join('./uploads', file_id + '_out.mid')
            info = os.path.join('./uploads', file_id + '.info')
            file.save(path)
            with open(info, 'w') as info_file:
                info_file.write('Neural Network Sample')

            song = generate_rnn(rnn)
            save(song, rnn.midi.ticks_per_beat, output)
            return redirect("https://mg.pantherman594.com/uploaded?file=" + file_id)
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
        <form id="form" method="post" enctype="multipart/form-data">
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
            document.getElementById("form").onsubmit = function(event) {
                document.getElementById("submitText").innerHTML = "Uploading...";
            };
        </script>
        """

@app.route("/list")
@cross_origin()
def serve_list():
    files = {}
    for file in os.listdir('./uploads'):
        if not file.endswith('.info'):
            continue
        file_id = file[:-5]
        info = os.path.join('./uploads', file)
        with open(info, 'r') as info_file:
            for line in info_file:
                files[file_id] = line
                break
    return jsonify(files)


@app.route("/uploaded")
def serve_updated():
    if 'file' not in request.args:
        return redirect('https://mg.pantherman594.com/')
    download_url = 'https://mg.pantherman594.com/uploads/' + request.args['file'] + '_out.mid'
    return "<span style=\"display:inline-block;width:100%;text-align:center;font:normal normal normal 14px/1.4em avenir-lt-w01_35-light1475496,sans-serif;\">Your file has been processed!<br /><a href=\"" + download_url + "\">Download</a></span>"

@app.route("/uploads/<path:filename>")
def serve_output(filename):
    if not filename.endswith('.mid'):
        return redirect('https://mg.pantherman594.com/')
    return send_from_directory('uploads', filename)

