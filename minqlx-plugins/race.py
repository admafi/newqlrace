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

GOTO_DISABLED = ("ndql", "bounce", "df_coldrun", "wernerjump", "puzzlemap", "track_comp", "track_comp_barriers",
                 "track_comp_weap", "gl", "10towers", "acc_donut")
HASTE = ("df_handbreaker4", "handbreaker4_long", "handbreaker", "df_piyofunjumps", "funjumpsmap", "df_luna", "insane1",
         "bounce", "df_nodown", "df_etleague", "df_extremepkr", "labyrinth", "airmaxjumps", "sarcasmjump", "criclejump",
         "df_verihard", "cursed_temple", "skacharohuth", "randommap", "just_jump_2", "just_jump_3", "criclejump",
         "eatme", "wernerjump", "bloodydave", "tranquil", "et_map2", "et_map3", "et_map4", "et_map5", "zeel_ponpon",
         "snorjumpb1", "snorjump2", "piyojump2", "woftct", "apex", "runkull", "snakejumps2", "applejump_b1",
         "zerojumps_b1", "bumblbee", "r7_golem", "r7_endless", "mj_xlarve", "airmaxjumps2", "alexjumps", "brokenrun",
         "modcomp019", "redemption", "r7_hui", "buttscar", "alkpotehasteweaps", "mistes_acr16", "bull_runner",
         "dfwc2017_6", "hastedick", "hastedick_slick")

# physics strings used for vql and pql args on rank and related functions
PHYSICS_PQL_STRINGS = ['pql', 'turbo', 'p', 't']
PHYSICS_VQL_STRINGS = ['vql', 'classic', 'v', 'c']
PHYSICS_STRINGS = PHYSICS_PQL_STRINGS + PHYSICS_VQL_STRINGS

G_ONLY = (
    "k4n", "ndql", "dfwc_xlarve", "kairos_jackson", "acc_donut", "concentration", "l1thrun", "gnj_torture4", "glados",
    "dfwc2017_2", "elco_eh", "elco_kab", "elco_woody", "hyper_atmospace", "dfwc2017_4")
BFG_FIX = ("aa_endless")
# Fixes respawn death loops by delaying auto respawn
RESPAWN_FIX = ("cuddles_3")
DMFLAGS = {"odessa", "gpl_arcaon", "rdk_14_fix", "rdk_18", "rdk_18_slick", "rdk_spiral", "dfwc2017_6", "dfwc04_2",
           "cuddles_6"}
