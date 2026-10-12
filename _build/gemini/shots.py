"""Shot list for the Gemini (Nano Banana) product and editorial photography, 2026-10-11.

Every entry: id (= output file stem, <SKU>_<n> or an editorial name), ref (reference image or None),
aspect (Gemini aspect), crop (final W, H) and prompt. run.py generates, post.py crops into renders/jpg.
Paddles, balls packaging, bags and covers use the earlier Blender render as the design reference so
colourways, swatches and the brand mark stay identical; everything else gets the logo as reference.
"""
import os

B = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(B, '..', 'renders', 'jpg')
REF = os.path.join(B, 'refs')
LOGO = os.path.join(REF, 'logo_ref.png')


def render(name):
    return os.path.join(R, name + '.jpg')


STUDIO = ("Premium e-commerce studio product photograph, medium-format camera, 85mm lens. Seamless warm "
          "chalk-cream paper backdrop (soft off-white with a hint of sand, like #EFE8DA) that continues "
          "smoothly under the product with no horizon line. Large soft key light from the upper left, gentle "
          "fill, a soft natural contact shadow. Product centered with a generous even margin on all sides, "
          "fully in frame, nothing cropped. Crisp focus, true-to-life materials and colors, calm and minimal, "
          "no people, no extra text, no watermark.")

COURT = ("Lifestyle product photograph on a real outdoor pickleball court: deep kitchen-green acrylic hard "
         "court surface with fine sandy texture and a crisp white painted line, warm late-afternoon sun with "
         "long soft shadows, shallow depth of field, editorial sports catalogue style, true-to-life colors, "
         "no people, no extra text, no watermark.")

PADDLE_REF = ("Use the attached 3D render only as the design reference: reproduce the same face artwork, "
              "colors, the small 'Third Shot' logo mark (a dotted arc over a short net post and a ball) and the "
              "printed lettering exactly, but as a real photographed product with true pickleball paddle "
              "proportions: {shape}, a slim round 5 inch handle with a wrapped grip, a thin edge guard, "
              "realistic {face} texture and subtle surface reflections.")

SHAPE = {
    'standard': 'a classic standard shape about 16 in long and 7.5 in wide with gently rounded corners',
    'elongated': 'an elongated shape about 16.5 in long and only 7.4 in wide, noticeably slimmer than standard',
    'widebody': 'a wide-body shape about 15.75 in long and 8 in wide with softly rounded top corners',
    'hybrid': 'a hybrid shape about 16.3 in long and 7.6 in wide',
    'junior': 'a smaller youth size about 15.5 in long and 7.5 in wide with a short handle',
}

