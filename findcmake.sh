emerge -1D --keep-going --autounmask-write `find /var/db/pkg/ -name CFLAGS -print0 | xargs -0 fgrep -l 'native'| sed 's/\/var\/db\/pkg\/\(.*\)\/CFLAGS$/=\1/'| xargs`
