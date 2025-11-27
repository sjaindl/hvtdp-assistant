from dataclasses import dataclass, field
from typing import List

@dataclass
class EndpointSpec:
    """Configuration for a single REST endpoint."""
    url: str
    type: str
    exclude_fields: List[str] = field(default_factory=list)
    description: str = ""
    important: bool = False
    summarize: bool = False

newsSpec = EndpointSpec(
    url = "https://www.hvtdpstainz.at/api/getNews.php",
    type = "news",
    exclude_fields = ["imagePath", "imagePathHome"],
    description = "Alle News des HV TDP Stainz. Entweder als plain news oder htmlNews.",
    important = False,
    summarize = True
)

fullSpecs = [
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getChefs.php",
        type = "vorstand",
        exclude_fields = ["imagePath"],
        description = "Liste an Vereinsfunktionären",
        important = True,
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getActiveMembership.php",
        type = "activeMembers",
        exclude_fields = [""],
        description = "Liste an aktiven Vereinsmitgliedern zum Stichtag",
        important = True,
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getSupportMembership.php",
        type = "supportMembers",
        exclude_fields = [""],
        description = "Liste an fördernden Vereinsmitgliedern zum Stichtag",
        important = True,
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getSquadPlayers.php",
        type = "squadPlayers",
        exclude_fields = ["imagePath"],
        description = "Übersicht aller Spieler im Meisterschaftskader: Gespielte Position, Beitrittsdatum und Namen",
        important = True,
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getActivePlayers.php",
        type = "activePlayers",
        exclude_fields = ["imagePath"],
        description = "Übersicht der weiteren aktiven Vereinsmitglieder, die nicht mehr im Meisterschaftskader sind: Gespielte Position, Beitrittsdatum und Namen",
        important = True,
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getDonations.php",
        type = "donations",
        exclude_fields = ["imagePath", "matchBallImagePath"],
        description = "Übersicht der Matchballspenden an den Verein inkl. Spender, das gesponserte Spiel und Datum",
        important = True,
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getPhotos.php",
        type = "events",
        exclude_fields = ["photos", "albumId"],
        description = "Übersicht der Vereinsveranstaltungen mit Saison und Datum",
        important = True,
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getGames.php",
        type = "games",
        exclude_fields = ["goalOfSeasonCandidate", "link", "gameId"],
        description = "Übersicht aller Spiele des HV TDP pro Saison inkl. Torschützen",
        important = True,
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getScorers.php",
        type = "scorers",
        exclude_fields = [""],
        description = "Zusammengefasste Liste mit Summe der Tore pro Spieler und Saison",
        important = True,
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getTicker.php",
        type = "tickers",
        exclude_fields = [""],
        description = "Das nächste wichtige Event des HV TDP Stainz",
        important = True,
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getGoalOfTheSeason.php",
        type = "goalOfSeason",
        exclude_fields = [""],
        description = "Das Umfrageergebnis der Wahl zum Tor der Saison 2024 mit genauen Stimmanzahlen",
        important = False,
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getPlayerOfTheSeason.php",
        type = "playerOfSeason",
        exclude_fields = [""],
        description = "Das Umfrageergebnis der Wahl zum Spieler der Saison 2024 mit genauen Stimmanzahlen",
        important = False,
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getItems.php",
        type = "fanshop",
        exclude_fields = ["imagePath"],
        description = "Das Sortiment aus dem Fanshop des HV TDP Stainz",
        important = True,
    ),

    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getPappfans.php",
        type = "pappfans",
        exclude_fields = ["imagePath"],
        description = "Zur Zeit von COVID waren keine Fans im Stadion erlaubt, aber es war möglich Pappfiguren zu erwerben und als Fans auf der Tribüne zu platzieren. Hier ist die Liste der Käufer der Pappfans.",
        important = False,
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getStandings.php",
        type = "standings",
        exclude_fields = [""],
        description = "Die Platzierungen bzw. Tabelle aller Mannschaften mit Anzahl der Siege, Niederlagen, Unentschieden, Punkte, Anzahl der Spiele und der Tordifferenz pro Saison.",
        important = True,
    ),
    newsSpec,
]
