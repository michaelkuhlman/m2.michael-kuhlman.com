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

RAW = os.path.expanduser('~/m2-gemini-raw')


def raw(name):
    """A finished Gemini photo used as the reference for follow-up shots of the same product."""
    return os.path.join(RAW, name + '.jpeg')


# 2026-10-12 paddle redesign (Michael: the Blender-derived face designs looked bad). Each paddle's studio shot is
# designed from scratch with only the logo as reference; its court shot and colourways use that photo as reference.
PADDLE_REF = ("Use the attached photo as the exact design reference: the same paddle with the same face graphic, "
              "colors, lettering, logo mark, edge guard and grip, completely unchanged.")

PRO = ("Photorealistic premium e-commerce studio product photograph of a {tier} pickleball paddle, with the "
       "design quality of the best performance paddle brands (Selkirk, CRBN, Six Zero, JOOLA pro models). ")

MARK = ("The small brand mark from the attached logo (a dotted arc over a short net post with a lime ball, no "
        "words) printed in {mark} near the top center. ")

POSE = ("The paddle stands upright, rotated slightly three-quarters to show the edge thickness, one lime-yellow "
        "outdoor pickleball resting at its base. Seamless warm chalk-cream paper backdrop (#EFE8DA), large soft key "
        "light from upper left, soft contact shadow, product centered with generous margin, fully in frame, crisp "
        "focus, realistic materials and reflections, no people, no other text, no watermark.")

SHAPE = {
    'standard': 'classic standard shape (16 in long, 7.5 in wide, gently rounded corners)',
    'elongated': 'elongated shape (16.5 in long, only 7.4 in wide, noticeably slimmer than standard)',
    'widebody': 'wide-body shape (15.75 in long, 8 in wide, softly rounded top corners)',
    'hybrid': 'elongated hybrid shape (16.5 in long, 7.6 in wide, softly rounded top corners)',
    'junior': 'smaller youth size (15.5 in long, 7.5 in wide) with a short handle',
}