PADDLES = [
    # sku, shape, face texture, short visual description, render
    ('TS-KLC16-VOLT', 'standard', 'woven Toray carbon fiber', 'charcoal carbon face with thin volt-yellow court lines, "KITCHEN LINE / CARBON 16"', 'TS-KLC16-VOLT_1'),
    ('TS-KLC16-CORAL', 'standard', 'woven Toray carbon fiber', 'charcoal carbon face with thin coral court lines, "KITCHEN LINE / CARBON 16"', 'TS-KLC16-CORAL_1'),
    ('TS-KLC16-GLACIER', 'standard', 'woven Toray carbon fiber', 'charcoal carbon face with thin glacier-blue court lines, "KITCHEN LINE / CARBON 16"', 'TS-KLC16-GLACIER_1'),
    ('TS-APX14', 'elongated', 'matte raw T700 carbon', 'near-black raw carbon face with a diagonal clay-orange band, clay grip, "APEX / ELONGATED 14"', 'TS-APX14_1'),
    ('TS-DZC16', 'widebody', 'satin carbon-fiberglass', 'deep forest-green face with lime chevrons, cream grip, "DROP ZONE / CONTROL 16"', 'TS-DZC16_1'),
    ('TS-SIG-RAW', 'hybrid', 'matte raw T700 carbon', 'black raw carbon face with a fine optic-yellow signature line, "SIGNATURE / RAW CARBON 16"', 'TS-SIG-RAW_1'),
    ('TS-HYB13', 'hybrid', 'satin carbon-fiberglass', 'navy face with a pale glacier-blue diagonal split, glacier grip, "ERNE HYBRID 13"', 'TS-HYB13_1'),
    ('TS-BLP14', 'elongated', 'satin Toray carbon', 'brick-red face with a charcoal band, charcoal grip, "BASELINE / POWER 14"', 'TS-BLP14_1'),
    ('TS-DCF', 'standard', 'smooth fiberglass', 'chalk-white face with forest-green court lines and forest edge and grip, "DINK CLUB / FIBERGLASS"', 'TS-DCF_1'),
    ('TS-ROOK', 'widebody', 'glossy polymer composite', 'bright blue face with a pattern of small optic-yellow dots, "ROOKIE / REC COMPOSITE"', 'TS-ROOK_1'),
    ('TS-JR', 'junior', 'smooth polymer composite', 'optic-yellow face with a forest-green band, forest edge and grip, "JUNIOR / SPARK"', 'TS-JR_1'),
    ('TS-WOOD', 'standard', 'laminated natural ash wood grain (no edge guard, solid wood, a leather-brown grip)', 'pale ash wood face with a printed kitchen-green logo, "CLASSIC / ASH TRAINER"', 'TS-WOOD_1'),
    ('TS-WTR', 'standard', 'matte raw T700 carbon', 'black raw carbon face with a clay-orange diagonal split and two slim removable metal weight bars along the edges, clay grip, "COACH / WEIGHTED TRAINER"', 'TS-WTR_1'),
]


