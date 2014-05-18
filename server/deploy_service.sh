#!/bin/bash
sudo cp forumserver_production.py /usr/sbin/forumserver
sudo cp forumserver /etc/init.d/
sudo update-rc.d forumserver defaults
