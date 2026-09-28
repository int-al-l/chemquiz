"""Curated concepts for the quiz.

One entry here becomes one card in Explore. The `photos` list holds every
catalog entry that shows *the same piece of glassware*, and those become the
photo variants a quiz question can draw from.

The merge rule is visual: two catalog entries collapse into one concept when a
photograph alone cannot separate them. That is what keeps a question honest --
because every option offered is a different concept, and every concept looks
different, a question can never have two right answers.

Cases where the rule bites:
  * "Reflux", "coiled" and "Graham" condensers all show a spiral inside a
    jacket. Which one you are holding depends on which path carries coolant,
    and that is invisible. One concept, eight photographs.
  * "Liebig", "West" and "distillation" condensers are all a straight inner
    tube in a jacket. One concept.
  * "Reducing" and "enlarging" adapters are the same object described from
    opposite ends.
  * "Evaporation flask" is a conical flask with a ground joint; it sits with
    the Erlenmeyer rather than beside it.
Numbers in `photos` are indices into products.json (photos only), the same
numbers printed on the review contact sheets.
"""

GROUPS = [
    ("flasks", "Flasks", "Vessels that hold a reaction or a sample."),
    ("condensers", "Condensers", "Cool vapour back to liquid, for reflux or distillation."),
    ("funnels", "Funnels", "Transfer, filter, separate and add liquids."),
    ("adapters", "Adapters", "Join, redirect and seal one piece of apparatus to another."),
    ("distillation", "Distillation", "Heads, columns and receivers for separating by boiling point."),
    ("extraction", "Extraction", "Pull a compound out of a solid or another solvent."),
    ("filtration", "Filtration", "Separate a solid from the liquid around it."),
    ("vacuum", "Vacuum & Schlenk", "Working under vacuum or an inert atmosphere."),
    ("chromatography", "Chromatography", "Separate a mixture on a stationary phase."),
    ("closures", "Stoppers & stopcocks", "Seal a joint or control a flow."),
]


