{
    "name": "Tournaments",
    "summary": "Tournaments",
    "description": "Tournaments",
    "category": "Tournaments",
    "version": "18.0.0.0.0",
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
        "security/models/game.xml",
        "security/models/match.xml",
        "security/models/platform.xml",
        "security/models/token.xml",
        "security/models/tournament.xml",

        "views/game.xml",
        "views/match.xml",
        "views/platform.xml",
        "views/token.xml",
        "views/tournament.xml",

        "actions/game.xml",
        "actions/match.xml",
        "actions/platform.xml",
        "actions/token.xml",
        "actions/tournament.xml",

        "menu/items.xml"
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
}
