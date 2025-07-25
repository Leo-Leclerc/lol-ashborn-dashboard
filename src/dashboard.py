import os
import time
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv

from .riot import get_summoner_info, get_rank_info, get_match_ids, get_match_details
from .sheets import open_sheet
from .charts import create_or_update_chart

load_dotenv()

def update_joueurs():
    ws = open_sheet("Joueurs")
    ws.clear()
    ws.append_row(["Nom", "PUUID", "Niveau", "Rang", "Winrate", "Dernière activité"])

    names = ws.col_values(1)[1:] or ["AshbornTop", "AshbornJgl", "AshbornMid", "AshbornAdc", "AshbornSup"]

    for name in names:
        summoner = get_summoner_info(name)
        summoner_id = summoner["id"]
        puuid = summoner["puuid"]
        level = summoner["summonerLevel"]

        rank = get_rank_info(summoner_id)
        if rank:
            tier, div, wins, losses = rank["tier"], rank["rank"], rank["wins"], rank["losses"]
            winrate = f"{round(wins / (wins + losses) * 100)}%"
            rang = f"{tier} {div}"
        else:
            winrate, rang = "0%", "UNRANKED"

        ws.append_row([name, puuid, level, rang, winrate, datetime.utcnow().strftime("%Y-%m-%d")])
        time.sleep(1)

def update_matchs():
    ws = open_sheet("Joueurs")
    names = ws.col_values(1)[1:]
    match_ws = open_sheet("Matchs")
    match_ws.clear()
    match_ws.append_row(["Date", "Match ID", "Type", "Champion", "KDA", "Durée", "Victoire", "Nom Joueur"])

    for name in names:
        puuid = get_summoner_info(name)["puuid"]
        for mid in get_match_ids(puuid):
            m = get_match_details(mid)
            info = m["info"]
            date = datetime.utcfromtimestamp(info["gameStartTimestamp"] / 1000).strftime("%Y-%m-%d")
            duration = info["gameDuration"] // 60
            mode = info["gameMode"]

            for p in info["participants"]:
                if p["puuid"] == puuid:
                    kda = round((p["kills"] + p["assists"]) / max(p["deaths"], 1), 2)
                    win = "Oui" if p["win"] else "Non"
                    match_ws.append_row([date, mid, mode, p["championName"], kda, duration, win, name])
                    break
            time.sleep(1)

def update_analyse():
    match_ws = open_sheet("Matchs")
    rows = match_ws.get_all_records()
    stats = defaultdict(lambda: {"k": 0, "d": 0, "w": 0, "t": 0, "c": 0})

    for r in rows:
        name = r["Nom Joueur"]
        stats[name]["k"] += float(r["KDA"])
        stats[name]["d"] += 1
        stats[name]["w"] += 1 if r["Victoire"] == "Oui" else 0
        stats[name]["t"] += 1
        stats[name]["c"] += 1 if r["Type"] == "CUSTOM" else 0

    ana_ws = open_sheet("Analyse")
    ana_ws.clear()
    ana_ws.append_row(["Nom Joueur", "KDA Moyen", "% Victoires", "Nombre de Matchs", "Customs joués"])
    for name, data in stats.items():
        kda_avg = round(data["k"] / data["d"], 2) if data["d"] else 0
        winrate = f"{round(data['w'] / data['t'] * 100)}%" if data["t"] else "0%"
        ana_ws.append_row([name, kda_avg, winrate, data["t"], data["c"]])

def update_evolution():
    evo_ws = open_sheet("Évolution")
    match_ws = open_sheet("Matchs")
    evo_ws.clear()
    evo_ws.append_row(["Date", "Nom Joueur", "KDA", "Victoire", "Nb matchs cumulés"])

    rows = match_ws.get_all_records()
    for r in rows:
        evo_ws.append_row([
            r["Date"],
            r["Nom Joueur"],
            float(r["KDA"]),
            1 if r["Victoire"] == "Oui" else 0,
            ""
        ])

def update_dashboard():
    update_joueurs()
    update_matchs()
    update_analyse()
    update_evolution()
    create_or_update_chart()
    print("✅ Dashboard Ashborn mis à jour avec graphique.")
