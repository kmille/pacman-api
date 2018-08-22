from flask import Flask, request, jsonify
import pacman


"""
import subprocess
from shlex import quote
f_name = "-h"
print(f_name)
print(quote(f_name))
with open(f_name, "w") as f:
    f.write("test")
subprocess.check_output("namcap -e checksums,filenames  {}".format(quote(f_name)), shell=True)
print("done")
#subprocess.check_output("namcap -e checksums,filenames  /etc/passwd", shell=True)
#subprocess.check_output("namcap -e checksums,filenames  hallo", shell=True)
"""

app = Flask(__name__)


@app.route("/install", methods=['GET', 'POST'])
def install():
    package = request.get_json(force=True)['package']
    return jsonify(pacman.install(package))
    

@app.route("/info", methods=['GET', 'POST'])
def get_info():
    package = request.get_json(force=True)['package']
    return jsonify(pacman.get_info(package))


@app.route("/check", methods=['GET', 'POST'])
def checksum():
    f_name = request.get_json(force=True)['name']
    f_content = request.get_json(force=True)['content']
    with open("/tmp/" + f_name.replace("..",""), "wb") as f:
        f.write(f_content.encode())
    return jsonify(pacman.get_info(package))

if __name__ == '__main__':
    app.run(debug=True)
