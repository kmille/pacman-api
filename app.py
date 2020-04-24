from flask import Flask, request, jsonify
from functools import wraps
import pacman
from os import remove, makedirs, system
from os.path import exists
from subprocess import check_output
from shlex import quote
from base64 import b64decode

app = Flask(__name__)
tmp_dir = "/tmp/pacman/" # trailing slash!
makedirs(tmp_dir, exist_ok=True)


def check_json(*params):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            system("pgrep pacman || rm /var/lib/pacman/db.lck > /dev/null 2>&1")
            if exists("/var/lib/pacman/db.lck"):
                return jsonify({'error': 'pacman currently in use'})
            if not all([p in request.get_json(force=True) for p in params]):
                return jsonify({"error": "missing parameter"}), 400
            return f(*args, **kw)
        return wrapper
    return decorator


@app.route("/info", methods=['GET', 'POST'])
@check_json('package')
def get_info():
    package = request.get_json(force=True)['package']
    return jsonify(pacman.get_info(package))


@app.route("/install", methods=['GET', 'POST'])
@check_json('package')
def install():
    package = request.get_json(force=True)['package']
    pacman.install(package)
    return jsonify({'status': 'OK'})


@app.route("/remove", methods=['GET', 'POST'])
@check_json()
def p_remove():
    pacman.remove("wget")
    return jsonify({'status': 'OK'})


@app.route("/is_installed", methods=['GET', 'POST'])
@check_json('package')
def is_installed():
    package = request.get_json(force=True)['package']
    return jsonify({'is_installed': pacman.is_installed(package)})


@app.route("/check", methods=['GET', 'POST'])
@check_json('name', 'content')
def checksum():
    f_name = request.get_json(force=True)['name']
    f_content = request.get_json(force=True)['content']
    with open(tmp_dir + f_name.replace("..", ""), "wb") as f:
        f.write(b64decode(f_content.encode()))
    stdout = check_output("/usr/bin/namcap -e checksums,filenames {}{}".format(tmp_dir, quote(f_name)), shell=True)
    remove(tmp_dir + f_name.replace("..", ""))
    return jsonify({'output': stdout.decode()})


if __name__ == '__main__':
    app.run(debug=False)