CONCEPTS = [
    # ---------------------------------------------------------------- flasks
    dict(slug="round-bottom-flask", name="Round-bottom flask", group="flasks",
         photos=[146], desc=146,
         aliases=["RBF", "Round bottomed flask", "Boiling flask", "Single neck round bottom flask"]),
    dict(slug="two-neck-flask", name="Two-neck round-bottom flask", group="flasks",
         photos=[152, 147], desc=152,
         aliases=["Two necked flask", "2-neck flask", "Double neck round bottom flask"]),
    dict(slug="three-neck-flask", name="Three-neck round-bottom flask", group="flasks",
         photos=[153, 154], desc=153,
         aliases=["Three necked flask", "3-neck flask", "Triple neck flask"]),
    dict(slug="four-neck-flask", name="Four-neck round-bottom flask", group="flasks",
         photos=[155, 159, 160], desc=160,
         aliases=["Four necked flask", "4-neck flask"]),
    dict(slug="pear-shaped-flask", name="Pear-shaped flask", group="flasks",
         photos=[149, 151, 326], desc=149,
         aliases=["Recovery flask", "Pear flask", "Teardrop flask"]),
    dict(slug="erlenmeyer-flask", name="Erlenmeyer flask", group="flasks",
         photos=[161, 148, 331], desc=161,
         aliases=["Conical flask", "Evaporation flask"]),
    dict(slug="filtering-flask", name="Filter flask", group="flasks",
         photos=[162, 332], desc=162,
         aliases=["Buchner flask", "Büchner flask", "Side-arm flask", "Filtering flask",
                  "Suction flask", "Vacuum flask for filtration"]),
    dict(slug="jacketed-reaction-flask", name="Jacketed reaction flask", group="flasks",
         photos=[157], desc=157,
         aliases=["Jacketed flask", "Double walled reaction flask"]),
    dict(slug="bottom-outlet-flask", name="Bottom-outlet reaction flask", group="flasks",
         photos=[158], desc=158,
         aliases=["Drain flask", "Flask with bottom outlet", "Bottom drain flask"]),
    dict(slug="dewar-flask", name="Dewar flask", group="flasks",
         photos=[91, 92], desc=91,
         aliases=["Dewar", "Vacuum flask", "Cryogenic flask"]),
    dict(slug="volumetric-flask", name="Volumetric flask", group="flasks",
         photos=[343, 342], desc=343,
         aliases=["Measuring flask", "Graduated flask", "Class A volumetric flask"]),
    dict(slug="beaker", name="Beaker", group="flasks",
         photos=[341], desc=341,
         aliases=["Glass beaker", "Low form beaker"]),
    dict(slug="crystallizing-dish", name="Crystallizing dish", group="flasks",
         photos=[345], desc=345,
         aliases=["Crystallising dish", "Crystallisation dish"]),
    dict(slug="kuderna-danish-flask", name="Kuderna-Danish flask", group="flasks",
         photos=[142], desc=142,
         aliases=["KD flask", "Kuderna Danish concentrator"]),
    dict(slug="conical-reaction-vial", name="Conical reaction vial", group="flasks",
         photos=[322, 323], desc=322,
         aliases=["Reaction vial", "Microscale vial", "V-vial"]),
    dict(slug="pressure-vessel", name="Pressure tube", group="flasks",
         photos=[200, 201, 202, 203], desc=200,
         aliases=["Heavy-wall pressure vessel", "Sealed tube", "Ace pressure tube",
                  "Pressure bottle", "Pressure vessel"]),
    dict(slug="peptide-synthesis-vessel", name="Peptide synthesis vessel", group="flasks",
         photos=[192, 193, 194, 195], desc=192,
         aliases=["Solid phase synthesis vessel", "SPPS vessel"]),

    # ------------------------------------------------------------ condensers
    dict(slug="liebig-condenser", name="Liebig condenser", group="condensers",
         photos=[87, 86, 85, 84, 68, 69], desc=87,
         aliases=["Straight condenser", "West condenser", "Distillation condenser",
                  "Liebig", "Jacketed straight condenser"]),
    dict(slug="coil-condenser", name="Coil condenser", group="condensers",
         photos=[74, 75, 76, 77, 78, 79, 80, 81], desc=74,
         aliases=["Coiled condenser", "Graham condenser", "Reflux condenser",
                  "Spiral condenser", "Coil reflux condenser"]),
    dict(slug="allihn-condenser", name="Allihn condenser", group="condensers",
         photos=[82, 83], desc=82,
         aliases=["Bulb condenser", "Allihn", "Reflux bulb condenser"]),
    dict(slug="friedrichs-condenser", name="Friedrichs condenser", group="condensers",
         photos=[73, 72, 71], desc=73,
         aliases=["Friedrich condenser", "Cold finger reflux condenser", "Friedrichs"]),
    dict(slug="cold-finger-condenser", name="Cold finger condenser", group="condensers",
         photos=[70], desc=70,
         aliases=["Cold finger", "Cold finger with drip tip"]),
    dict(slug="dewar-condenser", name="Dewar condenser", group="condensers",
         photos=[88], desc=88,
         aliases=["Vacuum jacketed cold finger", "Micro dewar condenser"]),
    dict(slug="rotary-evaporator-condenser", name="Rotary evaporator condenser", group="condensers",
         photos=[89, 90], desc=89,
         aliases=["Rotovap condenser", "Rotary evaporator coil condenser"]),
    dict(slug="air-condenser", name="Air condenser", group="condensers",
         photos=[319, 317], desc=319,
         aliases=["Air reflux condenser", "Air cooled condenser"]),

    # ----------------------------------------------------------- distillation
    dict(slug="vigreux-column", name="Vigreux column", group="distillation",
         photos=[65, 318], desc=65,
         aliases=["Vigreux", "Distilling column", "Fractionating column"]),
    dict(slug="distilling-head", name="Distilling head", group="distillation",
         photos=[119], desc=119,
         aliases=["Still head", "Distillation head", "Three-way head"]),
    dict(slug="jacketed-vigreux-head", name="Jacketed Vigreux head", group="distillation",
         photos=[130, 131, 129], desc=131,
         aliases=["Vacuum jacketed vigreux head", "Micro vigreux head",
                  "Jacketed Vigreux distillation head"]),
    dict(slug="short-path-apparatus", name="Short-path distillation apparatus", group="distillation",
         photos=[113, 115, 112, 110, 117, 118, 116], desc=113,
         aliases=["Short path apparatus", "Short path distillation head",
                  "Short path head", "Microscale distillation apparatus",
                  "Vacuum jacketed short path"]),
    dict(slug="cow-receiver", name="Cow receiver", group="distillation",
         photos=[122, 124], desc=122,
         aliases=["Pig", "Distillation cow", "Multi-receiver adapter", "Cow"]),
    dict(slug="dean-stark-trap", name="Dean-Stark trap", group="distillation",
         photos=[136, 137], desc=136,
         aliases=["Dean Stark", "Dean-Stark receiver", "Water separator", "Azeotropic trap"]),
    dict(slug="distillation-receiver", name="Distillation receiver", group="distillation",
         photos=[111, 125], desc=111,
         aliases=["Receiver adapter", "Graduated receiver", "Distilling receiver"]),
    dict(slug="kugelrohr-bulb", name="Kugelrohr distilling bulb", group="distillation",
         photos=[109], desc=109,
         aliases=["Kugelrohr", "Kugelrohr bulb", "Bulb-to-bulb distillation bulb"]),
    dict(slug="snyder-column", name="Snyder column", group="distillation",
         photos=[141], desc=141,
         aliases=["Snyder distillation column", "Snyder"]),

    # --------------------------------------------------------------- funnels
    dict(slug="buchner-funnel", name="Büchner funnel", group="funnels",
         photos=[185, 184, 182, 174], desc=184,
         aliases=["Buchner funnel", "Sintered glass funnel", "Fritted Buchner funnel",
                  "Filter funnel, Buchner"]),
    dict(slug="fritted-filter-funnel", name="Fritted filter funnel", group="funnels",
         photos=[176, 177, 175], desc=177,
         aliases=["Sintered filter funnel", "Conical fritted funnel", "Glass frit funnel",
                  "Filter funnel with fritted disc"]),
    dict(slug="powder-funnel", name="Powder funnel", group="funnels",
         photos=[178, 179, 180], desc=178,
         aliases=["Solids funnel", "Wide stem funnel", "Powder addition funnel"]),
    dict(slug="separatory-funnel", name="Separatory funnel", group="funnels",
         photos=[207, 206, 208, 209], desc=206,
         aliases=["Sep funnel", "Separating funnel", "Squibb funnel", "Sepfunnel"]),
    dict(slug="pressure-equalizing-funnel", name="Pressure-equalizing dropping funnel", group="funnels",
         photos=[211, 210], desc=211,
         aliases=["Pressure equalising funnel", "Addition funnel with pressure equalizing arm",
                  "Dropping funnel", "Equalizing addition funnel"]),
    dict(slug="addition-funnel", name="Solvent addition funnel", group="funnels",
         photos=[181], desc=181,
         aliases=["Solvent addition", "Graduated addition funnel"]),
    dict(slug="gooch-crucible", name="Gooch crucible", group="funnels",
         photos=[183], desc=183,
         aliases=["Filter crucible", "Sintered crucible", "Gooch"]),
    dict(slug="fritted-filter-tube", name="Fritted filter tube", group="funnels",
         photos=[189, 190], desc=189,
         aliases=["Filter tube", "Inline filter tube", "Fritted tube"]),

    # -------------------------------------------------------------- adapters
    dict(slug="reducing-adapter", name="Reducing adapter", group="adapters",
         photos=[1, 2, 0, 13], desc=1,
         aliases=["Enlarging adapter", "Expansion adapter", "Reduction adapter",
                  "Joint reducer", "Reducer", "Bushing adapter", "Bushing"]),
    dict(slug="ball-socket-adapter", name="Ball-socket adapter", group="adapters",
         photos=[3], desc=3,
         aliases=["Spherical joint adapter", "Ball joint adapter"]),
    dict(slug="inlet-adapter", name="Gas inlet adapter", group="adapters",
         photos=[4, 309], desc=4,
         aliases=["Inlet adapter", "Gas inlet tube adapter", "Gas adapter"]),
    dict(slug="thermometer-adapter", name="Thermometer adapter", group="adapters",
         photos=[6, 311, 312], desc=6,
         aliases=["Thermometer inlet adapter", "Screw cap thermometer adapter"]),
    dict(slug="vacuum-gas-adapter", name="Inert gas adapter", group="adapters",
         photos=[8, 10, 11, 12, 29, 9, 28], desc=8,
         aliases=["Gas inlet adapter with hose connection", "Argon adapter",
                  "Nitrogen adapter", "Vacuum adapter", "Vacuum / inert gas adapter"]),
    dict(slug="stopcock-vacuum-adapter", name="Vacuum adapter with stopcock", group="adapters",
         photos=[17, 16, 18, 19, 21, 310], desc=17,
         aliases=["Gas adapter with stopcock", "Vacuum adapter with PTFE stopcock",
                  "Inlet adapter with stopcock"]),
    dict(slug="claisen-adapter", name="Claisen adapter", group="adapters",
         photos=[43, 45, 314], desc=43,
         aliases=["Claisen head", "Claisen", "Claisen connecting adapter"]),
    dict(slug="vacuum-takeoff-adapter", name="Vacuum take-off adapter", group="adapters",
         photos=[30, 31, 39, 40, 315], desc=30,
         aliases=["Distillation adapter", "Bend adapter", "Take-off adapter",
                  "Distilling adapter", "Vacuum takeoff"]),
    dict(slug="drying-tube-adapter", name="Drying tube", group="adapters",
         photos=[35, 34], desc=35,
         aliases=["Drying tube adapter", "Calcium chloride tube", "Guard tube"]),
    dict(slug="anti-splash-adapter", name="Anti-splash adapter", group="adapters",
         photos=[54, 55, 56, 57], desc=54,
         aliases=["Splash head", "Anti splash head", "Splash adapter", "Anti-climb adapter"]),
    dict(slug="kjeldahl-trap", name="Kjeldahl trap", group="adapters",
         photos=[50, 51], desc=50,
         aliases=["Kjeldahl", "Kjeldahl splash trap"]),
    dict(slug="vapor-duct", name="Vapour duct", group="adapters",
         photos=[58], desc=58,
         aliases=["Vapor duct", "Rotovap vapour tube", "Rotary evaporator vapor tube",
                  "Rotary evaporator vapour duct"]),

    # ------------------------------------------------------------ extraction
    dict(slug="soxhlet-extractor", name="Soxhlet extractor", group="extraction",
         photos=[139], desc=139,
         aliases=["Soxhlet", "Soxhlet extraction body"]),
    dict(slug="extraction-thimble", name="Extraction thimble", group="extraction",
         photos=[140], desc=140,
         aliases=["Soxhlet thimble", "Glass thimble"]),
    dict(slug="concentrator-tube", name="Concentrator tube", group="extraction",
         photos=[143], desc=143,
         aliases=["Graduated concentrator tube", "Kuderna-Danish concentrator tube"]),

    # ------------------------------------------------------------ filtration
    dict(slug="filtration-apparatus", name="Membrane filtration apparatus", group="filtration",
         photos=[144, 145], desc=144,
         aliases=["Filtration apparatus", "Membrane filter holder", "47mm filter apparatus"]),

    # --------------------------------------------------------------- vacuum
    dict(slug="schlenk-flask", name="Schlenk flask", group="vacuum",
         photos=[170, 171, 166, 165, 167, 168, 163], desc=170,
         aliases=["Schlenk", "Reaction flask with stopcock", "Schlenk reaction flask"]),
    dict(slug="schlenk-tube", name="Schlenk tube", group="vacuum",
         photos=[173, 164, 169], desc=173,
         aliases=["Reaction tube", "Storage tube", "Schlenk storage tube",
                  "J Young tube", "Young's ampoule", "J Young ampoule", "Young ampoule"]),
    dict(slug="vacuum-manifold", name="Vacuum / inert gas manifold", group="vacuum",
         photos=[212, 213, 215, 217, 223, 225], desc=212,
         aliases=["Schlenk line", "Dual manifold", "Vacuum manifold", "Gas manifold",
                  "Double manifold"]),
    dict(slug="vacuum-trap", name="Vacuum trap", group="vacuum",
         photos=[238, 239, 240, 241], desc=238,
         aliases=["Cold trap", "Solvent trap", "Vacuum line trap"]),
    dict(slug="bubbler", name="Bubbler", group="vacuum",
         photos=[61, 62, 59], desc=61,
         aliases=["Oil bubbler", "Mineral oil bubbler", "Gas bubbler", "Bubbler trap"]),
    dict(slug="gas-washing-bottle", name="Gas washing bottle", group="vacuum",
         photos=[63, 64], desc=63,
         aliases=["Drechsel bottle", "Gas scrubber", "Washing bottle"]),
    dict(slug="gas-dispersion-tube", name="Gas dispersion tube", group="vacuum",
         photos=[186, 187, 188], desc=186,
         aliases=["Sparger", "Fritted gas dispersion tube", "Gas sparger"]),
    dict(slug="sublimator", name="Sublimation apparatus", group="vacuum",
         photos=[306, 307, 308], desc=306,
         aliases=["Sublimator", "Cold finger sublimator", "Vacuum sublimation apparatus"]),
    dict(slug="solvent-still-head", name="Solvent still head", group="vacuum",
         photos=[244, 245, 246, 248], desc=244,
         aliases=["Still head for solvent purification", "Solvent still",
                  "Solvent purification still head"]),
    dict(slug="high-vacuum-valve", name="High-vacuum valve", group="vacuum",
         photos=[295, 296, 298, 299, 301], desc=295,
         aliases=["PTFE valve", "Teflon valve", "J Young valve", "Kontes valve",
                  "High vacuum stopcock"]),

    # -------------------------------------------------------- chromatography
    dict(slug="chromatography-column", name="Chromatography column", group="chromatography",
         photos=[95, 97, 105, 104, 100, 106], desc=95,
         aliases=["Flash column", "Flash chromatography column", "Column",
                  "Glass chromatography column"]),
    dict(slug="chromatography-reservoir", name="Chromatography reservoir", group="chromatography",
         photos=[94, 108], desc=94,
         aliases=["Solvent reservoir", "Chromatography solvent reservoir"]),
    dict(slug="chromatography-column-reservoir",
         name="Chromatography column with reservoir", group="chromatography",
         photos=[98, 99, 102, 103], desc=98,
         aliases=["Column with reservoir", "Chromatography column and reservoir",
                  "Flash column with reservoir"]),
    dict(slug="tlc-tank", name="TLC developing tank", group="chromatography",
         photos=[96], desc=96,
         aliases=["TLC tank", "Developing chamber", "TLC chamber"]),

    # -------------------------------------------------------------- closures
    dict(slug="glass-stopper", name="Glass stopper", group="closures",
         photos=[249, 250, 251, 253], desc=249,
         aliases=["Penny-head stopper", "Ground glass stopper", "Stopper"]),
    dict(slug="ptfe-stopper", name="PTFE stopper", group="closures",
         photos=[254, 255, 256], desc=254,
         aliases=["Teflon stopper", "Plastic stopper"]),
    dict(slug="septum", name="Rubber septum", group="closures",
         photos=[270, 271, 272], desc=270,
         aliases=["Septum", "Suba seal", "Sleeve stopper septum", "Rubber seal"]),
    dict(slug="ptfe-stopcock", name="PTFE stopcock", group="closures",
         photos=[277, 280, 282, 284], desc=277,
         aliases=["Teflon stopcock", "PTFE tap", "Teflon tap"]),
    dict(slug="glass-stopcock", name="Glass stopcock", group="closures",
         photos=[285, 288, 289, 291], desc=285,
         aliases=["Ground glass stopcock", "Glass tap", "High vacuum glass stopcock"]),
    dict(slug="joint-clip", name="Joint clip", group="closures",
         photos=[258], desc=258,
         aliases=["Keck clip", "Keck clamp", "Joint clamp", "Taper joint clip"]),
]


