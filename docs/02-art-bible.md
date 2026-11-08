# 2 · Art bible

This is the single reference for anyone making art for the edition: you, a commissioned illustrator, or a carefully supervised AI-assisted workflow. The style-study pieces in `art/png/` were built to these rules.

## 2.1 The idea

**A cosy, intricate, pen-and-watercolour Hobbit that rewards slow looking.** Every page turn offers something to find: a pantry shelf to inspect, a mechanism to trace with a finger, a snail hiding in the corner. Think of an English hedgerow almanac crossed with an engineer's cutaway drawing: warm, domestic and curious, never grim.

Three pillars:

1. **Cutaways and cross-sections.** Show what is inside walls, hills, trees, mountains and machines: larders, cellars, stairs, chimneys, pulleys, roots and burrows.
2. **Abundant small detail.** Real plants, crockery, tools and food, drawn accurately and lovingly, with gentle humour in the details.
3. **Kid-safe wonder.** Danger is felt, not shown. Scary creatures stay in shadow or turn slightly comic, and nothing is bloody.

## 2.2 Style descriptors

Use this language in every brief and every AI prompt. **Never use an artist's name, a series title such as Brambly Hedge, or a film reference.**

> fine sepia pen line, soft transparent watercolour washes on warm cream paper, slight granulation, colours occasionally escaping the lines, gentle natural daylight or golden lamplight, botanically accurate English hedgerow plants (bramble, dog-rose, honeysuckle, hawthorn, oak, beech, ferns, mushrooms), rounded cosy architecture, intricate cross-section cutaway, small labelled rooms, abundant tiny domestic details, storybook warmth, children's classic illustration

**Avoid:** digital gloss, hard cel shading, heavy black outlines, photorealism, film-like lighting, neon colour, gore, horror faces.

## 2.3 Palette

Swatches come from `art/src/kit.py`, so all generated art matches.

| Role | Hex | Use |
|---|---|---|
| Sepia ink | `#3d2b1f` | all line work |
| Cream paper | `#f6eedb` | page tint inside plates |
| Earth / clay | `#c09668` `#d2a878` `#80593a` | cut soil, roots, tunnels |
| Grass / leaf | `#93b062` `#6e9446` `#7f9c4d` `#58773a` | hills, foliage |
| Bramble berry | `#6e3456` | ornaments, berries, chapter numerals |
| Dog-rose / pink | `#dc8e7c` `#e9b3a5` | flowers, curtains |
| Hearth | `#f2a63c` `#e46b2d` `#fbd96e` | fires, lamps, glow |
| Sky / water | `#b9d2dc` `#86adbf` `#5d8597` | skies, rivers, lakes |
| Stone | `#c2b7a4` `#a99d8a` | walls, mountains |
| Gold / brass | `#dcae3e` `#cfa23c` | doorknobs, treasure, keys |
| Door green | `#4e7d47` | the round door, home |

**Journey colour-script.** The palette shifts chapter by chapter so the reader *feels* the distance from home:

| Chapters | Mood | Dominant hues |
|---|---|---|
| I–III | Home, green country, an elven valley | fresh greens, cream, dog-rose pink, hearth gold |
| IV–VI | Mountains, tunnels, fire in the pines | stone greys, cool blues, ember orange at night |
| VII–IX | Bee-pastures, deep forest, elf-halls | honey gold, then deep moss green and violet, then torch-lit amber |
| X–XIV | Lake-town, the Mountain, the dragon | lake blue-grey, cold sky, treasure gold, dragon-fire red |
| XV–XVII | Ravens, gathering armies, storm | slate, steel, storm violet, with shafts of light |
| XVIII–XIX | Spring return, home again | the greens of Chapter I, only warmer |

## 2.4 Line, wash and texture

