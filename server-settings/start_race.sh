#!/bin/bash
cd ~/qlds/baseq3 || exit 1
source private.sh || exit 1

if [[ $1 == turbo ]]; then
    gamePort=$((27959 + $2))
    rconPort=$((gamePort + 1000))
    mapPool="mappool_qlrace.txt"
    mode="Turbo (PQL)"
    modeNumber=0
    modeTags="Turbo,PQL"
elif [[ $1 == classic ]]; then
    gamePort=$((27969 + $2))
    rconPort=$((gamePort + 1000))
    mapPool="mappool_qlrace_classic.txt"
    mode="Classic (VQL)"
    modeNumber=2
    modeTags="Classic,VQL"
else
    exit 1
fi

if [[ $LOCATION == DE ]]; then
    tags="QLRace.com,Germany,Frankfurt,$modeTags"
elif [[ $LOCATION == IL ]]; then
    tags="QLRace.com,Illinois,Chicago,$modeTags"
elif [[ $LOCATION == AU ]]; then
    tags="QLRace.com,Australia,Sydney,$modeTags"
else
    exit 1
fi

exec /home/steam/qlds/run_server_x64_minqlx.sh \
    +set com_hunkmegs 66 \
    +set fs_homepath /home/steam/.quakelive/$gamePort \
    +set net_port $gamePort \
    +set sv_hostname "QLRace.com $LOCATION - $mode #$2" \
    +set sv_mappoolFile $mapPool \
    +set sv_maxclients 18 \
    +set sv_tags $tags \
    +set zmq_rcon_enable 1 \
    +set zmq_rcon_password $RCON_PW \
    +set zmq_rcon_port $rconPort \
    +set zmq_stats_enable 1 \
    +set zmq_stats_password $STATS_PW \
    +set qlx_cleverBotKey $CB_KEY \
    +set qlx_cleverBotUser $CB_USER \
    +set qlx_raceKey $RACE_KEY \
    +set qlx_raceMode $modeNumber \
    +set qlx_servers "de.qlrace.com:27960, de.qlrace.com:27961, de.qlrace.com:27962, de.qlrace.com:27963, de.qlrace.com:27970, de.qlrace.com:27971, de.qlrace.com:27972, de.qlrace.com:27973, il.qlrace.com:27960, il.qlrace.com:27961, il.qlrace.com:27962, il.qlrace.com:27970, il.qlrace.com:27971, au.qlrace.com:27960, au.qlrace.com:27961, au.qlrace.com:27970, au.qlrace.com:27971"
