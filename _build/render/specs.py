"""Shared render specs (plain Python, imported by both system Python/PIL and Blender).

Units: paddle dimensions in inches (converted to metres in Blender).
Colours are sRGB hex; Blender converts to linear.
"""

PALETTE = {
    "kitchen": "#173A2E", "court": "#2E5E4A", "chalk": "#F4F0E6", "sand": "#E7DFCF",
    "optic": "#D9F24F", "clay": "#D0663F", "ink": "#13201B", "coral": "#EC7A5C",
    "glacier": "#9ED2E4", "charcoal": "#2A2F2D", "navy": "#1F3550", "blue": "#2F6FA8",
    "pink": "#F08DB0", "forest": "#1F4A3C",
}
P = PALETTE

# shape: (total length, width, handle length, top corner radius, bottom corner radius)
SHAPES = {
    "standard": (16.0, 7.5, 5.0, 1.55, 2.4),
    "elongated": (16.5, 7.4, 5.5, 1.35, 2.0),
    "widebody": (15.6, 8.1, 4.8, 1.9, 2.8),
    "hybrid": (16.25, 7.6, 5.25, 1.5, 2.2),
    "junior": (14.6, 7.0, 4.4, 1.5, 2.3),
}

# base: carbon | raw | solid | wood ; pattern: band | lines | split | chevron | dots | signature
PADDLES = {
    "TS-KLC16-VOLT": dict(shape="standard", thick=16, base="carbon", base_col=P["charcoal"], accent=P["optic"],
                          ink=P["chalk"], pattern="lines", title="KITCHEN LINE", sub="CARBON 16",
                          edge=P["charcoal"], grip=P["ink"]),
    "TS-KLC16-CORAL": dict(shape="standard", thick=16, base="carbon", base_col=P["charcoal"], accent=P["coral"],
                           ink=P["chalk"], pattern="lines", title="KITCHEN LINE", sub="CARBON 16",
                           edge=P["charcoal"], grip=P["ink"]),
    "TS-KLC16-GLACIER": dict(shape="standard", thick=16, base="carbon", base_col=P["charcoal"], accent=P["glacier"],
                             ink=P["chalk"], pattern="lines", title="KITCHEN LINE", sub="CARBON 16",
                             edge=P["charcoal"], grip=P["ink"]),
    "TS-APX14": dict(shape="elongated", thick=14, base="raw", base_col="#1C1E1F", accent=P["clay"],
                     ink=P["chalk"], pattern="band", title="APEX", sub="ELONGATED 14",
                     edge="#151617", grip=P["clay"]),
    "TS-DZC16": dict(shape="widebody", thick=16, base="solid", base_col=P["forest"], accent=P["optic"],
                     ink=P["chalk"], pattern="chevron", title="DROP ZONE", sub="CONTROL 16",
                     edge=P["kitchen"], grip=P["chalk"]),
    "TS-SIG-RAW": dict(shape="hybrid", thick=16, base="raw", base_col="#18191A", accent=P["optic"],
                       ink=P["chalk"], pattern="signature", title="SIGNATURE", sub="RAW CARBON 16",
                       edge="#111213", grip=P["ink"]),
    "TS-HYB13": dict(shape="hybrid", thick=13, base="carbon", base_col=P["navy"], accent=P["glacier"],
                     ink=P["chalk"], pattern="split", title="ERNE HYBRID", sub="13",
                     edge=P["navy"], grip=P["glacier"]),
    "TS-BLP14": dict(shape="elongated", thick=14, base="solid", base_col="#B9472F", accent=P["charcoal"],
                     ink=P["chalk"], pattern="band", title="BASELINE", sub="POWER 14",
                     edge="#3A1F18", grip=P["charcoal"]),
    "TS-DCF": dict(shape="standard", thick=16, base="solid", base_col=P["chalk"], accent=P["forest"],
                   ink=P["forest"], pattern="lines", title="DINK CLUB", sub="FIBERGLASS",
                   edge=P["forest"], grip=P["forest"]),
    "TS-ROOK": dict(shape="widebody", thick=13, base="solid", base_col=P["blue"], accent=P["optic"],
                    ink=P["chalk"], pattern="dots", title="ROOKIE", sub="REC COMPOSITE",
                    edge="#1E4A72", grip=P["ink"]),
    "TS-JR": dict(shape="junior", thick=13, base="solid", base_col=P["optic"], accent=P["forest"],
                  ink=P["forest"], pattern="band", title="JUNIOR", sub="SPARK",
                  edge=P["forest"], grip=P["forest"]),
    "TS-WOOD": dict(shape="standard", thick=10, base="wood", base_col="#C9A57A", accent=P["kitchen"],
                    ink=P["kitchen"], pattern="signature", title="CLASSIC", sub="ASH TRAINER",
                    edge=None, grip="#6B4A2F"),
    "TS-WTR": dict(shape="standard", thick=16, base="raw", base_col="#1A1B1C", accent=P["clay"],
                   ink=P["chalk"], pattern="split", title="COACH", sub="WEIGHTED TRAINER",
                   edge="#121314", grip=P["clay"], weights=True),
}

BALL_COLOURS = {
    "optic": "#D7EE3A", "orange": "#F08A2B", "glow": "#E6F7C8", "pink": "#F38DB4", "white": "#F2F0EA",
}
