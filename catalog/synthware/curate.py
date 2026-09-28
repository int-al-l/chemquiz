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
    "coil-condenser": ["4693_0", "wm:Graham (spiral) condenser-small.jpg", "wm:Graham condenser.jpg"],
    "dimroth-condenser": ["15694_0", "wm:Dimrothkühler.jpg", "wm:Dimroth kuehler.jpg"],
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
    "buchner-funnel": ["wm:Büchnertrichter frontal.jpg", "wm:Büchnertrichter frontal 02.jpg",
                       "wm:Ceramic Buchner funnel-03.jpg"],
    "fritted-filter-funnel": ["17405_0", "17405_1", "17405_2", "17405_3", "3467_0", "20356_0"],
    "powder-funnel": ["15595_0", "15477_0", "15477_1", "15477_2"],
    "glass-funnel": ["15725_0", "wm:Analysentrichter.png", "wm:Funnel MET DP234124.jpg"],
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
            "temperature — for crystallisations, titrations and anything that has to stay "
            "cold or warm for hours."
        ),
    },
    "graduated-cylinder": {
        "category": "measuring",
        "name": "Graduated cylinder",
        "aliases": ["Measuring cylinder"],
        "description": (
            "A tall, narrow cylinder on a stable foot, with a scale up the side, for "
            "measuring out a volume of liquid quickly. More accurate than the marks on a "
            "beaker, less accurate than a volumetric flask or pipette — the everyday choice "
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
            "set-up, gravity filtration; a long stem fills with filtrate, and its weight helps "
            "pull the liquid through the paper."
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

# --- added 2026-09-28: common lab equipment -----------------------------------
# Synthware has no clean photographs of most of these (posters only, or not
# glassware at all), so they come from Wikimedia Commons under open licences;
# COMMONS below records each file's credit, shown on the card.
PHOTOS.update({
    'volumetric-flask': ['wm:Brand volumetric flask 100ml.jpg', 'wm:Volumetric flask hg.jpg', 'wm:10mL Messkolben mit Schliff A.jpg', 'wm:Messkolben 10mL.jpg'],
    'test-tube': ['wm:Test tube blue background.jpg', 'wm:Glass tube with screw cap 1.jpg', 'wm:Glass tube with screw cap 3.jpg'],
    'vial': ['5071_1', '5071_2'],
    'nmr-tube': ['5457_0'],
    'capillary-tube': ['wm:Glass capillaries 50 100ul.jpg'],
    'weighing-bottle': ['wm:Weighing bottles.jpg'],
    'petri-dish': ['wm:Plastic Petri dish 04.jpg', 'wm:Plastic Petri dish 01.jpg'],
    'evaporating-dish': ['wm:Abdampfschalen verschiedene Groessen.jpg', 'wm:Abdampfschalen, porzellan innen glasiert.jpg'],
    'crucible': ['wm:Porzellantiegel.jpg', 'wm:TiegelmitSchuh.jpg'],
    'plastic-funnel': ['wm:Entonnoir plastique.JPG', 'wm:Kitchen Funnel.jpg', 'wm:Trichter.jpg'],
    'soxhlet-extractor': ['wm:Soxhlet-Extraktor.png', 'wm:Soxhletův extraktor.jpg', 'wm:Soxhlet-laitteisto.JPG'],
    'desiccator': ['wm:Exsikkator.png',
                   'wm:Vacuum desiccator belonging to Rosalind Franklin - DPLA - 98e0f871c48313a61b251e383c16b1e6 (page 4).jpg'],
    'drying-pistol': ['wm:Trockenpistole Abderhalden 02.jpg', 'wm:Abderhalden drying pistol.jpg'],
    'septum': ['wm:Rubberseptum.jpg'],
    'joint-clip': ['wm:Keck clips.jpg'],
    'volumetric-pipette': ['wm:Vollpipetten.jpg', 'wm:Vollpipette 50 mL.png'],
    'graduated-pipette': ['wm:Pipette 4.jpg', 'wm:Serological pipette.jpg', 'wm:Graduated pipette 10ml.jpg', '17539_0'],
    'pasteur-pipette': ['wm:Glass pasteur pipette.jpg', 'wm:Pasteur Pipets.jpg'],
    'micropipette': ['wm:Pipette de laboratoire sur fond blanc au Bénin 02.jpg', 'wm:Pipette de laboratoire sur fond blanc au Bénin 04.jpg'],
    'microsyringe': ['wm:Hamilton Microliter syringe.jpg'],
    'burette': ['wm:50 mL Buret.jpg'],
    'thermometer': ['wm:Laboratory thermometer-03.jpg', 'wm:Thermometer, max.JPG'],
    'balance': ['wm:Balance Mettler AJ100.jpg', 'wm:Analytical balance mettler ae-260.jpg', 'wm:Balance Scaltec.jpg'],
    'pressure-gauge': ['wm:MAXIMATOR-High-Pressure-Manometer-01a.jpg', 'wm:MAXIMATOR-High-Pressure-Manometer-01.jpg'],
    'bunsen-burner': ['wm:Mechero Bunsen.jpg', 'wm:Bunsen burner 2.jpg'],
    'tripod': ['wm:Laboratory tripod.jpg', 'wm:Dreifuß.png'],
    'support-stand': ['wm:Retort stand.jpg', 'wm:Ringstand with a ring clamp.jpg'],
    'clamp': ['wm:Metal laboratory clamp-02.jpg', 'wm:Universal clamp.jpg'],
    'burette-clamp': ['wm:A burette clamp.jpg', 'wm:Front facing Burette clamp.jpg', 'wm:Downward Burette Clamp.jpg'],
    'lab-jack': ['wm:Juchheim Laborgeräte lifting stage.jpg', 'wm:Lab jack-swissboy.jpg', 'wm:Lifting-plate hg.jpg'],
    'magnetic-stirrer': ['wm:RCT basic IKAMAG® safety control magnetic stirrer.jpg', 'wm:Magnetic stirrer (15549).jpg', 'wm:Heidolph-magnetic-stirrer-front-02.jpg'],
    'stir-bar': ['wm:Barreau magnetique.JPG', 'wm:Magnetic pellets.jpg'],
    'spatula': ['wm:Laboratory Spatula.JPG', 'wm:Spatel und Löffelspatel.png', 'wm:Spatulas-lab.jpg'],
    'tweezers': ['wm:Small tweezers-set 1.jpg', 'wm:Tweezers-variety.jpg', 'wm:Tweezers 2019.jpg'],
    'mortar-and-pestle': ['wm:Mortar and pestle-laboratory.jpg', 'wm:Mörser.png'],
    'safety-goggles': ['wm:2023 Okulary ochronne (1).jpg', 'wm:Empiral Vision Grey goggles.jpg'],
})

# Wikimedia Commons files used above, by file name.
COMMONS = {
    'Rubberseptum.jpg': {
        "credit": 'Diesel-50, public domain, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Rubberseptum.jpg',
    },
    'Keck clips.jpg': {
        "credit": 'Edgar181, public domain, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Keck_clips.jpg',
    },
    'Entonnoir plastique.JPG': {
        "credit": 'Nickele, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Entonnoir_plastique.JPG',
    },
    'Kitchen Funnel.jpg': {
        "credit": 'Donovan Govan, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Kitchen_Funnel.jpg',
    },
    'Trichter.jpg': {
        "credit": 'Ralph Aichinger, CC BY 2.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Trichter.jpg',
    },
    'Soxhlet-Extraktor.png': {
        "credit": 'Hannes Grobe, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Soxhlet-Extraktor.png',
    },
    'Soxhletův extraktor.jpg': {
        "credit": 'Milda 444, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Soxhlet%C5%AFv_extraktor.jpg',
    },
    'Soxhlet-laitteisto.JPG': {
        "credit": 'Pratodellaspiaggia, CC0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Soxhlet-laitteisto.JPG',
    },
    'Exsikkator.png': {
        "credit": 'Hannes Grobe/AWI, CC BY 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Exsikkator.png',
    },
    'Plastic Petri dish 04.jpg': {
        "credit": 'Lilly_M, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Plastic_Petri_dish_04.jpg',
    },
    'Plastic Petri dish 01.jpg': {
        "credit": 'Lilly_M, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Plastic_Petri_dish_01.jpg',
    },
    'Mortar and pestle-laboratory.jpg': {
        "credit": 'Nadina Wiórkiewicz, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Mortar_and_pestle-laboratory.jpg',
    },
    'Mörser.png': {
        "credit": 'MediaLab TH Köln, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:M%C3%B6rser.png',
    },
    'Small tweezers-set 1.jpg': {
        "credit": 'Nadina Wiórkiewicz, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Small_tweezers-set_1.jpg',
    },
    'Tweezers-variety.jpg': {
        "credit": 'Evan-Amos, public domain, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Tweezers-variety.jpg',
    },
    'Tweezers 2019.jpg': {
        "credit": 'Mrbeastmodeallday, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Tweezers_2019.jpg',
    },
    'Vollpipetten.jpg': {
        "credit": 'Gmhofmann, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Vollpipetten.jpg',
    },
    'Glass pasteur pipette.jpg': {
        "credit": 'Pualuu, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Glass_pasteur_pipette.jpg',
    },
    'Pasteur Pipets.jpg': {
        "credit": 'Beliason, CC BY 2.5, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Pasteur_Pipets.jpg',
    },
    'Pipette 4.jpg': {
        "credit": 'Anisa Ghogar, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Pipette_4.jpg',
    },
    'Serological pipette.jpg': {
        "credit": 'Paweena.S, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Serological_pipette.jpg',
    },
    'Graduated pipette 10ml.jpg': {
        "credit": 'Anisa Ghogar, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Graduated_pipette_10ml.jpg',
    },
    'RCT basic IKAMAG® safety control magnetic stirrer.jpg': {
        "credit": 'Lucasbosch, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:RCT_basic_IKAMAG%C2%AE_safety_control_magnetic_stirrer.jpg',
    },
    'Magnetic stirrer (15549).jpg': {
        "credit": 'Gannu03, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Magnetic_stirrer_(15549).jpg',
    },
    'Heidolph-magnetic-stirrer-front-02.jpg': {
        "credit": 'Lilly_M, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Heidolph-magnetic-stirrer-front-02.jpg',
    },
    'Barreau magnetique.JPG': {
        "credit": 'Epop, CC0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Barreau_magnetique.JPG',
    },
    'Magnetic pellets.jpg': {
        "credit": 'Manojkumar Subramani, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Magnetic_pellets.jpg',
    },
    'Hamilton Microliter syringe.jpg': {
        "credit": 'Michael Pereckas, CC BY 2.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Hamilton_Microliter_syringe.jpg',
    },
    'Pipette de laboratoire sur fond blanc au Bénin 02.jpg': {
        "credit": 'Adoscam, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Pipette_de_laboratoire_sur_fond_blanc_au_B%C3%A9nin_02.jpg',
    },
    'Pipette de laboratoire sur fond blanc au Bénin 04.jpg': {
        "credit": 'Adoscam, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Pipette_de_laboratoire_sur_fond_blanc_au_B%C3%A9nin_04.jpg',
    },
    'Weighing bottles.jpg': {
        "credit": 'Сергей 6662, CC0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Weighing_bottles.jpg',
    },
    'Brand volumetric flask 100ml.jpg': {
        "credit": 'Lucasbosch, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Brand_volumetric_flask_100ml.jpg',
    },
    'Volumetric flask hg.jpg': {
        "credit": 'Hannes Grobe, CC BY-SA 2.5, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Volumetric_flask_hg.jpg',
    },
    '10mL Messkolben mit Schliff A.jpg': {
        "credit": 'Ichwarsnur, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:10mL_Messkolben_mit_Schliff_A.jpg',
    },
    'Messkolben 10mL.jpg': {
        "credit": 'Ichwarsnur, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Messkolben_10mL.jpg',
    },
    'Laboratory thermometer-03.jpg': {
        "credit": 'Lilly_M, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Laboratory_thermometer-03.jpg',
    },
    'Thermometer, max.JPG': {
        "credit": 'איתן פרמן, CC BY 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Thermometer,_max.JPG',
    },
    'Glass capillaries 50 100ul.jpg': {
        "credit": 'Nadina Wiórkiewicz, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Glass_capillaries_50_100ul.jpg',
    },
    'Trockenpistole Abderhalden 02.jpg': {
        "credit": 'DOCTrial, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Trockenpistole_Abderhalden_02.jpg',
    },
    'Abderhalden drying pistol.jpg': {
        "credit": 'Ed Uthman, CC BY-SA 2.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Abderhalden_drying_pistol.jpg',
    },
    'Test tube blue background.jpg': {
        "credit": 'Blaž bohorč, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Test_tube_blue_background.jpg',
    },
    'Glass tube with screw cap 1.jpg': {
        "credit": 'Nadina Wiórkiewicz, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Glass_tube_with_screw_cap_1.jpg',
    },
    'Glass tube with screw cap 3.jpg': {
        "credit": 'Nadina Wiórkiewicz, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Glass_tube_with_screw_cap_3.jpg',
    },
    '50 mL Buret.jpg': {
        "credit": 'Gemsgy, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:50_mL_Buret.jpg',
    },
    'A burette clamp.jpg': {
        "credit": 'Stephanie cheks, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:A_burette_clamp.jpg',
    },
    'Front facing Burette clamp.jpg': {
        "credit": 'Gemsgy, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Front_facing_Burette_clamp.jpg',
    },
    'Downward Burette Clamp.jpg': {
        "credit": 'Gemsgy, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Downward_Burette_Clamp.jpg',
    },
    'Abdampfschalen verschiedene Groessen.jpg': {
        "credit": 'Simon A. Eugster, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Abdampfschalen_verschiedene_Groessen.jpg',
    },
    'Abdampfschalen, porzellan innen glasiert.jpg': {
        "credit": 'Lysippos, CC0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Abdampfschalen,_porzellan_innen_glasiert.jpg',
    },
    'Porzellantiegel.jpg': {
        "credit": 'Gmhofmann, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Porzellantiegel.jpg',
    },
    'TiegelmitSchuh.jpg': {
        "credit": 'Gmhofmann, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:TiegelmitSchuh.jpg',
    },
    '2023 Okulary ochronne (1).jpg': {
        "credit": 'Jacek Halicki, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:2023_Okulary_ochronne_(1).jpg',
    },
    'Empiral Vision Grey goggles.jpg': {
        "credit": 'Wishofflying, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Empiral_Vision_Grey_goggles.jpg',
    },
    'Laboratory Spatula.JPG': {
        "credit": 'Gamico94, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Laboratory_Spatula.JPG',
    },
    'Spatel und Löffelspatel.png': {
        "credit": 'MediaLab TH Köln, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Spatel_und_L%C3%B6ffelspatel.png',
    },
    'Spatulas-lab.jpg': {
        "credit": 'Cjp24, public domain, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Spatulas-lab.jpg',
    },
    'MAXIMATOR-High-Pressure-Manometer-01a.jpg': {
        "credit": 'CEphoto, Uwe Aranas, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:MAXIMATOR-High-Pressure-Manometer-01a.jpg',
    },
    'MAXIMATOR-High-Pressure-Manometer-01.jpg': {
        "credit": 'CEphoto, Uwe Aranas, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:MAXIMATOR-High-Pressure-Manometer-01.jpg',
    },
    'Mechero Bunsen.jpg': {
        "credit": 'Amfeli, CC BY 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Mechero_Bunsen.jpg',
    },
    'Bunsen burner 2.jpg': {
        "credit": 'Eunice Laurent, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Bunsen_burner_2.jpg',
    },
    'Laboratory tripod.jpg': {
        "credit": 'NagayaS, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Laboratory_tripod.jpg',
    },
    'Dreifuß.png': {
        "credit": 'MediaLab TH Köln, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Dreifu%C3%9F.png',
    },
    'Juchheim Laborgeräte lifting stage.jpg': {
        "credit": 'Lucasbosch, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Juchheim_Laborger%C3%A4te_lifting_stage.jpg',
    },
    'Lab jack-swissboy.jpg': {
        "credit": 'Masur, public domain, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Lab_jack-swissboy.jpg',
    },
    'Lifting-plate hg.jpg': {
        "credit": 'Hannes Grobe, CC BY 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Lifting-plate_hg.jpg',
    },
    'Balance Mettler AJ100.jpg': {
        "credit": 'Karelj, public domain, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Balance_Mettler_AJ100.jpg',
    },
    'Analytical balance mettler ae-260.jpg': {
        "credit": 'US DEA, public domain, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Analytical_balance_mettler_ae-260.jpg',
    },
    'Balance Scaltec.jpg': {
        "credit": 'Karelj, public domain, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Balance_Scaltec.jpg',
    },
    'Retort stand.jpg': {
        "credit": 'Tsaenmai, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Retort_stand.jpg',
    },
    'Ringstand with a ring clamp.jpg': {
        "credit": 'Tsaenmai, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Ringstand_with_a_ring_clamp.jpg',
    },
    'Metal laboratory clamp-02.jpg': {
        "credit": 'Lilly_M, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Metal_laboratory_clamp-02.jpg',
    },
    'Universal clamp.jpg': {
        "credit": 'Lucasbosch, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Universal_clamp.jpg',
    },
}


def commons_filename(title: str) -> str:
    """Local file name of a Commons photo inside <folder>/commons/."""
    import re  # noqa: PLC0415
    return re.sub(r"[^A-Za-z0-9._-]+", "_", title)


# Brought back now that Commons has clean photographs of them.
for _slug in ("volumetric-flask", "soxhlet-extractor", "septum", "joint-clip"):
    DROPPED.pop(_slug, None)

# Decks for the new cards. Added to the existing "labware" root.
NEW_CATEGORIES = [
    {"slug": "tubes", "image": "test-tube-2.jpg", "name": "Tubes, vials & dishes",
     "description": "Small vessels for samples: tubes, vials, dishes and crucibles.", "sort_order": 110},
    {"slug": "measuring", "image": "burette-1.jpg", "name": "Measuring",
     "description": "Pipettes, burettes, balances and gauges: measure a volume, a mass or a pressure.",
     "sort_order": 120},
    {"slug": "bench", "image": "bunsen-burner-1.jpg", "name": "Heating, stirring & support",
     "description": "Burners, stirrers, stands and clamps that hold and heat the apparatus.", "sort_order": 130},
    {"slug": "tools", "image": "spatula-2.jpg", "name": "Bench tools & safety",
     "description": "Hand tools used every day at the bench, and the goggles you wear there.", "sort_order": 140},
]


def _card(category, name, aliases, description, catalog_name=None):
    card = {"category": category, "name": name, "aliases": aliases, "description": description}
    if catalog_name:
        card["catalog_name"] = catalog_name
    return card


NEW_OR_CHANGED.update({
    # --- brought back ------------------------------------------------------------
    "volumetric-flask": _card(
        "flasks", "Volumetric flask", ["Measuring flask", "Graduated flask", "Class A volumetric flask"],
        "A flask calibrated to contain one exact volume, marked by a single ring on the narrow neck. "
        "Dissolve a weighed sample, then add solvent until the meniscus sits on the line: this is the "
        "standard way to make a solution of known concentration.", "VOLUMETRIC FLASK"),
    "soxhlet-extractor": _card(
        "distillation", "Soxhlet extractor", ["Soxhlet", "Soxhlet extraction body", "Soxhlet apparatus"],
        "An extractor that washes a solid with fresh, clean solvent over and over by itself. Solvent boils "
        "below, condenses above, fills the chamber holding the sample and siphons back when full — leaving "
        "the extracted material in the flask and running unattended for hours.", "SOXHLET EXTRACTOR"),
    "septum": _card(
        "closures", "Rubber septum", ["Septum", "Suba seal", "Sleeve stopper septum", "Rubber seal"],
        "A rubber cap over a joint or a vial, pierced by a syringe needle. The rubber closes behind the "
        "needle, so liquids and gases can be added to or taken out of a sealed flask without ever opening "
        "it to the air.", "SEPTUM, SLEEVE TYPE"),
    "joint-clip": _card(
        "closures", "Joint clip", ["Keck clip", "Keck clamp", "Joint clamp", "Taper joint clip"],
        "A small plastic clip that grips the rims of a taper joint and holds two pieces of glassware "
        "together. Clipped joints are what stop an apparatus coming apart under vacuum, on a rotary "
        "evaporator, or when someone knocks the bench.", "JOINT CLIP"),
    # --- existing cards: extra accepted names --------------------------------------
    "filtering-flask": {"aliases": ["Buchner flask", "Büchner flask", "Bunsen flask", "Side-arm flask",
                                    "Filtering flask", "Suction flask", "Vacuum flask for filtration"]},
    "glass-stopcock": {"aliases": ["Ground glass stopcock", "Glass tap", "Tap",
                                   "High vacuum glass stopcock"]},
    # --- tubes, vials & dishes -----------------------------------------------------
    "test-tube": _card(
        "tubes", "Test tube", ["Culture tube", "Reagent tube"],
        "A narrow glass tube, closed and rounded at one end. The quickest place to try a small reaction, "
        "warm a sample or watch for a colour change; a rack holds a row of them upright. Screw-cap "
        "versions store samples."),
    "vial": _card(
        "tubes", "Vial", ["Sample vial", "Screw-cap vial", "GC vial", "Autosampler vial", "HPLC vial"],
        "A small flat-bottomed glass bottle with a screw cap, for storing a few millilitres of a sample. "
        "The tiny vials that go into GC and HPLC autosamplers are the same idea, with a septum in the cap "
        "for the instrument's needle.", "VIAL, FLAT BOTTOM, THREADED"),
    "nmr-tube": _card(
        "tubes", "NMR tube", ["NMR sample tube", "5 mm NMR tube"],
        "A long, very thin, perfectly straight tube (usually 5 mm across) with a plastic cap. A solution "
        "of the sample in a deuterated solvent goes in it, and it is lowered into the magnet of the NMR "
        "spectrometer — the walls are made uniform so they don't distort the spectrum.", "NMR TUBE"),
    "capillary-tube": _card(
        "tubes", "Capillary tube", ["Capillary", "Melting point capillary", "Melting point tube",
                                   "TLC spotter", "Glass capillary"],
        "A hair-thin glass tube. Packed with a little solid and heated, it is how a melting point is "
        "measured; dipped in a solution, it draws liquid up by itself and dabs tiny spots onto a TLC plate."),
    "weighing-bottle": _card(
        "tubes", "Weighing bottle", ["Weighing jar", "Koch cup", "Weighing vessel"],
        "A short glass jar with a ground-glass lid. A solid is weighed in it with the lid on, so it cannot "
        "take up water from the air or lose solvent while it sits on the balance; it is also used to dry "
        "samples in an oven or desiccator."),
    "petri-dish": _card(
        "tubes", "Petri dish", ["Petri plate", "Culture dish"],
        "A shallow, flat, round dish with a lid that fits loosely over it. Biologists grow bacteria on a "
        "layer of agar in it; chemists use it to hold, dry or look at a small amount of a solid."),
    "evaporating-dish": _card(
        "tubes", "Evaporating dish", ["Evaporating basin", "Porcelain dish"],
        "A shallow porcelain bowl with a pouring lip. Heating a solution in it drives off the solvent and "
        "leaves the dissolved solid behind; porcelain takes direct heat that would crack ordinary glass."),
    "crucible": _card(
        "tubes", "Crucible", ["Porcelain crucible", "Crucible with lid"],
        "A small, thick cup of porcelain (or metal) that stands up to red heat. A sample is heated in it "
        "over a burner or in a furnace to burn off everything that can burn and weigh what is left."),
    # --- funnels, vacuum ---------------------------------------------------------------
    "plastic-funnel": _card(
        "funnels", "Plastic funnel", ["Polypropylene funnel", "Filling funnel, plastic"],
        "A light, unbreakable funnel moulded from plastic, for filling bottles and pouring solvents and "
        "aqueous solutions. Cheap and safe to drop; not for hot liquids or solvents that attack plastic."),
    "desiccator": _card(
        "vacuum", "Desiccator", ["Exsiccator", "Exicator", "Vacuum desiccator", "Dessicator"],
        "A heavy glass pot with a greased, tight-fitting lid and a perforated plate inside. A drying agent "
        "sits below the plate and samples above it, so they dry — or stay dry — in air with no water "
        "in it. Versions with a tap in the lid can be put under vacuum."),
    "drying-pistol": _card(
        "vacuum", "Drying pistol", ["Abderhalden drying pistol", "Abderhalden apparatus",
                                   "Fischer drying pistol", "Vacuum drying pistol"],
        "A pistol-shaped apparatus for drying a sample completely. The sample sits in the horizontal "
        "barrel under vacuum, with a drying agent at the end; a boiling solvent in the flask below heats "
        "the barrel to that solvent's boiling point, so the temperature is set by choosing the solvent.",
        "DRYING CHAMBER, ABDERHALDEN"),
    # --- measuring -----------------------------------------------------------------------
    "volumetric-pipette": _card(
        "measuring", "Volumetric pipette", ["Bulb pipette", "Class A pipette", "Single mark pipette"],
        "A long glass tube with a bulb in the middle and one ring on the upper stem. Filled to the ring, "
        "it delivers one exact volume — 10.00 mL, say — and is the most accurate way to transfer a "
        "measured amount of a solution."),
    "graduated-pipette": _card(
        "measuring", "Graduated pipette", ["Measuring pipette", "Mohr pipette", "Serological pipette"],
        "A straight glass tube marked with a scale along its length, so it can deliver any volume up to "
        "its capacity. Less accurate than a volumetric pipette, but one pipette covers many volumes. "
        "Filled with a pipette bulb or filler, never by mouth."),
    "pasteur-pipette": _card(
        "measuring", "Pasteur pipette", ["Dropper", "Glass dropper", "Transfer pipette, glass",
                                        "Babbitt pipette"],
        "A short glass tube drawn out to a long thin tip, used with a rubber bulb to move small amounts "
        "of liquid drop by drop. It has no scale — it is for transferring, not measuring — and is "
        "usually thrown away after use."),
    "micropipette": _card(
        "measuring", "Micropipette", ["Automatic pipette", "Pipettor", "Air displacement pipette",
                                     "Eppendorf pipette", "Micropipettor"],
        "A hand-held piston pipette with a dial for the volume and a plastic tip on the end. Press the "
        "plunger, draw up, press again to dispense: microlitre volumes, quickly and repeatably, with a "
        "fresh tip for every sample."),
    "microsyringe": _card(
        "measuring", "Microsyringe", ["Microliter syringe", "Hamilton syringe", "GC syringe"],
        "A tiny glass syringe with a fine steel needle and a scale in microlitres. Used to inject samples "
        "into a gas chromatograph and to add small, exact amounts of a liquid through a septum."),
    "burette": _card(
        "measuring", "Burette", ["Buret", "Titration burette"],
        "A long graduated glass tube with a tap at the bottom, clamped upright over a flask. Liquid is let "
        "out a little at a time and the volume used is read off the scale: it is the instrument of "
        "titration."),
    "thermometer": _card(
        "measuring", "Thermometer", ["Laboratory thermometer", "Glass thermometer", "Liquid-in-glass thermometer"],
        "A sealed glass tube with a bulb of liquid at the bottom and a temperature scale up the stem. The "
        "liquid expands as it warms and climbs the scale; in the lab it measures baths, reactions and the "
        "vapour in a distillation head."),
    "balance": _card(
        "measuring", "Electronic balance", ["Balance", "Analytical balance", "Scales",
                                           "Laboratory balance", "Top-pan balance"],
        "An electronic scale for weighing chemicals. Analytical balances read to 0.1 mg and sit inside "
        "a glass draught shield, because even air moving across the pan would change the reading."),
    "pressure-gauge": _card(
        "measuring", "Pressure gauge", ["Gauge", "Manometer", "Dial gauge", "Vacuum gauge"],
        "A dial that shows the pressure in a gas line, a cylinder regulator or a vacuum system. Inside, a "
        "curved metal tube straightens as the pressure rises and turns the needle."),
    # --- heating, stirring & support ---------------------------------------------------------
    "bunsen-burner": _card(
        "bench", "Bunsen burner", ["Bunsen", "Gas burner", "Laboratory burner"],
        "A metal tube on a heavy base that burns gas from the bench tap. A collar at the bottom lets in "
        "air: closed, the flame is yellow and cool; open, it turns into a hot, roaring blue cone."),
    "tripod": _card(
        "bench", "Tripod", ["Tripod stand", "Laboratory tripod"],
        "A three-legged iron stand that holds a beaker, a dish or a crucible above a Bunsen burner. A wire "
        "gauze or a clay triangle goes on top to support what is being heated."),
    "support-stand": _card(
        "bench", "Support stand", ["Retort stand", "Ring stand", "Lab stand", "Stand"],
        "A heavy metal base with an upright rod. Clamps and rings fixed to the rod hold flasks, "
        "condensers, funnels and burettes, and whole apparatus is built up around it."),
    "clamp": _card(
        "bench", "Clamp", ["Laboratory clamp", "Three-finger clamp", "Retort clamp", "Extension clamp",
                           "Universal clamp"],
        "Adjustable jaws on an arm, fixed to a stand with a boss head. It grips the neck of a flask or the "
        "body of a condenser and holds it in place — almost every set-up on the bench hangs from clamps."),
    "burette-clamp": _card(
        "bench", "Burette holder", ["Burette clamp", "Double burette clamp", "Buret holder"],
        "A clamp with two spring-loaded jaws that fixes to a stand and holds one or two burettes "
        "perfectly upright, so the scale can be read at eye level during a titration."),
    "lab-jack": _card(
        "bench", "Lab jack", ["Laboratory jack", "Lab lift", "Lifting platform", "Jack stand", "Scissor jack"],
        "A flat platform on a scissor mechanism, raised or lowered by turning a knob. It holds a heating "
        "bath or stirrer under a flask, and can be wound down to drop the heat away quickly."),
    "magnetic-stirrer": _card(
        "bench", "Magnetic stirrer", ["Stirrer", "Stir plate", "Hot plate stirrer", "Magnetic hotplate stirrer"],
        "A flat plate with a spinning magnet inside. It turns a stir bar in the flask on top without "
        "anything passing through the glass; most models also heat the plate."),
    "stir-bar": _card(
        "bench", "Magnetic stir bar", ["Stir bar", "Stirring bar", "Flea", "Stirring flea", "Stir bean"],
        "A small magnet sealed in white PTFE. Dropped into a flask on a magnetic stirrer, it spins and "
        "stirs the contents — which is why nearly every reaction flask has one."),
    # --- bench tools & safety -------------------------------------------------------------------
    "spatula": _card(
        "tools", "Spatula", ["Lab spatula", "Scoopula", "Spoon spatula", "Micro spatula"],
        "A small metal blade or scoop for moving solid chemicals: from the bottle to the balance, or out "
        "of a flask. Often flat at one end and spoon-shaped at the other."),
    "tweezers": _card(
        "tools", "Tweezers", ["Forceps", "Laboratory tweezers", "Twezzers"],
        "Steel tweezers for picking up small objects the fingers shouldn't touch: a stir bar, a weighing "
        "paper, a TLC plate, a crystal."),
    "mortar-and-pestle": _card(
        "tools", "Mortar and pestle", ["Mortar", "Pestle", "Mortar & pestle"],
        "A thick porcelain bowl and a club-shaped grinder. Grinding a solid between them turns lumps "
        "and crystals into a fine powder that dissolves or reacts faster."),
    "safety-goggles": _card(
        "tools", "Safety goggles", ["Goggles", "Safety glasses", "Safety spectacles", "Eye protection"],
        "Close-fitting protective glasses worn at all times in the lab. They keep splashes, flying glass "
        "and dust out of the eyes — the one piece of equipment that is never optional."),
})


# --- fixes after a review of the whole set, 2026-09-29 ----------------------------
# The coil condenser card showed two different condensers: a Dimroth (water in
# the coil) and a Graham (vapour in the coil), which do opposite jobs. They are
# two cards now. The Büchner funnel's only photo was a glass fritted funnel,
# indistinguishable from the fritted filter funnel card; it moves there and the
# Büchner card shows the porcelain funnel. Three of the glass funnel's photos
# were Synthware's powder funnels.
COMMONS.update({
    'Büchnertrichter frontal.jpg': {
        "credit": 'Ichwarsnur, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:B%C3%BCchnertrichter_frontal.jpg',
    },
    'Büchnertrichter frontal 02.jpg': {
        "credit": 'Ichwarsnur, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:B%C3%BCchnertrichter_frontal_02.jpg',
    },
    'Ceramic Buchner funnel-03.jpg': {
        "credit": 'Lilly_M, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Ceramic_Buchner_funnel-03.jpg',
    },
    'Analysentrichter.png': {
        "credit": 'MediaLab TH Köln, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Analysentrichter.png',
    },
    'Funnel MET DP234124.jpg': {
        "credit": 'The Metropolitan Museum of Art, CC0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Funnel_MET_DP234124.jpg',
    },
    'Dimrothkühler.jpg': {
        "credit": 'HaJo88, CC0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Dimrothk%C3%BChler.jpg',
    },
    'Dimroth kuehler.jpg': {
        "credit": 'Armin Kübelbeck, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Dimroth_kuehler.jpg',
    },
    'Graham (spiral) condenser-small.jpg': {
        "credit": 'Lilly_M, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Graham_(spiral)_condenser-small.jpg',
    },
    'Graham condenser.jpg': {
        "credit": 'Fleximus, CC0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Graham_condenser.jpg',
    },
    'Vacuum desiccator belonging to Rosalind Franklin - DPLA - 98e0f871c48313a61b251e383c16b1e6 (page 4).jpg': {
        "credit": 'Science History Institute, CC BY 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Vacuum_desiccator_belonging_to_Rosalind_Franklin_-_DPLA_-_98e0f871c48313a61b251e383c16b1e6_(page_4).jpg',
    },
    'Vollpipette 50 mL.png': {
        "credit": 'MediaLab TH Köln, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Vollpipette_50_mL.png',
    },
})

NEW_OR_CHANGED.update({
    # --- condensers ----------------------------------------------------------------
    "coil-condenser": {
        "name": "Graham condenser",
        "catalog_name": "CONDENSER, GRAHAM",
        "aliases": ["Coil condenser", "Coiled condenser", "Graham", "Spiral condenser"],
        "description": (
            "A glass spiral runs down the middle of a water jacket, and the vapour travels through "
            "the spiral itself, so it meets a long cooled path in a short piece of glass. It is a "
            "condenser for distillation: stood upright for reflux, the returning liquid gathers in "
            "the narrow coils and can block them."
        ),
    },
    "dimroth-condenser": _card(
        "condensers", "Dimroth condenser", ["Dimroth", "Dimroth coil condenser"],
        "A condenser turned inside out: cooling water runs through a glass coil in the middle, and the "
        "vapour rises around the coil inside the outer tube. Both water connections are at the top. The "
        "coil packs in a large cold surface while the returning liquid runs freely down past it, which "
        "makes the Dimroth one of the most efficient reflux condensers.", "CONDENSER, DIMROTH"),
    # --- funnels --------------------------------------------------------------------
    "buchner-funnel": {
        "aliases": ["Buchner funnel", "Porcelain Buchner funnel", "Filter funnel, Buchner"],
        "description": (
            "A porcelain funnel with a flat, perforated plate across its wide top. A disc of filter "
            "paper lies on the plate, the funnel sits in a filter flask on a rubber collar, and "
            "suction pulls the liquid through. It is the fast way to collect a solid and the usual "
            "last step of a precipitation. Glass funnels with a sintered disc in place of the plate "
            "and paper are fritted filter funnels."
        ),
    },
    "fritted-filter-funnel": {
        "aliases": ["Sintered filter funnel", "Sintered glass funnel", "Fritted Buchner funnel",
                    "Conical fritted funnel", "Glass frit funnel", "Filter funnel with fritted disc"],
    },
    "powder-funnel": {
        "description": (
            "A funnel with a short, very wide stem, so a dry solid can be tipped into a narrow flask "
            "neck without bridging in the stem and without dusting over the bench. Most end in a "
            "ground-glass joint, so they sit firmly in the neck instead of wobbling."
        ),
    },
    # --- adapters: the two differ only in the bend, so the names say so -------------
    "inlet-adapter": {
        "name": "Straight inlet adapter",
        "aliases": ["Inlet adapter", "Gas inlet adapter", "Straight hose adapter", "Hose adapter, straight"],
        "description": (
            "A ground-glass joint that ends in a straight hose barb. Pushed into the top of a "
            "condenser or a flask neck, it connects the apparatus to a gas line, a bubbler or a "
            "vacuum hose: the simplest way to keep a set-up under nitrogen or argon, or to lead "
            "fumes away from it."
        ),
    },
    "vacuum-gas-adapter": {
        "name": "Bent inlet adapter",
        "aliases": ["Inert gas adapter", "Bent hose adapter", "90° inlet adapter",
                    "Gas inlet adapter with hose connection", "Argon adapter", "Nitrogen adapter",
                    "Vacuum / inert gas adapter"],
        "description": (
            "A ground-glass joint with a hose barb bent through a right angle, so the tubing leaves "
            "sideways instead of straight up. On a flask neck that keeps the hose out of the way and "
            "stops its weight levering on the joint. Pumping a flask down and refilling it with "
            "nitrogen or argon through one of these is the usual way to get the air out before a "
            "sensitive reaction."
        ),
    },
    "stopcock-vacuum-adapter": {
        "description": (
            "An adapter with a hose connection and a tap, for joining a flask to a vacuum or "
            "inert-gas line. With the tap closed the flask stays sealed, so it can be taken off the "
            "line and carried away, or pumped out and refilled again and again without "
            "disconnecting anything."
        ),
    },
    "vacuum-takeoff-adapter": {
        "aliases": ["Vacuum adapter", "Distillation adapter", "Bend adapter", "Take-off adapter",
                    "Distilling adapter", "Vacuum takeoff"],
    },
    "anti-splash-adapter": {
        "aliases": ["Bump trap", "Rotovap bump trap", "Splash head", "Anti splash head",
                    "Splash adapter", "Anti-climb adapter"],
    },
    # --- vessels ----------------------------------------------------------------------
    "crystallizing-dish": {
        "description": (
            "A shallow, flat-bottomed glass dish with straight sides. In a synthesis lab it is most "
            "often a bath: filled with ice, water or oil, it sits on the stirrer under the flask. Its "
            "wide open surface also lets a solvent evaporate quickly and leave the dissolved solid "
            "behind as crystals."
        ),
    },
    "erlenmeyer-flask": {"aliases": ["Conical flask"]},
    "schlenk-tube": {
        "description": (
            "A narrow tube with a side arm and a stopcock or PTFE valve: the tube-shaped relative "
            "of the Schlenk flask. Small amounts of air-sensitive material are made or stored in it "
            "under inert gas, and like the flask it can be pumped out and refilled on a Schlenk line."
        ),
    },
    "gas-washing-bottle": {"aliases": ["Drechsel bottle", "Gas scrubber", "Gas wash bottle"]},
})

# Sharper photos and new cards from the Synthware shop at labware-shop.com.
from labware import NEW_CARDS as _LABWARE_CARDS, PHOTOS as _LABWARE_PHOTOS  # noqa: E402

PHOTOS.update(_LABWARE_PHOTOS)
NEW_OR_CHANGED.update(_LABWARE_CARDS)
for _slug in _LABWARE_PHOTOS:
    DROPPED.pop(_slug, None)

# --- new cards, 2026-09-29 ---------------------------------------------------------
# Everyday equipment the set was missing, all photographed from Commons. Still
# missing for want of a usable photograph: Wurtz and Claisen flasks, UV lamp.
PHOTOS.update({
    "dean-stark-trap": ["wm:Dean-Stark.JPG", "wm:Dean-Stark trap in use.jpg"],
    "rotary-evaporator": ["wm:Rotationsverdampfer ohne Vakuumpumpe.jpg", "wm:Rotationsverdampfer.jpg",
                          "wm:Heidolph Rotary evaporator.jpg"],
    "heating-mantle": ["wm:Electrothermal Heating Mantle.jpg", "wm:Topné hnízdo.jpg", "wm:Heating Mantle1.jpg"],
    "cork-ring": ["wm:Korkring.png", "wm:Round bottom flasks cork stand.jpg",
                  "wm:Korkové podstavce pro varné baňky s kulatým dnem.jpg"],
    "wash-bottle": ["wm:Lab wash-bottles water EtOH.jpg", "wm:Wash bottle.jpg", "wm:Wash bottle2.jpg"],
    "stirring-rod": ["wm:Stirring rod.jpg", "wm:Pyrex Glass Rod.jpg", "wm:Glass rod.jpg"],
    "watch-glass": ["wm:Uhrglas.png", "wm:Chroman sodný.JPG"],
    "rubber-stopper": ["wm:Rubber stopper holes.jpg", "wm:Rubber stopper.jpeg", "wm:Rubber bung 1.jpg"],
    "syringe": ["wm:Disposable syringe 5ml 3.jpg", "wm:Disposable syringe 30ml 3.jpg", "wm:Syringe with needle (2).JPG"],
    "tlc-plate": ["wm:TLC-isomers.jpg", "wm:Chiral TLC Baclofen.jpg"],
})
DROPPED.pop("dean-stark-trap", None)

COMMONS.update({
    'Dean-Stark.JPG': {
        "credit": 'Epop, CC0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Dean-Stark.JPG',
    },
    'Dean-Stark trap in use.jpg': {
        "credit": 'Mfomich, CC0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Dean-Stark_trap_in_use.jpg',
    },
    'Rotationsverdampfer.jpg': {
        "credit": 'Gmhofmann, public domain, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Rotationsverdampfer.jpg',
    },
    'Heidolph Rotary evaporator.jpg': {
        "credit": 'Edsel Little, CC BY-SA 2.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Heidolph_Rotary_evaporator.jpg',
    },
    'Rotationsverdampfer ohne Vakuumpumpe.jpg': {
        "credit": 'HaJo88, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Rotationsverdampfer_ohne_Vakuumpumpe.jpg',
    },
    'Electrothermal Heating Mantle.jpg': {
        "credit": 'Markbob1968, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Electrothermal_Heating_Mantle.jpg',
    },
    'Topné hnízdo.jpg': {
        "credit": 'Milda 444, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Topn%C3%A9_hn%C3%ADzdo.jpg',
    },
    'Heating Mantle1.jpg': {
        "credit": 'Naithik Shetty, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Heating_Mantle1.jpg',
    },
    'Lab wash-bottles water EtOH.jpg': {
        "credit": 'Masur, public domain, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Lab_wash-bottles_water_EtOH.jpg',
    },
    'Wash bottle.jpg': {
        "credit": 'Kessaya.gae, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Wash_bottle.jpg',
    },
    'Wash bottle2.jpg': {
        "credit": 'Kessaya.gae, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Wash_bottle2.jpg',
    },
    'Uhrglas.png': {
        "credit": 'MediaLab TH Köln, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Uhrglas.png',
    },
    'Chroman sodný.JPG': {
        "credit": 'Ondřej Mangl, public domain, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Chroman_sodn%C3%BD.JPG',
    },
    'Stirring rod.jpg': {
        "credit": 'TarnPraewan, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Stirring_rod.jpg',
    },
    'Pyrex Glass Rod.jpg': {
        "credit": 'TarnPraewan, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Pyrex_Glass_Rod.jpg',
    },
    'Glass rod.jpg': {
        "credit": 'TarnPraewan, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Glass_rod.jpg',
    },
    'Disposable syringe 5ml 3.jpg': {
        "credit": 'Nadina Wiórkiewicz (Nadine90), CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Disposable_syringe_5ml_3.jpg',
    },
    'Disposable syringe 30ml 3.jpg': {
        "credit": 'Nadina Wiórkiewicz (Nadine90), CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Disposable_syringe_30ml_3.jpg',
    },
    'Syringe with needle (2).JPG': {
        "credit": 'Intropin, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Syringe_with_needle_(2).JPG',
    },
    'Round bottom flasks cork stand.jpg': {
        "credit": 'Nadina Wiórkiewicz (Nadine90), CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Round_bottom_flasks_cork_stand.jpg',
    },
    'Korkové podstavce pro varné baňky s kulatým dnem.jpg': {
        "credit": 'Milda 444, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Korkov%C3%A9_podstavce_pro_varn%C3%A9_ba%C5%88ky_s_kulat%C3%BDm_dnem.jpg',
    },
    'Korkring.png': {
        "credit": 'MediaLab TH Köln, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Korkring.png',
    },
    'Rubber stopper holes.jpg': {
        "credit": 'U5780710, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Rubber_stopper_holes.jpg',
    },
    'Rubber stopper.jpeg': {
        "credit": 'Gharris, CC BY-SA 3.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Rubber_stopper.jpeg',
    },
    'Rubber bung 1.jpg': {
        "credit": 'Nadans., CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Rubber_bung_1.jpg',
    },
    'TLC-isomers.jpg': {
        "credit": 'Dvnyn, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:TLC-isomers.jpg',
    },
    'Chiral TLC Baclofen.jpg': {
        "credit": 'RBn53, CC BY-SA 4.0, via Wikimedia Commons',
        "url": 'https://commons.wikimedia.org/wiki/File:Chiral_TLC_Baclofen.jpg',
    },
})

NEW_OR_CHANGED.update({
    # --- distillation ------------------------------------------------------------------
    "dean-stark-trap": _card(
        "distillation", "Dean–Stark trap", ["Dean-Stark apparatus", "Dean Stark", "Dean-Stark receiver",
                                            "Water separator"],
        "A graduated side tube with a tap, fitted between a reaction flask and a reflux condenser. The "
        "solvent — usually toluene — boils off together with the water the reaction makes; both condense "
        "and drip into the tube, where the heavier water sinks and the solvent overflows back into the "
        "flask. Taking the water out drives the reaction to completion, and the scale shows how far it "
        "has got.", "DEAN-STARK TRAP"),
    "rotary-evaporator": _card(
        "distillation", "Rotary evaporator", ["Rotovap", "Rotavap", "Rotary evaporation apparatus"],
        "An instrument for removing solvent from a solution quickly and gently. The flask spins, half "
        "dipped in a warm water bath, so the liquid spreads into a thin film; under vacuum the solvent "
        "boils far below its normal boiling point, condenses on a cooled coil and runs into a receiving "
        "flask. Almost every organic product is concentrated on one.", "ROTARY EVAPORATOR"),
    # --- heating & support -------------------------------------------------------------------
    "heating-mantle": _card(
        "bench", "Heating mantle", ["Mantle heater", "Heating mantel", "Isomantle"],
        "A bowl of woven glass fabric with a heating wire inside, shaped to cradle a round-bottom flask. "
        "It heats the whole lower half of the flask evenly, with no open flame and no bath of hot oil, "
        "which makes it the usual way to heat a flask for a distillation or a reflux."),
    "cork-ring": _card(
        "bench", "Cork ring", ["Cork flask stand", "Cork support ring", "Flask stand"],
        "A thick ring of cork that a round-bottom flask sits in on the bench. Without it the flask would "
        "roll over; cork also does not scratch the glass and does not draw heat out of a hot flask as "
        "suddenly as a cold bench top would."),
    # --- bench tools --------------------------------------------------------------------------
    "wash-bottle": _card(
        "tools", "Wash bottle", ["Squeeze bottle", "Squirt bottle", "Rinse bottle"],
        "A soft plastic bottle with a bent nozzle. Squeezing it sends out a thin, aimed stream of water "
        "or solvent — for rinsing glassware, washing a solid on a filter, or bringing a volumetric flask "
        "up to the mark."),
    "stirring-rod": _card(
        "tools", "Glass rod", ["Stirring rod", "Glass stirring rod", "Stir rod"],
        "A plain rod of solid glass. It stirs a solution in a beaker, guides a liquid down into a funnel "
        "without splashing, scratches the inside of a flask to start crystals forming, and carries a "
        "drop of solution onto indicator paper."),
    # --- tubes & dishes -----------------------------------------------------------------------
    "watch-glass": _card(
        "tubes", "Watch glass", ["Watch-glass", "Clock glass"],
        "A round, slightly curved disc of glass, like the glass of an old pocket watch. It covers a "
        "beaker to keep dust out while vapour escapes, holds a little solid for weighing or drying, and "
        "lets a drop of solution evaporate where the residue can be seen."),
    # --- closures -------------------------------------------------------------------------------
    "rubber-stopper": _card(
        "closures", "Rubber stopper", ["Rubber bung", "Bung", "Bored stopper"],
        "A tapered plug of rubber for a flask or a test tube without a ground-glass joint. Bored through, "
        "it holds a thermometer, a glass tube or a funnel stem. Rubber swells in many organic solvents, "
        "so it belongs to aqueous work and to teaching labs."),
    # --- measuring ------------------------------------------------------------------------------
    "syringe": _card(
        "measuring", "Syringe", ["Disposable syringe", "Plastic syringe", "Luer syringe",
                                 "Syringe with needle"],
        "A plastic or glass barrel with a plunger and, usually, a steel needle on a Luer fitting. In the "
        "lab it measures out a liquid and moves it through a septum without opening the flask, so air- "
        "and moisture-sensitive reagents go straight from their bottle into the reaction."),
    # --- chromatography ------------------------------------------------------------------------
    "tlc-plate": _card(
        "chromatography", "TLC plate", ["Thin-layer chromatography plate", "Silica plate", "TLC sheet"],
        "A sheet of glass, aluminium or plastic coated with a thin layer of silica gel. Spots of the "
        "mixtures go on a pencil line near the bottom; after the plate has stood in solvent in a "
        "developing tank, the compounds sit at different heights and are seen under a UV lamp or with "
        "a stain."),
})
