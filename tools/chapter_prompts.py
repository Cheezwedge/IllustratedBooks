#!/usr/bin/env python3
"""
Image-generation prompts for the major events of every chapter.

    python3 tools/chapter_prompts.py

Writes
  docs/08-chapter-prompts.md                      (readable guide, variant B prompts shown)
  output/prompts/chapter-prompts-A-watercolour.txt (every prompt, soft-watercolour style)
  output/prompts/chapter-prompts-B-ink-wash.txt    (every prompt, ink & wash style)
  output/chapter-prompts.pdf

Scene descriptions are written for this project in plain visual language; they contain no text from
the novel. Characters are placeholders such as [HOBBIT]: replace them with YOUR character designs
(see CAST) and attach your character sheets. Keeping the book's names out of prompts also stops
models drifting towards film designs.
"""
import csv
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

CAST = [
    ("[HOBBIT]", "a small, round-bellied, cheerful little person about half the height of a man, with curly brown hair, "
                 "large bare feet with curly brown hair on top, wearing a bright green waistcoat with brass buttons and yellow breeches"),
    ("[WIZARD]", "a very tall old wizard with a long white beard, bushy eyebrows, a tall pointed blue hat, a long grey cloak, "
                 "a silver scarf, big boots and a wooden staff"),
    ("[DWARVES]", "thirteen sturdy dwarves with long beards tucked into their belts, each in a differently coloured hood "
                  "(dark green, scarlet, blue, purple, grey, brown, white, yellow, pale green), carrying packs, tools and musical instruments"),
    ("[DWARF-LEADER]", "a proud, dignified dwarf with a long grey-streaked beard and a sky-blue hood with a long silver tassel"),
    ("[CREATURE]", "a small, thin, slimy, pale creature with huge round pale eyes that glow faintly, kept half-hidden in shadow"),
    ("[DRAGON]", "a vast red-gold dragon with four legs and a separate pair of great folded wings, a long tail, and a belly "
                 "encrusted with gems except for one bare patch"),
    ("[HOST]", "a huge, black-haired, black-bearded man with great arms, in a coarse wool tunic, with a woodcutter's axe"),
    ("[ELF-LORD]", "a noble, kind elf-lord with long dark hair and a silver circlet, in flowing robes"),
    ("[ELF-KING]", "a tall, stern elf-king with golden hair and a crown of berries and red autumn leaves, carrying a carved oak staff"),
    ("[BOWMAN]", "a tall, grim, dark-haired bowman with a great yew longbow and a single black arrow"),
    ("[TROLLS]", "three enormous, dim, quarrelsome trolls with stony grey-green skin, lumpy noses and ragged clothes, more comic than scary"),
]

MEDIUM = {
    "A": ("Style: classic children's book illustration; delicate, slightly irregular hand-drawn outlines in warm sepia-brown ink; "
          "soft transparent watercolour washes layered with light coloured-pencil shading and gentle cross-hatching in the shadows; "
          "visible cream cold-press paper with white paper left for highlights; warm, earthy palette; storybook warmth; "
          "abundant small, true-to-life details."),
    "B": ("Style: classic children's book illustration; precise, confident dark sepia-brown ink linework with dense fine hatching "
          "and cross-hatching that models every form, tinted with transparent watercolour; strong but gentle light and shade; "
          "crisp, readable detail; cream paper; storybook warmth; abundant small, true-to-life details."),
}
CUTAWAY = ("Shown as a dollhouse-style, side-on cross-section with the front wall cut away: several levels of rooms seen at once, "
           "connected logically by stairs, ladders, chimneys and tunnels, every room crowded with appropriate everyday objects, "
           "with earth, stone and roots visible in the cut faces.")
SAFE = "Gentle and child-friendly: no gore, nothing menacing in the faces."
AVOID = ("Avoid: photorealism, 3D render, CGI, glossy digital painting, anime, heavy black outlines, neon colours, modern objects, "
         "any text or lettering, watermarks. Do not imitate any specific artist, book series, film or game, and do not resemble any "
         "film's character or set designs.")
FORMAT = {
    "plate": "Format: a tall portrait full-page illustration (2:3).",
    "spread": "Format: a wide landscape double-page spread (4:3); keep faces and key details away from the centre fold.",
    "half": "Format: a landscape half-page illustration (4:3) with soft edges fading into the page.",
    "inset": "Format: a small square spot illustration (1:1) on plain cream paper with soft edges.",
}