def shots():
    s = []

    def add(id, prompt, ref=None, aspect='3:4', crop=(1200, 1500), extra=None):
        s.append(dict(id=id, prompt=prompt, ref=ref, aspect=aspect, crop=crop, extra=extra or []))

    # ---------------------------------------------------------------- paddles
    for sku, shape, face, desc, rnd in PADDLES:
        base = PADDLE_REF.format(shape=SHAPE[shape], face=face)
        add(sku + '_1', f"Photorealistic studio product photo of this pickleball paddle ({desc}). {base} "
            f"The paddle stands upright, turned very slightly toward the camera, with one lime-yellow 40-hole "
            f"outdoor pickleball resting at the base of the handle. {STUDIO}", render(rnd))
        add(sku + '_2', f"Photorealistic photo of this pickleball paddle ({desc}). {base} The paddle lies "
            f"flat on the court at a diagonal next to the white kitchen line with two lime-yellow 40-hole "
            f"balls beside it, seen from above at about 50 degrees, the whole paddle in frame. {COURT}", render(rnd))
    # parent of the colourways: all three together (its own image comes after the Volt photos)
    add('TS-KLC16_1', "Photorealistic studio product photo of three identical pickleball paddles in three "
        "colourways, standing upright side by side and slightly overlapping, left to right: volt-yellow lines, "
        "coral lines, glacier-blue lines, each a charcoal woven carbon face with 'KITCHEN LINE / CARBON 16'. "
        + PADDLE_REF.format(shape=SHAPE['standard'], face='woven Toray carbon fiber') + ' ' + STUDIO,
        os.path.join(REF, 'ref_klc16_trio.jpg'))
    add('TS-SET-START_1', "Photorealistic overhead flat-lay studio photo of a starter kit laid out neatly on "
        "the backdrop: a bright blue wide-body paddle with small optic-yellow dots (like the left paddle in the "
        "reference), a forest-green zipped neoprene paddle cover, a clear tube of three lime-yellow 40-hole "
        "outdoor balls with a kitchen-green label, two rolled tacky overgrips, and an open kraft-and-forest-green "
        "shipping box with the 'Third Shot' logo printed on the lid. Keep the brand mark from the reference. "
        + STUDIO, render('TS-SET-START_1'))
    add('TS-SET-START_2', "Photorealistic studio product photo of two pickleball paddles standing side by side: "
        "a bright blue wide-body paddle with small optic-yellow dots ('ROOKIE / REC COMPOSITE') and a "
        "chalk-white fiberglass paddle with forest-green lines ('DINK CLUB / FIBERGLASS'), with a tube of "
        "three lime-yellow balls in front. Reproduce the face designs and 'Third Shot' logo from the reference "
        "with true paddle proportions and slim wrapped handles. " + STUDIO, render('TS-SET-START_1'))

    # ---------------------------------------------------------------- balls
    BALL = "lime-yellow (optic) seamless 40-hole outdoor pickleballs with crisp round holes and a fine matte texture"
    add('TS-T40-3_1', "Photorealistic studio product photo: a clear plastic tube of three " + BALL + ", "
        "kitchen-green cap and base and a kitchen-green wrap label reading 'TOUR 40' with the small Third Shot "
        "logo (as in the reference), standing upright, with one loose ball beside it. " + STUDIO, render('TS-T40-3_1'))
    add('TS-T40-3_2', "Photorealistic close-up studio photo of three " + BALL + " in a loose triangle, "
        "showing the seamless shell and 40 precise holes, macro detail. " + STUDIO, render('TS-T40-3_2'))
    add('TS-T40-12_1', "Photorealistic studio product photo of an open warm-apricot retail box holding twelve "
        + BALL + " in a 4x3 grid, the lid printed 'TOUR 40' with the Third Shot logo, as in the reference. "
        + STUDIO, render('TS-T40-12_1'))
    add('TS-T40-12_2', "Photorealistic photo of a handful of " + BALL + " scattered on the court near the "
        "white baseline. " + COURT, render('TS-T40-3_2'))
    add('TS-T40-48_1', "Photorealistic studio product photo of a kitchen-green plastic practice bucket with a "
        "wire handle and lid propped beside it, filled to the top with " + BALL + ", a few balls on the floor "
        "next to it, small Third Shot logo on the bucket as in the reference. " + STUDIO, render('TS-T40-48_1'))
    add('TS-G26-6_1', "Photorealistic studio product photo: a tidy pyramid of six softer indoor pickleballs "
        "(volt-yellow, 26 larger round holes) next to a clear tube with a clay-orange 'GYM 26' label and the "
        "Third Shot logo, as in the reference. " + STUDIO, render('TS-G26-6_1'))
    add('TS-G26-6_2', "Photorealistic photo of two volt-yellow 26-hole indoor pickleballs on a polished maple "
        "gym floor with painted court lines, soft window light, shallow depth of field, no people, no text.")
    add('TS-GLOW-3_1', "Photorealistic studio product photo: a clear tube of three pale glow-in-the-dark "
        "40-hole pickleballs (soft mint-white), dark kitchen-green cap and label reading 'TWILIGHT GLOW', with "
        "one ball beside it, as in the reference. " + STUDIO, render('TS-GLOW-3_1'))
    add('TS-GLOW-3_2', "Photorealistic photo of three glow-in-the-dark 40-hole pickleballs glowing a soft "
        "luminous green on an outdoor court at dusk, deep blue twilight sky, court lights off, the balls are the "
        "brightest thing in frame, gentle bokeh, no people, no text.")
    add('TS-T40-PINK_1', "Photorealistic studio product photo: a pyramid of six pink seamless 40-hole outdoor "
        "pickleballs beside a clear tube with a deep berry 'TOUR 40 PINK' label and the Third Shot logo, as in "
        "the reference. " + STUDIO, render('TS-T40-PINK_1'))
    add('TS-T40-PINK_2', "Photorealistic photo of three pink seamless 40-hole pickleballs resting on the court "
        "beside the white kitchen line. " + COURT, render('TS-T40-PINK_2'))
    add('TS-T40-BULK_1', "Photorealistic studio product photo of the Tour 40 range together: a kitchen-green "
        "practice bucket full of " + BALL + ", an open apricot 12-ball box and a clear 3-ball tube with a "
        "kitchen-green label, arranged as a group, Third Shot branding as in the reference. " + STUDIO,
        render('TS-T40-BULK_1'))

    # ---------------------------------------------------------------- bags & covers
    BAG = ("Use the reference for the color, the small rubber 'Third Shot' logo patch and the general design, but "
           "make it a real, well-made sewn bag with natural fabric texture, stitching, zips and webbing straps. ")
    add('TS-BAG-CLUB-FOREST_1', "Photorealistic studio product photo of a structured forest-green court "
        "backpack in recycled 600D polyester with a black water-resistant base, front zip pocket, two side "
        "paddle handles peeking from the top sleeve, standing upright, front three-quarter view. " + BAG + STUDIO,
        render('TS-BAG-CLUB-FOREST_1'))
    add('TS-BAG-CLUB-FOREST_2', "Photorealistic studio photo of the same forest-green court backpack with the "
        "main compartment unzipped and open, showing a grey fleece-lined sleeve holding two pickleball paddles, a "
        "ventilated shoe pocket at the bottom and a slim laptop sleeve. " + BAG + STUDIO, render('TS-BAG-CLUB-FOREST_1'))
    add('TS-BAG-CLUB-SAND_1', "Photorealistic studio product photo of a structured sand-beige court backpack "
        "with forest-green zips and trim and a black water-resistant base, front zip pocket, standing upright, "
        "front three-quarter view. " + BAG + STUDIO, render('TS-BAG-CLUB-SAND_1'))
    add('TS-BAG-CLUB_1', "Photorealistic photo of a forest-green court backpack hanging on a green chain-link "
        "court fence by its top loop, a paddle handle sticking out of the top sleeve, outdoor pickleball court "
        "behind, warm late-afternoon light, shallow depth of field, no people, no text. " + BAG,
        render('TS-BAG-CLUB-FOREST_1'))
    add('TS-BAG-TOUR_1', "Photorealistic studio product photo of a large charcoal tournament duffel bag in "
        "900D polyester with tan leather pull tabs, a thin optic-yellow piping stripe and a rubber Third Shot "
        "patch, two carry handles and a shoulder strap, front three-quarter view. " + BAG + STUDIO,
        render('TS-BAG-TOUR_1'))
    add('TS-BAG-TOUR_2', "Photorealistic studio photo of the same charcoal duffel with the main compartment "
        "open, showing a silver thermal-lined paddle compartment holding several paddles, and the end shoe tunnel "
        "unzipped. " + BAG + STUDIO, render('TS-BAG-TOUR_1'))
    add('TS-BAG-SLING_1', "Photorealistic studio product photo of a slim charcoal ripstop-nylon crossbody "
        "sling bag with a fleece-lined paddle sleeve (one paddle handle visible at the top), a small front zip "
        "pocket with an optic-yellow zip pull, and a black adjustable strap curving above it. " + BAG + STUDIO,
        render('TS-BAG-SLING_1'))
    add('TS-BAG-SLING_2', "Photorealistic photo of the same charcoal crossbody sling hanging from a court "
        "fence post, a paddle handle and two lime balls visible, outdoor court behind, warm afternoon light, "
        "shallow depth of field, no people, no text. " + BAG, render('TS-BAG-SLING_1'))
    COVER = ("a 3 mm neoprene pickleball paddle cover with a full zip around the edge, the paddle shape visible "
             "inside, a small printed 'Third Shot' logo as in the reference, soft neoprene texture, lying at a "
             "slight angle. ")
    add('TS-COVER-FOREST_1', "Photorealistic studio product photo of a forest-green " + COVER + STUDIO, render('TS-COVER-FOREST_1'))
    add('TS-COVER-OPTIC_1', "Photorealistic studio product photo of an optic-yellow " + COVER + STUDIO, render('TS-COVER-OPTIC_1'))
    add('TS-COVER-CLAY_1', "Photorealistic studio product photo of a clay-orange " + COVER + STUDIO, render('TS-COVER-CLAY_1'))
    add('TS-COVER_1', "Photorealistic studio product photo of three neoprene paddle covers fanned out "
        "(forest green, optic yellow, clay orange), each with a full zip and a small 'Third Shot' logo, one "
        "partly unzipped showing a carbon paddle inside. " + STUDIO, os.path.join(REF, 'ref_cover_trio.jpg'))
    add('TS-CASE_1', "Photorealistic studio product photo of a charcoal molded EVA hard-shell pickleball paddle "
        "case shaped like a paddle, with a wrap-around zip, a grab handle and a small embossed Third Shot logo "
        "(use the attached logo), closed, three-quarter view. " + STUDIO, LOGO)
    add('TS-CASE_2', "Photorealistic studio photo of the same charcoal hard-shell paddle case open like a clam, "
        "showing a soft grey felt-lined interior with a black carbon pickleball paddle inside and a mesh lid "
        "pocket holding two balls. " + STUDIO, LOGO)
    add('TS-POUCH_1', "Photorealistic studio product photo of a small forest-green neoprene ball pouch with a "
        "stainless steel carabiner clip, two lime-yellow 40-hole balls visible at its open top, small printed "
        "Third Shot logo (use the attached logo). " + STUDIO, LOGO)

    # ---------------------------------------------------------------- apparel
    LOGO_TXT = "Use the attached logo: the brand mark (dotted arc, net post and lime ball) is small and neatly embroidered, "
    CAP = ("a six-panel brushed cotton twill baseball cap with a pre-curved brim and a small embroidered Third "
           "Shot paddle-and-ball mark on the front, three-quarter front view, floating slightly with a soft shadow. ")
    add('TS-CAP-FOREST_1', "Photorealistic studio product photo of a forest-green " + CAP + LOGO_TXT + "in chalk and lime thread. " + STUDIO, LOGO)
    add('TS-CAP-CHALK_1', "Photorealistic studio product photo of a chalk off-white " + CAP + LOGO_TXT + "in kitchen-green and lime thread. " + STUDIO, LOGO)
    add('TS-CAP-CLAY_1', "Photorealistic studio product photo of a clay terracotta-orange " + CAP + LOGO_TXT + "in chalk thread. " + STUDIO, LOGO)
    add('TS-CAP_1', "Photorealistic studio product photo of three cotton twill baseball caps stacked and "
        "fanned: forest green, chalk off-white and clay terracotta, each with a small embroidered Third Shot "
        "mark. " + LOGO_TXT + "different thread colors. " + STUDIO, LOGO)
    VISOR = ("a lightweight performance sports visor with a 3 in curved brim, a terry-lined sweatband, open top "
             "and a hook-and-loop strap, a small Third Shot mark printed on the front, three-quarter front view. ")
    add('TS-VISOR-CHALK_1', "Photorealistic studio product photo of a chalk off-white " + VISOR + LOGO_TXT + "in kitchen green. " + STUDIO, LOGO)
    add('TS-VISOR-OPTIC_1', "Photorealistic studio product photo of an optic-yellow " + VISOR + LOGO_TXT + "in kitchen green. " + STUDIO, LOGO)
    add('TS-VISOR-FOREST_1', "Photorealistic studio product photo of a forest-green " + VISOR + LOGO_TXT + "in chalk and lime. " + STUDIO, LOGO)
    add('TS-VISOR_1', "Photorealistic photo of a chalk off-white sports visor resting on a pickleball paddle on "
        "the court, small Third Shot mark on the visor. " + LOGO_TXT + "in kitchen green. " + COURT, LOGO)
    add('TS-BUCKET_1', "Photorealistic studio product photo of a packable sand-beige nylon ripstop bucket hat "
        "with a 2.75 in brim, small mesh vent panels and a chin cord with a toggle, a small woven Third Shot "
        "label on the side. " + LOGO_TXT + "on a small label. " + STUDIO, LOGO)
    add('TS-BEANIE_1', "Photorealistic studio product photo of a charcoal merino rib-knit cuffed beanie, "
        "standing upright as if worn, with a small woven Third Shot label on the cuff. " + LOGO_TXT + "on the label. " + STUDIO, LOGO)
    add('TS-HEADBAND_1', "Photorealistic studio product photo of two rolled and one flat wicking sports "
        "headbands, 2 in wide, one forest green and one optic yellow, a thin silicone grip strip visible inside, "
        "small printed Third Shot mark. " + LOGO_TXT + "printed. " + STUDIO, LOGO)
    add('TS-WRIST_1', "Photorealistic studio product photo of a pair of thick chalk off-white cotton terry "
        "wristbands, 3.5 in wide, one standing and one lying, small embroidered kitchen-green Third Shot mark. "
        + LOGO_TXT + "in kitchen green. " + STUDIO, LOGO)

    # ---------------------------------------------------------------- court & training
    add('TS-NET_1', "Photorealistic photo of a regulation portable pickleball net set up on a driveway-style "
        "court: black powder-coated steel frame with wheeled feet, black polyester net with a white vinyl "
        "headband printed with a small Third Shot logo (use the attached logo), a black wheeled carry bag beside "
        "it, warm afternoon light, three-quarter view, the whole 22 ft net in frame, no people.", LOGO, '4:3',
        (1500, 1200))
    add('TS-NET_2', "Photorealistic studio product photo of a long black nylon wheeled carry bag for a portable "
        "pickleball net, with steel frame poles partly visible at the open end and a small Third Shot logo "
        "patch (use the attached logo), lying on its side. " + STUDIO, LOGO)
    add('TS-RETRIEVER_1', "Photorealistic studio product photo of a 40 in anodized aluminum pickleball ball "
        "retriever tube in kitchen green with a spring-steel pickup head at the bottom, standing upright and "
        "slightly tilted, partly filled with lime-yellow 40-hole balls visible through a slot, a few balls at its "
        "base, small Third Shot logo on the tube (use the attached logo). " + STUDIO, LOGO)
    add('TS-CONES_1', "Photorealistic studio product photo of twelve low-profile flexible dish cones in four "
        "colors (optic yellow, clay orange, forest green, chalk white), two neat stacks plus a few laid out in "
        "front, 7.5 in diameter, matte plastic. " + STUDIO)
    add('TS-LINES_1', "Photorealistic studio product photo of a court line marker kit: four rolls of 2 in white "
        "vinyl line tape and twelve small orange rubber L-shaped corner markers, arranged neatly, with a "
        "kraft-paper sleeve band printed with the Third Shot logo (use the attached logo). " + STUDIO, LOGO)
    add('TS-REBOUND_1', "Photorealistic photo of a freestanding dink rebounder net, 7 ft wide and 4 ft tall, "
        "black powder-coated steel frame with a tensioned black polyester rebound net angled slightly back, "
        "standing on an outdoor kitchen-green pickleball court with a few lime balls near it, a small Third Shot "
        "logo tag (use the attached logo), warm afternoon light, no people.", LOGO, '4:3', (1500, 1200))
    add('TS-LADDER_1', "Photorealistic photo taken from above at a steep angle of a 15 ft agility ladder with "
        "black nylon webbing and ten flat optic-yellow rungs laid straight on a kitchen-green pickleball court "
        "next to the white kitchen line, warm afternoon light, no people, no text.")

    # ---------------------------------------------------------------- accessories
    add('TS-OVERGRIP_1', "Photorealistic studio product photo of a 3-pack of tacky pickleball overgrips: a "
        "slim kitchen-green retail box with a clear window showing three rolled overgrips (white, optic yellow, "
        "black), the box printed with the Third Shot logo (use the attached logo) and 'TACKY OVERGRIP', one grip "
        "partly unrolled in front. " + STUDIO, LOGO)
    add('TS-GRIP_1', "Photorealistic studio product photo of a perforated cushioned replacement grip, black "
        "with fine perforations, half unrolled in a gentle spiral with its backing strip, next to a slim "
        "chalk-and-green packaging sleeve with the Third Shot logo (use the attached logo). " + STUDIO, LOGO)
    add('TS-EDGE_1', "Photorealistic studio product photo of a roll of clear polyurethane edge guard tape, 1 in "
        "wide, on a forest-green core with the Third Shot logo (use the attached logo), with a strip applied "
        "along the edge of a black carbon pickleball paddle lying beside it. " + STUDIO, LOGO)
    add('TS-LEAD_1', "Photorealistic studio product photo of a small roll of thin silver lead tuning tape, "
        "0.25 in wide, on a kitchen-green dispenser card printed with the Third Shot logo (use the attached "
        "logo) and fine inch markings, a few cut strips beside it. " + STUDIO, LOGO)
    add('TS-ERASER_1', "Photorealistic studio product photo of a natural honey-colored crepe rubber eraser "
        "block, 4 x 2 x 1 in, with its crinkled texture, resting on the textured face of a black raw-carbon "
        "pickleball paddle, a kraft paper band with the Third Shot logo (use the attached logo) around the block. "
        + STUDIO, LOGO)
    add('TS-BOTTLE_1', "Photorealistic studio product photo of a 24 oz double-wall stainless steel water bottle "
        "with a matte forest-green powder coat, brushed steel rim and a black loop cap, small chalk-colored "
        "printed Third Shot logo (use the attached logo), standing upright with light condensation-free finish. "
        + STUDIO, LOGO)
    add('TS-TOWEL_1', "Photorealistic studio product photo of a sand-beige waffle-weave microfiber court towel, "
        "neatly folded with a forest-green clip loop and a small woven Third Shot label (use the attached logo). "
        + STUDIO, LOGO)
    add('TS-MOUNT_1', "Photorealistic photo of a solid black walnut wall mount with two brass pegs holding two "
        "pickleball paddles (a black raw-carbon paddle and a forest-green paddle) on a warm off-white painted "
        "wall in a tidy garage game room, a small engraved Third Shot logo on the walnut (use the attached logo), "
        "soft daylight, no people.", LOGO)

    # ---------------------------------------------------------------- editorial / banners
    add('hero', "Wide cinematic photorealistic banner photo for a premium pickleball gear brand. Low angle on a "
        "deep kitchen-green outdoor pickleball court at golden hour. On the right half: three premium pickleball "
        "paddles standing upright and fanned (from the reference: black Signature raw carbon with optic line, "
        "charcoal Kitchen Line with volt lines, black Apex with a clay-orange band), with lime-yellow 40-hole "
        "balls scattered on the court in front, the net softly out of focus behind. The left 45 percent of the "
        "frame is calm, dark, softly lit green court and background with nothing in it (space for a headline). "
        "Warm rim light, rich deep greens, editorial sports photography, no people, no text, no watermark.",
        os.path.join(B, '..', '..', 'pub', 'media', 'wysiwyg', 'thirdshot', 'hero.jpg'), '16:9', (1920, 960))
    CAT = ("Photorealistic wide editorial category banner, the subject grouped in the central third of the "
           "frame with calm breathing room on all sides (it is cropped to both 4:3 and a very wide strip), warm natural light, palette of deep kitchen green, chalk cream, "
           "optic yellow and clay orange, no people, no text, no watermark. ")
    add('cat_paddles', "A fan of four premium pickleball paddles (forest green with lime chevrons, black raw "
        "carbon, navy with glacier-blue split, brick red) standing in a wooden rack on a chalk-cream workshop "
        "bench, a lime ball in front, matching the designs in the reference. " + CAT, render('TS-DZC16_1'), '16:9', (1200, 900), [('catbanner_paddles', (1600, 700))])
    add('cat_balls', "A kitchen-green practice bucket overflowing with lime-yellow 40-hole pickleballs on a "
        "green outdoor court, balls rolling out in front, low angle golden-hour light. " + CAT, render('TS-T40-48_1'), '16:9', (1200, 900), [('catbanner_balls', (1600, 700))])
    add('cat_bags', "A forest-green court backpack and a charcoal duffel sitting on a courtside bench with a "
        "paddle handle peeking out, chain-link fence and green court softly blurred behind. " + CAT,
        render('TS-BAG-CLUB-FOREST_1'), '16:9', (1200, 900), [('catbanner_bags', (1600, 700))])
    add('cat_apparel', "A forest-green cap, a chalk visor and a pair of terry wristbands arranged on a "
        "courtside bench with a folded sand towel, small embroidered Third Shot mark on the cap (use the attached "
        "logo). " + CAT, LOGO, '16:9', (1200, 900), [('catbanner_apparel', (1600, 700))])
    add('cat_training', "Training setup on a green outdoor pickleball court: four colored dish cones along "
        "the white kitchen line, a yellow-rung agility ladder and a ball retriever tube with lime balls, seen "
        "from a high angle. " + CAT, None, '16:9', (1200, 900), [('catbanner_training', (1600, 700))])
    add('cat_accessories', "Neat overhead knolling flat lay on a chalk-cream surface: tacky overgrips, a roll "
        "of edge guard tape, lead tape, a crepe rubber eraser block, a forest-green insulated bottle and a folded "
        "sand microfiber towel, branded with the small Third Shot logo (use the attached logo). " + CAT, LOGO, '16:9', (1200, 900), [('catbanner_accessories', (1600, 700))])
    add('spotlight', "Photorealistic hero product photo of this flagship pickleball paddle (black raw carbon "
        "face with a fine optic-yellow signature line, 'SIGNATURE / RAW CARBON 16'). "
        + PADDLE_REF.format(shape=SHAPE['hybrid'], face='matte raw T700 carbon') + " Standing upright against a "
        "warm chalk-cream backdrop with one lime ball at its base, dramatic but soft side light that rakes across "
        "the raw carbon weave, centered, generous margins, square composition, no text added.",
        render('TS-SIG-RAW_1'), '1:1', (1200, 1200))
    add('story', "Photorealistic overhead flat lay on a deep kitchen-green textured pickleball court surface "
        "with a white painted line crossing the frame: a black raw-carbon paddle with an optic-yellow line, three "
        "lime-yellow balls, a forest-green insulated bottle, a folded sand towel and a rolled overgrip, warm "
        "morning sun with soft long shadows, small Third Shot logo on the paddle (use the attached logo), "
        "editorial, no people, no extra text.", LOGO, '3:4', (1200, 1400))
    add('workshop', "Photorealistic interior photo of a small converted paddle workshop: a long wooden "
        "workbench under warm window light with pickleball paddles in progress (raw carbon faces, edge guard "
        "tape, grips being wrapped), a wall rack of finished paddles in green, black and clay-orange, a bucket of "
        "lime balls on the floor, tools neatly arranged, a small Third Shot logo sign on the wall (use the "
        "attached logo), calm craft atmosphere, no people.", LOGO, '16:9', (1600, 1000))
    return s


if __name__ == '__main__':
    for x in shots():
        print(x['id'], x['aspect'], x['crop'], os.path.basename(x['ref'] or '-'))
    print(len(shots()))
