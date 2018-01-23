#!/bin/bash
# dicts with specific settings for every server
declare -A server_1=( [hostname]="QLRace.com GOOSY - Classic (VQL) #1" \
		      [tags]="qlrace, race, qlrace.com, DE, vql" \
		      [maxClients]="16" \
		      [password]="mafia" \
		      [raceMode]="2")
declare -A server_2=( [hostname]="QLRace.com HYDRA - Classic (VQL) #2" \
		      [tags]="qlrace, race, qlrace.com, DE, vql" \
		      [maxClients]="16" \
		      [password]="mafia" \
		      [raceMode]="2")
declare -A server_3=( [hostname]="QLRace.com TUNA - Turbo (PQL) #1" \
		      [tags]="qlrace, race, qlrace.com, DE, pql" \
		      [maxClients]="16" \
		      [password]="mafia" \
		      [raceMode]="0")
declare -A server_4=( [hostname]="QLRace.com DRAGON - Turbo (PQL) #2" \
		      [tags]="qlrace, race, qlrace.com, DE, pql" \
		      [maxClients]="16" \
		      [password]="mafia" \
		      [raceMode]="0")
declare -A server_5=( [hostname]="QLRace.com FOXY - CTF Classic" \
		      [tags]="qlrace, race, qlrace.com, DE, vql, ctf" \
		      [maxClients]="12" \
		      [password]="mafia" \
		      [raceMode]="2")
declare -A server_6=( [hostname]="QLRace.com KIDDO - CTF Turbo" \
		      [tags]="qlrace, race, qlrace.com, DE, pql, ctf" \
		      [maxClients]="12" \
		      [password]="mafia" \
		      [raceMode]="0")
declare -A server_7=( [hostname]="QLRace.com ET - Classic (VQL)" \
		      [tags]="qlrace, race, qlrace.com, DE, vql, et" \
		      [maxClients]="16" \
		      [password]="" \
		      [raceMode]="2")
declare -A server_8=( [hostname]="QLRace.com SORGY - Testserver" \
		      [tags]="qlrace, race, qlrace.com, DE, test" \
		      [maxClients]="8" \
		      [password]="mafia" \
		      [raceMode]="2")