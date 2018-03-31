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

#### Create the container and update hosts file

```
$ docker create -p 127.0.0.1:27017:27017 -v $(pwd)/db:/data/db --name mongo mvertes/alpine-mongo
```

**NOTE:** make sure you have an entry in your `/etc/hosts` file mapping `mongodb` to
`127.0.0.1`:

```
$ sudo -s
# echo "127.0.0.1 mongodb" >> /etc/hosts
```

#### Start mongo

```
$ docker start mongo
```

Create a config file:

```
$ cat blockdeals.org
STEEM_USER="steem_account_to_post_as"
POSTING_KEY="posting_key_of_blockdeals"
ACTIVE_KEY="active_posting_key_of_blockdeals"
```

You can now run the app in dev mode via:

```
$ BLOCKDEALS_SETTINGS="$(pwd)/blockdeals.cfg" UNLOCK="blockdeals" python blockdeals.py
```

## Production Deployment

To spin up a test production server run:

```
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

You should definitely run this and test your changes before committing or
pushing your changes.  A `git push` will trigger an upgrade of the server.

## Setting your account up to allow blockdeals to post on your behalf

Launch the `cli_wallet`:

```
$ docker run --rm -it steemit/steem /usr/local/steemd-default/bin/cli_wallet -s wss://rpc.buildteam.io
```

Now enable `blockdeals` to have posting permissions on your account:

```
>>> set_password pass
>>> unlock pass
>>> import_key 5H.... your_active_key ...E
>>> list_my_accounts
>>> update_account_auth_account "youraccount" "posting" "blockdeals" 1 true
>>> update_account_auth_account "youraccount" "posting" "blockdeals" 0 true
```

The `update_account_auth_account` with `1` adds and the one with `0` removes
