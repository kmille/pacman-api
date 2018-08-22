from flask import Flask, request, jsonify
import pacman
from os import remove, makedirs
from os.path import exists
from subprocess import check_output
from shlex import quote
from ipdb import set_trace
from base64 import b64decode

app = Flask(__name__)
tmp_dir = "/tmp/pacman/" # trailing slash!
makedirs(tmp_dir, exist_ok=True)


@app.route("/info", methods=['GET', 'POST'])
def get_info():
    if exists("var/lib/pacman/db.lck"):
        return jsonify({'error': 'pacman currently in use'})
    package = request.get_json(force=True)['package']
    return jsonify(pacman.get_info(package))


@app.route("/install", methods=['GET', 'POST'])
def install():
    if exists("var/lib/pacman/db.lck"):
        return jsonify({'error': 'pacman currently in use'})
    package = request.get_json(force=True)['package']
    pacman.install(package)
    return jsonify({'status': 'OK'})
    

@app.route("/check", methods=['GET', 'POST'])
def checksum():
    f_name = request.get_json(force=True)['name']
    f_content = request.get_json(force=True)['content']
    with open(tmp_dir + f_name.replace("..",""), "wb") as f:
        f.write(b64decode(f_content.encode()))
    stdout = check_output("/usr/bin/namcap -e checksums,filenames {}{}".format(tmp_dir, quote(f_name)), shell=True)
    remove(tmp_dir + f_name.replace("..","")) 
    return jsonify({'output': stdout.decode()})

if __name__ == '__main__':
    app.run(debug=True)
