"""Which Synthware photographs show each card -- chosen by eye.

Every photo here was looked at on a contact sheet (see build.py). The rules:

* Only clean product photographs: plain white, grey or dark background, the
  piece on its own. Synthware's advertising posters (teal background, Chinese
  captions, dimension arrows drawn across the glass) are never used, nor are
  line drawings, nor photos with rulers, hands or inset close-ups.
* A photo goes to a card only if it shows that card's piece and could not be
  mistaken for another card's -- the quiz relies on one right answer.
* Cards for which Synthware has no clean photo are dropped (DROPPED below).

Files are named <product id>_<n> as downloaded by tools/fetch_synthware.py.
"""

PHOTOS = {
    # --- flasks & vessels ----------------------------------------------------
    "round-bottom-flask": ["5688_0", "5688_1", "5688_2", "5688_3", "11299_0"],
    "two-neck-flask": ["20924_0", "20924_1", "20924_3", "6516_0", "6516_1"],
    "three-neck-flask": ["9156_0", "9156_1", "9156_2", "2028_0", "2028_1", "16945_0"],
    "pear-shaped-flask": ["6992_0", "6992_1", "6992_2", "6992_3"],
    "erlenmeyer-flask": ["15657_0", "15657_1", "15657_2", "15657_3"],
    "filtering-flask": ["14711_0", "14711_1", "14711_2", "14711_3"],
    "jacketed-reaction-flask": ["18060_0", "18060_1", "18060_2", "18060_3", "18137_0", "18146_0"],
    "bottom-outlet-flask": ["14181_0", "14181_1", "14181_2", "14181_3", "14155_0"],
    "dewar-flask": ["1648_0", "1648_2", "1659_0", "1516_0", "1675_0", "1675_1"],
    "beaker": ["13872_0", "13872_2", "13872_3", "11433_0"],
    "crystallizing-dish": ["515_0"],
    "kuderna-danish-flask": ["7806_0", "15278_0", "15278_1"],
    "conical-reaction-vial": ["1221_0", "1221_1", "1221_2", "1454_0", "1454_1"],
    "pressure-vessel": ["19917_0", "19917_1", "19917_2", "19917_3"],
    "peptide-synthesis-vessel": ["18329_0", "18329_1", "18329_2", "18329_3"],
    "flat-bottom-flask": ["9592_0", "9592_1", "9592_2", "9592_3"],
    "jacketed-beaker": ["11452_0", "11444_0", "11444_1", "11444_2"],
    "graduated-cylinder": ["1808_0", "1808_1", "1808_3"],
    "reagent-bottle": ["8084_1"],
    # --- condensers ------------------------------------------------------------
    "liebig-condenser": ["8856_0", "11259_0"],
    "coil-condenser": ["15694_0", "4693_0"],
    "allihn-condenser": ["19943_0", "19943_1", "19943_2", "20167_0", "20167_1"],
    "friedrichs-condenser": ["20182_0", "20182_1", "20182_2", "22511_0"],
    "cold-finger-condenser": ["12227_0"],
    "dewar-condenser": ["21643_0", "21717_0"],
    "rotary-evaporator-condenser": ["4959_1", "14601_0", "14604_0", "14604_1"],
    "air-condenser": ["16750_0", "16750_1", "16750_2"],
    # --- distillation ------------------------------------------------------------
    "vigreux-column": ["9576_0", "9576_1", "9576_2", "9576_3"],
    "distilling-head": ["8434_0"],
    "jacketed-vigreux-head": ["9734_0"],
    "short-path-apparatus": ["14335_0", "11326_0", "12715_0"],
    "cow-receiver": ["14573_0", "14573_1"],
    "kugelrohr-bulb": ["21598_0", "21598_1", "21598_2", "21598_3"],
    "snyder-column": ["15285_0"],
    # --- funnels -----------------------------------------------------------------
    "buchner-funnel": ["20356_0"],
    "fritted-filter-funnel": ["17405_0", "17405_1", "17405_2", "17405_3", "3467_0"],
    "powder-funnel": ["15595_0"],
    "glass-funnel": ["15477_0", "15477_1", "15477_2", "15725_0"],
    "separatory-funnel": ["11668_0", "11668_2", "11920_0", "11920_2", "14938_0", "14938_2", "18568_0"],
    "pressure-equalizing-funnel": ["14898_0", "14898_1", "3610_0", "3610_2", "23812_0", "16574_0", "16574_2"],
    "fritted-filter-tube": ["3414_0", "3414_2"],
    # --- adapters ----------------------------------------------------------------
    "reducing-adapter": ["12796_0", "12796_1", "12796_2", "12796_3"],
    "ball-socket-adapter": ["13030_0", "13055_0"],
    "inlet-adapter": ["8306_0", "8306_1", "8306_2", "3835_0"],
    "thermometer-adapter": ["4625_0", "4625_1", "4625_2", "4639_0", "4646_0"],
    "vacuum-gas-adapter": ["8419_0", "8419_1", "8419_2", "8419_3"],
    "stopcock-vacuum-adapter": ["4861_0", "4861_1", "9417_0", "21554_0", "21554_1", "9412_0", "12553_0", "9424_0"],
    "claisen-adapter": ["15606_0", "15606_1", "15606_2", "15606_3", "15819_0"],
    "vacuum-takeoff-adapter": ["8808_0"],
    "drying-tube-adapter": ["14480_0", "16026_0", "8821_0", "16374_1"],
    "anti-splash-adapter": ["14085_0", "14085_1", "14085_2", "16049_1", "16049_2", "16150_1", "14034_0", "14034_1"],
    "kjeldahl-trap": ["13051_0", "13051_1", "13051_2"],
    "vapor-duct": ["10290_1", "10290_2", "10290_3"],
    "thermowell": ["8939_0"],
    # --- extraction / filtration ----------------------------------------------------
    "concentrator-tube": ["15287_0"],
    "filtration-apparatus": ["14697_1", "14697_2", "14697_3"],
    # --- vacuum & schlenk -----------------------------------------------------------
    "schlenk-flask": ["2134_0", "2134_1", "2134_2", "2134_3", "4722_0", "4779_0"],
    "schlenk-tube": ["2190_0", "2190_1", "2190_2", "2190_3", "20963_0"],
    "vacuum-manifold": ["16354_0", "16354_1", "16354_3", "16436_0", "16468_0", "16440_0", "16496_0"],
    "vacuum-trap": ["4930_0", "4930_1", "4930_2", "4930_3", "4883_0", "4883_1", "4883_2"],
    "bubbler": ["10872_0", "1318_0", "10838_0"],
    "gas-washing-bottle": ["12708_0"],
    "gas-dispersion-tube": ["16849_0", "16849_1", "18931_0"],
    "sublimator": ["34040_0"],
    "solvent-still-head": ["37372_0"],
    "high-vacuum-valve": ["7400_0"],
    # --- chromatography ---------------------------------------------------------------
    "chromatography-column": ["20984_0", "32354_0", "14631_0", "19336_0"],
    "chromatography-reservoir": ["10613_0"],
    "chromatography-column-reservoir": ["27704_0"],
    "tlc-tank": ["9650_0"],
    # --- closures -----------------------------------------------------------------------
    "glass-stopper": ["1604_0", "19019_0", "5614_0", "7362_0"],
    "ptfe-stopper": ["7582_0", "7582_1", "7582_2"],
    "ptfe-stopcock": ["6666_0"],
    "glass-stopcock": ["13356_0", "16172_0"],
}

