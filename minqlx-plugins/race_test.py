# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Race plugin for minqlx. Adds commands such as !pb, !top, !all etc
"""

import minqlx
import random
import re
import requests
import time

PARAMS = ({}, {"weapons": "false"}, {"physics": "classic"}, {"physics": "classic", "weapons": "false"})
OLDTOP_URL = "https://cdn.rawgit.com/QLRace/oldtop/master/oldtop/"

# physics strings used for vql and pql args on rank and related functions
PHYSICS_PQL_STRINGS = ['pql', 'turbo', 'p', 't']
PHYSICS_VQL_STRINGS = ['vql', 'classic', 'v', 'c']
PHYSICS_STRINGS = PHYSICS_PQL_STRINGS + PHYSICS_VQL_STRINGS

_RE_POWERUPS = re.compile(r'print ".+\^3 got the (Haste|Battle Suit|Quad Damage|Invisibility|Regeneration)!\^7\n"')


class race_test(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("new_game", self.handle_new_game)
        self.add_hook("map", self.handle_map)
        self.add_hook("server_command", self.handle_server_command)
        self.add_hook("stats", self.handle_stats, priority=minqlx.PRI_HIGHEST)
        self.add_hook("player_spawn", self.handle_player_spawn, priority=minqlx.PRI_HIGHEST)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("team_switch", self.handle_team_switch)
        self.add_hook("client_command", self.handle_client_command)
        self.add_hook("frame", self.handle_frame)
        self.add_command(("slap", "slay"), self.cmd_disabled, priority=minqlx.PRI_HIGH)
        self.add_command("updatemaps", self.cmd_updatemaps)
        self.add_command(("pb", "me", "spb", "sme", "p", "sp"), self.cmd_pb, usage="[map] <vql/pql>")
        self.add_command(("rank", "srank", "r", "sr"), self.cmd_rank, usage="[rank] [map] <vql/pql>")
        self.add_command(("top", "stop", "t", "st", "oldtop", "oldstop", "ot", "ost"), self.cmd_top,
                         usage="[amount] [map] <vql/pql>")
        self.add_command(("all", "sall", "a", "sa"), self.cmd_all, usage="[map] <vql/pql>")
        self.add_command(("ranktime", "sranktime", "rt", "srt"), self.cmd_ranktime, usage="<time> [map]")
        self.add_command(("avg", "savg"), self.cmd_avg, usage="[id] <vql/pql>")
        self.add_command("randommap", self.cmd_random_map, usage='[amount]')
        self.add_command("recent", self.cmd_recent, usage="[amount]")
        self.add_command(("goto", "tp"), self.cmd_goto, usage="<id>")
        self.add_command("savepos", self.cmd_savepos)
        self.add_command("loadpos", self.cmd_loadpos)
        self.add_command("maps", self.cmd_maps, usage="[prefix]", priority=minqlx.PRI_HIGH)
        self.add_command(("timer", "starttimer", "stoptimer"), self.cmd_timer)
        self.add_command(("reset", "resettime", "resetscore"), self.cmd_reset)
        self.add_command(("commands", "cmds", "help"), self.cmd_commands, priority=minqlx.PRI_HIGH)
        self.add_command("vote", self.cmd_vote_random_map, usage="<n> | Use !randommap before !vote")
        self.add_command("voterandom", self.cmd_callvote_random_map)

        self.set_cvar_once("qlx_raceMode", "0")  # 0 = Turbo/PQL, 2 = Classic/VQL
        self.set_cvar_once("qlx_raceBrand", "QLRace.com")  # Can set to "" to not brand

        self.move_player = {}  # Queued !goto/!loadto positions. {steam_id: position}
        self.goto = {}  # Players which have used !goto/!loadpos. {steam_id: score}
        self.savepos = {}  # Saved player positions. {steam_id: player.state.position}
        self.frame = {}  # The frame when player used !timer. {steam_id: frame}
        self.current_frame = 0  # Number of frames the map has been playing for.
        self.lagged = {}
        self.map_restart = False

        self.maps = []
        self.old_maps = []
        self.get_maps()

    def handle_new_game(self):
        """Brands map title on new game."""
        map_name = self.game.map.lower()
        self.brand_map(map_name)
        self.set_cvar("g_gravity", "800")

    def handle_map(self, map_name, factory):
        """Brands map title and updates list of race maps on map change.
        Also Clears savepos and move_player dicts.
        """
        map_name = map_name.lower()
        if self.get_cvar("qlx_raceBrand"):
            self.brand_map(map_name)
        self.get_maps()
        self.savepos = {}
        self.move_player = {}
        self.lagged = {}
        self.current_frame = 0
        if self.game.factory not in ("qlrace_classic", "qlrace_turbo"):
            return
        self.set_cvar("pmove_chainjump", "0")

        # This one is not in the racemapsettings plugin because it sets self.map_restart
        if map_name == "gl":
            if self.get_cvar("g_startingHealth", int) != 3000:
                self.map_restart = True
            self.set_cvar("g_startingHealth", "3000")
        else:
            self.set_cvar("g_startingHealth", "100")

    def handle_server_command(self, player, cmd):
        """Stops server printing powerup messages."""
        if _RE_POWERUPS.fullmatch(cmd):
            return minqlx.RET_STOP_EVENT

    def handle_stats(self, stats):
        """Resets a player's score if they used !goto or !loadpos."""
        if stats["TYPE"] == "PLAYER_RACECOMPLETE":
            steam_id = int(stats["DATA"]["STEAM_ID"])
            if steam_id in self.goto:
                player = self.player(steam_id)
                player.score = self.goto[steam_id]
                player.tell("^7Your time does not count because you used ^6!goto ^7or ^6!loadpos.")

    def handle_player_spawn(self, player):
        """Spawns player instantly
        Moves player to position if they used !goto or !loadpos.
        Removes player from frame dict."""
        map_name = self.game.map.lower()
        if self.map_restart:
            self.map_restart = False
            minqlx.console_command("map_restart")

        if player.team == "free":
            player.is_alive = True

        if player.steam_id in self.move_player and player.is_alive:
            if player.steam_id not in self.goto:
                player.tell("^6Your time will not count, unless you kill yourself.")
                self.goto[player.steam_id] = player.score

            minqlx.set_position(player.id, self.move_player.pop(player.steam_id))

        self.frame.pop(player.steam_id, None)

    def handle_player_disconnect(self, player, reason):
        """Removes player from goto, savepos and move_player dicts when
        they disconnect."""
        self.goto.pop(player.steam_id, None)
        self.savepos.pop(player.steam_id, None)
        self.move_player.pop(player.steam_id, None)
        self.frame.pop(player.steam_id, None)

    def handle_team_switch(self, player, old_team, new_team):
        """Removes player from goto, move_player and frame dicts when
        they spectate."""
        if new_team == "spectator":
            self.goto.pop(player.steam_id, None)
            self.move_player.pop(player.steam_id, None)
            self.frame.pop(player.steam_id, None)

    def handle_client_command(self, player, cmd):
        """Disables readyup command if warmup ready % is more
        than 1.
        Removes players from goto and frame dicts on kill."""
        if cmd == "readyup" and self.get_cvar("sv_warmupReadyPercentage", float) > 1:
            player.tell("readyup is disabled since sv_warmupReadyPercentage is more than 1")
            return minqlx.RET_STOP_EVENT

        if cmd == "kill" and player.team == "free":
            self.goto.pop(player.steam_id, None)
            self.frame.pop(player.steam_id, None)
            return minqlx.RET_USAGE

    def handle_frame(self):
        """Increments current frame and center_prints timer to all
        player who used !timer. Also removes player from goto
        dict if they died(death event wasn't getting triggered)."""
        if not self.game:
            return

        self.current_frame += 1

        for p in self.frame:
            ms = (self.current_frame - self.frame[p]) * 25
            self.player(p).center_print(race_test. time_string(ms))

        # makes new dict with dead players removed
        self.goto = {p: score for p, score in self.goto.items() if self.player(p).health > 0}

    def cmd_callvote_random_map(self, player, msg, channel):
        """Callvotes a random map."""
        map_name = random.choice(self.maps)
        minqlx.client_command(player.id, "cv map {}".format(map_name))

    def cmd_disabled(self, player, msg, channel):
        """Disables !slap and !slay."""
        player.tell("^6{} ^7is disabled".format(msg[0]))
        return minqlx.RET_STOP_ALL

    def cmd_updatemaps(self, player, msg, channel):
        """Updates list of race maps"""
        self.get_maps()

    def cmd_pb(self, player, msg, channel):
        """Outputs the player's personal best time for a map."""
        @minqlx.thread
        def pb(map_name, mode=None, weapons=None, physics=None):
            records = self.get_records(map_name, weapons, mode)
            rank, time = records.pb(player.steam_id)
            if not weapons:
                map_name += "^2(strafe)"
            if physics:
                physics_string = "^3({})".format(physics)
                map_name += "^2({})".format(physics)
            else:
                physics_string = ""
            if rank:
                channel.reply("{}{}".format(records.output(player, rank, time), physics_string))
            else:
                channel.reply("^2No time found for ^7{} ^2on ^3{}".format(player, map_name))

        physics = None
        map_prefix = self.game.map.lower()
        if len(msg) == 2:
            if msg[1].lower() in PHYSICS_STRINGS:
                physics = msg[1].lower()
            else:
                map_prefix = msg[1].lower()
        elif len(msg) == 3:
            if msg[2].lower() in PHYSICS_STRINGS:
                physics = msg[2].lower()
            map_prefix = msg[1].lower()
        elif len(msg) != 1 and len(msg) > 3:
            return minqlx.RET_USAGE

        map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
        mode = self.weapons_physics_to_mode(weapons, physics)
        pb(map_name, mode, weapons, physics)

    @staticmethod
    def weapons_physics_to_mode(weapons, physics):
        """Convert weapons bool and physics string to mode int"""
        if weapons and physics in PHYSICS_VQL_STRINGS:
            return 2
        elif weapons and physics in PHYSICS_PQL_STRINGS:
            return 0
        elif not weapons and physics in PHYSICS_VQL_STRINGS:
            return 3
        elif not weapons and physics in PHYSICS_PQL_STRINGS:
            return 1
        else:
            return None

    def cmd_rank(self, player, msg, channel):
        """Outputs the x rank time for a map. Default rank
        if none is given is 1.
        """

        @minqlx.thread
        def get_rank(map_name, mode=None, weapons=None, physics=None):
            records = self.get_records(map_name, weapons, mode)
            name, actual_rank, time = records.rank(rank)
            if not weapons:
                map_name += "^2(strafe)"
            if physics:
                physics_string = "^3({})".format(physics)
                map_name += "^2({})".format(physics)
            else:
                physics_string = ""
            if time:
                if actual_rank != rank:
                    tied = True
                else:
                    tied = False
                channel.reply("{}{}".format(records.output(name, rank, time, tied), physics_string))
            else:
                channel.reply("^2No rank ^3{} ^2time found on ^3{}".format(rank, map_name))

        physics = None
        rank = 1
        map_prefix = self.game.map.lower()
        if len(msg) == 2:
            if msg[1].isdigit():
                rank = int(msg[1])
            elif msg[1].lower() in PHYSICS_STRINGS:
                physics = msg[1].lower()
            else:
                map_prefix = msg[1]
        elif len(msg) == 3:
            if msg[1].isdigit():
                rank = int(msg[1])
                if msg[2].lower() in PHYSICS_STRINGS:
                    physics = msg[2].lower()
                else:
                    map_prefix = msg[2]
            else:
                map_prefix = msg[1]
                if msg[2].lower() in PHYSICS_STRINGS:
                    physics = msg[2].lower()
        elif len(msg) == 4:
            rank = int(msg[1])
            map_prefix = msg[2]
            if msg[3].lower() in PHYSICS_STRINGS:
                physics = msg[3].lower()
        elif len(msg) > 4 and len(msg) != 1:
            return minqlx.RET_USAGE

        map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
        get_rank(map_name, self.weapons_physics_to_mode(weapons, physics), weapons, physics)

    def cmd_top(self, player, msg, channel):
        """Outputs top x amount of times for a map. Default amount
        if none is given is 10. Maximum amount is 20."""
        amount = 10
        map_prefix = self.game.map
        physics = None
        if len(msg) == 2:
            try:
                amount = int(msg[1])
            except ValueError:
                if msg[1].lower() in PHYSICS_STRINGS:
                    physics = msg[1].lower()
                else:
                    map_prefix = msg[1]
        elif len(msg) == 3:
            try:
                amount = int(msg[1])
                if msg[2].lower() in PHYSICS_STRINGS:
                    physics = msg[2].lower()
                else:
                    map_prefix = msg[2]
            except ValueError:
                map_prefix = msg[1]
                if msg[2].lower() in PHYSICS_STRINGS:
                    physics = msg[2].lower()
        elif len(msg) == 4:
            try:
                amount = int(msg[1])
                map_prefix = msg[2]
                if msg[3].lower() in PHYSICS_STRINGS:
                    physics = msg[3].lower()
            except ValueError:
                return minqlx.RET_USAGE
        elif len(msg) > 4 and len(msg) != 1:
            return minqlx.RET_USAGE

        if amount > 20:
            channel.reply("^2Please use value <=20")
            return

        if msg[0][1].lower() == "o":
            map_name = self.map_prefix(map_prefix, old=True)
            if map_name not in self.old_maps:
                channel.reply("^3{} ^2has no times on ql.leeto.fi".format(map_prefix))
            else:
                self.old_top(map_name, msg[0], amount, channel, physics)
        else:
            map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
            mode = self.weapons_physics_to_mode(weapons, physics)
            self.top(map_name, weapons, amount, channel, mode, physics)

    @minqlx.thread
    def top(self, map_name, weapons, amount, channel, mode=None, physics=None):
        records = self.get_records(map_name, weapons, mode)
        if not weapons:
            map_name += "^2(strafe)"
        if physics:
            map_name += "^2({})".format(physics)
        if not records.records:
            channel.reply("^2No times were found on ^3{}".format(map_name))
            return

        output = ["^3{}".format(map_name)]
        for i in range(amount):
            try:
                record = records.records[i]
                if i == 0:
                    wr = record["time"]
                    time_diff = ""
                elif record["rank"] > 1:
                    time_diff = "+{}".format(race_test. time_string(record["time"] - wr))

                output.append("^3{:>2}. ^7{:30} ^3{:>10} ^1{:>12}"
                              .format(record["rank"], record["name"], race_test. time_string(record["time"]), time_diff))
            except IndexError:
                break

        for line in output:
            channel.reply(line)

    @minqlx.thread
    def old_top(self, map_name, command, amount, channel, physics):  #
        if "s" in command.lower():
            weapons = False
            if not physics:
                mode = self.get_cvar("qlx_raceMode", int) + 1
            else:
                mode = self.weapons_physics_to_mode(weapons, physics)
        else:
            weapons = True
            if not physics:
                mode = self.get_cvar("qlx_raceMode", int)
            else:
                mode = self.weapons_physics_to_mode(weapons, physics)

        try:
            records = requests.get("{}/{}/{}.json".format(OLDTOP_URL, map_name, mode)).json()["records"]
        except requests.exceptions.RequestException as e:
            self.logger.error(e)
            return

        if not weapons:
            map_name += "^2(strafe)"
        if physics:
            map_name += "^2({})".format(physics)
        if not records:
            channel.reply("^2No old times were found on ^3{}".format(map_name))
            return

        output = ["^3{}".format(map_name)]
        for i in range(amount):
            try:
                record = records[i]
                if i == 0:
                    wr = record["time"]
                    time_diff = ""
                elif record["rank"] > 1:
                    time_diff = "+{}".format(race_test. time_string(record["time"] - wr))

                output.append("^3{:>2}. ^7{:30} ^3{:>10} ^1{:>12}"
                              .format(record["rank"], record["name"], race_test. time_string(record["time"]), time_diff))
            except IndexError:
                break

        for line in output:
            channel.reply(line)

    def cmd_all(self, player, msg, channel):
        """Outputs the ranks and times of everyone on
        the server for a map.
        """

        @minqlx.thread
        def get_all(map_name, mode=None, weapons=None, physics=None):
            records = self.get_records(map_name, weapons, mode).records
            players = {p.steam_id for p in self.players()}
            times = []
            for record in records:
                if record["player_id"] in players:
                    times.append(" ^3{}. ^7{} ^2{}".format(record["rank"], record["name"],
                                                           race_test. time_string(record["time"])))
            if not weapons:
                map_name += "^2(strafe)"
            if physics:
                map_name += "^2({})".format(physics)
            if times:
                self.output_times(map_name, times, channel)
            else:
                channel.reply("^2No times were found for anyone on ^3{} ^2:(".format(map_name))

        map_prefix = self.game.map
        physics = None
        if len(msg) == 2:
            if msg[1].lower() in PHYSICS_STRINGS:
                physics = msg[1].lower()
            else:
                map_prefix = msg[1]
        elif len(msg) == 3:
            map_prefix = msg[1]
            if msg[2].lower() in PHYSICS_STRINGS:
                physics = msg[2].lower()
        elif len(msg) != 1 and len(msg) > 3:
            return minqlx.RET_USAGE

        map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
        mode = self.weapons_physics_to_mode(weapons, physics)
        get_all(map_name, mode, weapons, physics)

    def cmd_ranktime(self, player, msg, channel):
        """Outputs which rank a time would be."""

        @minqlx.thread
        def ranktime(map_name):
            records = self.get_records(map_name, weapons)
            rank = records.rank_from_time(time)
            last_rank = records.last_rank + 1
            if not rank:
                rank = last_rank

            if not weapons:
                map_name += "^2(strafe)"

            channel.reply("^3{} ^2would be rank ^3{} ^2of ^3{} ^2on ^3{}"
                          .format(race_test.time_string(time), rank, last_rank, map_name))

        if len(msg) == 1 and player.score != 2147483647 and player.score != 0:
            time = player.score
            map_prefix = self.game.map
        elif len(msg) == 2:
            time = race_test.time_ms(msg[1])
            map_prefix = self.game.map
        elif len(msg) == 3:
            time = race_test.time_ms(msg[1])
            map_prefix = msg[2]
        else:
            channel.reply("^7Usage: ^6{0} <time> [map] ^7or just ^6{0} ^7if you have set a time".format(msg[0]))
            return

        map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
        ranktime(map_name)

    def cmd_avg(self, player, msg, channel):
        """Outputs a player average rank."""

        @minqlx.thread
        def avg(player, mode):
            """API Doc: https://qlrace.com/apidoc/1.0/records/player.html"""
            try:
                data = requests.get("https://qlrace.com/api/player/{}".format(player.steam_id),
                                    params=PARAMS[mode]).json()
            except requests.exceptions.RequestException as e:
                self.logger.error(e)
                return

            name = data["name"]
            total_maps = len(data["records"])
            if name is not None and total_maps > 0:
                avg = data["average"]
                medals = data["medals"]
                if not physics:
                    channel.reply("^7{} ^2average {}rank: ^3{:.2f}^2({} maps) ^71st: ^3{} ^72nd: ^3{} ^73rd: ^3{}"
                                  .format(player, strafe, avg, total_maps, medals[0], medals[1], medals[2]))
                else:
                    channel.reply("^7{} ^2average {}rank ({}): ^3{:.2f}^2({} maps) ^71st: ^3{} ^72nd: ^3{} ^73rd: ^3{}"
                                  .format(player, strafe, physics, avg, total_maps, medals[0], medals[1], medals[2]))
            else:
                channel.reply("^7{} ^2has no {}records :(".format(player, strafe))

        physics = None
        if len(msg) == 2:
            try:
                i = int(msg[1])
                target_player = self.player(i)
                if not (0 <= i < 64) or not target_player:
                    raise ValueError
                player = target_player
            except (ValueError, minqlx.NonexistentPlayerError):
                if msg[1].lower() in PHYSICS_STRINGS:
                    physics = msg[1].lower()
                else:
                    player.tell("Invalid ID.")
                    return minqlx.RET_STOP_ALL
        elif len(msg) == 3:
            try:
                i = int(msg[1])
                if msg[2].lower() in PHYSICS_STRINGS:
                    physics = msg[2].lower()
                target_player = self.player(i)
                if not (0 <= i < 64) or not target_player:
                    raise ValueError
                player = target_player
            except (ValueError, minqlx.NonexistentPlayerError):
                player.tell("Invalid ID.")
                return minqlx.RET_STOP_ALL
        elif len(msg) > 3 and len(msg) != 1:
            return

        if msg[0][1].lower() == "s":
            if physics:
                mode = self.weapons_physics_to_mode(False, physics)
            else:
                mode = self.get_cvar("qlx_raceMode", int) + 1
            strafe = "strafe "
        else:
            if physics:
                mode = self.weapons_physics_to_mode(True, physics)
            else:
                mode = self.get_cvar("qlx_raceMode", int)
            strafe = ""
        avg(player, mode)

    def cmd_vote_random_map(self, player, msg, channel):
        """Usage: !vote <n> where n is the map number displayed next to the map by cmd_random_map
        Only does something after cmd_random_map has been called at least once
        Votes the map name indicated by <n> by randommap"""
        if self.random_maps is None:
            return minqlx.RET_USAGE
        elif len(msg) > 2 or len(msg) == 1:
            return minqlx.RET_USAGE
        else:
            try:
                minqlx.client_command(player.id, "cv map {}".format(self.random_maps[int(msg[1])-1]))
            except (ValueError, IndexError):
                return minqlx.RET_USAGE

    @minqlx.thread
    def cmd_random_map(self, player, msg, channel):
        """Display msg[1] number of random maps and show the number of records on them for the current physics mode (strafe and weapons)"""
        # Determine number of random maps to show, max 5 min 1
        number_of_maps = 3
        if msg and len(msg) == 2:
            try:
                number_of_maps = int(msg[1])
                if number_of_maps > 5:
                    number_of_maps = 5
                elif number_of_maps <= 0:
                    number_of_maps = 3
            except ValueError:
                pass
        elif len(msg) > 2 and len(msg) != 1:
            return minqlx.RET_USAGE
        # Get random map names and create data structure to store record counts
        maps = {_map.lower(): {} for _map in random.sample(self.maps, number_of_maps)}
        # Get current physics modes
        weapons_mode = self.get_cvar('qlx_raceMode', int)
        strafe_mode = weapons_mode + 1
        # Get the number of strafe and weapon records for each map for the current physics modes
        for _map in maps.keys():
            try:
                # Get weapons records
                data_json = requests.get('https://qlrace.com/api/map/{}'.format(_map),
                                         params=PARAMS[weapons_mode]).json()
                maps[_map]['weapons'] = len(data_json['records'])
                # Get strafe records
                data_json = requests.get('https://qlrace.com/api/map/{}'.format(_map),
                                         params=PARAMS[strafe_mode]).json()
                maps[_map]['strafe'] = len(data_json['records'])
            except requests.exceptions.RequestException as e:
                # qlrace.com api unreachable
                self.logger.error(e)
                return
        # Display the results
        channel.reply('^7!vote <n> to vote map')
        channel.reply('^7(n) ^3map^1(strafe/weapons) ' + ' '.join(["^7({}) ^3{} ^1({}/{})".format(i + 1,
                                                                                                 _map,
                                                                                                 record_counts[
                                                                                                     'strafe'],
                                                                                                 record_counts[
                                                                                                     'weapons'])
                                                                  for i, (_map, record_counts) in
                                                                  enumerate(maps.items())]))
        # Store maps in self.random_maps for use by cmd_vote_random_map
        self.random_maps = list(maps.keys())

    def cmd_recent(self, player, msg, channel):
        """Outputs the most recent maps from QLRace.com"""

        @minqlx.thread
        def recent():
            """API Doc: https://qlrace.com/apidoc/1.0/Maps/maps.html"""
            try:
                data = requests.get("https://qlrace.com/api/maps?sort=recent").json()
            except requests.exceptions.RequestException as e:
                self.logger.error(e)
                return

            maps = '^7, ^3'.join(data["maps"][:amount])
            channel.reply("Most recent maps(by first record date): ^3{}".format(maps))

        amount = 10
        if len(msg) == 2:
            try:
                amount = int(msg[1])
                if not (0 <= amount <= 30):
                    raise ValueError
            except ValueError:
                player.tell("amount must be positive integer <= 30")
                return minqlx.RET_STOP_ALL
        elif len(msg) > 2:
            return minqlx.RET_USAGE
        recent()

    def cmd_goto(self, player, msg, channel):
        """Go to a player's location.
        Player needs to kill themselves/rejoin for a time to count."""
        map_name = self.game.map.lower()
        try:
            goto_disabled = self._loaded_plugins['racemapsettings'].GOTO_DISABLED
            if map_name in goto_disabled:
                player.tell("^1!goto is disabled on {}".format(map_name))
                return minqlx.RET_STOP_ALL
        except KeyError:
            # racemapsettings plugin is not loaded
            pass

        if len(msg) == 2:
            try:
                i = int(msg[1])
                target_player = self.player(i)
                if not (0 <= i < 64) or not target_player or not self.player(i).is_alive or i == player.id:
                    raise ValueError
            except ValueError:
                player.tell("Invalid ID.")
                return minqlx.RET_STOP_ALL
            except minqlx.NonexistentPlayerError:
                player.tell("Invalid ID.")
                return minqlx.RET_STOP_ALL
        elif len(msg) != 2:
            return minqlx.RET_USAGE

        if player.team == "spectator":
            if 'spec_delay' in self.plugins and player.steam_id in self.plugins['spec_delay'].spec_delays:
                player.tell("^6You must wait 15 seconds before joining after spectating")
                return minqlx.RET_STOP_ALL

            self.move_player[player.steam_id] = target_player.state.position
            player.team = "free"
        else:
            player.score = 2147483647
            self.move_player[player.steam_id] = target_player.state.position
            minqlx.player_spawn(player.id)  # respawn player so he can't cheat

    def cmd_savepos(self, player, msg, channel):
        """Saves current position."""
        if player.team != "spectator":
            # add player to savepos dict
            self.savepos[player.steam_id] = player.state.position
            player.tell("^6Position saved. Your time won't count if you use !loadpos, unless you kill yourself.")
        else:
            player.tell("Can't save position as spectator.")
        return minqlx.RET_STOP_ALL

    def cmd_loadpos(self, player, msg, channel):
        """Loads saved position."""
        try:
            goto_disabled = self._loaded_pluginsp['racemapsettings'].GOTO_DISABLED
            if self.game.map.lower() in goto_disabled:
                player.tell("^1!loadpos is disabled on {}".format(self.game.map))
                return minqlx.RET_STOP_ALL
        except KeyError:
            # racemapsettings plugin is not loaded.
            pass

        if player.team != "spectator":
            if player.steam_id in self.savepos:
                self.move_player[player.steam_id] = self.savepos[player.steam_id]
                minqlx.player_spawn(player.id)  # respawn player so he can't cheat
            else:
                player.tell("^1You have to save your position first.")
        else:
            player.tell("^1Can't load position as spectator.")
        return minqlx.RET_STOP_ALL


    def cmd_maps(self, player, msg, channel):
        """Tells player all the maps which have a record on QLRace.com.
        Outputs in 4 columns so you are not spammed with 450+ lines in console."""

        @minqlx.thread
        def output_maps():
            for i, (a, b, c, d) in enumerate(zip(maps[::4], maps[1::4], maps[2::4], maps[3::4])):
                if (i + 1) % 26 == 0:
                    time.sleep(0.4)
                player.tell('{:<23} {:<23} {:<23} {:<}'.format(a, b, c, d))

        if len(msg) <= 1:
            maps = self.maps
        else:
            maps = [x for x in self.maps if x.startswith(msg[1].lower())]
            if not maps:
                player.tell("^6There is no maps which match that prefix.")
                return minqlx.RET_STOP_ALL
        output_maps()
        return minqlx.RET_STOP_ALL


    def cmd_timer(self, player, msg, channel):
        """Starts/stops personal timer."""
        if player.team == "spectator":
            player.tell("^1You need to join the game to use this command.")
        else:
            if msg[0].startswith("!stop"):
                try:
                    del self.frame[player.steam_id]
                except KeyError:
                    player.tell("^1There is no timer started.")
            else:
                self.frame[player.steam_id] = self.current_frame
        return minqlx.RET_STOP_ALL


    def cmd_reset(self, player, msg, channel):
        """Resets a players time in race. It is for when you
        complete a strafe time and you don't want it to save."""
        if player.team == "spectator":
            player.tell("^1You need to join the game to use this command.")
        else:
            player.score = 2147483647
            player.tell("Your score(time) was reset.")


    def cmd_commands(self, player, msg, channel):
        """Outputs list of race commands."""
        channel.reply("Commands: ^3!(s)pb !(s)rank !(s)top !old(s)top !(s)all !(s)ranktime !(s)avg !randommap !recent")
        channel.reply("^3!voterandom !goto !savepos !loadpos !maps !haste !removehaste !timer !stoptimer")
        return minqlx.RET_STOP_ALL


    def output_times(self, map_name, times, channel):
        """Outputs times to the channel. Will split lines
        so that each record is on one line only.
        :param map_name: Map name
        :param times: List of map times
        :param channel: Channel to reply to
        """
        output = ["^2{}:".format(map_name)]
        for time in times:
            if len(output[len(output) - 1]) + len(time) < 100:
                output[len(output) - 1] += time
            else:
                output.append(time)

        for out in output:
            channel.reply(out.lstrip())


    @minqlx.thread
    def get_maps(self):
        """Gets the list of race maps from QLRace.com and
        adds current map to the list if it isn't already.
        API Doc: https://qlrace.com/apidoc/1.0/Maps/maps.html
        """
        try:
            self.maps = requests.get("https://qlrace.com/api/maps").json()["maps"]
            self.old_maps = requests.get("{}/maps.json".format(OLDTOP_URL)).json()["maps"]
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

        current_map = self.game.map.lower()
        if current_map not in self.maps:
            self.maps.append(current_map)


    def map_prefix(self, map_prefix, old=False):
        """Returns the first map which matches the prefix.
        :param map_prefix: Prefix of a map
        :param old: Optional, whether to use old maps list.
        """
        if old:
            maps = self.old_maps
        else:
            maps = self.maps

        if map_prefix.lower() in maps:
            return map_prefix.lower()

        return next((x for x in maps if x.startswith(map_prefix.lower())), None)


    def get_map_name_weapons(self, map_prefix, command, channel):
        """Returns map name and weapons boolean.
        :param map_prefix: Prefix of a map
        :param command: Command the player entered
        :param channel: Channel to reply to.
        """
        map_name = self.map_prefix(map_prefix)
        if not map_name:
            channel.reply("^2No map found for ^3{}. ^2If this is wrong, ^6!updatemaps".format(map_prefix))
            return minqlx.RET_STOP_EVENT
        weapons = False if command[1].lower() == "s" else True
        return map_name, weapons


    def get_records(self, map_name, weapons, mode=None):
        """Returns race records from QLRace.com
        :param map_name: Map name
        :param weapons: Weapons boolean
        :param mode: If not None use this arg as the mode instead of the current mode
        """
        if mode is not None:
            return RaceRecords(map_name, mode)
        elif weapons:
            mode = self.get_cvar("qlx_raceMode", int)
            return RaceRecords(map_name, mode)
        else:
            mode = self.get_cvar("qlx_raceMode", int) + 1
            return RaceRecords(map_name, mode)


    def brand_map(self, map_name):
        """Brands map title with "<qlx_raceBrand> - map name".
        :param map_name: Current map
        """
        brand_map = "{} - {}".format(self.get_cvar("qlx_raceBrand"), map_name)
        minqlx.set_configstring(3, brand_map)


    @staticmethod
    def time_ms(time_string):
        """Returns time in milliseconds.
        :param time_string: Time as a string, examples 2.300, 1:12.383
        """
        minutes, seconds = (["0"] + time_string.split(":"))[-2:]
        return int(60000 * int(minutes) + round(1000 * float(seconds)))


    @staticmethod
    def time_string(time):
        """Returns a time string in the format s.ms or m:s.ms if time is more than
        or equal to 1 minute.
        :param time: Time in milliseconds
        """
        time = int(time)
        s, ms = divmod(time, 1000)
        ms = str(ms).zfill(3)
        if s < 60:
            return "{}.{}".format(s, ms)
        m, s = divmod(s, 60)
        s = str(s).zfill(2)
        return "{}:{}.{}".format(m, s, ms)


