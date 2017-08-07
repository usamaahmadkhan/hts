#!/bin/bash

. scripts/bash_helpers.sh
. scripts/log_helpers.sh

log "Adding services to secure terminal"
for i in rlogin rsh rexec;
  do echo $i >> /etc/securetty; done

log "Installing necessary packages for LTP suite"
sudo zypper install -y xinetd
sudo zypper install -y rsh
sudo zypper install -y telnet-server
sudo zypper install -y finger
sudo zypper install -y rdist
sudo zypper install -y rsync
sudo zypper install -y vsftpd
sudo zypper install -y apache2

log "Fixing ftp service"
sudo service xinetd stop
sudo service vsftpd restart

log "Removing restriction on root to have access. Commenting out root"
sed -i -e "s/root/#root/g" /etc/ftpusers

log "Enabling anonymous users for FTP"
sed -i -e "s/anonymous_enable=NO/anonymous_enable=YES/g" /etc/vsftpd.conf
sed -i -e "s/#anon_upload_enable=YES/anon_upload_enable=YES/g" /etc/vsftpd.conf
sed -i -e "s/#anon_mkdir_write_enable=YES/anon_mkdir_write_enable=YES/g" /etc/vsftpd.conf
