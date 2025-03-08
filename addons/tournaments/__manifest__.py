{
    "name": "Tournaments",
    "summary": "Tournaments",
    "description": "Tournaments",
    "category": "Tournaments",
    "version": "18.0.0.1.1",
    "license": "GPL-3",
    "sequence": 0,
    "depends": [
        "base",
        "base_setup",
        "mail",
        "web",
        "pegi",
        "maxmind_geoip2"
    ],
    "data": [
        "data/ir_module_category.xml",

        "security/profiles.xml",
        "security/models/badword.xml",
        "security/models/entrant.xml",
        "security/models/game.xml",
        "security/models/match.xml",
        "security/models/nickname.xml",
        "security/models/platform.xml",
        "security/models/token.xml",
        "security/models/tournament.xml",

        "views/badword.xml",
        "views/entrant.xml",
        "views/game.xml",
        "views/match.xml",
        "views/nickname.xml",
        "views/platform.xml",
        "views/token.xml",
        "views/tournament.xml",

        "actions/badword.xml",
        "actions/entrant.xml",
        "actions/game.xml",
        "actions/match.xml",
        "actions/nickname.xml",
        "actions/platform.xml",
        "actions/token.xml",
        "actions/tournament.xml",

        "menu/items.xml"
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
}
