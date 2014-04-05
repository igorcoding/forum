#!/bin/bash
sudp cp forumserver.py /usr/sbin/forumserver
sudo cp forumserver /etc/init.d/
sudo update-rc.d forumserver defaults
