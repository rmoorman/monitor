#!/bin/bash

SDIR=$(cd "$(dirname "$0")"; pwd)
BDIR=$(cd "$(dirname "$0")/.."; pwd)

IPATH="$SDIR/static"
SPATH="$BDIR/application/static"

wget -P "$IPATH" http://code.jquery.com/jquery-2.1.3.min.js
wget -P "$IPATH" http://fortawesome.github.io/Font-Awesome/assets/font-awesome-4.3.0.zip
wget -P "$IPATH" --default-page=kube.zip  http://imperavi.com/webdownload/kube/get/
wget -P "$IPATH" http://momentjs.com/downloads/moment-with-locales.min.js
wget -P "$IPATH" http://www.flotcharts.org/downloads/flot-0.8.3.zip

unzip -j -d "$IPATH" "$IPATH/flot*zip" "*jquery.flot*.min.js"
unzip -j -d "$IPATH" "$IPATH/font-awesome*zip" "*.min.css" "*-webfont*"
unzip -j -d "$IPATH" "$IPATH/kube*zip" "*.min.*"

mkdir -p "$SPATH/css" "$SPATH/fonts" "$SPATH/js"

mv "$IPATH"/*.css "$SPATH/css"
mv "$IPATH/"*.{eot,svg,ttf,woff2,woff} "$SPATH/fonts"
mv "$IPATH"/*.js "$SPATH/js"
cp "$IPATH/"*.png "$SPATH"
rm "$IPATH/"*.zip*

echo '--'
echo '--'
echo '/'
ls "$SPATH"
echo '--'
echo '/css'
ls "$SPATH/css"
echo '--'
echo '/fonts'
ls "$SPATH/fonts"
echo '--'
echo '/js'
ls "$SPATH/js"
echo '--'
echo '--'
