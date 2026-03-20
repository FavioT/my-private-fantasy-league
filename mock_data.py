# Mock data para desarrollo - Evita llamadas repetidas a la API de ESPN

MOCK_TEAMS = [
    {
        "id": 1,
        "name": "Team Alpha",
        "wins": 15,
        "losses": 8
    },
    {
        "id": 2,
        "name": "Thunder Squad",
        "wins": 14,
        "losses": 9
    },
    {
        "id": 3,
        "name": "Ballers United",
        "wins": 13,
        "losses": 10
    },
    {
        "id": 4,
        "name": "Hoop Dreams",
        "wins": 12,
        "losses": 11
    },
    {
        "id": 5,
        "name": "Court Kings",
        "wins": 11,
        "losses": 12
    },
    {
        "id": 6,
        "name": "Slam Dunk Masters",
        "wins": 10,
        "losses": 13
    },
    {
        "id": 7,
        "name": "Fast Break",
        "wins": 9,
        "losses": 14
    },
    {
        "id": 8,
        "name": "Rim Rockers",
        "wins": 8,
        "losses": 15
    }
]

MOCK_PLAYERS = {
    1: {
        "teamName": "Team Alpha",
        "players": [
            {"playerId": 1, "name": "LeBron James", "position": "SF", "team": "LAL", "injured": False, "injuryStatus": None},
            {"playerId": 2, "name": "Stephen Curry", "position": "PG", "team": "GSW", "injured": False, "injuryStatus": None},
            {"playerId": 3, "name": "Kevin Durant", "position": "SF", "team": "PHX", "injured": False, "injuryStatus": None},
            {"playerId": 7, "name": "Giannis Antetokounmpo", "position": "PF", "team": "MIL", "injured": False, "injuryStatus": None},
            {"playerId": 5, "name": "Luka Doncic", "position": "PG", "team": "DAL", "injured": False, "injuryStatus": None},
            {"playerId": 4, "name": "Joel Embiid", "position": "C", "team": "PHI", "injured": True, "injuryStatus": "Out - Knee"},
            {"playerId": 8, "name": "Jayson Tatum", "position": "SF", "team": "BOS", "injured": False, "injuryStatus": None},
            {"playerId": 9, "name": "Anthony Davis", "position": "PF", "team": "LAL", "injured": False, "injuryStatus": None},
            {"playerId": 10, "name": "Damian Lillard", "position": "PG", "team": "MIL", "injured": False, "injuryStatus": None},
            {"playerId": 11, "name": "Nikola Jokic", "position": "C", "team": "DEN", "injured": False, "injuryStatus": None}
        ]
    },
    2: {
        "teamName": "Thunder Squad",
        "players": [
            {"playerId": 12, "name": "Shai Gilgeous-Alexander", "position": "PG", "team": "OKC", "injured": False, "injuryStatus": None},
            {"playerId": 6, "name": "Kawhi Leonard", "position": "SF", "team": "LAC", "injured": True, "injuryStatus": "Day to Day - Load Management"},
            {"playerId": 13, "name": "Trae Young", "position": "PG", "team": "ATL", "injured": False, "injuryStatus": None},
            {"playerId": 14, "name": "Bam Adebayo", "position": "C", "team": "MIA", "injured": False, "injuryStatus": None},
            {"playerId": 15, "name": "Devin Booker", "position": "SG", "team": "PHX", "injured": False, "injuryStatus": None},
            {"playerId": 16, "name": "Jimmy Butler", "position": "SF", "team": "MIA", "injured": False, "injuryStatus": None},
            {"playerId": 17, "name": "Ja Morant", "position": "PG", "team": "MEM", "injured": False, "injuryStatus": None},
            {"playerId": 18, "name": "Paul George", "position": "SF", "team": "LAC", "injured": False, "injuryStatus": None},
            {"playerId": 19, "name": "Karl-Anthony Towns", "position": "C", "team": "NYK", "injured": False, "injuryStatus": None},
            {"playerId": 20, "name": "Donovan Mitchell", "position": "SG", "team": "CLE", "injured": False, "injuryStatus": None}
        ]
    },
    3: {
        "teamName": "Ballers United",
        "players": [
            {"name": "Jaylen Brown", "position": "SG", "team": "BOS", "injured": False, "injuryStatus": None},
            {"name": "Zion Williamson", "position": "PF", "team": "NOP", "injured": True, "injuryStatus": "Out - Hamstring"},
            {"name": "Brandon Ingram", "position": "SF", "team": "NOP", "injured": False, "injuryStatus": None},
            {"name": "CJ McCollum", "position": "SG", "team": "NOP", "injured": False, "injuryStatus": None},
            {"name": "De'Aaron Fox", "position": "PG", "team": "SAC", "injured": False, "injuryStatus": None},
            {"name": "Tyrese Haliburton", "position": "PG", "team": "IND", "injured": False, "injuryStatus": None},
            {"name": "Pascal Siakam", "position": "PF", "team": "IND", "injured": False, "injuryStatus": None},
            {"name": "Domantas Sabonis", "position": "C", "team": "SAC", "injured": False, "injuryStatus": None},
            {"name": "Jalen Brunson", "position": "PG", "team": "NYK", "injured": False, "injuryStatus": None},
            {"name": "Julius Randle", "position": "PF", "team": "NYK", "injured": False, "injuryStatus": None}
        ]
    },
    4: {
        "teamName": "Hoop Dreams",
        "players": [
            {"name": "LaMelo Ball", "position": "PG", "team": "CHA", "injured": False, "injuryStatus": None},
            {"name": "Cade Cunningham", "position": "PG", "team": "DET", "injured": False, "injuryStatus": None},
            {"name": "Paolo Banchero", "position": "PF", "team": "ORL", "injured": False, "injuryStatus": None},
            {"name": "Franz Wagner", "position": "SF", "team": "ORL", "injured": False, "injuryStatus": None},
            {"name": "Scottie Barnes", "position": "SF", "team": "TOR", "injured": False, "injuryStatus": None},
            {"name": "Evan Mobley", "position": "PF", "team": "CLE", "injured": False, "injuryStatus": None},
            {"name": "Darius Garland", "position": "PG", "team": "CLE", "injured": False, "injuryStatus": None},
            {"name": "Alperen Sengun", "position": "C", "team": "HOU", "injured": False, "injuryStatus": None},
            {"name": "Jalen Green", "position": "SG", "team": "HOU", "injured": False, "injuryStatus": None},
            {"name": "Fred VanVleet", "position": "PG", "team": "HOU", "injured": False, "injuryStatus": None}
        ]
    },
    5: {
        "teamName": "Court Kings",
        "players": [
            {"name": "Kyrie Irving", "position": "PG", "team": "DAL", "injured": False, "injuryStatus": None},
            {"name": "Bradley Beal", "position": "SG", "team": "PHX", "injured": False, "injuryStatus": None},
            {"name": "Kristaps Porzingis", "position": "C", "team": "BOS", "injured": True, "injuryStatus": "Questionable - Ankle"},
            {"name": "Tyler Herro", "position": "SG", "team": "MIA", "injured": False, "injuryStatus": None},
            {"name": "Terry Rozier", "position": "PG", "team": "MIA", "injured": False, "injuryStatus": None},
            {"name": "Nikola Vucevic", "position": "C", "team": "CHI", "injured": False, "injuryStatus": None},
            {"name": "DeMar DeRozan", "position": "SF", "team": "CHI", "injured": False, "injuryStatus": None},
            {"name": "Coby White", "position": "PG", "team": "CHI", "injured": False, "injuryStatus": None},
            {"name": "Jaren Jackson Jr.", "position": "PF", "team": "MEM", "injured": False, "injuryStatus": None},
            {"name": "Desmond Bane", "position": "SG", "team": "MEM", "injured": False, "injuryStatus": None}
        ]
    },
    6: {
        "teamName": "Slam Dunk Masters",
        "players": [
            {"name": "Victor Wembanyama", "position": "C", "team": "SAS", "injured": False, "injuryStatus": None},
            {"name": "Devin Vassell", "position": "SG", "team": "SAS", "injured": False, "injuryStatus": None},
            {"name": "Anfernee Simons", "position": "PG", "team": "POR", "injured": False, "injuryStatus": None},
            {"name": "Jerami Grant", "position": "PF", "team": "POR", "injured": False, "injuryStatus": None},
            {"name": "Jamal Murray", "position": "PG", "team": "DEN", "injured": False, "injuryStatus": None},
            {"name": "Michael Porter Jr.", "position": "SF", "team": "DEN", "injured": False, "injuryStatus": None},
            {"name": "Chris Paul", "position": "PG", "team": "GSW", "injured": False, "injuryStatus": None},
            {"name": "Andrew Wiggins", "position": "SF", "team": "GSW", "injured": False, "injuryStatus": None},
            {"name": "Draymond Green", "position": "PF", "team": "GSW", "injured": False, "injuryStatus": None},
            {"name": "Klay Thompson", "position": "SG", "team": "GSW", "injured": False, "injuryStatus": None}
        ]
    },
    7: {
        "teamName": "Fast Break",
        "players": [
            {"name": "Mikal Bridges", "position": "SF", "team": "NYK", "injured": False, "injuryStatus": None},
            {"name": "OG Anunoby", "position": "SF", "team": "NYK", "injured": False, "injuryStatus": None},
            {"name": "Jarrett Allen", "position": "C", "team": "CLE", "injured": False, "injuryStatus": None},
            {"name": "Lauri Markkanen", "position": "PF", "team": "UTA", "injured": False, "injuryStatus": None},
            {"name": "Jordan Clarkson", "position": "SG", "team": "UTA", "injured": False, "injuryStatus": None},
            {"name": "Collin Sexton", "position": "PG", "team": "UTA", "injured": False, "injuryStatus": None},
            {"name": "Walker Kessler", "position": "C", "team": "UTA", "injured": False, "injuryStatus": None},
            {"name": "John Collins", "position": "PF", "team": "UTA", "injured": False, "injuryStatus": None},
            {"name": "Jordan Poole", "position": "SG", "team": "WAS", "injured": False, "injuryStatus": None},
            {"name": "Kyle Kuzma", "position": "PF", "team": "WAS", "injured": False, "injuryStatus": None}
        ]
    },
    8: {
        "teamName": "Rim Rockers",
        "players": [
            {"name": "Zach LaVine", "position": "SG", "team": "CHI", "injured": True, "injuryStatus": "Out - Foot"},
            {"name": "Marcus Smart", "position": "PG", "team": "MEM", "injured": False, "injuryStatus": None},
            {"name": "Jrue Holiday", "position": "PG", "team": "BOS", "injured": False, "injuryStatus": None},
            {"name": "Derrick White", "position": "PG", "team": "BOS", "injured": False, "injuryStatus": None},
            {"name": "Al Horford", "position": "C", "team": "BOS", "injured": False, "injuryStatus": None},
            {"name": "Malcolm Brogdon", "position": "PG", "team": "POR", "injured": False, "injuryStatus": None},
            {"name": "Clint Capela", "position": "C", "team": "ATL", "injured": False, "injuryStatus": None},
            {"name": "Dejounte Murray", "position": "PG", "team": "ATL", "injured": False, "injuryStatus": None},
            {"name": "Brook Lopez", "position": "C", "team": "MIL", "injured": False, "injuryStatus": None},
            {"name": "Khris Middleton", "position": "SF", "team": "MIL", "injured": False, "injuryStatus": None}
        ]
    }
}
