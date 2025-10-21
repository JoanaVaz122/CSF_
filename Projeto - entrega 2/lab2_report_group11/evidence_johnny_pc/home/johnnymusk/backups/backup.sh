#!/bin/bash

timestamp() {
    date +%s
}


TS=$(timestamp)
USER=ironcaesar
HOST=10.0.2.134
DIR=/home/$USER/backups
ZIPFILE=backup_$TS.zip
BACKUP_PASS=$(~/backups/pass_gen.sh $TS)

zip -r --password $BACKUP_PASS $ZIPFILE ~/Documents/ZYRA/
rsync -avz "$ZIPFILE" backupserver:$DIR
rm $ZIPFILE

