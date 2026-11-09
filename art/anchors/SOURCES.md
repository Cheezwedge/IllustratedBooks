# Where the reference images came from

Keep one entry per image in this folder. This record backs up the AI-content disclosure (rights doc §1.7) and shows how each reference was made.

## U1_three_panel_cutaways.jpg

- **Made with:** Google Gemini app, "auto" model choice, November 2026, by the project owner.
- **Size:** 928 × 1144 px. Style reference only, not print art.
- **Prompts used (as typed):**
  1. "I would like to create an illustrated version of the original Hobbit book that I could potentially sell in countries where it is open domain. I like the art style of the brambly hedge, including detailed cutaways of some of the inner working and mechanisms, trees, holes, and storage spaces throughout the book. Could you help me generate some artwork that would have a similar style to the Brambly hedge for the Hobbit, and have it be kid friendly. Generate an image of the first example you give"
  2. (after a first image that was not kept) "Can you generate 3 more images? Use the brambly hedge art as the inspiration, research all of the artwork inside those books."
- **Status:** **reference only, not for publication.** The prompt named a specific book series and asked the tool to study its artwork. The image itself does not reproduce any recognisable page from that series, but final art must not be made this way. Use the neutral prompts in `docs/07-style-prompt-library.md`, and replace this anchor with a neutrally prompted image once one scores well on the §7.8 checklist.
- **Known faults:** misspelled labels ("SMEAKING", "ARKKENSTONE", "SMYTHED"); duplicated labels; an elf-lord's house drawn as a treehouse with stables in the trees, which contradicts the book.

## U2_three_panel_blank_labels.jpg

- **Made with:** Google Gemini app, November 2026, by the project owner, using the neutral "variant B worked example" prompt from `docs/07-style-prompt-library.md` with U1 attached as a reference.
- **What happened:** Gemini treated the attached U1 as an image to *edit* and returned almost the same picture with every label box emptied, rather than a new composition.
- **Status:** **reference only, not for publication.** It is derived from U1, so it inherits U1's provenance and its story faults (the treehouse house, the horse on a tree platform).
- **Labels:** set in real type with `tools/label_placards.py`. Words are in `U2_three_panel_blank_labels.labels.json`; output is `output/labelled/U2_three_panel_labelled.png`.