# --------------------------------------------------------------------------
# What each piece is, for someone new to a chemistry bench
# --------------------------------------------------------------------------
#
# The catalog's own prose is written for a buyer who already knows what the
# thing is: it gives wall thickness, joint size and part numbers. A student
# meeting a piece of glassware for the first time needs the other half -- what
# it is, why it is that shape, and what it is used for. That is what these say.
# Two or three sentences each, plain language, and an application wherever one
# makes the purpose concrete.

DESCRIPTIONS = {
    # ---------------------------------------------------------------- flasks
    "round-bottom-flask":
        "The standard vessel for running a reaction. Its curved bottom spreads "
        "heat evenly and lets the liquid swirl without corners where solid can "
        "settle, and the ground-glass neck takes a condenser or a stopper. "
        "Almost anything that is heated, stirred or distilled starts here.",
    "two-neck-flask":
        "A round-bottom flask with a second opening, so something can be added "
        "or measured while the first neck is occupied. Usually the middle neck "
        "carries a condenser and the side neck a thermometer, a gas line or a "
        "dropping funnel.",
    "three-neck-flask":
        "Three openings on one flask: typically a condenser in the middle, a "
        "thermometer or inert-gas line on one side and an addition funnel on "
        "the other. It is the workhorse for reactions that have to be stirred, "
        "heated and fed at the same time.",
    "four-neck-flask":
        "A round-bottom flask with four ground-glass openings, for apparatus "
        "that needs more attachments than a three-neck flask can carry -- "
        "stirrer, condenser, thermometer and an inlet all at once.",
    "pear-shaped-flask":
        "A flask that tapers to a point, so the last few millilitres collect in "
        "a narrow tip instead of spreading over a wide floor. That makes it the "
        "flask of choice for evaporating a small sample down and recovering it "
        "afterwards.",
    "erlenmeyer-flask":
        "The cone-shaped flask: narrow at the neck, wide at the base. The shape "
        "makes it stable and easy to swirl without splashing, which is why it "
        "is used for titrations, for dissolving and mixing, and for storing "
        "solutions under a stopper.",
    "filtering-flask":
        "A thick-walled conical flask with a side arm for a vacuum hose. A "
        "Büchner funnel sits in the neck, the pump pulls the liquid through the "
        "filter paper, and the filtrate collects below. The heavy wall matters: "
        "a thin flask under vacuum can implode.",
    "jacketed-reaction-flask":
        "A flask built inside a second glass wall. Fluid from a circulating "
        "bath flows through the gap, so the contents can be held at a chosen "
        "temperature far more steadily than a bath and a hotplate allow.",
    "bottom-outlet-flask":
        "A reaction flask with a valve at its lowest point, so the contents are "
        "drained from below instead of poured out over the neck. Useful for "
        "slurries and for large volumes, where tipping a full flask would be "
        "awkward or unsafe.",
    "dewar-flask":
        "A double-walled vessel with a vacuum between the walls, which blocks "
        "almost all heat flow. It holds liquid nitrogen and dry-ice baths for "
        "hours. A domestic thermos works on exactly the same principle.",
    "volumetric-flask":
        "A flask calibrated to contain one exact volume, marked by a single "
        "ring on the narrow neck. Dissolve a weighed sample, then add solvent "
        "until the meniscus sits on the line: this is the standard way to make "
        "a solution of known concentration.",
    "beaker":
        "The plain, straight-sided cup of the laboratory. Its graduations are "
        "rough, so it is for mixing, dissolving, heating and holding liquids -- "
        "never for measuring a volume you intend to trust.",
    "crystallizing-dish":
        "A shallow, flat-bottomed dish with a wide open surface. Solvent "
        "evaporates from it quickly and leaves the dissolved solid behind as "
        "crystals, which is the simplest way to grow crystals or to dry a "
        "solid.",
    "kuderna-danish-flask":
        "A large flask narrowing into a graduated tube, used to boil a big "
        "volume of solvent down to a millilitre or two without losing the trace "
        "material dissolved in it. Standard equipment in environmental "
        "analysis, where a litre of extract has to become one small sample.",
    "conical-reaction-vial":
        "A tiny conical vessel for milligram-scale work. The V-shaped bottom "
        "keeps a very small volume in a deep, narrow column, where it can still "
        "be stirred and drawn up with a syringe.",
    "pressure-vessel":
        "A heavy-walled tube that can be sealed and heated well above the "
        "boiling point of its contents. Holding the solvent liquid under its "
        "own pressure lets a reaction run far hotter than open glassware "
        "allows; the thick wall and the screw seal are what make that safe.",
    "peptide-synthesis-vessel":
        "A vessel with a glass frit in its floor, for chemistry done on solid "
        "beads. Reagents are shaken with the beads and then drained away "
        "through the frit while the beads stay behind -- repeated cycle by "
        "cycle to build up a peptide chain.",

    # ------------------------------------------------------------ condensers
    "liebig-condenser":
        "A straight inner tube inside a water jacket: the classic condenser. "
        "Vapour passes down the middle, cooling water flows around it, and the "
        "vapour turns back into liquid. This is the standard condenser for a "
        "simple distillation.",
    "coil-condenser":
        "A spiral of tubing inside a jacket, which packs far more cooled "
        "surface into the same length of glass than a straight tube. The extra "
        "contact suits refluxing and low-boiling solvents that a plain Liebig "
        "would let escape.",
    "allihn-condenser":
        "A condenser whose inner tube is a chain of bulbs. They add surface and "
        "hold the returning liquid a moment longer, which makes this the "
        "traditional choice for reflux -- boiling a reaction for hours without "
        "losing solvent.",
    "friedrichs-condenser":
        "A cold finger spiralled inside the jacket, so the cooled surface sits "
        "in the middle of the vapour stream rather than around the outside. A "
        "very efficient reflux condenser for solvents that are hard to hold.",
    "cold-finger-condenser":
        "A finger of glass cooled from the inside and dipped into the vapour. "
        "Whatever touches it condenses on its outer surface and drips back. "
        "Cold fingers are used for reflux in tight spaces and for collecting "
        "sublimed solids.",
    "dewar-condenser":
        "A cold finger with a vacuum jacket, filled with dry ice or liquid "
        "nitrogen instead of water. It reaches temperatures water cooling "
        "cannot, which is what it takes to condense very volatile material.",
    "rotary-evaporator-condenser":
        "The coiled glass condenser of a rotary evaporator. Solvent evaporated "
        "from the spinning flask condenses here and runs down into the "
        "receiving flask -- how a solution is concentrated quickly and at low "
        "temperature.",
    "air-condenser":
        "A plain tube with no water jacket, cooled by the air around it. For "
        "solvents that boil high enough that is cooling enough, and with no "
        "hoses it is simpler and safer, especially for a reaction left running "
        "overnight.",

    # ---------------------------------------------------------- distillation
    "vigreux-column":
        "A tube with rows of indentations pointing inwards, fitted between the "
        "flask and the still head. Vapour condenses on them and re-evaporates "
        "over and over, and each of those cycles enriches it in the "
        "lower-boiling component. That is what separates two liquids whose "
        "boiling points are close.",
    "distilling-head":
        "The piece that sits on the boiling flask and turns the vapour towards "
        "the condenser, with an opening on top for a thermometer. Reading the "
        "vapour temperature there is how you know which component is coming "
        "over.",
    "jacketed-vigreux-head":
        "A Vigreux column and a still head in one piece, wrapped in a vacuum "
        "jacket so that heat is not lost through the wall. Keeping the column "
        "at its own temperature sharpens the separation, especially on small "
        "quantities.",
    "short-path-apparatus":
        "Boiling flask, condenser and receiver joined over the shortest "
        "possible distance. Little surface means little material lost on the "
        "way, so it is used for small or precious samples, and under vacuum for "
        "compounds that would decompose at their normal boiling point.",
    "cow-receiver":
        "A rotating receiver with several flasks hanging from it. Turning the "
        "cow brings a fresh flask under the outlet, so one fraction after "
        "another can be collected without breaking the vacuum.",
    "dean-stark-trap":
        "A graduated side arm that catches the water carried over during a "
        "reflux: the water collects and can be measured, while the solvent "
        "overflows back into the flask. It is what drives reactions that "
        "release water, such as making an ester, by removing the water as it "
        "forms.",
    "distillation-receiver":
        "The adapter between the condenser and the receiving flask, often "
        "graduated and usually with a port for a vacuum line. It guides the "
        "distillate into the flask and lets the distillation run under reduced "
        "pressure.",
    "kugelrohr-bulb":
        "One of a chain of bulbs used to distil small amounts over a very short "
        "path. The sample is heated in an oven while the chain rotates, and "
        "each fraction condenses in the next, cooler bulb -- with almost no "
        "glassware for it to be lost on.",
    "snyder-column":
        "A column of bulbs with loose glass floats inside. Rising vapour lifts "
        "each float and slips past; falling liquid closes it again. On a "
        "concentrator it lets the solvent boil away while holding back the "
        "material dissolved in it.",

    # --------------------------------------------------------------- funnels
    "buchner-funnel":
        "A flat filter plate on a wide cylinder. Paper (or a built-in glass "
        "frit) sits on the plate, the funnel goes into a filtering flask, and "
        "suction pulls the liquid through. It is the fast way to collect a "
        "solid and the usual last step of a precipitation.",
    "fritted-filter-funnel":
        "A funnel with a disc of fused glass instead of paper. The frit comes "
        "in graded porosities, does not tear or react, and can be washed and "
        "used again -- which matters when the liquid would attack paper or must "
        "not pick up fibres.",
    "powder-funnel":
        "A funnel with a short, very wide stem, so a dry solid can be tipped "
        "into a narrow flask neck without bridging in the stem and without "
        "dusting over the bench.",
    "separatory-funnel":
        "A pear-shaped funnel with a stopcock, for separating two liquids that "
        "do not mix. Shaking moves a compound into whichever solvent dissolves "
        "it better; the layers settle and the lower one is run off through the "
        "tap. This extraction is one of the most-used operations in organic "
        "chemistry.",
    "pressure-equalizing-funnel":
        "A dropping funnel with a side tube joining its top to the flask below. "
        "The pressure stays equal on both sides, so liquid flows steadily even "
        "in a closed, inert or evacuated apparatus, and no vapour is pushed out "
        "past the stopcock.",
    "addition-funnel":
        "A graduated funnel with a tap, for adding a liquid to a reaction "
        "slowly and by a measured amount. Controlling the rate of addition is "
        "how a strongly exothermic reaction is kept from running away.",
    "gooch-crucible":
        "A small crucible with a fritted glass base. A precipitate is filtered "
        "straight into it, dried and weighed in the same vessel -- the "
        "classical route to a gravimetric analysis.",
    "fritted-filter-tube":
        "A glass frit sealed inside a tube with a joint at each end, so "
        "filtering can happen inside a closed line rather than in the open air. "
        "Used for air-sensitive material and for filtering under inert gas.",

    # -------------------------------------------------------------- adapters
    "reducing-adapter":
        "A short adapter with a large joint at one end and a small one at the "
        "other, so pieces with different joint sizes can be connected. Read "
        "from the other end it is an enlarging adapter -- the same piece, the "
        "opposite direction.",
    "ball-socket-adapter":
        "An adapter between a spherical ball-and-socket joint and a conical "
        "one. Spherical joints can pivot a few degrees while staying sealed, "
        "which is what lets a rigid glass line reach an apparatus that does not "
        "quite line up with it.",
    "inlet-adapter":
        "A tube that carries gas through a joint and into a flask. Used to "
        "sweep an apparatus with nitrogen or argon, or to bubble a reagent gas "
        "through the reaction itself.",
    "thermometer-adapter":
        "A small adapter that holds a thermometer or a probe in a joint with a "
        "seal around it, so the tip sits in the liquid or the vapour while the "
        "flask stays closed.",
    "vacuum-gas-adapter":
        "An adapter with a hose connection, for putting a flask on a vacuum "
        "line or under inert gas. Pumping down and refilling with nitrogen or "
        "argon through one of these is the usual way to get the air out before "
        "a sensitive reaction.",
    "stopcock-vacuum-adapter":
        "The same connection to a vacuum or gas line, with a tap on it. The tap "
        "means the flask can be isolated, carried away, or pumped and refilled "
        "again and again without disconnecting anything.",
    "claisen-adapter":
        "A Y-shaped adapter that turns one flask neck into two. It is the "
        "quickest way to give a single-neck flask room for both a condenser and "
        "a thermometer, or a stirrer and an addition funnel.",
    "vacuum-takeoff-adapter":
        "The bend that carries the distillate from the condenser down into the "
        "receiving flask, with a side port for the vacuum line.",
    "drying-tube-adapter":
        "A small tube of drying agent fitted to the top of an apparatus. Air "
        "can move in and out as things heat and cool, but the moisture in it is "
        "caught on the way -- the simple protection for a reaction that water "
        "would spoil.",
    "anti-splash-adapter":
        "A bulb with a baffle inside, placed between the flask and the "
        "condenser. Liquid that bumps upwards hits the baffle and falls back "
        "instead of contaminating the distillate. It is standard on a rotary "
        "evaporator.",
    "kjeldahl-trap":
        "A splash trap for the Kjeldahl determination of nitrogen, where a "
        "strongly alkaline solution is boiled. It keeps droplets of that "
        "solution out of the distillate, which would otherwise ruin the "
        "analysis.",
    "vapor-duct":
        "The rotating tube at the heart of a rotary evaporator. It holds the "
        "flask, turns it, and carries the vapour out through a seal to the "
        "condenser while the whole apparatus is under vacuum.",

    # ------------------------------------------------------------ extraction
    "soxhlet-extractor":
        "An extractor that washes a solid with fresh, clean solvent over and "
        "over by itself. Solvent boils below, condenses above, fills the "
        "chamber holding the sample and siphons back when full -- leaving the "
        "extracted material in the flask and running unattended for hours.",
    "extraction-thimble":
        "The porous cup that holds the sample inside a Soxhlet extractor. "
        "Solvent passes through its wall; the solid stays where it is put.",
    "concentrator-tube":
        "A graduated tube that fits beneath a Kuderna-Danish flask. The "
        "concentrated extract ends up in it, where a volume of one or two "
        "millilitres can still be read off accurately.",

    # ------------------------------------------------------------ filtration
    "filtration-apparatus":
        "A funnel clamped onto a fritted support with a membrane disc between "
        "them. Suction pulls the sample through and the membrane holds back "
        "everything above a chosen particle size -- used for sterilising "
        "solutions and for preparing samples for analysis.",

    # ---------------------------------------------------------------- vacuum
    "schlenk-flask":
        "A flask with a side arm and a stopcock, made for work under vacuum or "
        "inert gas. On a vacuum line it can be pumped out and refilled with "
        "argon several times before anything is added, so a reaction sensitive "
        "to air or moisture never meets either.",
    "schlenk-tube":
        "The tube-shaped member of the same family: a narrow vessel with a "
        "stopcock, for reacting or storing small amounts of air-sensitive "
        "material under inert gas.",
    "vacuum-manifold":
        "The double manifold of a Schlenk line -- one tube to the vacuum pump, "
        "one to inert gas, and a row of taps between them. Each port can be "
        "switched from pump to gas and back, which is what makes air-free work "
        "routine.",
    "vacuum-trap":
        "A cold trap in the line ahead of a vacuum pump. Solvent vapour freezes "
        "on its cold wall instead of reaching the pump oil, which protects the "
        "pump and keeps the vacuum deep.",
    "bubbler":
        "A small vessel of oil in the gas line. Gas leaving the apparatus "
        "bubbles out through the oil, so the flow can be seen and counted, and "
        "the oil stops air coming back the other way.",
    "gas-washing-bottle":
        "A bottle in which gas is bubbled through a liquid on its way past -- "
        "to dry it, to wash out an impurity, or to trap something harmful "
        "before it reaches the room.",
    "gas-dispersion-tube":
        "A tube ending in a glass frit. Gas leaving the frit breaks into very "
        "fine bubbles, which puts far more gas surface in contact with the "
        "liquid and dissolves it much faster.",
    "sublimator":
        "A vessel with a cold finger above the sample. Under vacuum a solid "
        "that sublimes passes straight to vapour and re-forms as crystals on "
        "the cold surface -- a purification that never involves a solvent.",
    "solvent-still-head":
        "The head of a solvent still. Solvent is refluxed over a drying agent "
        "until it is dry, then the tap is turned and the dry solvent collects "
        "in the side chamber, to be drawn off under inert gas.",
    "high-vacuum-valve":
        "A valve with a PTFE plug and O-rings in place of a greased glass tap. "
        "It holds high vacuum without grease, so nothing can dissolve into the "
        "sample and the valve cannot seize shut.",

    # -------------------------------------------------------- chromatography
    "chromatography-column":
        "A vertical glass tube packed with silica gel, with a tap at the "
        "bottom. The mixture is loaded on top and solvent pushed through; "
        "compounds travel at different speeds and come out one after another. "
        "This is how most organic products are purified.",
    "chromatography-reservoir":
        "A wide reservoir that sits on top of a column and holds a large volume "
        "of solvent, so the column can run for a long time without being topped "
        "up by hand.",
    "chromatography-column-reservoir":
        "A column and its solvent reservoir blown as a single piece. Fewer "
        "joints means less to leak and one less thing to clamp during a long "
        "separation.",
    "tlc-tank":
        "A flat glass chamber with a lid, for thin-layer chromatography. A "
        "little solvent lies in the bottom, the plate stands in it, and the "
        "solvent climbs the plate by capillary action and separates the spots "
        "as it goes. It is the quickest way to see whether a reaction has "
        "finished.",

    # -------------------------------------------------------------- closures
    "glass-stopper":
        "A ground-glass plug that closes a joint. Glass on glass seals tightly "
        "with no plastic or rubber for a solvent to attack, which is why "
        "stoppered flasks are used for storing reactive solutions.",
    "ptfe-stopper":
        "A stopper machined from PTFE. It seals without grease, does not stick "
        "or freeze into the joint, and resists almost every chemical -- the "
        "practical alternative to a glass stopper.",
    "septum":
        "A rubber cap over a joint or a vial, pierced by a syringe needle. The "
        "rubber closes behind the needle, so liquids and gases can be added to "
        "or taken out of a sealed flask without ever opening it to the air.",
    "ptfe-stopcock":
        "A tap whose plug is PTFE, sealed with O-rings. It needs no grease, so "
        "nothing leaches into what flows past, and it is the usual stopcock on "
        "modern separatory funnels and columns.",
    "glass-stopcock":
        "The traditional tap: a ground glass plug in a ground glass barrel, "
        "sealed with a film of grease. Cheap, chemically inert and still "
        "standard on high-vacuum glassware, though the grease has to be "
        "renewed.",
    "joint-clip":
        "A small plastic clip that grips the rims of a taper joint and holds "
        "two pieces of glassware together. Clipped joints are what stop an "
        "apparatus coming apart under vacuum, on a rotary evaporator, or when "
        "someone knocks the bench.",
}


