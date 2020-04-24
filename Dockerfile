FROM archlinux/base
ADD app.py /app.py
ADD flag.txt /flag.txt
ADD requirements.txt /requirements.txt

# update the system
RUN pacman -Suy --noconfirm --overwrite '*'

RUN pacman -S --noconfirm grep procps-ng namcap python-virtualenv python-pip
RUN virtualenv -p python3 /venv
RUN source /venv/bin/activate && pip install -r /requirements.txt

WORKDIR /
CMD /venv/bin/gunicorn --bind 0.0.0.0:5000 app:app

