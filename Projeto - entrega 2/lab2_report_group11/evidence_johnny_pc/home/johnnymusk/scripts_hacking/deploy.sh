#!/bin/bash
set -e

echo "Zipping Zyra Website"
cd ~/Documents
zip -r ~/zyra.zip ZYRA

echo "Copying Zip To INESC machine"
scp ~/zyra.zip csf:/home/muskyboi/

echo "Initializing Zyra Website"
ssh -t csf "
    rm -rf Website/ZYRA; \
    unzip -o /home/muskyboi/zyra.zip -d Website; \
    cd Website/ZYRA; \
    npm install; \
    npm install vhost; \
    sudo node server.js
"
