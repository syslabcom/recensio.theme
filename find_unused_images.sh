#!/usr/bin/env bash
for FILEPATH in $(find . -path ./recensio/theme/skins -prune -or \( -name "*.png" -or -name "*.jpg" \) -printf '%p '); do
    FILE=$(python -c "print('${FILEPATH}'.split('/')[-1])");
    COUNT=$(grep -RI --exclude-dir=.svn --exclude-dir=.git -l $FILE ../recensio.*/recensio/* | wc -l);
    if [[ $COUNT == '0' ]]; then
        echo $FILEPATH;
    fi;
done