class RaceRecords:
    """Race records object. Gets records using QLRace.com API."""

    def __init__(self, map_name, mode):
        self.map_name = map_name.lower()
        self.mode = mode
        self.weapons = True if mode % 2 == 0 else False
        self.records = self.get_data()
        self.last_rank = len(self.records)
        if self.records:
            self.first_time = self.records[0]["time"]

    def rank(self, rank):
        """Returns name, actual rank and time of the rank.
        :param rank: Rank of a record
        """
        try:
            record = self.records[rank - 1]
        except IndexError:
            return None, None, None

        name = record["name"]
        actual_rank = record["rank"]
        time = record["time"]
        return name, actual_rank, time

    def rank_from_time(self, time):
        """Returns the rank the time would be.
        :param time: Time in milliseconds
        """
        for i, record in enumerate(self.records):
            if time <= record["time"]:
                return i + 1

    def pb(self, player_id):
        """Returns a players rank and time.
        :param player_id: Player id
        """
        for record in self.records:
            if player_id == record["player_id"]:
                time = record["time"]
                rank = record["rank"]
                return rank, time
        return None, None

    def output(self, name, rank, time, tied=False):
        """Returns record output with time difference to world record.
        :param name: Name of the player
        :param rank: Rank of the record
        :param time: Time of the record
        :param tied: Whether the record is tied with anyone else
        """
        if rank != 1:
            time_diff = str(time - self.first_time)
            time_diff = time_diff.zfill(3)
            time_diff = "^0[^1+" + race_test. time_string(time_diff) + "^0]"
        else:
            time_diff = ""
        time = race_test. time_string(time)
        strafe = "^2(strafe)" if not self.weapons else ""
        tied = "tied " if tied else ""
        return "^7{} ^2is {}rank ^3{} ^2of ^3{} ^2with ^3{}{} ^2on ^3{}{}" \
            .format(name, tied, rank, self.last_rank, time, time_diff, self.map_name, strafe)

    def get_data(self):
        """Returns the records for the map and mode from QLRace.com
        API Doc: https://qlrace.com/apidoc/1.0/records/map.html"""
        try:
            r = requests.get("https://qlrace.com/api/map/{}".format(self.map_name), params=PARAMS[self.mode])
            r.raise_for_status()
            return r.json()["records"]
        except requests.exceptions.RequestException:
            return []