# Cards removed because Synthware has no clean photograph of them (only
# posters, line drawings, or no such product).
DROPPED = {
    "four-neck-flask": "posters only",
    "volumetric-flask": "not in the Synthware catalogue",
    "dean-stark-trap": "posters only",
    "distillation-receiver": "line drawings and posters only",
    "addition-funnel": "posters only",
    "gooch-crucible": "posters only",
    "soxhlet-extractor": "posters only",
    "extraction-thimble": "posters only",
    "septum": "posters only",
    "joint-clip": "not in the Synthware catalogue",
}

# New cards, and existing cards whose name or text changes with the new photos.
NEW_OR_CHANGED = {
    "flat-bottom-flask": {
        "category": "flasks",
        "name": "Flat-bottom flask",
        "aliases": ["Florence flask", "Boiling flask, flat bottom"],
        "description": (
            "A round flask with a flattened base, so it stands on the bench on its own. "
            "Handy for making up and storing solutions. For heating hard or for vacuum, "
            "chemists prefer a round-bottom flask: the flat base is where stress gathers "
            "and where the glass cracks first."
        ),
    },
    "jacketed-beaker": {
        "category": "flasks",
        "name": "Jacketed beaker",
        "aliases": ["Double-walled beaker"],
        "description": (
            "A beaker inside a second glass wall. Water or coolant from a circulator flows "
            "through the gap between the walls and holds whatever is inside at a steady "
            "temperature -- for crystallisations, titrations and anything that has to stay "
            "cold or warm for hours."
        ),
    },
    "graduated-cylinder": {
        "category": "flasks",
        "name": "Graduated cylinder",
        "aliases": ["Measuring cylinder"],
        "description": (
            "A tall, narrow cylinder on a stable foot, with a scale up the side, for "
            "measuring out a volume of liquid quickly. More accurate than the marks on a "
            "beaker, less accurate than a volumetric flask or pipette -- the everyday choice "
            "when 'about 50 mL' is good enough. Read the level at the bottom of the curved "
            "surface (the meniscus)."
        ),
    },
    "reagent-bottle": {
        "category": "flasks",
        "name": "Reagent bottle",
        "aliases": ["Media bottle", "Screw-cap bottle", "Duran bottle"],
        "description": (
            "A sturdy glass bottle with a screw cap, for storing solutions and solvents. "
            "The cap seals tightly and the rough scale on the side shows about how much is "
            "left. Brown-glass versions protect chemicals that are broken down by light."
        ),
    },
    "glass-funnel": {
        "category": "funnels",
        "name": "Glass funnel",
        "aliases": ["Filling funnel", "Funnel"],
        "description": (
            "The simple cone and stem, for pouring a liquid into a narrow opening without "
            "spilling. Lined with a folded filter paper it becomes the most basic filtration "
            "set-up, gravity filtration. Many lab funnels end in a ground-glass joint so "
            "they sit firmly in a flask neck instead of wobbling."
        ),
    },
    "thermowell": {
        "category": "adapters",
        "name": "Thermowell",
        "aliases": ["Thermometer well", "Thermometer pocket"],
        "description": (
            "A glass tube closed at the bottom that reaches through a joint into the flask. "
            "A thermometer or temperature probe slides inside it, so the reaction's own "
            "temperature is measured without the probe touching the chemicals and without "
            "letting air in."
        ),
    },
    # Extraction and Filtration would be one-card decks now; fold them in.
    "concentrator-tube": {"category": "distillation"},
    "filtration-apparatus": {"category": "funnels"},
    "ptfe-stopper": {
        "name": "PTFE stopcock plug",
        "catalog_name": "STOPCOCK REPLACEMENT PLUG, PTFE",
        "aliases": ["PTFE plug", "Teflon plug", "Stopcock key"],
        "description": (
            "The turning part of a stopcock, made of PTFE (Teflon): a tapered plug with a "
            "hole bored through it and a handle to turn it. Turn the hole in line with the "
            "tube and liquid flows; turn it across and the flow stops. PTFE seals without "
            "grease and does not stick, and a worn plug can simply be swapped for a new one."
        ),
    },
}
