#!/bin/bash

# https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-centos-7

log()
{
    # Logs messages to logger and stdout
    # Reads log messages from $1 or stdin
    if [[ "$${1-UNDEF}" != "UNDEF" ]]
    then
        # Log message is $1
        logger -i -t "$${__SCRIPTNAME}" -s -- "$1" 2> /dev/console
        echo "$${__SCRIPTNAME}: $1"
    else
        # Log message is stdin
        while IFS= read -r IN
        do
            log "$IN"
        done
    fi
}  # ----------  end of function log  ----------

die()
{
    [ -n "$1" ] && log "$1"
    log "$${__SCRIPTNAME} failed"'!'
    exit 1
}  # ----------  end of function die  ----------

log "$${__SCRIPTNAME} starting!"

# Get instance hostname
HOSTNAME=$(curl http://169.254.169.254/latest/meta-data/local-hostname)

# Install nginx
yum install -y epel-release || \
  die "Failed to add the CentOS 7 EPEL repository. Exit code was $?"
rpm -Uvh http://nginx.org/packages/centos/7/x86_64/RPMS/nginx-1.14.0-1.el7_4.ngx.x86_64.rpm || \
  die "Failed to install nginx. Exit code was $?"
log "Installed nginx."

## Configure firewalld
firewall-offline-cmd --zone=public --add-service=http || \
  die "Failed to add http to firewalld. Exit code was $?"
firewall-offline-cmd --zone=public --add-service=https || \
  die "Failed to add https to firewalld. Exit code was $?"
systemctl restart firewalld || \
  die "Failed to restart firewalld. Exit code was $?"
log "firewall configured for nginx"

# Install git
yum install -y git || \
  die "Failed to install git. Exit code was $?"
log "Successfully installed git"

# Configure the flask app
git clone https://github.com/userhas404d/terrasnow-enterprise.git /home/maintuser/terrasnow || \
  die "Failed to pull terrasnow. Exit code was $?"
log "Successfully pulled terrasnow repo"
cd /home/maintuser/terrasnow || \
  die "Failed to navigate to the terrasnow directory. Exit code was $?"
log "Sucessfully navigated to the terrasnow directory."
python3 -m venv flask || \
  die "Failed to create flask venv. Exit code was $?"
log "Started flask app."
source flask/bin/activate || \
  die "Failed to enter python venv. Exit code was $?"
log "Entered python venv."
pip install gunicorn flask || \
  die "Failed to install gunicorn. Exit code was $?"
log "Successfully installed gunicorn."

# configure the app to autostart on boot

cat > /etc/systemd/system/terrasnow.service << EOF
[Unit]
Description=Gunicorn instance to serve terrasnow
After=network.target

[Service]
User=maintuser
Group=nginx
WorkingDirectory=/home/maintuser/terrasnow
Environment="PATH=/home/maintuser/terrasnow/flask/bin"
ExecStart=/home/maintuser/terrasnow/flask/bin/gunicorn -w 4 -b 127.0.0.1:8000 wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Configure terrasnow service to start automatically
sudo systemctl start terrasnow || \
  die "Failed to start terrasnow. Exit code was $?"
log "Started terrasnow service."
sudo systemctl enable terrasnow || \
  die "Failed to set terrasnow to autostart. Exit code was $?"
log "Set terrasnow service to autostart."


# Change owner of application directory to maintuser
chown maintuser /home/maintuser/terrasnow || \
  die "Failed allow nginx user execute permissions to applicaiton directory. Exit code was $?"
log "Added excute permissions for nginx user on application directory."

# Add the nginx user to same group as maintuser
sudo usermod -a -G maintuser nginx || \
  die "Failed add nginx user to maintuser group. Exit code was $?"
log "Added nginx to maintuser group."

# Create reverse proxy main config
cat > /etc/nginx/conf.d/default.conf << EOF
server {
    listen       80;
    server_name  localhost;

    location / {
    proxy_pass http://127.0.0.1:8000/webhook;
    }

  }
EOF

# stop nginx in order to re-load the new configuration
systemctl stop nginx || \
  die "Failed stop nginx. Exit code was $?"
log "Nginx stopped."

# configure nginx to auto start
systemctl start nginx || \
  die "Failed start nginx. Exit code was $?"
log "Nginx started."
systemctl enable nginx || \
  die "Failed set nginx to autostart. Exit code was $?"
log "Nginx configured to autostart."

# allow ngix proxy-pass on selinux
# http://stackoverflow.com/questions/23948527/13-permission-denied-while-connecting-to-upstreamnginx
# https://www.centos.org/docs/5/html/Deployment_Guide-en-US/sec-sel-building-policy-module.html
cat > /tmp/mynginx.te << EOF
module mynginx 1.0;

require {
        type httpd_t;
        type soundd_port_t;
        class tcp_socket name_connect;
}

#============= httpd_t ==============

#!!!! This avc can be allowed using the boolean 'httpd_can_network_connect'
allow httpd_t soundd_port_t:tcp_socket name_connect;
EOF

cd /tmp/
checkmodule -M -m -o mynginx.mod mynginx.te || \
  die "Failed to create policy module. Exit code was $?"
log "Created SE policy module."
semodule_package -o mynginx.pp -m mynginx.mod || \
  die "Failed to create SE policy package. Exit code was $?"
log "Created SE policy package."
semodule -i mynginx.pp || \
  die "Failed to apply SE policy package. Exit code was $?"
log "Applied SE policy package."
