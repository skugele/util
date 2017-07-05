#! /bin/bash

find -iname '*.pdf' -exec sh -c 'pdftotext "{}" - 2>/dev/null | grep --with-filename --label="{}" --color "internal"' \;
find -iname '*.doc' -exec sh -c 'catdoc "{}" 2>/dev/null | grep --with-filename --label="{}" --color "action"' \;