PADDLES = [
    # sku, tier, shape, design (face, graphic, wordmark), mark colour, edge + grip, court-shot scene
    ('TS-KLC16-VOLT', '$200 flagship carbon', 'standard',
     "a charcoal woven Toray carbon face with a crisp visible twill weave; the graphic is a minimalist top-down "
     "pickleball court drawn in thin volt-yellow (#DDF542) lines over the lower half, the kitchen zone filled with a "
     "translucent volt-yellow gradient that fades upward into the carbon; bold condensed sans-serif wordmark "
     "'KITCHEN LINE' printed horizontally in volt yellow just above the court drawing, with a small '16' beside it",
     'white', "Matte black edge guard with a fine volt-yellow line, sculpted black throat, black perforated "
     "cushion grip with a volt-yellow end cap.", 'flat'),
    ('TS-APX14', '$230 power carbon', 'elongated',
     "a matte raw black T700 carbon face with a fine twill weave; the graphic is a bold faceted clay-orange (#C9603A) "
     "angular slash that cuts from the upper right edge down to the middle left, broken into sharp geometric shards "
     "with a subtle orange-to-ember gradient; large clean sans-serif wordmark 'APEX' running vertically up the right "
     "side of the face in white", 'white', "Black edge guard with a clay-orange line, black throat, clay-orange "
     "perforated grip with a black end cap.", 'net'),
    ('TS-DZC16', '$190 control', 'widebody',
     "a deep forest-green (#173A2E) satin carbon-fiberglass face covered with fine lime topographic contour lines "
     "that tighten into a small glowing lime target circle in the lower third (the 'drop zone'); elegant wide-spaced "
     "sans-serif wordmark 'DROP ZONE' printed horizontally in cream below the target", 'cream', "Forest-green edge "
     "guard, forest throat, cream perforated grip with a forest end cap.", 'flat'),
    ('TS-SIG-RAW', '$250 signature raw carbon', 'hybrid', None, None, None, 'net'),
    ('TS-HYB13', '$180 all-court', 'hybrid',
     "a navy (#1D2B4A) satin face split diagonally by a glacier-blue (#9CC9E0) panel in the upper right, the seam "
     "dissolving into a fine halftone dot gradient; clean sans-serif wordmark 'HYBRID' printed vertically along the "
     "left side in white with a small '13' below it", 'white', "Navy edge guard with a glacier line, navy throat, "
     "glacier-blue perforated grip with a navy end cap.", 'flat'),
    ('TS-BLP14', '$190 power', 'elongated',
     "a satin Toray carbon face in a rich brick-red (#A63A2B) to deep crimson vertical gradient, with bold black "
     "horizontal speed stripes of varying thickness across the lower third; heavy italic sans-serif wordmark "
     "'BASELINE' printed horizontally in black above the stripes", 'black', "Black edge guard, black throat, "
     "charcoal perforated grip with a brick-red end cap.", 'net'),
    ('TS-DCF', '$110 fiberglass club', 'standard',
     "a glossy chalk-white (#F4F0E6) fiberglass face with refined forest-green (#173A2E) line art of a pickleball "
     "court in perspective in the lower half and a single small lime ball dot on the kitchen line, a thin forest-green "
     "pinstripe border inset around the face; classic serif wordmark 'Dink Club' printed in forest green above the "
     "court, country-club elegance", 'forest green', "Forest-green edge guard, forest throat, forest-green grip with "
     "a cream end cap.", 'flat'),
    ('TS-ROOK', '$70 recreational', 'widebody',
     "a glossy cobalt-blue (#1F5FD1) composite face with a dynamic burst of optic-yellow halftone dots that radiates "
     "from the lower left corner and fades out toward the top; chunky rounded sans-serif wordmark 'ROOKIE' printed "
     "horizontally in white across the middle", 'white', "Black edge guard, black throat, black cushion grip with a "
     "cobalt end cap.", 'flat'),
    ('TS-JR', '$50 junior', 'junior',
     "a bright optic-yellow (#D9F24F) smooth composite face crossed by a playful forest-green zig-zag lightning band "
     "through the middle with a few small forest sparks around it; rounded bold sans-serif wordmark 'SPARK' printed "
     "in forest green under the band", 'forest green', "Forest-green edge guard, forest throat, short forest-green "
     "grip with a yellow end cap.", 'net'),
    ('TS-WOOD', '$45 heritage wood', 'standard',
     "a solid laminated pale ash wood face with clearly visible natural grain and a satin lacquer, no edge guard, the "
     "wood edge showing its fine layered plies; a thin kitchen-green pinstripe border screen-printed around the face "
     "and a vintage serif wordmark 'Classic' printed in kitchen green in the lower third", 'kitchen green',
     "No edge guard (bare sanded wood edge), wooden throat, tan stitched leather grip with a wooden end cap.", 'flat'),
    ('TS-WTR', '$150 weighted training', 'standard',
     "a matte raw black T700 carbon face split diagonally with a clay-orange (#C9603A) lower panel, and two slim "
     "brushed-steel weight bars screwed along the left and right edges of the face; bold stencil sans-serif wordmark "
     "'COACH' printed horizontally in white across the orange panel", 'white', "Black edge guard, black throat, "
     "clay-orange perforated grip with a black end cap.", 'net'),
]

SIG_PROMPT = ("Photorealistic premium e-commerce studio product photograph of a high-end carbon fiber pickleball paddle, the kind sold for $250 by a top performance brand (think the design quality of Selkirk, CRBN, Six Zero or JOOLA pro paddles). Paddle design 'SIGNATURE': elongated hybrid shape (16.5 in long, 7.6 in wide, softly rounded top corners), a raw matte black T700 carbon face with a visible fine twill weave that catches the light, a bold modern graphic: a sweeping optic-yellow (#D9F24F) gradient brush stroke that rises diagonally from the lower left throat and fades into the carbon, thin parallel pin-stripes following its curve. Large clean sans-serif wordmark 'SIGNATURE' running vertically up the left side of the face in optic yellow. The small brand mark from the attached logo (dotted arc over a short net post with a lime ball, no words) printed in white near the top center. Glossy black edge guard with a fine yellow line, a sculpted black throat, a black perforated cushion grip with a yellow end-cap. " + POSE)