def all_photo_indices():
    seen = {}
    for concept in CONCEPTS:
        for index in concept["photos"]:
            if index in seen:
                raise SystemExit(
                    f"photo #{index} is claimed by both '{seen[index]}' and "
                    f"'{concept['slug']}' -- a photo may belong to one concept only, "
                    "otherwise a question could have two right answers."
                )
            seen[index] = concept["slug"]
    return seen


def normalise_answer(value):
    """Mirror of backend/app/text.py normalize(), for build-time checks."""
    import re
    import unicodedata

    text = unicodedata.normalize("NFKD", value)
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    text = re.sub(r"(\d)\s*[/-]\s*(\d)", r"\1 \2", text)
    text = re.sub(r"[^\w\s/]", " ", text).replace("/", " ")
    words = [w for w in text.split() if w not in {"a", "an", "the", "with", "and"}]
    return " ".join(words)


def check_aliases():
    """No alias may name two concepts.

    Typed answers are graded by matching a normalised string, so an alias
    shared between two items would mark a correct answer wrong on whichever
    item did not own it.
    """
    norm = normalise_answer
    owner, clashes = {}, []
    for concept in CONCEPTS:
        for text in [concept["name"], *concept["aliases"]]:
            key = norm(text)
            if key in owner and owner[key] != concept["slug"]:
                clashes.append((text, owner[key], concept["slug"]))
            owner[key] = concept["slug"]
    return clashes


if __name__ == "__main__":
    used = all_photo_indices()

    for text, first, second in check_aliases():
        raise SystemExit(
            f"alias {text!r} names both '{first}' and '{second}' -- typed mode "
            "would mark a correct answer wrong for one of them."
        )
    groups = {g[0] for g in GROUPS}
    for concept in CONCEPTS:
        if concept["group"] not in groups:
            raise SystemExit(f"{concept['slug']}: unknown group {concept['group']}")
        if concept["desc"] not in concept["photos"]:
            raise SystemExit(f"{concept['slug']}: desc index not among its photos")

    print(f"{len(CONCEPTS)} concepts in {len(GROUPS)} groups, {len(used)} photos used")
    for slug, name, _ in GROUPS:
        members = [c for c in CONCEPTS if c["group"] == slug]
        photos = sum(len(c["photos"]) for c in members)
        print(f"  {name:<24} {len(members):>2} concepts  {photos:>3} photos")
