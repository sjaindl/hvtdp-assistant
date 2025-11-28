from dataclasses import dataclass
from typing import List

@dataclass
class GetToolSpec:
    name: str
    description: str
    url: str

HVTDP_API_GET_SPECS: List[GetToolSpec] = [
    GetToolSpec(
        name="Tabelle",
        description="Liefert die Tabellen für alle Saisonen.",
        url="https://www.hvtdpstainz.at/api/getStandings.php?llm=true",
    ),
    GetToolSpec(
        name="Pappfans",
        description="Liefert eine Liste an Pappfans.",
        url="https://www.hvtdpstainz.at/api/getPappfans.php?llm=true",
    ),
    GetToolSpec(
        name="Vereinsveranstaltungen",
        description="Übersicht über alle vergangenen Vereinsveranstaltungen.",
        url="https://www.hvtdpstainz.at/api/getPhotos.php?llm=true",
    ),
    GetToolSpec(
        name="Fanshop",
        description="Liefert Daten aus dem Fanshop.",
        url="https://www.hvtdpstainz.at/api/getItems.php?llm=true",
    ),
    GetToolSpec(
        name="Fördernde_Mitglieder",
        description="Liefert eine Liste an fördernden Mitgliedern des HV TDP Stainz.",
        url="https://www.hvtdpstainz.at/api/getSupportMembership.php?llm=true",
    ),
    GetToolSpec(
        name="Spieler",
        description="Gibt eine Liste an aktiven Spielern im Kader des HV TDP Stainz zurück",
        url="https://www.hvtdpstainz.at/api/getSquadPlayers.php?llm=true",
    ),
    GetToolSpec(
        name="Inaktive_Spieler",
        description="Gibt eine Liste der Spieler im Ruhestand des HV TDP Stainz zurück.",
        url="https://www.hvtdpstainz.at/api/getActivePlayers.php?llm=true",
    ),

    GetToolSpec(
        name="Torschützen",
        description="Liefert eine Übersicht über Torschützen des HV TDP nach Spiel",
        url="https://www.hvtdpstainz.at/api/getGames.php?llm=true",
    ),
    GetToolSpec(
        name="Tor_des_Jahres",
        description="Liefert das Ergebnis zur Abstimmung zum Tor des Jahres",
        url="https://www.hvtdpstainz.at/api/getGoalOfTheSeason.php?llm=true",
    ),
    GetToolSpec(
        name="Matchballspenden",
        description="Liefert eine Liste aller Matchballspenden",
        url="https://www.hvtdpstainz.at/api/getDonations.php?llm=true",
    ),
    GetToolSpec(
        name="Vorstand",
        description="Gibt Infos über den Vorstand des HV TDP Stainz",
        url="https://www.hvtdpstainz.at/api/getChefs.php?llm=true",
    ),
    GetToolSpec(
        name="Aktive_Mitglieder",
        description="Liefert eine Liste von Mitgliedern des HV TDP Stainz",
        url="https://www.hvtdpstainz.at/api/getActiveMembership.php?llm=true",
    ),
    GetToolSpec(
        name="Spieler der Saison",
        description="Ergebnis der Abstimmung zum Spieler der Saison 2024",
        url="https://www.hvtdpstainz.at/api/getPlayerOfTheSeason.php?llm=true",
    ),
]
