#!/bin/bash
gameport=`expr $1 + 27960`
rconport=`expr $1 + 28960`
servernum=`expr $1 + 1`

exec /home/steam/Steam/steamapps/common/qlds/run_server_x64_minqlx.sh \
+set net_strict 1 \
+set net_port $gameport \
+set fs_homepath /home/steam/.quakelive/$gameport \
+set zmq_rcon_enable 1 \
+set zmq_rcon_password "" \
+set zmq_rcon_port $rconport \
+set zmq_stats_enable 1 \
+set zmq_stats_password "" \
+set zmq_stats_port $gameport \
+set qlx_owner "76561198021129477"