KLC_VARIANT = ("Photorealistic studio product photo of exactly the same paddle as in the attached photo: identical "
               "shape, carbon face, court drawing, 'KITCHEN LINE' wordmark, logo mark, pose, ball, lighting and "
               "backdrop, with one change only: every volt-yellow accent (court lines, kitchen gradient, wordmark, "
               "'16', edge line and grip end cap) is recoloured to {colour}. " + POSE)

SCENE = {
    'flat': ("It lies flat on the court at a diagonal next to the white kitchen line with two lime-yellow balls "
             "beside it, seen from above at about 50 degrees, the whole paddle in frame. "),
    'net': ("It leans upright against the base of a black pickleball net post on the court, two lime-yellow balls "
            "at its foot, seen from a low three-quarter angle, the whole paddle in frame, the net softly out of "
            "focus behind. "),
}


def shots():
    s = []

    def add(id, prompt, ref=None, aspect='3:4', crop=(1200, 1500), extra=None):
        s.append(dict(id=id, prompt=prompt, ref=ref, aspect=aspect, crop=crop, extra=extra or []))

    # ---------------------------------------------------------------- paddles
    for sku, tier, shape, design, mark, trim, scene in PADDLES:
        if sku == 'TS-SIG-RAW':
            add(sku + '_1', SIG_PROMPT, LOGO)
        else:
            add(sku + '_1', PRO.format(tier=tier) + f"Paddle design: {SHAPE[shape]}, {design}. "
                + MARK.format(mark=mark) + trim + ' ' + POSE, LOGO)
        add(sku + '_2', "Photorealistic photo of exactly this pickleball paddle. " + PADDLE_REF + ' '
            + SCENE[scene] + COURT, raw(sku + '_1'))
        if sku == 'TS-KLC16-VOLT':
            for v, colour in (('CORAL', 'warm coral (#E8735A)'), ('GLACIER', 'pale glacier blue (#9CC9E0)')):
                add(f'TS-KLC16-{v}_1', KLC_VARIANT.format(colour=colour), raw('TS-KLC16-VOLT_1'))
                add(f'TS-KLC16-{v}_2', "Photorealistic photo of exactly this pickleball paddle. " + PADDLE_REF
                    + ' ' + SCENE['flat'] + COURT, raw(f'TS-KLC16-{v}_1'))
    # parent of the colourways: all three together (ref = the three new studio photos side by side)
    add('TS-KLC16_1', "Photorealistic studio product photo of the three paddles in the attached reference "
        "(volt-yellow, coral and glacier-blue colourways of the 'KITCHEN LINE' carbon paddle), standing upright "
        "side by side and slightly overlapping, left to right volt, coral, glacier, each reproduced exactly. "
        "Seamless warm chalk-cream paper backdrop (#EFE8DA), soft key light from upper left, soft contact shadows, "
        "all three fully in frame with generous margin, no other text, no watermark.",
        os.path.join(REF, 'ref_klc16_trio_v2.jpg'))
    add('TS-SET-START_1', "Photorealistic overhead flat-lay studio photo of a starter kit laid out neatly on "
        "the backdrop: the cobalt-blue 'ROOKIE' wide-body paddle with the optic-yellow halftone burst "
        "(the left paddle in the reference, reproduced exactly), a forest-green zipped neoprene paddle cover, a clear tube of three lime-yellow 40-hole "
        "outdoor balls with a kitchen-green label, two rolled tacky overgrips, and an open kraft-and-forest-green "
        "shipping box with the 'Third Shot' logo printed on the lid. Keep the brand mark from the reference. "
        + STUDIO, os.path.join(REF, 'ref_set_v2.jpg'))
    add('TS-SET-START_2', "Photorealistic studio product photo of two pickleball paddles standing side by side: "
        "the cobalt-blue 'ROOKIE' paddle and the "
        "chalk-white 'Dink Club' fiberglass paddle from the reference, with a tube of "
        "three lime-yellow balls in front. Reproduce both paddles exactly as in the reference. " + STUDIO, os.path.join(REF, 'ref_set_v2.jpg'))

    # ---------------------------------------------------------------- balls
    BALL = "lime-yellow (optic) seamless 40-hole outdoor pickleballs with crisp round holes and a fine matte texture"
    add('TS-T40-3_1', "Photorealistic studio product photo: a clear plastic tube of three " + BALL + ", "
        "kitchen-green cap and base and a kitchen-green wrap label reading 'TOUR 40' with the small Third Shot "
        "logo (as in the reference), standing upright, with one loose ball beside it. " + STUDIO, render('TS-T40-3_1'))
    add('TS-T40-3_2', "Photorealistic close-up studio photo of three " + BALL + " in a loose triangle, "
        "showing the seamless shell and 40 precise holes, macro detail. " + STUDIO, render('TS-T40-3_1'))
    add('TS-T40-12_1', "Photorealistic studio product photo of an open warm-apricot retail box holding twelve "
        + BALL + " in a 4x3 grid, the lid printed 'TOUR 40' with the Third Shot logo, as in the reference. "
        + STUDIO, render('TS-T40-12_1'))
    add('TS-T40-12_2', "Photorealistic photo of a handful of " + BALL + " scattered on the court near the "
        "white baseline. " + COURT, render('TS-T40-3_1'))
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
        "beside the white kitchen line. " + COURT, render('TS-T40-PINK_1'))
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
        "paddles standing upright and fanned (the three paddles in the reference, reproduced exactly: "
        "black 'SIGNATURE' raw carbon with the optic-yellow sweep, charcoal 'KITCHEN LINE' with the volt court drawing, "
        "black 'APEX' with the clay-orange faceted slash), with lime-yellow 40-hole "
        "balls scattered on the court in front, the net softly out of focus behind. The left 45 percent of the "
        "frame is calm, dark, softly lit green court and background with nothing in it (space for a headline). "
        "Warm rim light, rich deep greens, editorial sports photography, no people, no text, no watermark.",
        os.path.join(REF, 'ref_hero_v2.jpg'), '16:9', (1920, 960))
    CAT = ("Photorealistic wide editorial category banner, the subject grouped in the central third of the "
           "frame with calm breathing room on all sides (it is cropped to both 4:3 and a very wide strip), warm natural light, palette of deep kitchen green, chalk cream, "
           "optic yellow and clay orange, no people, no text, no watermark. ")
    add('cat_paddles', "A fan of the four premium pickleball paddles in the reference ('DROP ZONE' forest "
        "green, 'SIGNATURE' black raw carbon, 'HYBRID' navy with glacier split, 'BASELINE' brick red) standing in a wooden rack on a chalk-cream workshop "
        "bench, a lime ball in front, matching the designs in the reference. " + CAT, os.path.join(REF, 'ref_catpaddles_v2.jpg'), '16:9', (1200, 900), [('catbanner_paddles', (1600, 700))])
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
    add('spotlight', "Photorealistic hero product photo of this flagship pickleball paddle ('SIGNATURE', black raw "
        "carbon with an optic-yellow sweep). " + PADDLE_REF + " Standing upright against a "
        "warm chalk-cream backdrop with one lime ball at its base, dramatic but soft side light that rakes across "
        "the raw carbon weave, centered, generous margins, square composition, no text added.",
        raw('TS-SIG-RAW_1'), '1:1', (1200, 1200))
    add('story', "Photorealistic overhead flat lay on a deep kitchen-green textured pickleball court surface "
        "with a white painted line crossing the frame: the black 'SIGNATURE' raw-carbon paddle from the reference (reproduced exactly), three "
        "lime-yellow balls, a forest-green insulated bottle, a folded sand towel and a rolled overgrip, warm "
        "morning sun with soft long shadows, editorial, no people, no extra text.", raw('TS-SIG-RAW_1'), '3:4', (1200, 1400))
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
