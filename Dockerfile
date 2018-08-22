FROM base/archlinux
ADD app.py /app.py
ADD flag.txt /flag.txt
ADD requirements.txt /requirements.txt

RUN pacman -Sy --noconfirm
RUN pacman -Su --noconfirm python-pip namcap
RUN pip install -r /requirements.txt

WORKDIR /
CMD gunicorn --bind 0.0.0.0:5000 app:app

