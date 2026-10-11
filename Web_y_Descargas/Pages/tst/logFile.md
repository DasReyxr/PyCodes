First, I created the index.html file then I need to use nginx if I want to host properly my website, so I need to install nginx and create the directory where my website will be hosted.

```bash
sudo apt install nginx

SITE="tst"
sudo mkdir -p /var/www/$SITE
sudo chown $USER /var/www/$SITE
```
then i configure the nginx server to host my website, so I need to create a configuration file for my site in the /etc/nginx/sites-available directory.
```
nano /etc/nginx/sites-available/$SITE
```
```
server {
    listen 8080;
    server_name _;
    root /var/www/tst;
    index index.html;
    location / {
        try_files $uri $uri/ =404;
    }
}
```

## Manjaro Version

First, I created the index.html file then I need to use nginx if I want to host properly my website, so I need to install nginx and create the directory where my website will be hosted.

```bash
yay -S nginx

SITE="tst"
sudo mkdir -p /var/www/$SITE
sudo chown $USER /var/www/$SITE
```
### Configuration
then i configure the nginx server to host my website, so I need to create a configuration file for my site in the /etc/nginx/sites-available directory.
```
sudo mkdir -p /etc/nginx/conf.d
sudo nano /etc/nginx/nginx.conf
```
then add this line on http block
```
include /etc/nginx/conf.d/*.conf;
```
### Tst Configuration
then create the configuration file for my site in the /etc/nginx/conf.d directory.
```
sudo nano /etc/nginx/conf.d/tst.conf
```
```
server {
    listen 8080;
    server_name _;
    root /var/www/tst;
    index index.html;
    location / {
        try_files $uri $uri/ =404;
    }
}
```

### Enable the site and restart nginx
```
sudo nginx -t
sudo systemctl enable --now nginx    
```

If u want to turn it off
sudo systemctl disable --now nginx