# id -> (title, scene, cutaway?)
SCENES = {
    # I An Unexpected Party
    "P-01-01": ("A fine morning at the round door",
                "A bright, peaceful morning in green hilly country. [HOBBIT] stands at the round green door of his hillside home, which has "
                "a brass knob in the exact middle, round windows and flower boxes. At the little garden gate, [WIZARD] leans on his staff, "
                "smiling under his hat. A winding lane, a hedge of dog-roses, buttercups in the grass, a mill and a few other round doors "
                "in the hills far behind.", False),
    "S-01-01": ("Cutaway: the hobbit-hole",
                "A cutaway of a comfortable burrow-home tunnelled into a green hill, all on one level: a long tunnel-like hall with "
                "panelled walls, tiled floor and rows of coat-pegs; doors opening to bedrooms, bathrooms, cellars, many pantries, "
                "wardrobes full of clothes, kitchens and dining-rooms; deep round windows on one side looking over a garden and meadows "
                "sloping to a river. The grassy hill above has a tree and chimney pots with smoke. [HOBBIT] in his armchair by the parlour fire.", True),
    "P-01-02": ("Music by the fire",
                "Night inside the burrow-home parlour, lit only by a log fire. [DWARVES] sit and stand around the hearth playing fiddles, "
                "flutes, a drum, harps and viols, deep in shadow and firelight, while [HOBBIT] sits in an armchair, spellbound. Smoke rings "
                "drift up; dark mountains seem to rise in the shapes of the shadows on the wall.", False),
    "H-01-03": ("The map and the key",
                "Close-up by lamplight: [WIZARD]'s long hand spreads an old parchment map of mountains, a forest and a lake across a "
                "table among teacups; a small silver key with an odd ward lies on it; the faces of [DWARF-LEADER] and [HOBBIT] lean in.", False),
    # II Roast Mutton
    "P-02-01": ("Rain on the road",
                "A grey, rainy evening in lonely hill country. A line of laden ponies trudges along a muddy track; [DWARVES] hunch in "
                "dripping coloured hoods, [HOBBIT] bounces miserably on a small pony at the back. A ruined tower on a hill, a swollen "
                "river, dark wet woods ahead.", False),
    "P-02-02": ("Three trolls at their fire",
                "Night in a wood: [TROLLS] sit round a huge fire roasting mutton on long spits, swigging from jugs and squabbling. "
                "Behind a tree trunk in the foreground, [HOBBIT] creeps closer, wide-eyed. Warm firelight on tree trunks, sparks, "
                "a big black cooking pot. Funny rather than frightening.", False),
    "I-02-04": ("Turned to stone",
                "First light of dawn on three huge stone figures frozen in squabbling poses in a woodland clearing, moss already "
                "on their shoulders and a small bird perched on one stone nose.", False),
    # III A Short Rest
    "P-03-01": ("The hidden valley at dusk",
                "Twilight on the edge of a steep ravine: the travellers with their ponies look down a zigzag path into a hidden valley "
                "with a rushing river, a waterfall, pine woods, and lantern lights twinkling in the trees around a glowing house.", False),
    "S-03-01": ("Cutaway: the Last Homely House",
                "A cutaway of a large, welcoming timber-and-stone house in a valley by a river: a hall of fire with a great hearth and "
                "listeners on benches, kitchens and pantries full of food, a library of maps and old books, guest bedrooms, stables for "
                "ponies, terraces over the water. [ELF-LORD] studies a map by moonlight at a window.", True),
    "H-03-01": ("Moon-letters",
                "At a moonlit window, [ELF-LORD] holds an old map up to the light of a crescent moon; faint silver letters shine on the "
                "parchment; [WIZARD] and [DWARF-LEADER] watch in wonder.", False),
    # IV Over Hill and Under Hill
    "P-04-01": ("Thunder-battle",
                "A night storm in a high mountain pass: lightning over jagged peaks, and far across the valley, vast misty stone-giants "
                "hurl boulders at one another like a game. The tiny company and ponies press against the cliff under a narrow ledge "
                "in the rain.", False),
    "S-04-01": ("Cutaway: under the mountains",
                "A cutaway beneath a mountain: a maze of tunnels and caves, a great cavern lit by a red fire with forges, clanking "
                "machines, chains, wheels and hammers, small comic-grotesque goblins at work, winding passages, a narrow back door, "
                "and the travellers being hustled along a tunnel. Busy and whimsical, not frightening.", True),
    "H-04-01": ("The crack opens",
                "Inside a dry cave at night, a crack yawns open in the back wall while the company sleeps; ponies vanish into the dark "
                "and long, knobbly goblin arms reach out of the shadows; [HOBBIT] wakes with a start.", False),
    # V Riddles in the Dark
    "S-05-01": ("Cutaway: down to the lake",
                "A cutaway of tunnels sloping down through rock to a vast underground lake with a tiny rocky island; dripping stalactites, "
                "the faint path of [HOBBIT] creeping down with a dimly glowing small sword; a little boat on the black water.", True),
    "P-05-01": ("The riddle game",
                "Deep under the mountain by a cold black lake: [HOBBIT] stands with a small glowing sword held out, facing [CREATURE] "
                "crouched on a rock in a little boat, its pale eyes glowing. Faint blue light from the sword, dark water, "
                "the feeling of a tense, clever game.", False),
    "H-05-02": ("Squeezing through the door",
                "[HOBBIT], invisible except for a faint outline and shadow, squeezes through a half-open stone door past dozing goblin "
                "guards into a crack of daylight, brass buttons popping off his waistcoat.", False),
    # VI Out of the Frying-Pan into the Fire
    "P-06-01": ("Up the trees",
                "A moonlit glade among tall fir trees on a mountain slope: the company cling in the treetops while wolves circle "
                "below as grey shadows with glinting eyes; [WIZARD] in the tallest tree holds a glowing pine-cone; one dwarf "
                "dangles from a branch holding another's legs.", False),
    "P-06-02": ("The eagles",
                "Dawn over burning pine woods: great golden-brown eagles lift the company high into a rose-coloured sky, each "
                "traveller clutched gently in their talons or riding on their backs, the smoke and the mountains falling away below.", False),
    "H-06-03": ("The eyrie",
                "A high rock shelf at sunset: the eagles' eyrie with a small fire roasting supper, the company resting wrapped in "
                "cloaks, and the whole wide land spread out far below with a river and a dark forest on the horizon.", False),
    # VII Queer Lodgings
    "P-07-01": ("The Carrock",
                "Morning: the eagles set the company down on a huge flat-topped rock standing in the middle of a broad river, with "
                "rough steps cut into it, meadows and woods on the far banks.", False),
    "S-07-01": ("Cutaway: the great wooden hall",
                "A cutaway of a farmstead: a long timber hall with carved tree-trunk pillars and a fire in the middle of the floor, "
                "a sleeping platform, barns, a dairy with churns, stores of honey and cream, stalls for ponies, sheep and dogs, rows "
                "of beehives in a garden of clover and flowers. [HOST] at the head of a long table.", True),
    "P-07-02": ("Supper served by animals",
                "Inside the long timber hall by firelight: dogs walking on their hind legs, ponies and woolly sheep carry in trestle "
                "tables, torches, bowls of honey, cream and loaves for the guests; [HOST] laughs at the head of the table; "
                "[DWARVES], [WIZARD] and [HOBBIT] stare in delight.", False),
    "H-07-01": ("Bee-pastures",
                "The travellers walk through sunny fields of clover and tall flowers buzzing with enormous furry bees, past rows "
                "of straw beehives and a low hedge.", False),
    # VIII Flies and Spiders
    "P-08-01": ("Inside the forest",
                "A dim green tunnel of ancient trees, twisted trunks and hanging moss, a narrow path disappearing into darkness; "
                "black squirrels on branches, pairs of small glinting eyes in the shadows, the company walking in single file.", False),
    "P-08-02": ("Above the leaves",
                "[HOBBIT] pokes his head out of the very top of a tall oak above a sea of dark green leaves stretching to the "
                "horizon, in dazzling sunshine, surrounded by fluttering velvety black butterflies.", False),
    "P-08-03": ("The spider colony",
                "A gloomy forest clearing hung with silvery webs: dwarves wrapped like parcels in silk hang from the branches; "
                "big, round, comically cross spiders with many eyes scuttle about, while [HOBBIT] throws stones from behind a tree. "
                "Exciting but funny, never horrifying.", False),
    "H-08-02": ("Feast in a glade",
                "Through the trees, an elvish feast by torchlight in a clearing: elves in green and brown sing and eat at long "
                "tables; the hungry dwarves stumble out of the dark towards the light.", False),
    # IX Barrels Out of Bond
    "S-09-01": ("Cutaway: halls and cellars",
                "A cutaway of caves under a forested hill: halls with torches, a throne carved in the rock where [ELF-KING] sits, "
                "dungeon cells with wooden doors, a vaulted wine cellar of barrels, a trapdoor over an underground river and an "
                "arched water-gate with a raised portcullis opening to daylight.", True),
    "P-09-01": ("Down the trapdoor",
                "In a torchlit stone cellar, barrels tumble one after another through an open trapdoor into a dark river below "
                "with big splashes; [HOBBIT] grabs at the very last barrel as it rolls away.", False),
    "P-09-02": ("Riding the river",
                "A misty forest river at dawn: barrels bob and spin in the current, dwarves' hooded heads poking out of a few; "
                "[HOBBIT], soaked, sits astride one barrel holding on tight; beech and oak trees lean over the water.", False),
    # X A Warm Welcome
    "P-10-01": ("The town on the lake",
                "A wooden town built on great stilts far out on a long misty lake, joined to the shore by a long wooden bridge; "
                "boats, lanterns, smoke from chimneys, and a single lonely mountain on the far horizon.", False),
    "S-10-01": ("Cutaway: the stilt town",
                "A cutaway of a lake-town on stilts: wooden houses with storerooms and ladders, walkways and a market square, "
                "warehouses of barrels, boats moored beneath, a crane hoisting a barrel, and a large hall where townsfolk gather.", True),
    "H-10-02": ("Off up the lake",
                "Boats laden with supplies and ponies setting out up the lake; crowds of townsfolk waving from the walkways and "
                "bridges; flags and morning mist.", False),
    # XI On the Doorstep
    "P-11-01": ("The hidden bay",
                "High on the side of a great mountain, a small grassy ledge before a smooth grey rock wall; [HOBBIT] sits alone "
                "with his chin in his hands gazing west over a vast bare valley at evening.", False),
    "I-11-01": ("The thrush and the snail",
                "A close-up natural-history study: a speckled thrush on a grey stone, holding a snail and knocking it on the rock, "
                "small mountain plants around.", False),
    "P-11-02": ("The keyhole",
                "The last red ray of the setting sun falls on the smooth rock wall and reveals a keyhole; [DWARF-LEADER] turns "
                "an old key while [HOBBIT] and the others gather close, a thrush watching from a ledge.", False),
    # XII Inside Information
    "S-12-01": ("Cutaway: inside the Mountain",
                "A cutaway of a great mountain: a small secret door and a long tunnel sloping down, vast carved halls with pillars "
                "and stairs, forges and old dwarf workshops, the great treasure hall deep inside with [DRAGON] asleep on the hoard, "
                "a river flowing out of the front gate. [HOBBIT] tiny in the tunnel.", True),
    "P-12-01": ("The sleeping dragon",
                "In a vast dim stone hall, [DRAGON] lies curled asleep on an enormous hoard of gold coins, goblets, crowns and jewels; "
                "a warm golden glow rises from the treasure; a thin wisp of smoke curls from a nostril. [HOBBIT] peeks from a tunnel "
                "mouth, tiny in comparison. Majestic and awe-inspiring rather than frightening.", False),
    "H-12-02": ("A riddling conversation",
                "Amid the gold, [DRAGON] has one huge eye half-open, peering at an empty-looking shadow on the coins where "
                "[HOBBIT] stands invisible, only his faint outline showing.", False),
    # XIII Not at Home
    "H-13-01": ("The great white gem",
                "In the empty, dark treasure hall, [HOBBIT] holds up a flickering torch and finds a great white gem glowing like "
                "a star on a mound of gold.", False),
    "P-13-01": ("Choosing armour",
                "In the treasure hall by lamplight, [DWARVES] try on helmets, mail-shirts and gilded belts with delight; [HOBBIT] "
                "admires a small shining silver mail-coat that fits him, like a costume fitting.", False),
    "H-13-02": ("The old halls",
                "The company climbs great carved stairways through vast crumbling dwarf halls by torchlight, broken pillars and "
                "fallen stones, shafts of daylight in the distance.", False),
    # XIV Fire and Water
    "P-14-01": ("Dragon over the lake town",
                "Night: [DRAGON] sweeps down over the wooden lake town, wings wide; lanterns, ringing bells, people hurrying to boats, "
                "reflections of fire on the water. Dramatic but safe for children: no one shown hurt.", False),
    "H-14-01": ("The black arrow",
                "[BOWMAN] on a wooden walkway draws his great bow, a thrush on his shoulder; high above, [DRAGON] tumbles towards the "
                "lake in a vast cloud of steam and sparks.", False),
    "H-14-02": ("On the shore",
                "Morning on the lake shore: townsfolk sheltering in tents and around fires, sharing food and blankets; elves arrive "
                "with carts of supplies; the mountain far away.", False),
    # XV The Gathering of the Clouds
    "H-15-01": ("The old raven",
                "On a stone by the great gate, an ancient, bedraggled raven talks gravely with [DWARF-LEADER] and the dwarves, "
                "[HOBBIT] listening.", False),
    "P-15-01": ("Building the wall",
                "[DWARVES] busily build a thick stone wall across the great front gate of the mountain, passing stones hand to hand, "
                "with the river and the valley below.", False),
    "H-15-02": ("Camp in the valley",
                "At dusk, the campfires and tents of men and elves fill the valley below the mountain, banners and lanterns, "
                "seen from the dwarves' wall.", False),
    # XVI A Thief in the Night
    "H-16-01": ("Down the rope",
                "Night: [HOBBIT] climbs carefully down a rope from the top of the stone wall towards the river, stars overhead, "
                "a small bundle at his belt.", False),
    "P-16-01": ("The gift in the tent",
                "In a lantern-lit tent, [HOBBIT] unwraps a great glowing white gem before [ELF-KING] and [BOWMAN], who stare in "
                "astonishment; [WIZARD] watches quietly from a dark corner.", False),
    # XVII The Clouds Burst
    "H-17-01": ("An army over the hills",
                "A host of dwarves with shields and mattocks marches over the eastern hills at dawn under a grey sky.", False),
    "P-17-01": ("The valley under storm",
                "A vast panorama from high above: armies in the valley before the mountain under a darkening stormy sky, seen so far "
                "away that they are tiny shapes and banners; no close fighting, no injuries shown.", False),
    "P-17-02": ("The eagles are coming",
                "Great eagles sweep in from the west in a long line against dark storm clouds lit gold by the setting sun; "
                "[HOBBIT] on a rocky hilltop points up, shouting with joy.", False),
    # XVIII The Return Journey
    "H-18-01": ("Farewell by candlelight",
                "A quiet, gentle farewell in a candle-lit tent between [HOBBIT] and [DWARF-LEADER], who rests on a simple bed; "
                "warm light, no injuries shown, tender and sad.", False),
    "P-18-01": ("Homeward in spring",
                "Spring woodland with blossom and fresh green leaves: [HOBBIT] rides a pony with two small chests strapped behind, "
                "beside [WIZARD] on a horse, along a path out of the forest.", False),
    "I-18-02": ("Yule in the great hall",
                "A cosy winter feast in the long timber hall, snow outside the open door, a roaring fire, garlands, the animals "
                "and the guests at long tables.", False),
    # XIX The Last Stage
    "P-19-01": ("Back in the hidden valley",
                "A starry night in the hidden valley: elves singing in the trees with lanterns, the river rushing below, "
                "the travellers arriving down the path, glad and weary.", False),
    "H-19-01": ("The auction",
                "[HOBBIT], just home and travel-stained, stops at his garden gate astonished: his furniture is spread across the "
                "lawn and neighbours are bidding for his chairs, clocks and umbrellas. Comic.", False),
    "S-19-01": ("Cutaway: the hobbit-hole set to rights",
                "A cutaway of the burrow-home put back in order: treasure chests in the cellar, a study with maps on the walls, "
                "a small sword over the mantel, a writing desk with a growing manuscript, pantries full again, [HOBBIT] writing by "
                "the fire.", True),
    "P-19-02": ("Tea with old friends",
                "Years later, an autumn evening: [WIZARD] and a white-bearded dwarf in a scarlet hood visit [HOBBIT]; they laugh "
                "over tea and cake by the fire in the cosy parlour.", False),
}


