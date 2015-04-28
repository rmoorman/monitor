#!/bin/bash

SDIR=$(cd "$(dirname "$0")"; pwd)
BDIR=$(cd "$(dirname "$0")/.."; pwd)

SPATH="$BDIR/application/static"
IPATH="$SDIR/static"

mkdir -p "$SPATH/js" "$SPATH/css"

wget --default-page=kube.zip -P "$SPATH" http://imperavi.com/webdownload/kube/get/
wget -P "$SPATH" http://www.flotcharts.org/downloads/flot-0.8.3.zip
wget -P "$SPATH" http://momentjs.com/downloads/moment-with-locales.min.js
wget -P "$SPATH" http://code.jquery.com/jquery-2.1.3.min.js

unzip -j -d "$SPATH" "$SPATH/kube.zip" *.min.*
unzip -j -d "$SPATH" "$SPATH/flot-0.8.3.zip" *jquery.flot*.min.js

for jsf in "$SPATH/*.js"; do
    mv $jsf "$SPATH/js"
done
for csf in "$SPATH/*.css"; do
    mv $csf "$SPATH/css"
done

for zsf in "$SPATH/*.zip*"; do
    rm $zsf
done

for psf in "$IPATH/*.png"; do
    cp $psf $SPATH
done

ls $SPATH
ls "$SPATH/css"
ls "$SPATH/js"