- **Ink:** 0.2–0.5 pt at print size, slightly wobbly and broken in places. Use thicker strokes only on silhouette edges.
- **Washes:** transparent and layered (two or three passes), with edges that darken slightly as they dry. Let a wash drift 0.5–1 mm off the line now and then.
- **Shadows:** a cool violet-grey (`#5d4c66`) at about 25% opacity. Never use black.
- **Light:** interiors glow from lamps and hearths, with a soft radial bloom. Exteriors use morning or evening light with long, soft shadows.
- **Paper:** a faint cream grain under everything.

## 2.5 Cutaway conventions

1. **The cut face** is warm earth (or stone, or wood) and is busy with pebbles, roots, root-hairs, strata lines, a worm, a beetle, a buried treasure.
2. **Rooms are arched cavities.** Draw a darker rim where earth meets plaster, wooden wainscot, tiled floors and a lamp in each room.
3. **Show connections** between rooms: stairs, passages, chimney flues and pipes, so a child can trace a route with a finger.
4. **Label** rooms in small italic hand-lettering ("the Pantry"). Labels sit in clear wall space and never cover detail.
5. **Look-for details:** every cutaway hides at least three, and one of them is always **the snail** (§2.7).
6. **Mechanisms** must be plausible. Gears mesh, ropes run over pulleys, levers have pivots and counterweights. Children notice.

## 2.6 Characters

You (or your illustrator) design all characters from the text. No character art is included in this repository: these designs are the heart of the edition and should be uniquely yours.

| Character | Book-based design notes | Steer away from |
|---|---|---|
| The hobbit | Small (about half human height), round-bellied, curly brown hair, bare hairy feet, bright waistcoat colours (the book favours green and yellow), good-humoured, fussy, brave when needed | film actor likeness, film costume colours and cut |
| The wizard | Very tall, old, long white beard, bushy eyebrows, tall pointed **blue** hat, grey cloak, silver scarf, big boots, a staff | film or actor likeness |
| Thirteen dwarves | Each instantly recognisable: hood colour, beard shape, instrument, size. Checking the hood colours against your source text is the quickest way to stay faithful | film hairstyles, armour, prosthetic faces |
| The dragon | Red-gold, four legs **and** a separate pair of wings, a jewel-crusted belly with one bare patch, majestic and vain, more awe than terror | the film design (wings as forelimbs) |
| The cave-creature | Small, thin, pale lamp-like eyes, paddling a little boat; keep him half-hidden in shadow | film CGI likeness |
| Goblins, wolves, spiders | Comic-grotesque rather than horrifying; big expressive eyes on the spiders; no gore | horror-film designs |

Produce a **character sheet** for each before any scene art: front, side and back views, a height chart, a colour swatch and three expressions. Lock these before production.

## 2.7 The hidden snail

A small brown snail appears **somewhere on every full-page plate and every cutaway spread**. Sometimes it is obvious, sometimes cunning: on a barrel, in a teacup, on a dragon's treasure-pile. A back-matter page, "Did you find the snail?", lists the answers with page numbers. This gives young readers a reason to study every big picture.

## 2.8 Illustration types and sizes

Master art is **RGB at 300 ppi at final size**. The two "with bleed" sizes are for the print PDF. The layout engine handles bleed, so supply art at the size given.

| Code | Type | Final size (in) | Pixels @300 | Placement |
|---|---|---|---|---|
| **S** | Cutaway spread | 14.25 × 10.25 | 4275 × 3075 | Across two facing pages. Keep faces and labels out of the central 0.75 in (gutter). |
| **P** | Full-page plate | 7.125 × 10.25 | 2138 × 3075 | Full bleed. Keep important content 0.5 in inside every edge, and 0.75 in from the spine side. |
| **H** | Half-page | 5.5 × 4.0 | 1650 × 1200 | Top or bottom of a text page; may have a soft vignetted edge. |
| **I** | Inset spot | 2.6 × 2.6 | 780 × 780 | Text wraps around it. Transparent background, irregular edge. |
| **O** | Chapter opener | 5.5 × 2.0 banner, 1.5 in emblem | — | Bramble banner plus emblem roundel (done as style study). |
| **V** | Vignette / tailpiece | 2.4 × 0.7 | — | End of each chapter. |
| **M** | Margin critter | 0.9 × 0.7 | 270 × 210 | Automatic, outer bottom corner of any page with no other art. |
| **D** | Drop cap | 1.0 × 1.0 | 300 × 300 | First letter of each chapter (A–Z done). |

