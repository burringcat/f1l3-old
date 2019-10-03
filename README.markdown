# F1L3  
## Introduction
F1L3 is a server-side encrypted file hosting service, it uses AES-256-CBC to encrypt your files on the server storage, and the server(gunicorn) connects to its reversed proxy using https(usually).  

The generated URL includes the encryption key.  
This is *NOT* a strong encryption and *DON'T* upload your secret files if you don't trust the owner of the server, the server owner can just print the keys out, but F1L3 doesn't require JavaScript or anything bloated on the client side. If you need an end-to-end encrypted file hosting server, check [lufi](https://framagit.org/luc/lufi).  

Choose wisely! :^)

## Demo
A demo site is available at [f.odinfinch.xyz](https://f.odinfinch.xyz).
You can upload your file directly (check the site to see how long your files will be kept):
```
curl -F'file=@yourfile.png' https://f.odinfinch.xyz/u/
```
## Self Hosting
This requires a unix-like system with a reversed proxy util(nginx or [caddy](https://caddyserver.com/)) and python3 installed.
### Quick Start
#### Caddy
I'll use caddy for the proxy server, and nginx will be similar. After you install caddy, create a file named `Caddyfile` with the content below.
```
https://f1l3.your-host.com {
 proxy / https://localhost:8000 {
 transparent
 insecure_skip_verify
}
}
```
In the current directory, run caddy in the background.
```
nohup sudo caddy &
```
This will generate a TLS certificate for f1l3.your-host.com automatically and listens to incoming traffic and then send the traffic to localhost:8000 using encrypted connection. So now we need to make our F1L3 server listen to localhost:8000 with HTTPS enabled.

#### F1L3 Server
Keep caddy running in the background. Clone the repository, and go to that directory. Now install the virtualenv package for python 3: 
```
sudo pip3 install virtualenv
```

And create a virtualenv by running 
```
virtualenv venv
```
Activate the virtual environment with 
```
source venv/bin/activate
```
 Remember to activate the virtual environment every time you do something to the F1L3 server.

After activating the virtual environment, run 
```
pip install -r requirements.txt
``` 
to install dependencies. After that, run 
```
./run.sh
``` 
to run the server. 
> NOTE: 
> Remember to give it your actual host (aka f1l3.your-host.com).
> 
> In case of permission denied, run chmod +x run.sh to give run.sh execute permission.

`run.sh` will create a sqlite3 database at `db.sqlite3` and create self-signed SSL certificate at `local_cert` and generate a secret key in `.env` and run the server using `gunicorn`. 

The files uploaded will be saved in the `media` directory encrypted. You can edit `.env` and `f1l3/settings.py` to change your settings.

Have fun!

## Developers
### Environment Variables
#### Variables
`F1L3_DEBUG`: will set settings.py to True if set. When debugging, the secret key will be set to a default one and host will be set to `localhost:8000`

`F1L3_SECRET_KEY`: This is required if `F1L3_DEBUG` is not set. This works as the django secret key. There is a script which can generate a random new key at `scripts/gen_secret_key.py`

`F1L3_HOST`: This is used in generated URLs.

#### manage.py 
`manage.py` will automatically load the `.env` file. I suggest run `run.sh` first to generate `.env` file and then run `manage.py` for development server.