"""Which repos stand in the city, and the palettes it is drawn in."""

OWNER = "New1Direction"

# Left to right. Flagship towers get a taller spire and a coral sign.
TOWERS = [
    {"repo": "korg", "url": "https://github.com/New1Direction/korg"},
    {"repo": "OntologyEX", "url": "https://github.com/New1Direction/OntologyEX"},
    {"repo": "ningen-shikkaku", "url": "https://github.com/New1Direction/ningen-shikkaku"},
    {"repo": "korgex", "url": "https://github.com/New1Direction/korgex"},
    {"repo": "repo.ing", "url": "https://repo.ing", "flagship": True},
    {"repo": "ohiyo", "url": "https://ohiyo.gg", "flagship": True},
    {"repo": "webmcp-anything", "url": "https://github.com/New1Direction/webmcp-anything"},
    {"repo": "RepoLens", "url": "https://github.com/New1Direction/RepoLens"},
    {"repo": "okto", "url": "https://github.com/New1Direction/okto"},
    {"repo": "thumper", "url": "https://github.com/New1Direction/thumper"},
]

# Night for GitHub's dark theme, dawn for its light theme.
THEMES = {
    "dark": {
        "sky": ["#0b0a17", "#1a1430", "#43203a", "#c24a33"],
        "ink": "#f6f1e7",
        "soft": "#a9a4c2",
        "accent": "#ff7a59",
        "spark": "#7ad7f0",
        "cell_a": "#1c1733",
        "cell_b": "#241d40",
        "lit_star": "#ff7a59",
        "lit_guest": "#f6f1e7",
        "ground": "#2b2545",
        "orb": "#f6f1e7",
        "glow": "#ff7a59",
    },
    "light": {
        "sky": ["#cfd9f2", "#f3d9cf", "#ffd1b3", "#ffb38a"],
        "ink": "#2a2440",
        "soft": "#6b6585",
        "accent": "#e2553a",
        "spark": "#2f7f9c",
        "cell_a": "#e6dfd0",
        "cell_b": "#dcd4c2",
        "lit_star": "#e2553a",
        "lit_guest": "#33473c",
        "ground": "#cfc7b4",
        "orb": "#fff6e6",
        "glow": "#ff9d6e",
    },
}
