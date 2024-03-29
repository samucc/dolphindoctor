#!/bin/bash
#

backup_dir='../data/backup/'

if [ ! -d $backup_dir ];then
    mkdir $backup_dir
fi

mysqldump -uroot -h127.0.0.1 -p dolphindoctor -P3307 > ${backup_dir}/dolphindoctor_$(date +'%Y-%m-%d_%H:%M:%S').sql