BATTLESUIT30 = {"gpl_arcaon"}
G_AND_MG = ("blockworld", "caep4", "climbworld", "df_etleague", "df_extremepkr", "df_handbreaker4", "df_lickape",
            "df_lickfudge", "df_lickhq", "df_lickrevived", "df_lickrevived2", "df_licksux", "df_nodown",
            "df_o3jvelocity", "df_palmslane", "df_piyofunjumps", "df_qsnrun", "df_verihard", "drtrixiipro", "hangtime",
            "ingus", "marvin", "northrun", "pea_impostor", "poptart", "purpletorture", "r7_pyramid", "raveroll",
            "sl1k_tetris_easy", "snorjumpb1", "sodomia", "timelock2", "timelock4", "vanilla_03", "vanilla_04",
            "vanilla_07", "vanilla_10", "walkathon", "weirdwild", "wraiths", "yellowtorture", "run139", "inder_inder",
            "quartz", "timelock3", "daytime", "blub", "aa_lum", "kairos_nosf", "aa_torture", "cube_torture",
            "track_comp", "track_comp_barriers", "dfru_xlarve", "track", "gl", "qportal", "heaven_or_hell", "cpu_egypt",
            "bug4", "sunsetpads", "hangtime2", "hangy67", "jjm2", "thisisamap", "telemaze", "xt4zy_nextone", "jrng",
            "10towers", "daanstrafe01", "daanstrafe02", "daanstrafe03", "xt4zy_trythis", "inder_stalker2",
            "kairos_torture1", "kairos_torture2", "kairos_torture3", "boris_torture2", "daanstrafe04", "daanstrafe05",
            "climborama", "daanstrafe07", "timewaste", "dfwc2014_2", "dkr14", "brokenrun", "discord", "adrenaline",
            "acab", "fulltorture", "effect_rust7", "frcup13",
            "brofist", "fulltorture", "fatus_le_grand", "kairos_daedalus", "stumpf", "bangtime", "run_afk",
            "fatus_le_baton", "hightime", "stones",
            "scream_dead", "cyberkitten_run1", "tamb9", "r7_a", "r7_blade", "r7_confort", "r7_daemond", "r7_factory",
            "r7_geoff", "r7_ka1n", "r7_luminator",
            "r7_mud", "r7_nork", "r7_pain_easy", "r7_praet", "r7_q3dm15run", "r7_sands", "r7_snow", "r7_tower",
            "r7_trail", "r7_udhk", "r7_verdant", "r7_wild",
            "r7_yellow", "r7_zot", "r7_crashiq", "stammer_bridges", "hereannh_powerslick", "srr_powerslick", "aa_fuxed",
            "parkourushi", "exe_05", "mu_rks",
            "run_wrecker1", "bdfcomp050_10", "r7_mini", "laa_laa", "po", "dipsy", "tinkiwinki", "inderusty",
            "boris_redan", "dfwc2017_1", "tilestrafes", "zeel_uminati", "inder_strangeland", "odessa", "chile9",
            "chile13", "chile15", "chile18", "chile20", "chile25", "gpl_strangeland_strafe", "architects_grinders2",
            "boroda", "gpl_arcaon_fix", "j4n_govno", "kabcorp_snapvan", "redblueline_combo", "rdk_14_fix", "rdk_18",
            "rdk_18_slick", "rdk_spiral", "stammer_licorice", "dark_temple", "e_penetration", "pornstar_run22", "tsd_rocket",
            "bdfcomp042", "dfwc2017_6", "dfwc04_2", "cuddles_7", "cuddles_8", "cuddles_6")

PG = ("think1", "xproject", "plasmax", "wub_junk", "pgultimate", "tinyplams", "df_lickcells", "df_lickcells2",
      "mj_xlarve", "huntetris", "modcomp019", "creed", "prince_quake2", "bdfcomp041", "r7_godz", "r7_noobclimb",
      "j4n_pgb", "elco_gbparadise", "flat_pgb", "kabcorp_longknight_pgb", "mu_mpitz", "ppgb", "azyme_gb",
      "prince_quake", "raus_egypt")
RL = ("runstolfer", "charon", "charon_bw", "kozmini1", "kozmini2", "kozmini3", "kozmini4", "kozmini5", "kozmini6",
      "kozmini7", "kozmini8", "jumpspace", "pornstarghost2", "mistes_acr16", "futs_bunker_df", "futs_bunker_slick_df",
      "mu_gp", "mu_gpl_slick", "wdc03", "sdc30", "cityrocket_fixed", "inder_rocketrun", "killua_hykon",
      "bug11", "bug11_slick", "bug22", "bug22_slick", "cliff15")
GL = ("grenadorade", "uprising", "xlarve06", "vivid")

_RE_POWERUPS = re.compile(r'print ".+\^3 got the (Haste|Battle Suit|Quad Damage|Invisibility|Regeneration)!\^7\n"')


