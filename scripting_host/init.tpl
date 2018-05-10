#!/bin/bash

# https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-14-04

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

# Configure filewall
firewall-offline-cmd --zone=public --add-service=http || \
  die "Failed to add http to firewalld. Exit code was $?"
firewall-offline-cmd --zone=public --add-service=https || \
  die "Failed to add https to firewalld. Exit code was $?"
systemctl restart firewalld || \
  die "Failed to restart firewalld. Exit code was $?"
log "firewall configured for nginx"

# Configure nginx server block for terrasnow
cat > /etc/nginx/sites-available/terrasnow << EOF
server {
    listen 80;
    server_name $HOSTNAME;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/user/terrasnow/terrasnow.sock;
    }
}
EOF
log "Nginx server block configured."

# Link the file to the sites-enabled directory
ln -s /etc/nginx/sites-available/terrasnow /etc/nginx/sites-enabled || \
  die "Failed to create link to sites-enabled directory. Exit code was $?"

# restart nginx to load the new config
systemctl restart nginx || \
  die "Failed to restart nginx. Exit code was $?"
log "Successfully restarted nginx."

# Install git
yum install -y git || \
  die "Failed to install git. Exit code was $?"
log "Successfully installed git"

# Install python3
yum install -y https://centos7.iuscommunity.org/ius-release.rpm || \
  die "Failed to install python-lastest. Exit code was $?"
log "Successfully installed python"
# yum update -y || \
#  die "failed to run yum update. Exit code was $?"
# log "Sccuessfully ran yum update."

# Configure the flask app
git clone https://github.com/userhas404d/terrasnow-enterprise.git || \
  die "Failed to pull terrasnow. Exit code was $?"
log "Successfully pulled terrasnow repo"
python3 -m venv flask || \
  die "Failed to create flask venv. Exit code was $?"
log "Started flask app."
source flask/bin/activate || \
  die "Failed to enter python venv. Exit code was $?"
log "Entered python venv."
pip install gunicorn flask || \
  die "Failed to install gunicorn. Exit code was $?"
log "Successfully installed gunicorn."
