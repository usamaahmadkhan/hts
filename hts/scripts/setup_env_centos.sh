#!/bin/bash

. scripts/bash_helpers.sh
. scripts/log_helpers.sh

log "Adding services to secure terminal"
for i in rlogin rsh rexec;
  do echo $i >> /etc/securetty; done

log "Installing necessary packages for LTP suite"
sudo yum install xinetd -y
sudo yum install rsh rsh-server -y
sudo yum install telnet-server -y
sudo yum install finger -y
sudo yum install perl-Net-SFTP-Foreign curl -y
sudo yum install librsync -y
sudo yum install vsftpd -y
sudo yum install mod_proxy_uwsgi mod_xsendfile -y

log "Fixing ftp service"
sudo service xinetd stop
sudo service vsftpd restart

log "Removing restriction on root to have access. Commenting out root"
sed -i -e "s/root/#root/g" /etc/vsftpd/ftpusers

log "Enabling anonymous users for FTP"
sed -i -e "s/anonymous_enable=NO/anonymous_enable=YES/g" /etc/vsftpd/vsftpd.conf
sed -i -e "s/#anon_upload_enable=YES/anon_upload_enable=YES/g" /etc/vsftpd/vsftpd.conf
sed -i -e "s/#anon_mkdir_write_enable=YES/anon_mkdir_write_enable=YES/g" /etc/vsftpd/vsftpd.conf
