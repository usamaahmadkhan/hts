#!/bin/bash

. scripts/bash_helpers.sh
. scripts/log_helpers.sh

log "Adding services to secure terminal"
for i in rlogin rsh rexec;
  do echo $i >> /etc/securetty; done

log "Installing necessary packages for LTP suite"
sudo apt-get install xinetd -y
sudo apt-get install rsh-server -y
sudo apt-get install telnetd-ssl -y
sudo apt-get install cfingerd -y
sudo apt-get install rdist -y
sudo apt-get install rsync -y
sudo apt-get install vsftpd -y
sudo apt-get install apache2 -y

log "Fixing ftp service"
sudo service xinetd stop
sudo service vsftpd restart

log "Removing restriction on root to have access. Commenting out root"
sed -i -e "s/root/#root/g" /etc/ftpusers

log "Enabling anonymous users for FTP"
sed -i -e "s/anonymous_enable=NO/anonymous_enable=YES/g" /etc/vsftpd.conf
sed -i -e "s/#anon_upload_enable=YES/anon_upload_enable=YES/g" /etc/vsftpd.conf
sed -i -e "s/#anon_mkdir_write_enable=YES/anon_mkdir_write_enable=YES/g" /etc/vsftpd.conf
