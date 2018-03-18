# blockdeals

Steem based website for recording deals and bargins around the world.

## Setting up your development environment

Ensure you have python 3.6 available on your system (required for
the Steem library). If there isn't a package available for your
distro try building from source:

```
$ wget https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tgz
$ tar xvf Python-3.6.4.tgz
$ cd Python-3.6.4
$ ./configure --enable-optimizations
$ make -j8
$ sudo make altinstall
```

Now setup your environment:

```
$ virtualenv -p python3.6 venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

### Spin up a local mongodb instance

```
$ docker run -p 127.0.0.1:27017:27017 $(pwd)/db:/data/db mvertes/alpine-mongo
```
NOTE: make sure you have an entry in your `/etc/hosts` file mapping `mongodb` to
`127.0.0.1`

You can now run the app in dev mode via: `python blockdeals.py`


## Production Deployment

Simply `git push` your changes will trigger an upgrade of the
production server. To spin up a test production server run:

```
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```