class race(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("new_game", self.handle_new_game)
        self.add_hook("map", self.handle_map)
        self.add_hook("vote_called", self.handle_vote_called)
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
        self.add_command(("haste", "removehaste"), self.cmd_haste)
        self.add_command(("timer", "starttimer", "stoptimer"), self.cmd_timer)
        self.add_command(("reset", "resettime", "resetscore"), self.cmd_reset)
        self.add_command(("commands", "cmds", "help"), self.cmd_commands, priority=minqlx.PRI_HIGH)
        self.add_command("vote", self.cmd_vote_random_map, usage="<n> | Use !randommap before !vote")

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
        Also sets correct starting weapons for the map and clears savepos
        and move_player dicts.
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

        self.set_starting_weapons(map_name)
        self.set_starting_ammo(map_name)

        self.set_cvar("pmove_chainjump", "0")

        if self.get_cvar("qlx_raceMode", int) == 0:
            gl_v = "700" if map_name in ("k4n", "uprising", "jjm2", "vivid") else "800"
            self.set_cvar("g_velocity_gl", gl_v)
            ramp_jump = "0" if map_name in ("10towers", "vivid") else "1"
            self.set_cvar("pmove_rampJump", ramp_jump)
            self.set_cvar("g_knockback_rl_self", "1.2")
            self.set_cvar("pmove_jumptimedeltamin", "100.0")
        elif self.get_cvar("qlx_raceMode", int) == 2:
            ramp_jump = "1" if map_name in ("dontlookdown", "acab") else "0"
            self.set_cvar("pmove_RampJump", ramp_jump)
            self.set_cvar("g_knockback_rl_self", "1.0")

        if map_name == "puzzlemap":
            self.set_cvar("g_infiniteAmmo", "1")
            self.set_cvar("g_startingWeapons", "3")
            minqlx.load_plugin("puzzlemap")
        else:
            if "puzzlemap" in self.plugins:
                minqlx.unload_plugin("puzzlemap")

        if map_name == "walkathon":
            self.set_cvar("g_respawn_delay_min", "1000")
            self.set_cvar("g_respawn_delay_max", "1000")
        else:
            self.set_cvar("g_respawn_delay_min", "10")
            self.set_cvar("g_respawn_delay_max", "10")

        if map_name == "pornstarghost3":
            self.set_cvar("g_maxFlightFuel", "10000")
        elif map_name == "tomb":
            self.set_cvar("g_maxFlightFuel", "2500")
        elif map_name == "tatmt_long":
            self.set_cvar("g_maxFlightFuel", "500")
        elif map_name == "bokluk":
            self.set_cvar("g_maxFlightFuel", "3500")
        elif map_name == "dkr14":
            self.set_cvar("g_maxFlightFuel", "3000")
        else:
            self.set_cvar("g_maxFlightFuel", "16000")

        if map_name == "gl":
            if self.get_cvar("g_startingHealth", int) != 3000:
                self.map_restart = True
            self.set_cvar("g_startingHealth", "3000")
        else:
            self.set_cvar("g_startingHealth", "100")

        if map_name in ("track_comp", "track_comp_barriers"):
            self.set_cvar("pmove_noPlayerClip", "0")
            self.set_cvar("g_damage_g", "1")
            self.set_cvar("g_damage_mg", "1")
            self.set_cvar("g_knockback_g", "0")
            self.set_cvar("g_knockback_mg", "0")
        elif map_name == "track_comp_weap":
            self.set_cvar("pmove_noPlayerClip", "0")
            self.set_cvar("g_damage_g", "25")
            self.set_cvar("g_damage_mg", "3")
            self.set_cvar("g_damage_gl", "20")
            self.set_cvar("g_damage_rl", "20")
            self.set_cvar("g_damage_rg", "10")
            self.set_cvar("g_knockback_g", "1.2")
            self.set_cvar("g_knockback_mg", "0")
            self.set_cvar("g_knockback_gl", "1.2")
            self.set_cvar("g_knockback_gl_self", "0")
            self.set_cvar("g_knockback_rl", "1")
            self.set_cvar("g_knockback_rl_self", "0")
            self.set_cvar("g_knockback_rg", "10")
            self.set_cvar("g_splashdamage_gl", "20")
            self.set_cvar("g_splashdamage_rl", "16")
        elif map_name in (
                "cos1_beta7", "j4n_pgb", "elco_gbparadise", "flat_pgb", "kabcorp_longknight_pgb", "ppgb", "azyme_gb"):
            self.set_cvar("g_knockback_pg_self", "1.3")
        elif map_name == "gpl_arcaon":
            self.set_cvar("g_battlesuitDampen", "0")
            self.set_cvar("g_startinghealthbonus", "25")
        else:
            self.set_cvar("pmove_noPlayerClip", "1")
            self.set_cvar("g_knockback_gl_self", "1.10")
            self.set_cvar("g_knockback_pg_self", "1.3")
            self.set_cvar("g_battlesuitDampen", "0.25")
            self.set_cvar("g_startinghealthbonus", "0")

        if map_name in DMFLAGS:
            self.set_cvar("dmflags", "0")
            self.set_cvar("g_battleSuitDampen", "0")
        else:
            self.set_cvar("dmflags", "28")
        # Set to fix issues with getting in a dying loop on respawn
        if map_name in RESPAWN_FIX:
            self.set_cvar("g_respawn_delay_max", "9999")

    def set_starting_weapons(self, map_name):
        if map_name in G_AND_MG:
            self.set_cvar("g_startingWeapons", "3")
            infinite = "1" if map_name in ("poptart", "climbworld", "qportal") else "0"
            self.set_cvar("g_infiniteAmmo", infinite)
        elif map_name in GL:
            self.set_cvar("g_startingWeapons", "11")
            infinite = "0" if map_name in ("uprising", "xlarve06", "vivid") else "1"
            self.set_cvar("g_infiniteAmmo", infinite)
        elif map_name in G_ONLY:
            self.set_cvar("g_startingWeapons", "1")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name in BFG_FIX:
            self.set_cvar("weapon_reload_bfg", "200")
            self.set_cvar("g_velocity_bfg", "2000")
            self.set_cvar("g_infiniteAmmo", "1")
        elif map_name in PG:
            self.set_cvar("g_startingWeapons", "131")
            infinite = "0" if map_name in ("mj_xlarve", "raus_egypt") else "1"
            self.set_cvar("g_infiniteAmmo", infinite)
        elif map_name == "modcomp019":
            self.set_cvar("g_startingWeapons", "200")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name in RL:
            self.set_cvar("g_startingWeapons", "19")
            infinite = "0" if map_name in ("pornstarghost2", "mistes_acr16") else "1"
            self.set_cvar("g_infiniteAmmo", infinite)
        elif map_name == "elco_arca":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "slickplane2_strafe":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "slickplane2":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "rtairs":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "lovet_arcaon":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "lovet_arcaon_slick":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "rocketx":
            self.set_cvar("g_startingWeapons", "17")
            self.set_cvar("g_infiniteAmmo", "1")
        elif map_name == "bfgx":
            self.set_cvar("g_startingWeapons", "257")
            self.set_cvar("g_infiniteAmmo", "1")
        elif map_name == "chile19":
            self.set_cvar("g_startingWeapons", "257")
            self.set_cvar("g_infiniteAmmo", "1")
        elif map_name == "r7_bfgf":
            self.set_cvar("g_startingWeapons", "257")
            self.set_cvar("g_infiniteAmmo", "1")
            self.set_cvar("weapon_reload_bfg", "200")
            self.set_cvar("g_velocity_bfg", "2000")
        elif map_name == "nmn":
            self.set_cvar("g_startingWeapons", "16")
            self.set_cvar("g_infiniteAmmo", "1")
        elif map_name == "wsm":
            self.set_cvar("g_startingWeapons", "129")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "spiderman":
            self.set_cvar("g_startingWeapons", "515")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "runkull":
            self.set_cvar("g_startingWeapons", "128")
            self.set_cvar("g_infiniteAmmo", "1")
        elif map_name == "tr1ckhouse":
            self.set_cvar("g_startingWeapons", "411")
            self.set_cvar("g_infiniteAmmo", "1")
        elif map_name == "zalupa":
            self.set_cvar("g_startingWeapons", "64")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "forty2go":
            self.set_cvar("g_startingWeapons", "65")
            self.set_cvar("g_infiniteAmmo", "1")
        elif map_name == "track_comp_weap":
            self.set_cvar("g_startingWeapons", "91")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "tomb":
            self.set_cvar("g_startingWeapons", "131")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "m_und_f":
            self.set_cvar("g_startingWeapons", "17")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "bumblbee":
            self.set_cvar("g_startingWeapons", "155")
            self.set_cvar("g_infiniteAmmo", "1")
        elif map_name == "fm_2":
            self.set_cvar("g_startingWeapons", "144")
            self.set_cvar("g_startingAmmo_gl", "0")
        elif map_name == "mk_bowserscastle_slick":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "mk_bowserscastle":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "pornstar_apple":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "gpl_strangeland":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "wdc03":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_infiniteAmmo", "1")
        elif map_name == "j4n_ufgnuk":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "run4eg":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "sdc30":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_infiniteAmmo", "1")
        elif map_name == "cityrocket_fixed":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_infiniteAmmo", "1")

        else:
            self.set_cvar("g_startingWeapons", "147")
            self.set_cvar("g_infiniteAmmo", "1")

    def set_starting_ammo(self, map_name):
        if map_name == "hangtime":
            self.set_cvar("g_startingAmmo_mg", "1")
        elif map_name == "10towers":
            self.set_cvar("g_startingAmmo_mg", "-1")
        else:
            self.set_cvar("g_startingAmmo_mg", "100")

        if map_name in ("uprising", "xlarve06"):
            self.set_cvar("g_startingAmmo_gl", "1")
        elif map_name == "vivid":
            self.set_cvar("g_startingAmmo_gl", "3")
        else:
            self.set_cvar("g_startingAmmo_gl", "10")

        if map_name == "track_comp_weap":
            self.set_cvar("g_startingAmmo_rl", "10")
        elif map_name == "pornstarghost2":
            self.set_cvar("g_startingAmmo_rl", "1")
        elif map_name == "mistes_acr16":
            self.set_cvar("g_startingAmmo_rl", "4")
        elif map_name == "m_und_f":
            self.set_cvar("g_startingAmmo_rl", "5")
        elif map_name == "elco_arca":
            self.set_cvar("g_startingAmmo_rl", "2")
        elif map_name == "slickplane2_strafe":
            self.set_cvar("g_startingAmmo_rl", "4")
        elif map_name == "slickplane2":
            self.set_cvar("g_startingAmmo_rl", "4")
        elif map_name == "rtairs":
            self.set_cvar("g_startingAmmo_rl", "2")
        elif map_name == "lovet_arcaon":
            self.set_cvar("g_startingAmmo_rl", "5")
        elif map_name == "lovet_arcaon_slick":
            self.set_cvar("g_startingAmmo_rl", "5")
        elif map_name == "mk_bowserscastle_slick":
            self.set_cvar("g_startingAmmo_rl", "10")
        elif map_name == "mk_bowserscastle":
            self.set_cvar("g_startingAmmo_rl", "10")
        elif map_name == "pornstar_apple":
            self.set_cvar("g_startingAmmo_rl", "2")
        elif map_name == "gpl_strangeland":
            self.set_cvar("g_startingAmmo_rl", "20")
        elif map_name == "j4n_ufgnuk":
            self.set_cvar("g_startingAmmo_rl", "7")
        elif map_name == "run4eg":
            self.set_cvar("g_startingAmmo_rl", "10")
        else:
            self.set_cvar("g_startingAmmo_rl", "5")

        if map_name == "zalupa":
            self.set_cvar("g_startingAmmo_rg", "30")
        elif map_name == "track_comp_weap":
            self.set_cvar("g_startingAmmo_rg", "10")
        else:
            self.set_cvar("g_startingAmmo_rg", "5")

        if map_name == "wsm":
            self.set_cvar("g_startingAmmo_pg", "1")
        elif map_name == "tomb":
            self.set_cvar("g_startingAmmo_pg", "5")
        elif map_name == "mj_xlarve":
            self.set_cvar("g_startingAmmo_pg", "150")
        elif map_name == "raus_egypt":
            self.set_cvar("g_startingAmmo_pg", "80")
        elif map_name == "flat_pgb":
            self.set_cvar("g_infiniteAmmo", "0")
            self.set_cvar("g_startingAmmo_pg", "1")
        elif map_name == "kabcorp_longknight_pgb":
            self.set_cvar("g_infiniteAmmo", "0")
            self.set_cvar("g_startingAmmo_pg", "5")

        else:
            self.set_cvar("g_startingAmmo_pg", "50")

    def handle_vote_called(self, player, vote, args):
        """Cancels the vote when a duplicated map is voted for."""
        if vote.lower() == "map" and len(args) > 0:
            disabled_maps = ("q3w2", "q3w3", "q3w5", "q3w7", "q3wcp1", "q3wcp14", "q3wcp17", "q3wcp18",
                             "q3wcp22", "q3wcp23", "q3wcp5", "q3wcp9", "q3wxs1", "q3wxs2", "wintersedge",
                             "red_planet_escape_1")
            map_name = args.split()[0]
            if map_name.lower() in disabled_maps:
                player.tell("^3{} ^2is disabled(duplicate map).".format(map_name))
                return minqlx.RET_STOP_ALL

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
        """Spawns player instantly and gives quad/haste on some maps.
        Moves player to position if they used !goto or !loadpos.
        Removes player from frame dict."""
        map_name = self.game.map.lower()
        if self.map_restart:
            self.map_restart = False
            minqlx.console_command("map_restart")

        if player.team == "free":
            player.is_alive = True

            if map_name == "wsm":
                player.powerups(quad=999999)
            elif map_name == "mega_rl2":
                player.powerups(quad=999999)
            elif map_name in HASTE:
                player.powerups(haste=999999)
            elif map_name in BATTLESUIT30:
                player.powerups(battlesuit=30)
            elif map_name == "bokluk":
                player.flight(fuel=3500, max_fuel=3500)

        if player.steam_id in self.move_player and player.is_alive:
            if player.steam_id not in self.goto:
                player.tell("^6Your time will not count, unless you kill yourself.")
                self.goto[player.steam_id] = player.score

            minqlx.set_position(player.id, self.move_player.pop(player.steam_id))

            if map_name == "kraglejump":
                player.powerups(haste=60)  # some stages need haste and some don't, so 60 is a compromise...

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
        than 1. Spawns player right away if they use /kill and
        Removes them from goto and frame dicts."""
        if cmd == "readyup" and self.get_cvar("sv_warmupReadyPercentage", float) > 1:
            player.tell("readyup is disabled since sv_warmupReadyPercentage is more than 1")
            return minqlx.RET_STOP_EVENT

        if cmd == "kill" and player.team == "free":
            map_name = self.game.map.lower()
            if map_name not in DMFLAGS:
                minqlx.player_spawn(player.id)
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
            self.player(p).center_print(race.time_string(ms))

        # makes new dict with dead players removed
        self.goto = {p: score for p, score in self.goto.items() if self.player(p).health > 0}

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
                    time_diff = "+{}".format(race.time_string(record["time"] - wr))

                output.append("^3{:>2}. ^7{:30} ^3{:>10} ^1{:>12}"
                              .format(record["rank"], record["name"], race.time_string(record["time"]), time_diff))
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
                    time_diff = "+{}".format(race.time_string(record["time"] - wr))

                output.append("^3{:>2}. ^7{:30} ^3{:>10} ^1{:>12}"
                              .format(record["rank"], record["name"], race.time_string(record["time"]), time_diff))
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
                                                           race.time_string(record["time"])))
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
                          .format(race.time_string(time), rank, last_rank, map_name))

        if len(msg) == 1 and player.score != 2147483647 and player.score != 0:
            time = player.score
            map_prefix = self.game.map
        elif len(msg) == 2:
            time = race.time_ms(msg[1])
            map_prefix = self.game.map
        elif len(msg) == 3:
            time = race.time_ms(msg[1])
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
        if map_name in GOTO_DISABLED:
            player.tell("^1!goto is disabled on {}".format(map_name))
            return minqlx.RET_STOP_ALL

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
        if self.game.map.lower() in GOTO_DISABLED:
            player.tell("^1!loadpos is disabled on {}".format(self.game.map))
            return minqlx.RET_STOP_ALL

        if player.team != "spectator":
            if player.steam_id in self.savepos:
                player.score = 2147483647
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


    def cmd_haste(self, player, msg, channel):
        """Gives/removes haste on haste maps."""
        if player.team == "spectator":
            player.tell("^1You cannot use ^3{} ^1as a spectator!".format(msg[0]))
            return minqlx.RET_STOP_ALL

        if self.game.map.lower() in HASTE:
            duration = 0 if "remove" in msg[0].lower() else 999999
            player.powerups(haste=duration)
        else:
            player.tell("^1You cannot use ^3{} ^1on non haste maps.".format(msg[0]))
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
        channel.reply("^3!goto !savepos !loadpos !maps !haste !removehaste !timer !stoptimer")
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
            time_diff = "^0[^1+" + race.time_string(time_diff) + "^0]"
        else:
            time_diff = ""
        time = race.time_string(time)
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
