# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Map settings plugin for qlrace.
Contains the old settings to be used for existing maps and is able to load settings from pk3s.
"""

import minqlx
import os
from zipfile import ZipFile
import configparser

# server pk3 root directory
PK3_ROOT = "D:\Libraries\Documents\pycharmprojects\\newqlrace\\testdata"
# Dict with default settings for .race files.
# Settings defaulting to None will use the server's current cvar setting as their default value.
RACE_FILE_SETTINGS_DEFAULTS = {
    'infinite_ammo': 0,
    'weapons': 3,
    'mg_ammo': 100,
    'sg_ammo': None,
    'gl_ammo': None,
    'rl_ammo': None,
    'lg_ammo': None,
    'rg_ammo': None,
    'pg_ammo': None,
    'bfg_ammo': None,
    'ng_ammo': None,
    'pl_ammo': None,
    'hmg_ammo': None,
    'haste_duration': 0,
    'quad_duration': 0,
    'battlesuit_duration': 0,
    'regeneration_duration': 0,
    'flight_fuel': 0,
    'max_flight_fuel': 16000,
    'self_damage': 0,
    'goto_disabled': 0
}


class racemapsettings(minqlx.Plugin):
    # Maps with the !goto command disabled.
    GOTO_DISABLED = ["ndql", "bounce", "df_coldrun", "wernerjump", "puzzlemap", "track_comp", "track_comp_barriers",
                     "track_comp_weap", "gl", "10towers", "acc_donut"]
    # Maps to give haste on.
    HASTE = ["df_handbreaker4", "handbreaker4_long", "handbreaker", "df_piyofunjumps", "funjumpsmap", "df_luna",
             "insane1",
             "bounce", "df_nodown", "df_etleague", "df_extremepkr", "labyrinth", "airmaxjumps", "sarcasmjump",
             "criclejump",
             "df_verihard", "cursed_temple", "skacharohuth", "randommap", "just_jump_2", "just_jump_3", "criclejump",
             "eatme", "wernerjump", "bloodydave", "tranquil", "et_map2", "et_map3", "et_map4", "et_map5", "zeel_ponpon",
             "snorjumpb1", "snorjump2", "piyojump2", "woftct", "apex", "runkull", "snakejumps2", "applejump_b1",
             "zerojumps_b1", "bumblbee", "r7_golem", "r7_endless", "mj_xlarve", "airmaxjumps2", "alexjumps",
             "brokenrun",
             "modcomp019", "redemption", "r7_hui", "buttscar", "alkpotehasteweaps", "mistes_acr16", "bull_runner",
             "dfwc2017_6", "hastedick", "hastedick_slick", "r7_bfgf"]
    # Maps to give quad and haste on.
    QUAD_HASTE = ["r7_bfgf"]
    # Maps using only gauntlet.
    G_ONLY = ["k4n", "ndql", "dfwc_xlarve", "kairos_jackson", "acc_donut", "concentration", "l1thrun", "gnj_torture4",
              "glados",
              "dfwc2017_2", "elco_eh", "elco_kab", "elco_woody", "hyper_atmospace", "dfwc2017_4"]
    # Maps using bfg with infinite ammo.
    BFG = ["lick_ape", "lick_revived", "lick_revived2"]
    # Maps to apply respawn loop fix on. Forces a delay between respawns.
    RESPAWN_FIX = ["cuddles_3"]
    # Maps to enable self-damage on.
    DMFLAGS = ["odessa", "gpl_arcaon", "rdk_14_fix", "rdk_18", "rdk_18_slick", "rdk_spiral", "dfwc2017_6", "dfwc04_2",
               "cuddles_6"]
    # Maps to give 30 sec of battlesuit on.
    BATTLESUIT30 = ["gpl_arcaon"]
    # Maps to give gauntlet and mg on.
    G_AND_MG = ["blockworld", "caep4", "climbworld", "df_etleague", "df_extremepkr", "df_handbreaker4", "df_lickape",
                "df_lickfudge", "df_lickhq", "df_lickrevived", "df_lickrevived2", "df_licksux", "df_nodown",
                "df_o3jvelocity", "df_palmslane", "df_piyofunjumps", "df_qsnrun", "df_verihard", "drtrixiipro",
                "hangtime",
                "ingus", "marvin", "northrun", "pea_impostor", "poptart", "purpletorture", "r7_pyramid", "raveroll",
                "sl1k_tetris_easy", "snorjumpb1", "sodomia", "timelock2", "timelock4", "vanilla_03", "vanilla_04",
                "vanilla_07", "vanilla_10", "walkathon", "weirdwild", "wraiths", "yellowtorture", "run139",
                "inder_inder",
                "quartz", "timelock3", "daytime", "blub", "aa_lum", "kairos_nosf", "aa_torture", "cube_torture",
                "track_comp", "track_comp_barriers", "dfru_xlarve", "track", "gl", "qportal", "heaven_or_hell",
                "cpu_egypt",
                "bug4", "sunsetpads", "hangtime2", "hangy67", "jjm2", "thisisamap", "telemaze", "xt4zy_nextone", "jrng",
                "10towers", "daanstrafe01", "daanstrafe02", "daanstrafe03", "xt4zy_trythis", "inder_stalker2",
                "kairos_torture1", "kairos_torture2", "kairos_torture3", "boris_torture2", "daanstrafe04",
                "daanstrafe05",
                "climborama", "daanstrafe07", "timewaste", "dfwc2014_2", "dkr14", "brokenrun", "discord", "adrenaline",
                "acab", "fulltorture", "effect_rust7", "frcup13",
                "brofist", "fulltorture", "fatus_le_grand", "kairos_daedalus", "stumpf", "bangtime", "run_afk",
                "fatus_le_baton", "hightime", "stones",
                "scream_dead", "cyberkitten_run1", "tamb9", "r7_a", "r7_blade", "r7_confort", "r7_daemond",
                "r7_factory",
                "r7_geoff", "r7_ka1n", "r7_luminator",
                "r7_mud", "r7_nork", "r7_pain_easy", "r7_praet", "r7_q3dm15run", "r7_sands", "r7_snow", "r7_tower",
                "r7_trail", "r7_udhk", "r7_verdant", "r7_wild",
                "r7_yellow", "r7_zot", "r7_crashiq", "stammer_bridges", "hereannh_powerslick", "srr_powerslick",
                "aa_fuxed",
                "parkourushi", "exe_05", "mu_rks",
                "run_wrecker1", "bdfcomp050_10", "r7_mini", "laa_laa", "po", "dipsy", "tinkiwinki", "inderusty",
                "boris_redan", "dfwc2017_1", "tilestrafes", "zeel_uminati", "inder_strangeland", "odessa", "chile9",
                "chile13", "chile15", "chile18", "chile20", "chile25", "gpl_strangeland_strafe", "architects_grinders2",
                "boroda", "gpl_arcaon_fix", "j4n_govno", "kabcorp_snapvan", "redblueline_combo", "rdk_14_fix", "rdk_18",
                "rdk_18_slick", "rdk_spiral", "stammer_licorice", "dark_temple", "e_penetration", "pornstar_run22",
                "tsd_rocket",
                "bdfcomp042", "dfwc2017_6", "dfwc04_2", "cuddles_7", "cuddles_8", "cuddles_6", "eksha_p0thunter",
                "jolly_holiday", "lick_shit", "lick_sux", "lick_torr"]
    # Maps to give gauntlet, mg, pg, rl and gl on.
    G_MG_PG_RL_GL = ["moonstone", "ump1ctf1", "ump1ctf2", "ump1ctf3", "ump1ctf4", "ump1ctf5", "ump1ctf6", "ump1ctf7",
                     "ump1ctf8",
                     "ump3ctf1", "ump3ctf2", "ump3ctf3", "ump3ctf4", "ump3ctf5", "ump3ctf6", "ump3ctf7", "coldwarctf",
                     "halterra1",
                     "kineterra1", "map_dreadnought", "map_leviathan", "map_tahuge", "q3ctfp22mav", "nor3ctf1",
                     "q3f_swamp",
                     "fi_ctf1m", "ump2ctf2", "ump2ctf3", "ump2ctf4", "ump2ctf5"]
    # Maps to give pg on.
    PG = ["think1", "xproject", "plasmax", "wub_junk", "pgultimate", "tinyplams", "df_lickcells", "df_lickcells2",
          "mj_xlarve", "huntetris", "modcomp019", "creed", "prince_quake2", "bdfcomp041", "r7_godz", "r7_noobclimb",
          "j4n_pgb", "elco_gbparadise", "flat_pgb", "kabcorp_longknight_pgb", "mu_mpitz", "ppgb", "azyme_gb",
          "prince_quake", "raus_egypt", "lick_fudge", "lick_cells", "lick_cells2"]
    # Maps to give rl on.
    RL = ["runstolfer", "charon", "charon_bw", "kozmini1", "kozmini2", "kozmini3", "kozmini4", "kozmini5", "kozmini6",
          "kozmini7", "kozmini8", "jumpspace", "pornstarghost2", "mistes_acr16", "futs_bunker_df",
          "futs_bunker_slick_df",
          "mu_gp", "mu_gpl_slick", "wdc03", "sdc30", "cityrocket_fixed", "inder_rocketrun", "killua_hykon",
          "bug11", "bug11_slick", "bug22", "bug22_slick", "cliff15", "lick_ass", "lick_google", "lick_longer", "lick_max",
          "lick_sewage"]
    # Maps to give gl on.
    GL = ["grenadorade", "uprising", "xlarve06", "vivid"]
    # Disabled maps (ie duplicate or broken maps). These can't be voted.
    DISABLED_MAPS = ["q3w2", "q3w3", "q3w5", "q3w7", "q3wcp1", "q3wcp14", "q3wcp17", "q3wcp18",
                     "q3wcp22", "q3wcp23", "q3wcp5", "q3wcp9", "q3wxs1", "q3wxs2", "wintersedge",
                     "red_planet_escape_1", "ump3ctf4"]

    def __init__(self):
        super().__init__()
        self.add_hook("map", self.handle_map)
        self.add_hook("vote_called", self.handle_vote_called)
        self.add_hook("player_spawn", self.handle_player_spawn)
        self.add_hook("client_command", self.handle_client_command)
        self.add_command(("haste", "removehaste"), self.cmd_haste)

        # Scan pk3s for .race map settings files.
        self.settings_files = {}
        self.index_race_map_settings_files()
        # Set to true if map settings were loaded from a .race file.
        # In that case the below class variables are to be used instead of looking
        # up settings in a hard coded list.
        self.using_race_file = False
        # Holds powerup durations for current map
        self.quad_duration = 0
        self.haste_duration = 0
        self.battlesuit_duration = 0
        self.regeneration_duration = 0
        self.flight_fuel = 0
        # Is set to true if goto is disabled on the current map
        self.goto_disabled = False
        # Is set to true when self damage is disabled on the current map
        self.self_damage = False

    def handle_map(self, map_name, factory):
        """Sets correct starting weapons and ammo on map load."""
        if self.game.factory not in ("qlrace_classic", "qlrace_turbo"):
            return
        # Look for .race map settings file and use that if it exists
        # Otherwise fall back to the old method
        try:
            settings_dict = self.parse_race_map_settings_file(map_name)
            self.apply_race_map_settings(settings_dict)
            # Apply settings that need to be applied regardless of map
            # These were taken from old_handle_map
            if self.get_cvar("qlx_raceMode", int) == 0:
                self.set_cvar("g_velocity_gl", "800")
                self.set_cvar("pmove_rampJump", "1")
                self.set_cvar("g_knockback_rl_self", "1.2")
                self.set_cvar("pmove_jumptimedeltamin", "100.0")
            elif self.get_cvar("qlx_raceMode", int) == 2:
                self.set_cvar("pmove_rampJump", "0")
                self.set_cvar("g_knockback_rl_self", "1.0")
            if "puzzlemap" in self.plugins:
                minqlx.unload_plugin("puzzlemap")
            self.set_cvar("g_respawn_delay_min", "10")
            self.set_cvar("g_respawn_delay_max", "10")
            self.set_cvar("pmove_noPlayerClip", "1")
            self.set_cvar("g_knockback_gl_self", "1.10")
            self.set_cvar("g_knockback_pg_self", "1.3")
            if not self.self_damage:
                self.set_cvar("g_battlesuitDampen", "0.25")
            self.set_cvar("g_startinghealthbonus", "0")
        except ValueError:
            # No .race file exists
            self.using_race_file = False
            self.old_handle_map(map_name, factory)

    def old_handle_map(self, map_name, factory):
        self.set_starting_weapons(map_name)
        self.set_starting_ammo(map_name)
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

        if map_name in self.DMFLAGS:
            self.set_cvar("dmflags", "0")
            self.set_cvar("g_battleSuitDampen", "0")
            self.set_cvar("g_dropPowerups", "0")
        else:
            self.set_cvar("dmflags", "28")
        # Set to fix issues with getting in a dying loop on respawn
        if map_name in self.RESPAWN_FIX:
            self.set_cvar("g_respawn_delay_max", "9999")

    def set_starting_weapons(self, map_name):
        if map_name in self.G_AND_MG:
            self.set_cvar("g_startingWeapons", "3")
            infinite = "1" if map_name in ("poptart", "climbworld", "qportal") else "0"
            self.set_cvar("g_infiniteAmmo", infinite)
        elif map_name in self.GL:
            self.set_cvar("g_startingWeapons", "11")
            infinite = "0" if map_name in ("uprising", "xlarve06", "vivid") else "1"
            self.set_cvar("g_infiniteAmmo", infinite)
        elif map_name in self.G_ONLY:
            self.set_cvar("g_startingWeapons", "1")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name in self.BFG:
            self.set_cvar("g_startingWeapons", "257")
            self.set_cvar("g_infiniteAmmo", "1")
        elif map_name in self.PG:
            self.set_cvar("g_startingWeapons", "131")
            infinite = "0" if map_name in ("mj_xlarve", "raus_egypt") else "1"
            self.set_cvar("g_infiniteAmmo", infinite)
        elif map_name in self.G_MG_PG_RL_GL:
            self.set_cvar("g_startingWeapons", "155")
            self.set_cvar("g_infiniteAmmo", "1")
        elif map_name == "modcomp019":
            self.set_cvar("g_startingWeapons", "200")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name in self.RL:
            self.set_cvar("g_startingWeapons", "19")
            infinite = "0" if map_name in ("pornstarghost2", "mistes_acr16") else "1"
            self.set_cvar("g_infiniteAmmo", infinite)
        elif map_name == "lick_gays":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_startingAmmo_rl", "3")
            self.set_cvar("g_infiniteAmmo", "0")
        elif map_name == "lick_girls":
            self.set_cvar("g_startingWeapons", "19")
            self.set_cvar("g_startingAmmo_rl", "25")
            self.set_cvar("g_infiniteAmmo", "0")
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
            map_name = args.split()[0]
            if map_name.lower() in self.DISABLED_MAPS:
                player.tell("^3{} ^2is disabled(duplicate map).".format(map_name))
                return minqlx.RET_STOP_ALL

    def handle_player_spawn(self, player):
        """Give powerups based on the map."""
        map_name = self.game.map.lower()
        if player.team == "free":
            if self.using_race_file:
                kwargs = {}
                if self.quad_duration > 0:
                    kwargs['quad'] = self.quad_duration
                if self.haste_duration > 0:
                    kwargs['haste'] = self.haste_duration
                if self.regeneration_duration > 0:
                    kwargs['regeneration'] = self.regeneration_duration
                if self.battlesuit_duration > 0:
                    kwargs['battlesuit'] = self.battlesuit_duration
                player.powerups(**kwargs)
                if self.flight_fuel:
                    player.flight(fuel=self.flight_fuel)
            else:
                # No .race file loaded, use old method
                if map_name == "wsm":
                    player.powerups(quad=999999)
                elif map_name == "mega_12":
                    player.powerups(quad=999999)
                elif map_name in self.HASTE:
                    player.powerups(haste=999999)
                elif map_name in self.QUAD_HASTE:
                    player.powerups(haste=999999)
                    player.powerups(quad=999999)
                elif map_name in self.BATTLESUIT30:
                    player.powerups(battlesuit=30)
                elif map_name == "bokluk":
                    player.flight(fuel=3500, max_fuel=3500)
                elif map_name == "kraglejump":
                    player.powerups(haste=60)  # some stages need haste and some don't, so 60 is a compromise...

    def handle_client_command(self, player, cmd):
        """Spawns player right away if they use /kill and self damage is disabled."""
        if cmd == "kill" and player.team == "free":
            map_name = self.game.map.lower()
            if map_name not in self.DMFLAGS or self.using_race_file and not self.self_damage:
                minqlx.player_spawn(player.id)

    def cmd_haste(self, player, msg, channel):
        """Gives/removes haste on haste maps."""
        if player.team == "spectator":
            player.tell("^1You cannot use ^3{} ^1as a spectator!".format(msg[0]))
            return minqlx.RET_STOP_ALL

        if self.game.map.lower() in self.HASTE:
            duration = 0 if "remove" in msg[0].lower() else 999999
            player.powerups(haste=duration)
        else:
            player.tell("^1You cannot use ^3{} ^1on non haste maps.".format(msg[0]))
        return minqlx.RET_STOP_ALL

    def index_race_map_settings_files(self):
        """Search all pk3s in the pk3 root for <bsp_name>.race files.

        Returns:
            dict -- {key=bsp_name: value=pk3_path, ...}
        """
        # get paths to all pk3 files on the server
        pk3_paths = []
        for directory in [d for d in os.listdir(PK3_ROOT) if os.path.isdir(os.path.join(PK3_ROOT, d))]:
            pk3_paths += [os.path.join(PK3_ROOT, directory, x) for x in os.listdir(os.path.join(PK3_ROOT, directory))
                          if '.pk3' in x]
        # store available .race files.
        self.settings_files = {}
        for pk3_path in pk3_paths:
            with ZipFile(pk3_path, 'r') as pk3:
                # get the map names
                map_names = [os.path.splitext(x.split('/')[-1])[0] for x in pk3.namelist() if '.bsp' in x]
                # look for any corresponding .race files
                for file in pk3.namelist():
                    name, ext = os.path.splitext(file.split('/')[-1])
                    if ext == '.race' and name in map_names:
                        self.settings_files[name] = pk3_path

    def parse_race_map_settings_file(self, map_name):
        """Reads the map settings to be used from the .race file.
        Any optional settings that are undefined are given a default value.
        This function is to be called during handle_map

        Params:
            map_name (str) -- the name of the map/bsp file

        Returns:
            dict -- {key=setting, value=value}

        Raises:
            ValueError -- when map_name is not in self.settings_files
        """
        # Check if a .race file for the map exists
        try:
            pk3_path = self.settings_files[map_name]
        except KeyError:
            raise ValueError(f'{map_name} supplied no .race map settings file')
        # Open map_name.race in the pk3 and extract the settings
        with ZipFile(pk3_path, 'r') as pk3:
            # Insert a dummy section header so we can use the built in configparser module.
            config_string = '[dummy section]\n' + pk3.read(f'{map_name}.race').decode('utf-8')
        config = configparser.ConfigParser()
        config.read_string(config_string)
        settings_dict = dict(config.items('dummy section'))
        # Assign default values to undefined settings
        omitted_settings = list(filter(lambda x: x not in list(settings_dict.keys()),
                                       list(RACE_FILE_SETTINGS_DEFAULTS.keys())))
        settings_dict.update({x: RACE_FILE_SETTINGS_DEFAULTS[x] for x in omitted_settings})
        return settings_dict

    def apply_race_map_settings(self, settings_dict):
        """Applies all settings in the given settings_dict to the server"""
        # Set infiniteammo
        self.set_cvar('g_infiniteAmmo', str(settings_dict['infinite_ammo']))
        # Set starting weapons
        self.set_cvar('g_startingWeapons', str(settings_dict['weapons']))
        # Set starting ammo
        if settings_dict['mg_ammo'] is not None:
            self.set_cvar('g_startingAmmo_mg', str(settings_dict['mg_ammo']))
        if settings_dict['sg_ammo'] is not None:
            self.set_cvar('g_startingAmmo_sg', str(settings_dict['sg_ammo']))
        if settings_dict['gl_ammo'] is not None:
            self.set_cvar('g_startingAmmo_gl', str(settings_dict['gl_ammo']))
        if settings_dict['rl_ammo'] is not None:
            self.set_cvar('g_startingAmmo_rl', str(settings_dict['rl_ammo']))
        if settings_dict['lg_ammo'] is not None:
            self.set_cvar('g_startingAmmo_lg', str(settings_dict['lg_ammo']))
        if settings_dict['rg_ammo'] is not None:
            self.set_cvar('g_startingAmmo_rg', str(settings_dict['rg_ammo']))
        if settings_dict['pg_ammo'] is not None:
            self.set_cvar('g_startingAmmo_pg', str(settings_dict['pg_ammo']))
        if settings_dict['bfg_ammo'] is not None:
            self.set_cvar('g_startingAmmo_bfg', str(settings_dict['bfg_ammo']))
        if settings_dict['ng_ammo'] is not None:
            self.set_cvar('g_startingAmmo_ng', str(settings_dict['ng_ammo']))
        if settings_dict['pl_ammo'] is not None:
            self.set_cvar('g_startingAmmo_pl', str(settings_dict['pl_ammo']))
        if settings_dict['hmg_ammo'] is not None:
            self.set_cvar('g_startingAmmo_hmg', str(settings_dict['hmg_ammo']))
        # Save powerup durations
        # These are given on player spawn by handle_player_spawn
        self.quad_duration = min(int(settings_dict['quad_duration']), 999999)
        self.haste_duration = min(int(settings_dict['haste_duration']), 999999)
        self.battlesuit_duration = min(int(settings_dict['battlesuit_duration']), 999999)
        self.regeneration_duration = min(int(settings_dict['regeneration_duration']), 999999)
        self.flight_fuel = int(settings_dict['flight_fuel'])
        if settings_dict['max_flight_fuel'] is not None:
            self.set_cvar("g_maxFlightFuel", str(settings_dict['max_flight_fuel']))
        # Self damage settings
        if int(settings_dict['self_damage']) == 1:
            self.set_cvar("dmflags", "0")
            self.set_cvar("g_battleSuitDampen", "0")
            self.set_cvar("g_dropPowerups", "0")
            self.self_damage = True
        else:
            self.set_cvar("dmflags", "28")
            self.self_damage = False
        # Goto settings
        if int(settings_dict['goto_disabled']) == 1:
            self.goto_disabled = True
        else:
            self.goto_disabled = False
        self.using_race_file = True