def load(name):
    with open(os.path.join(ROOT, "plan", name), newline="") as f:
        return list(csv.DictReader(f))


def assemble(iid, item, palette, variant):
    title, scene, cut = SCENES[iid]
    t = item["type"] if item else ("spread" if iid.startswith("S-") else "plate")
    parts = [FORMAT.get(t, FORMAT["plate"]), scene]
    if cut or t == "spread":
        parts.append(CUTAWAY)
    if t in ("plate", "spread"):
        parts.append("Hide a tiny brown snail somewhere in the picture.")
    parts += [f"Colour mood: {palette}.", MEDIUM[variant], SAFE, AVOID]
    return " ".join(parts)


def main():
    items = {r["id"]: r for r in load("illustrations.csv")}
    chapters = load("chapters.csv")
    NUM = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX"]
    os.makedirs(os.path.join(ROOT, "output", "prompts"), exist_ok=True)
    txt = {"A": [], "B": []}
    md = ["# 8 · Prompts for the major events of every chapter", "",
          f"{len(SCENES)} ready-to-paste prompts, roughly three key moments per chapter, taken from the illustration plan "
          "(IDs match `plan/illustrations.csv`). The prompts shown below use **style variant B (ink & wash)**. "
          "Plain-text files with every prompt in both styles, for easy copying, are in `output/prompts/`.", "",
          "## How to use", "",
          "1. **Replace every [PLACEHOLDER] with your own character description** (cast list below). Attach your character sheets "
          "if the tool accepts images.",
          "2. **For a new picture, do not attach an old one.** If you attach a style anchor, add: \"Create an entirely new composition; "
          "take only line, colour and texture from the attached image.\"",
          "3. **Generate two to four versions** and score them with the checklist in docs/07 §7.8. Keep notes in `art/ai/log.csv` "
          "or `art/anchors/SOURCES.md`.",
          "4. **Never add the book's character names, an artist's name, a series title or a film title.** Names pull models towards "
          "film designs.", "",
          "## Cast: define each look once", "",
          "These starter descriptions follow the book. **Replace them with your own designs** before producing real art "
          "(art bible §2.6), and keep the same wording in every prompt so the characters stay consistent.", "",
          "| Placeholder | Starter description |", "|---|---|"]
    for k, v in CAST:
        md.append(f"| `{k}` | {v} |")
    md.append("")
    for c in chapters:
        n = int(c["chapter"])
        ids = [i for i in SCENES if int(i.split("-")[1]) == n]
        md += [f"## {NUM[n]}. {c['title']}", "", f"*Colour mood: {c['palette']}*", ""]
        for v in ("A", "B"):
            txt[v].append(f"===== CHAPTER {NUM[n]}: {c['title'].upper()} =====\n")
        for iid in ids:
            item = items.get(iid)
            title = SCENES[iid][0]
            kind = (item or {}).get("type", "")
            md += [f"**{iid} · {title}** ({kind})", "", "```text", assemble(iid, item, c["palette"], "B"), "```", ""]
            for v in ("A", "B"):
                txt[v].append(f"[{iid}] {title} ({kind})\n{assemble(iid, item, c['palette'], v)}\n")
    md += ["*Scene descriptions were written for this project in plain visual language and contain no text from the novel.*", ""]
    with open(os.path.join(ROOT, "docs", "08-chapter-prompts.md"), "w") as f:
        f.write("\n".join(md))
    cast_txt = "CAST - replace each placeholder with your own character description:\n" + "\n".join(f"{k} = {v}" for k, v in CAST) + "\n\n"
    for v, name in (("A", "chapter-prompts-A-watercolour.txt"), ("B", "chapter-prompts-B-ink-wash.txt")):
        with open(os.path.join(ROOT, "output", "prompts", name), "w") as f:
            f.write(cast_txt + "\n".join(txt[v]))
    import style_kit
    style_kit.build_pdf_from(os.path.join(ROOT, "docs", "08-chapter-prompts.md"), os.path.join(ROOT, "output", "chapter-prompts.pdf"))
    print(f"{len(SCENES)} prompts -> docs/08-chapter-prompts.md, output/prompts/*.txt, output/chapter-prompts.pdf")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