File naming: `art/final/<ID>.png`, e.g. `art/final/P-05-01.png`. The build picks these up automatically and replaces the labelled placeholder in the dummy.

## 2.9 Working with an illustrator

- **Contract:** worldwide, all-media, perpetual rights, either a copyright **assignment** or an exclusive licence. You will want to sell in more countries as the book enters the public domain (2033, 2034, 2044). Include a moral-rights consent for cropping and colour adjustment.
- **Brief each piece** with: its ID, the scene summary from `plan/illustrations.csv`, the size code, the colour-script row, the look-for details, and the character sheets.
- **Approval stages:** thumbnail, then pencil, then ink, then colour. Most changes should happen at the pencil stage.
- **Budget:** about 200 pieces is a large commission. To make it affordable, re-use the M, V, D and O libraries (largely done) and phase the H and I spots.

## 2.10 If you use AI image tools

1. **Prompt with the style descriptors in §2.2 plus the scene brief.** Never use artist names, series titles or film titles.
2. **Treat AI output as underpainting.** Repaint faces, hands and characters by hand from your character sheets for consistency, and keep layered files as evidence of human authorship.
3. **Check every image** for accidental resemblance to the films or to published illustrations. Reject anything that looks familiar.
4. **Disclose AI content** where platforms require it (KDP does).

**Example prompt (scene P-09-01):**

> Children's classic book illustration, full page, portrait. Thirteen small travellers bobbing down a fast forest river inside wooden barrels, only their hooded heads poking out, one small figure clinging on top of a barrel. Beech and oak forest banks, morning light through mist, water splashes. Fine sepia pen line, soft transparent watercolour washes on warm cream paper, slight granulation, botanically accurate plants, gentle humour, storybook warmth. A tiny brown snail riding on one barrel lid.

## 2.11 How the style-study art is made, and its limits

The pieces in `art/png/` are painted by code: `art/src/wc.py` is a small raster watercolour engine. It imitates the physical behaviour of the medium:

- **Transparent glazes:** each wash multiplies the paint beneath it, so colours mix and deepen like real pigment layers.
- **Wet edges:** the wash edge wanders slightly, and pigment pools along it as it dries.
- **Granulation:** pigment settles into the hollows of a cold-press paper surface.
- **Mottling:** washes are uneven in density.
- **Modelling:** every form is darker away from a light at the upper left, with fine pen hatching on the shadow side.
- **Pen work:** lines are fine and tapered, sometimes broken, with a faint pencil under-drawing.
- **Reserved whites:** highlights are bare paper.
- **Vignettes:** spot illustrations fade softly into the page.

`art/src/detail.py` holds the high-detail motifs:

- tree crowns built leaf by leaf
- grass blades and wildflowers
- wood grain, flagstones and gingham
- patterned crockery, preserves, herb bunches, netted hams
- an inglenook fire

**What it is good for:** it fixes the look of the edition: palette, line weight, density, cutaway conventions, page decoration. It also gives an illustrator, or an image tool, an exact layout to work over.

**What it is not:** no procedural code reaches the draughtsmanship of a master hand-painted picture book. That means observed form, characterful faces and hands, the hundred small decisions in every object. For a commercial edition at that level:

1. Commission an illustrator with this bible and these style studies as the brief, **or**
2. If you use an image model on a GPU service, use these renders as **image-to-image starting points** (composition locked, model adds finish at a low denoising strength), then paint over by hand. Follow §2.10, and keep your layered files.

Art painted by this code (or by any AI tool) counts as **AI-generated** for platform disclosure. It may not be protected by copyright in some countries (see rights doc §1.7). The "original illustrations" that differentiate the edition are safest when a human makes or substantially reworks them.
