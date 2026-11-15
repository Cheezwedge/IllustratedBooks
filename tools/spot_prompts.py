#!/usr/bin/env python3
"""
Prompts for small pictures scattered through the story: spot illustrations, little vignettes, margin
decorations and chapter tailpieces, each tied to a moment in its chapter.

    python3 tools/spot_prompts.py

Writes
  output/prompts/spot-prompts-A-watercolour.txt
  output/prompts/spot-prompts-B-ink-wash.txt
  plan/embellishments.csv          (ID, chapter, kind, position, title, description) for placing them

'position' is how far through the chapter the moment comes (0 = start, 1 = end), so each picture can sit
beside the passage it belongs to. Descriptions are written for this project; they quote nothing from the novel.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chapter_prompts as C  # noqa: E402

ROOT = C.ROOT
KIND = {
    "spot": "Format: a small square spot illustration (1:1) to sit in the text, the subject isolated on plain cream paper with soft edges and plenty of empty space around it.",
    "vignette": "Format: a small wide vignette (3:2) for the top or bottom of a page, isolated on plain cream paper, fading softly at the edges.",
    "margin": "Format: a tall, narrow margin decoration (1:3) to run beside the text, isolated on plain cream paper.",
    "tail": "Format: a small, wide chapter-end tailpiece (3:1), a balanced decorative still life, isolated on plain cream paper.",
}

# chapter -> [(position, kind, title, description)]
SPOTS = {
    1: [(0.02, "spot", "Smoke rings", "A few perfect smoke rings floating up into a blue morning sky above a round green door and a flower box."),
        (0.08, "margin", "A hedge of dog-roses", "A climbing dog-rose with pink flowers, buds and a bumblebee, rising up the margin."),
        (0.15, "spot", "The secret mark", "A small mysterious scratched sign glinting on shiny green paintwork beside a brass knob."),
        (0.25, "vignette", "Hoods on the pegs", "A row of wooden pegs holding coloured hoods (dark green, scarlet, blue, purple, grey, brown, white, yellow, pale green, and one sky-blue with a silver tassel)."),
        (0.32, "spot", "The doorbell", "An old brass bell-pull swinging beside a round door, with motion lines as it rings."),
        (0.4, "vignette", "Tea for thirteen", "A crowded tea table: seed-cake, raspberry jam, apple tart, mince pies, cheese, a cold chicken, pickles and a big teapot."),
        (0.47, "spot", "Flying plates", "Plates and cups tossed up in an arc over a sink, none of them broken, with soap bubbles."),
        (0.55, "margin", "Instruments", "A tall stack of musical instruments: a harp, fiddles, flutes, a drum and a viol, tied with ribbon."),
        (0.7, "spot", "A dwarf's hood and beard", "A long forked beard tucked into a belt under a sky-blue hood with a silver tassel."),
        (0.78, "spot", "The old map", "An old parchment map with mountains, a forest, a lake and a red arrow, its corners curling."),
        (0.84, "spot", "The key", "A small silver key with an odd ward on a fine chain, lying on parchment."),
        (0.95, "spot", "A candle at bedtime", "A candlestick and a nightcap on a bedside table by a round window, a moon outside."),
        (1.0, "tail", "Breakfast left behind", "A tailpiece of a teacup, a half-eaten slice of toast and a pocket-handkerchief left on a table.")],
    2: [(0.05, "spot", "The note under the clock", "A folded note tucked under a mantel clock, a dusty breakfast plate beside it."),
        (0.12, "vignette", "Running down the lane", "A tiny figure hurrying down a country lane past hedges, without hat or walking stick, a mill in the distance."),
        (0.2, "spot", "Packs and ponies", "A heap of travel packs, bedrolls and saddlebags beside a grazing pony."),
        (0.3, "margin", "Rain", "Slanting rain over dripping foxgloves and ferns, a toadstool sheltering a beetle."),
        (0.45, "spot", "Mutton on a spit", "Meat roasting on a long spit over a crackling fire, sparks rising."),
        (0.55, "spot", "Ale jugs", "Enormous rough jugs of ale and a battered cooking pot, sized for giants."),
        (0.62, "spot", "The squeaking purse", "A lumpy leather purse with an alarmed face drawn in its stitching, as if squeaking."),
        (0.85, "vignette", "Stone at sunrise", "The first rays of sunrise over a woodland clearing, three tall grey boulders shaped like hunched figures, a robin on one."),
        (0.95, "spot", "Swords from the cave", "Three old swords and a knife laid on a cloak, one with runes on the blade."),
        (1.0, "tail", "Troll's gold buried", "A tailpiece of a small pot of gold coins half-buried under tree roots, a spade beside it.")],
    3: [(0.1, "margin", "The zigzag path", "A narrow zigzag path dropping down a steep ravine edged with pines and heather."),
        (0.2, "vignette", "Lanterns in the trees", "Lanterns hanging among birch and pine branches at dusk, with fireflies."),
        (0.35, "spot", "A singing elf", "A tiny laughing figure in green sitting on a branch with a harp, silhouetted against a twilight sky."),
        (0.5, "spot", "The hall of fire", "A great stone hearth with a long fire and benches before it, a harp leaning against a pillar."),
        (0.65, "spot", "Runes on a blade", "Close-up of an old sword hilt and blade engraved with flowing runes."),
        (0.78, "spot", "Moon-letters", "A crescent moon above a parchment where faint silver letters glow."),
        (0.9, "spot", "New horseshoes", "Fresh horseshoes, nails and a farrier's hammer on an anvil."),
        (1.0, "tail", "Midsummer morning", "A tailpiece of a waterfall, pine sprigs and a sprig of midsummer flowers in morning light.")],
    4: [(0.08, "margin", "The mountain path", "A thin path climbing between crags, a pony with packs, clouds below."),
        (0.18, "spot", "Lightning", "A jagged fork of lightning splitting a dark sky over peaks."),
        (0.22, "spot", "A thrown boulder", "A great boulder flying through misty air with a puff of spray, comic rather than scary."),
        (0.32, "spot", "A dry cave", "The low mouth of a sheltering cave with packs stacked inside."),
        (0.45, "spot", "Goblin tools", "Crude goblin hammers, tongs, chains and a cogwheel on a forge bench, in red light."),
        (0.6, "vignette", "Goblin machinery", "Clanking wooden wheels, chains, pulleys and a bellows in a red-lit cavern, no figures."),
        (0.72, "spot", "Glowing blades", "Two sword blades glowing pale blue in the dark."),
        (1.0, "tail", "A lost button", "A tailpiece of a single brass button lying in the dark on a cave floor beside a dropped candle stub.")],
    5: [(0.05, "spot", "Alone in the dark", "A tiny glow of a small sword in total darkness, a faint outline of a hand."),
        (0.12, "spot", "A ring on the floor", "A plain gold ring lying on a tunnel floor, catching a faint glint."),
        (0.22, "vignette", "The black lake", "A still black underground lake with a rocky island and a little boat."),
        (0.3, "spot", "Pale eyes", "Two round pale glowing eyes in the dark over black water, mysterious not scary."),
        (0.4, "margin", "Stalactites", "Dripping stalactites and stalagmites with tiny drops of water, running down the margin."),
        (0.5, "spot", "Riddle: roots and peak", "A mountain with deep roots drawn beneath it and a cloud on its peak."),
        (0.56, "spot", "Riddle: wind", "Leaves, dandelion seeds and a feather swirling on the wind."),
        (0.62, "spot", "Riddle: an egg", "A speckled egg in a mossy nest."),
        (0.68, "spot", "Riddle: a fish", "A silver fish swimming in dark water."),
        (0.74, "spot", "Riddle: time", "An hourglass beside a crumbling stone and a tiny sapling."),
        (0.8, "spot", "A pocket", "A waistcoat pocket with something round and golden peeking out."),
        (0.95, "spot", "Popped buttons", "Brass buttons scattered on a stone doorstep in a crack of daylight."),
        (1.0, "tail", "Daylight at last", "A tailpiece of sunlight bursting through a narrow rock crack, a few mountain flowers.")],
    6: [(0.05, "vignette", "Sunlit slope", "A sunny mountainside dell with heather, rocks and a blue sky."),
        (0.2, "spot", "Counting dwarves", "Thirteen coloured hoods in a row seen from behind, one empty space."),
        (0.32, "margin", "The scree slope", "Loose stones tumbling down a steep slope towards pine trees."),
        (0.45, "spot", "Wolf eyes", "Pairs of yellow eyes glinting between dark tree trunks, more mysterious than scary."),
        (0.55, "spot", "A flaming pine-cone", "A burning pine-cone with blue and gold flames, trailing sparks."),
        (0.65, "margin", "A fir tree", "A tall fir tree with someone's boots and a cloak dangling from a branch."),
        (0.78, "spot", "An eagle's talon", "A great golden eagle's foot gently holding a small cloak."),
        (0.88, "vignette", "The eyrie", "A high rock ledge with a small fire, a nest of sticks and a view over miles of land."),
        (1.0, "tail", "Eagle feathers", "A tailpiece of three golden-brown eagle feathers crossed with a sprig of pine.")],
    7: [(0.05, "spot", "The Carrock", "A great flat-topped rock with carved steps standing in a river."),
        (0.15, "margin", "Clover and bees", "Tall clover, thistles and foxgloves with enormous furry bees, running up the margin."),
        (0.2, "spot", "A giant bee", "A huge furry bumblebee on a clover head, accurate and gentle."),
        (0.28, "spot", "Beehives", "A row of straw bee skeps on a bench in a sunny garden."),
        (0.38, "spot", "Two at a time", "Two coloured hoods peeking round a big wooden door."),
        (0.5, "vignette", "Animals serving supper", "Dogs on hind legs and a woolly sheep carrying trays of honey, cream and bread, gently funny."),
        (0.6, "spot", "Honey and cream", "Wooden bowls of honey and cream with a honeycomb and a wooden spoon."),
        (0.7, "spot", "A bear's paw print", "A large bear's paw print in moonlit grass by a gate."),
        (0.85, "spot", "Honey-cakes", "A basket of twice-baked honey-cakes wrapped in a checked cloth."),
        (0.95, "margin", "The forest gate", "Two leaning trees forming a dark arch over a path, ivy hanging down."),
        (1.0, "tail", "Ponies going home", "A tailpiece of two ponies trotting away along a meadow path at sunset.")],
    8: [(0.05, "margin", "Forest trunks", "Twisted dark tree trunks with moss, fungi and hanging cobwebs."),
        (0.12, "spot", "Black squirrels", "Two black squirrels with bright eyes on a mossy branch."),
        (0.18, "spot", "The enchanted stream", "A dark stream with a small boat tied on the far bank."),
        (0.25, "spot", "A sleeping dwarf", "A stout dwarf in a pale green hood, fast asleep and snoring on a stretcher of branches."),
        (0.35, "spot", "Velvet butterflies", "Velvety black butterflies with purple sheen in sunlight above leaves."),
        (0.45, "vignette", "An elvish feast", "Torches and long tables in a forest clearing seen through trees, lights twinkling."),
        (0.55, "spot", "Naming the sword", "A small sword stuck point-down in the moss, gleaming, beside a broken strand of web."),
        (0.65, "spot", "Silk bundles", "Bundles wrapped in grey silk hanging from a branch, comic and not scary."),
        (0.72, "spot", "A cross spider", "A big round cartoonish spider with many eyes looking cross and confused, not frightening."),
        (0.8, "margin", "Webs and dew", "Strands of silvery web with dewdrops running down the margin."),
        (1.0, "tail", "A broken web", "A tailpiece of a torn cobweb between two twigs with a small stone caught in it.")],
    9: [(0.05, "vignette", "Bridge to the halls", "A narrow stone bridge over a dark river to great carved cave doors with torches."),
        (0.2, "spot", "A dungeon door", "A heavy wooden cell door with an iron grille and a lantern beside it."),
        (0.3, "spot", "The butler's keys", "A great iron ring of keys on a belt."),
        (0.42, "spot", "Wine flagons", "Two empty wine flagons and goblets tipped over on a table."),
        (0.52, "margin", "Stacked barrels", "A tall stack of wine barrels in a vaulted cellar, running down the margin."),
        (0.6, "spot", "Straw and a lid", "A barrel with straw poking out and a lid being hammered on."),
        (0.7, "spot", "The trapdoor", "An open trapdoor in a cellar floor with water glinting below."),
        (0.82, "margin", "River and reeds", "Rushing river water with reeds, a heron and a barrel bobbing past."),
        (1.0, "tail", "Barrels ashore", "A tailpiece of three wet barrels resting on a pebbly shore with reeds.")],
    10: [(0.08, "vignette", "Town on stilts", "Wooden houses on tall stilts over a misty lake, seen from the shore."),
         (0.25, "spot", "A lake boat", "A long wooden boat with oars and a lantern moored to a post."),
         (0.4, "spot", "Old songs", "A harp and a scroll of old songs on a bench, a candle beside them."),
         (0.55, "spot", "A feast", "A great platter of fish, bread and fruit with goblets on a long table."),
         (0.7, "spot", "A dreadful cold", "A handkerchief, a steaming mug and a pair of slippers by a fire."),
         (0.85, "margin", "Flags and lanterns", "Bunting, flags and lanterns strung along a wooden walkway."),
         (1.0, "tail", "The lonely mountain", "A tailpiece of a single distant mountain across water, a few birds.")],
    11: [(0.1, "margin", "Desolation", "Bare, burned tree stumps and stones climbing the margin, one brave green shoot."),
         (0.2, "spot", "Ruined town", "Broken towers and houses of a ruined town in a valley."),
         (0.35, "spot", "The grassy ledge", "A small grassy ledge with packs, a smooth rock wall behind."),
         (0.5, "spot", "Chipping at rock", "Picks and mattocks lying beside a scratched rock wall."),
         (0.6, "spot", "A thrush and a snail", "A speckled thrush with a snail beside a grey stone (the snail motif)."),
         (0.8, "spot", "The keyhole", "A keyhole revealed in smooth rock, lit red-gold by the setting sun."),
         (1.0, "tail", "Key and moss", "A tailpiece of an old key lying on a mossy stone with a snail shell.")],
    12: [(0.08, "margin", "The long tunnel", "A tunnel sloping downwards into a faint red glow, running down the margin."),
         (0.25, "spot", "Gold coins", "A spill of gold coins, a crown and jewels catching warm light."),
         (0.35, "spot", "The two-handled cup", "A large golden two-handled cup with engraved patterns."),
         (0.48, "spot", "A wisp of smoke", "A curl of smoke and a few sparks rising from a dark cave mouth."),
         (0.6, "spot", "One open eye", "A single huge red-gold eye half-open, a reflection of gold in it, majestic not frightening."),
         (0.72, "spot", "The bare patch", "A jewel-crusted dragon's belly with one bare patch where a gem is missing."),
         (0.85, "spot", "Scorched ledge", "Scorched grass and smoking stones on a mountain ledge."),
         (1.0, "tail", "Treasure tailpiece", "A tailpiece of goblets, coins and a jewelled crown in a small heap.")],
    13: [(0.1, "spot", "A flickering torch", "A torch with a small flickering flame in darkness."),
         (0.25, "spot", "The great white gem", "A large white gem glowing like a star with soft rays of light."),
         (0.45, "spot", "A mail-coat", "A small shining silver mail-coat laid out with a plumed helmet."),
         (0.58, "margin", "Carved pillars", "Tall carved dwarf pillars and broken stairs running up the margin."),
         (0.7, "spot", "Old dwarf tools", "Ancient hammers, chisels and lanterns on a dusty workbench."),
         (0.85, "spot", "A raven's lookout", "An old stone look-out post above a river valley with a raven perched on it."),
         (1.0, "tail", "Helmet and shield", "A tailpiece of a dwarf helmet resting on a small round shield.")],
    14: [(0.1, "margin", "Bells and lanterns", "Bells ringing and lanterns swinging on wooden posts, running down the margin."),
         (0.25, "spot", "Fiery sky", "A red glow over dark water at night, sparks drifting down."),
         (0.4, "spot", "A thrush whispering", "A speckled thrush perched on a gloved hand beside a great bow."),
         (0.5, "spot", "The black arrow", "A single black-feathered arrow, its point gleaming."),
         (0.62, "vignette", "Steam over the lake", "Great clouds of steam and sparks rising over a dark lake, no figures."),
         (0.8, "spot", "Shelter by the shore", "Tents, campfires and cooking pots on a lake shore at dawn."),
         (1.0, "tail", "Bow and quiver", "A tailpiece of a yew longbow and quiver lying among reeds.")],
    15: [(0.1, "spot", "An old raven", "An ancient, bedraggled raven on a stone, looking wise."),
         (0.25, "margin", "Birds on the wing", "Flocks of birds streaming up the margin against grey cloud."),
         (0.45, "spot", "Building the wall", "Stones stacked in a rough wall with a trowel and a bucket of mortar."),
         (0.6, "spot", "Banners in the valley", "Banners and tents seen far below in a valley, small and distant."),
         (0.75, "spot", "A herald's horn", "A brass horn with a tasselled cord resting on a stone."),
         (1.0, "tail", "Campfires at dusk", "A tailpiece of three small campfires glowing at dusk under a crescent moon.")],
    16: [(0.15, "spot", "A rope over the wall", "A knotted rope hanging down a stone wall under stars."),
         (0.35, "margin", "Stars and river", "A starry sky above a winding river, running down the margin."),
         (0.6, "spot", "The gem unwrapped", "A glowing white gem being unwrapped from a cloth on a camp table by lantern light."),
         (0.85, "spot", "A wizard's hat", "A tall pointed blue hat and a wooden staff leaning in a tent corner."),
         (1.0, "tail", "Lantern and cloak", "A tailpiece of a lantern and a folded cloak by a tent flap.")],
    17: [(0.1, "spot", "A dwarf army's shields", "A row of round dwarf shields and mattocks, glinting."),
         (0.3, "margin", "Storm clouds", "Dark, rolling storm clouds with shafts of light, running up the margin."),
         (0.5, "spot", "A lookout hill", "A rocky hilltop with a small figure in a helmet watching, the valley below."),
         (0.75, "spot", "The eagles come", "A line of great eagles silhouetted against gold-lit clouds."),
         (0.9, "spot", "A dented helmet", "A small dented helmet lying in the heather with a stone beside it."),
         (1.0, "tail", "After the storm", "A tailpiece of a sprig of heather and a fallen eagle feather in clear light.")],
    18: [(0.15, "spot", "Candle in a tent", "A single candle burning beside a folded blue hood with a silver tassel."),
         (0.3, "spot", "A memorial stone", "A plain stone in a quiet hall with flowers laid upon it."),
         (0.5, "spot", "Two small chests", "Two small wooden chests of treasure strapped to a pony's saddle."),
         (0.65, "margin", "Spring blossom", "Hawthorn and apple blossom on a branch, running down the margin."),
         (0.8, "vignette", "Yule in the hall", "Garlands, a Yule log and a long table in a timber hall, snow at the door."),
         (0.95, "margin", "The road home", "A winding green road through spring hedges, running up the margin."),
         (1.0, "tail", "Pack and stick", "A tailpiece of a travel pack, a walking stick and a sprig of spring flowers.")],
    19: [(0.1, "spot", "Elves singing", "Lanterns among valley trees at night with stars and a waterfall."),
         (0.25, "spot", "Digging up gold", "A spade and a pot of gold coins dug up from under a tree's roots."),
         (0.45, "vignette", "The auction", "Furniture, clocks, umbrellas and chairs spread across a garden lawn with a sale sign that has no letters."),
         (0.55, "spot", "Teaspoons missing", "A velvet-lined box with several silver teaspoons missing."),
         (0.7, "spot", "Writing memoirs", "A writing desk with a quill, an inkpot and a growing stack of handwritten pages, a map pinned above."),
         (0.8, "spot", "A sword over the mantel", "A small sword hanging over a mantelpiece beside a clock."),
         (0.9, "spot", "Tea for three", "A teapot, three cups and a plate of cake by a fireside."),
         (1.0, "tail", "The round door again", "A final tailpiece of a round green door with a brass knob, roses around it and a snail on the step.")],
}

MEDIUM = {
    "A": ("Style: delicate, slightly irregular hand-drawn outlines in warm sepia-brown ink; soft transparent watercolour with light "
          "coloured-pencil shading; cream paper with white paper left for highlights; warm, earthy palette; accurate, charming detail; "
          "classic children's book illustration."),
    "B": ("Style: precise, confident dark sepia-brown ink linework with fine hatching that models the form, tinted with transparent "
          "watercolour; gentle light and shade; crisp detail; cream paper; classic children's book illustration."),
}
AVOID = ("No background scenery beyond what is described, no frame, no border, no text, lettering or watermarks. Gentle and "
         "child-friendly. Do not imitate any specific artist, book series, film or game.")


def main():
    chapters = {int(c["chapter"]): c for c in C.load("chapters.csv")}
    num = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX"]
    rows, out = [], {"A": [], "B": []}
    head = ("Small pictures to scatter through the story. Each ID (E-chapter-number) has a kind (spot, vignette, margin or tailpiece) and "
            "a position: how far through the chapter the moment comes (0 = start, 1 = end), so the picture can sit beside that passage.\n\n")
    for ch in sorted(SPOTS):
        for v in out:
            out[v].append(f"===== CHAPTER {num[ch]}: {chapters[ch]['title'].upper()} =====\n")
        for i, (pos, kind, title, desc) in enumerate(SPOTS[ch], 1):
            iid = f"E-{ch:02d}-{i:02d}"
            rows.append([iid, ch, kind, pos, title, desc])
            for v in out:
                p = f"{KIND[kind]} {desc} Colour mood: {chapters[ch]['palette']}. {MEDIUM[v]} {AVOID}"
                out[v].append(f"[{iid}] {title} ({kind}, about {int(pos * 100)}% through the chapter)\n{p}\n")
    for v, name in (("A", "spot-prompts-A-watercolour.txt"), ("B", "spot-prompts-B-ink-wash.txt")):
        with open(os.path.join(ROOT, "output", "prompts", name), "w") as f:
            f.write(head + "\n".join(out[v]))
    with open(os.path.join(ROOT, "plan", "embellishments.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "chapter", "kind", "position", "title", "description"])
        w.writerows(rows)
    print(f"{len(rows)} small-picture prompts -> output/prompts/spot-prompts-*.txt, plan/embellishments.csv")


if __name__ == "__main__":
    main()
