"""Cards and descriptions from Organikum, vol. 1 (Russian edition, Mir 2008).

Every piece of equipment the book describes was checked against the set. Pieces
that were already cards keep their photos and get the book's practical points
added to their text (DESCRIPTIONS). The rest become new cards (NEW_CARDS), with
photos from the Synthware shop download ("lw:") or Wikimedia Commons ("wm:",
credited in COMMONS). Pieces for which no clean photograph could be found are
listed in NO_PHOTO and are not cards.
"""


PHOTOS = {'ground-glass-joint': ['wm:Ground glass joint open.jpg', 'wm:Ground glass joint closed.jpg'],
 'screw-clamp': ['wm:Tubing clamp-single 1.jpg',
                 'wm:Tubing clamp-single 2.jpg',
                 'wm:Tubing clamp-single 3.jpg'],
 'microscope-slide': ['wm:Fedolemez.jpg', 'wm:Glass slide.jpg'],
 'pointed-flask': ['wm:Spitzkolben.png'],
 'centrifuge-tube': ['wm:50ml Falcon tubes-01.jpg', 'wm:Zentrifugenglas.jpg', 'wm:25ml tube.jpg'],
 'ampoule': ['lw:ampul-drying_0', 'lw:ampul-drying_2', 'lw:ampul-drying-1_0'],
 'stoppered-bottle': ['wm:Pharmacy-bottles-blue hg.jpg', 'wm:Bottle, apothecary (AM 629318-1).jpg'],
 'test-tube-rack': ['wm:Reagenzglasständer Zucker-Museum.jpg', 'wm:3D printed test tube rack in use.jpg'],
 'test-tube-holder': ['wm:Test Tube Holder2 2015.JPG',
                      'wm:Two small test tubes held in spring clamps.jpg',
                      'wm:Vorsicht beim Erhitzen von Flüssigkeiten im Reagenzglas.jpg'],
 'intensive-condenser': ['lw:condenser-reflux-large-cooling-capacity_0',
                         'lw:condenser-reflux-large-cooling-capacity_1',
                         'lw:condenser-reflux-large-cooling-capacity_2',
                         'wm:Intensivkuehler.jpg'],
 'anschutz-adapter': ['lw:adapter-connecting-y-shaped_0',
                      'lw:adapter-connecting-y-shaped_1',
                      'lw:adapter-connecting-y-shaped_2'],
 'three-neck-adapter': ['lw:adapter-claisen-three-neck_0',
                        'lw:adapter-claisen-three-neck_1',
                        'lw:adapter-claisen-three-neck_2'],
 'stirrer-motor': ['wm:RZR 2051 control.jpg', 'wm:Mechanical stirrer engine.jpg'],
 'stirrer-bearing': ['lw:adapter-for-stirring-blade_0',
                     'lw:stirring-seals-for-overhead-stirrer-teflon-with-o-ring_0',
                     'lw:stirring-seals-for-overhead-stirrer-teflon-with-o-ring_1'],
 'ultrasonic-bath': ['wm:Bandelin-sonorex hg.jpg', 'wm:Ultrasonic bath 1.jpg', 'wm:Cuves ultrasons.jpg'],
 'shaker': ['wm:19112007040.jpg',
            'wm:Velkokapacitni trepacka - shaker.jpg',
            'wm:Laboratory microbiological shaker with cultures-01.jpg'],
 'rotameter': ['wm:Flowmeter float.JPG', 'wm:Rotameter.jpg', 'wm:Flow-tube-meter hg.jpg'],
 'woulfe-bottle': ['wm:Woulfe bottle 01.jpg', 'wm:Woulfe bottle 02.jpg', 'wm:Woulfesche Flasche Glas.jpg'],
 'gas-cylinder': ['wm:2008-07-24 Bundle of compressed gas bottles.jpg',
                  'wm:Gas cylinder ammonia.jpg',
                  'wm:P3230006 (7322939).jpg'],
 'gas-regulator': ['wm:Gas regulator.jpg',
                   'wm:A nitrogen gas cylinder with pressure-relief devices.jpg',
                   'wm:Pressure regulator by AGA.jpg'],
 'hot-plate': ['wm:Hot plate 2015.JPG', 'wm:Laboratory hot plate.JPG'],
 'wire-gauze': ['wm:12.5cm by 12.5cm Wire Gauze.jpg', 'wm:15cm by 15cm Wire Gauze.jpg', 'wm:Wire Gauze.jpg'],
 'water-bath': ['wm:Bain-marie laboratoire.JPG', 'wm:Circulating water bath 2015.jpg', 'wm:Wasserbad.jpg'],
 'oil-bath': ['wm:Oil bath.jpg'],
 'boiling-chips': ['wm:Siedesteinchen.jpg', 'wm:Siedesteinen auf Uhrglas.jpg'],
 'circulator': ['wm:ThermoFlex 900-Recirculating Chiller.jpg'],
 'heat-gun': ['wm:Hot air gun (1).jpg', 'wm:Hot air gun (2).jpg', 'wm:Heat Gun.JPG'],
 'drying-oven': ['wm:Trockenschrank.jpg', 'wm:Drying owen 1.jpg', 'wm:Drying owen 2.jpg'],
 'fume-hood': ['wm:Fume-hood.jpg', 'wm:Fume hood.jpg', 'wm:Fume hood MB.jpg'],
 'autoclave': ['wm:Figure-1-High-pressure-reactors-and-control-reactors.jpg'],
 'glass-autoclave': ['wm:Glass Pressure Reactor.jpg'],
 'water-aspirator': ['wm:Aspirator sample1.jpg', 'wm:CIglass aspirator 3.jpg'],
 'diaphragm-pump': ['wm:Diaphragm pump.JPG'],
 'rotary-vane-pump': ['wm:Edwards E2M2 2-Stage Rotary Vane Vacuum Pump (15957733526).jpg',
                      'wm:High-vacuum pump.jpg',
                      'wm:Öl-Rotations-Vakuumpumpe der Firma Vacuubrand Wertheim - LABW - Staatsarchiv '
                      'Wertheim S-N 70 G 3173.jpg'],
 'diffusion-pump': ['wm:Me holding a mercury based diffusion pump (for size comparison).jpg',
                    'wm:A simplified oil diffusion pump.jpg',
                    'wm:M6 Diffusion Pump.jpg'],
 'mcleod-gauge': ['wm:McLeod gauge.jpg', 'wm:McLeod gauge 01.jpg'],
 'three-way-stopcock': ['lw:stopcock-glass-t-bore-1_0',
                        'lw:stopcock-glass-t-bore-1_1',
                        'lw:stopcock-glass-t-bore_0'],
 'drying-column': ['lw:gas-drying-chamber_0', 'lw:gas-drying-chamber_1'],
 'hickman-head': ['lw:adapter-distillation-hickman_2',
                  'lw:adapter-distillation-hickman-hinkle_2',
                  'lw:adapter-distillation-hickman-side-arm_2'],
 'hot-filtration-funnel': ['lw:funnel-filter-buchner-jacketed_0',
                           'lw:funnel-filter-buchner-jacketed-1_0',
                           'lw:funnel-filter-buchner-jacketed_1'],
 'filter-paper': ['wm:Paper filters-laboratory 1.jpg', 'wm:Paper filters-laboratory 3.jpg'],
 'centrifuge': ['wm:Heraeus Multifuge 3SR centrifuge 1.jpg',
                'wm:Heraeus Multifuge 3SR centrifuge 3.jpg',
                'wm:Beckman-Coulter preparative centrifuge Avanti J25-01.jpg'],
 'spinning-band-column': ['wm:Distillation bande tournante 100 6504.jpg', 'wm:Bande tournante 100 6499.jpg'],
 'empty-column': ['lw:column-distilling_1'],
 'jacketed-column': ['lw:column-distilling-full-jacketed_1',
                     'lw:column-distilling-full-jacketed_0',
                     'lw:column-distilling-full-jacketed_2'],
 'liquid-extractor': ['lw:liquid-extraction-apparatus-teflon-stopcock_0',
                      'lw:liquid-extraction-apparatus_0',
                      'lw:extractor-liquid-liquid-continuous_0'],
 'uv-lamp': ['wm:UV cabinet for thin layer chromatography.jpg',
             'wm:UV-handlamp hg.jpg',
             "wm:Wood's UV lamp.JPG"],
 'fraction-collector': ['wm:Fraction collector - sampler LAMBDA OMNICOLL.jpg',
                        'wm:Fraction Collector Tube Rack.jpg'],
 'hplc': ['wm:HPLC to ICP-MS.JPG'],
 'gas-chromatograph': ['wm:Gas chromatographs with functional detectors in CAFIA laboratory, Czech '
                       'Republic.jpg',
                       'wm:Gas chromatograph for GCxGC analyzes connected to a QTOF mass detector and '
                       'GC-IRMS interface, in CAFIA laboratory, Czech Republic.png'],
 'thiele-tube': ['wm:Thiele Tube.jpg'],
 'melting-point-apparatus': ['wm:MEL-TEMP melting point instrument.jpg',
                             'wm:Gallenkamp Melting Point Apparatus.jpg'],
 'ebulliometer': ['wm:Ebulliometro.jpg', 'wm:Ebulliometer for measuring wine alcohol.JPG'],
 'abbe-refractometer': ['wm:Abbe Refractometer in JXTCM.jpg', 'wm:Refractometre ABBE 2009 jflm.jpg'],
 'polarimeter': ['wm:Automatic Polarimeter with Filling Funnel.jpg',
                 'wm:Modular circular polarimeter.jpg',
                 'wm:Soviet portable polarimeter in its case.jpg'],
 'saccharimeter': ['wm:Polarimeter Saccharimeter-UNIL 603.867-IMG 2052-white.jpg',
                   'wm:Saccharimeter Zucker-Museum.jpg',
                   'wm:Saccharimeter c1906 Zucker-Museum.jpg'],
 'cuvette': ['wm:Cuvette.jpg', 'wm:分光液槽.jpg', 'wm:Cuvette with penny.jpg'],
 'uv-vis-spectrometer': ['wm:DU640 spectrophotometer.jpg', 'wm:Spektrofotometri.jpg', 'wm:Wiki21039722.jpg'],
 'ir-spectrometer': ['wm:FTIR spectrometer.png', 'wm:FTIR Spectrometer + ATR.jpg', 'wm:FTIR 3000 1.jpg'],
 'nmr-spectrometer': ['wm:Bruker 300 MHz NMR Spectrometer.jpg',
                      'wm:Bruker Avance DPX 250 NMR Spectrometer.jpg',
                      'wm:NMR Bruker Avance II 700.jpg'],
 'mass-spectrometer': ['wm:Model 21-103 Mass Spectrometer in use at Exxon analytical research laboratory '
                       '1974.jpeg',
                       'wm:HR-ICP-MS, high-resolution inductively coupled plasma ionization mass '
                       'spectrometer used for multi-element analysis, in CAFIA laboratory, Czech '
                       'Republic.png',
                       'wm:EA-IRMS, isotope ratio mass spectrometer with elemental analyzer for the '
                       'determination of isotope ratios of stable isotopes in wines, spirits, honey and '
                       'natural sweeteners, in CAFIA laboratory.jpg'],
 'diffractometer': ['wm:Scxrd.jpg', 'wm:Equi-inclination 3-circle diffractometer.jpg'],
 'boss-head': ['lw:bosshead_0', 'lw:bosshead-1_0', 'lw:bosshead-2_0'],
 'graduated-receiver': ['lw:distilling-receiver-graduated-with-hooks_0',
                        'lw:distilling-receiver-graduated-with-hooks_1',
                        'lw:distilling-receiver-graduated-with-hooks_2'],
 'teclu-burner': ['wm:Teclu burner.jpg', 'wm:Brulilo Teclu.JPG', 'wm:Teclu Burner in museum.png']}

NEW_CARDS = {'ground-glass-joint': {'category': 'adapters',
                        'name': 'Ground-glass joint',
                        'aliases': ['Taper joint',
                                    'Standard taper joint',
                                    'Cone and socket',
                                    'Ground joint',
                                    'NS joint'],
                        'description': 'The standard way glassware is joined: a ground inner cone (the male '
                                       'part) slides into a ground outer socket (the female part). Joints '
                                       'are made to standard sizes, written as the widest diameter and the '
                                       'length in millimetres (NS 29/32, NS 14.5/23), so any flask fits any '
                                       'condenser of the same size and an apparatus goes together like a '
                                       'construction kit. Turn the parts gently as you join them, and keep '
                                       'resins and strong alkali off the ground surfaces.'},
 'screw-clamp': {'category': 'bench',
                 'name': 'Screw clamp',
                 'aliases': ['Hoffman clamp', 'Tubing clamp', 'Hose clamp', 'Pinchcock'],
                 'description': 'A small metal frame with a screw that squeezes a piece of rubber tubing. '
                                'Tightened fully it closes the tube; opened a little it lets through a '
                                'controlled trickle of gas or air — for example to set the pressure of a '
                                'water-pump vacuum by letting in a tiny leak.'},
 'microscope-slide': {'category': 'tubes',
                      'name': 'Microscope slide and cover slip',
                      'aliases': ['Slide', 'Glass slide', 'Cover slip', 'Cover glass', 'Microscope slide'],
                      'description': 'A thin flat strip of glass, with an even thinner square cover glass '
                                     'laid on top. A few crystals pressed between them can be watched under '
                                     'a microscope — on a hot-stage microscope, as they melt.'},
 'pointed-flask': {'category': 'flasks',
                   'name': 'Pointed flask',
                   'aliases': ['Conical-bottom flask', 'Pointed-bottom flask', 'Kjeldahl-type pointed flask'],
                   'description': 'A flask whose bottom narrows to a point. The last drops of a liquid '
                                  'gather in the tip, so a distillation of a few millilitres can be taken '
                                  'almost to dryness without loss — the reason it is used as a distilling '
                                  'flask for semimicro amounts.'},
 'centrifuge-tube': {'category': 'tubes',
                     'name': 'Centrifuge tube',
                     'aliases': ['Conical centrifuge tube', 'Falcon tube', 'Glass centrifuge tube'],
                     'description': 'A strong tube, often with a conical bottom, made to be spun in a '
                                    'centrifuge. The solid is packed into the tip, the liquid is poured or '
                                    'sucked off, and the last solvent can be pumped away with the tube '
                                    'connected to a vacuum line. Ordinary test tubes must not go into a '
                                    'centrifuge.'},
 'ampoule': {'category': 'tubes',
             'name': 'Ampoule',
             'aliases': ['Ampule', 'Sealed ampoule', 'Glass ampoule'],
             'description': 'A small glass vessel sealed shut in a flame. Small amounts of a substance, or '
                            'substances that air, light or moisture would spoil, are kept in ampoules; one '
                            'can be made from a test tube by drawing out its neck. It is filled no more than '
                            'half-way through a long-stemmed funnel, so nothing touches the neck that is to '
                            'be sealed.'},
 'stoppered-bottle': {'category': 'flasks',
                      'name': 'Glass-stoppered bottle',
                      'aliases': ['Reagent bottle with glass stopper',
                                  'Ground-glass stoppered bottle',
                                  'Narrow-mouth bottle',
                                  'Wide-mouth bottle',
                                  'Powder bottle'],
                      'description': 'The traditional bottle for keeping reagents, closed with a '
                                     'ground-glass stopper. Wide-mouthed ones take solids and thick liquids, '
                                     'narrow-mouthed ones liquids; brown glass protects substances that '
                                     'light decomposes. Every bottle must carry a clear label.'},
 'test-tube-rack': {'category': 'tubes',
                    'name': 'Test tube rack',
                    'aliases': ['Tube rack', 'Test tube stand', 'Test-tube rack'],
                    'description': 'A stand with rows of holes that holds test tubes upright, so several '
                                   'small reactions can be set up and watched side by side.'},
 'test-tube-holder': {'category': 'tools',
                      'name': 'Test tube holder',
                      'aliases': ['Test tube clamp', 'Test tube tongs', 'Tube holder'],
                      'description': 'A spring clip on a handle, wooden or metal, that grips a test tube so '
                                     'it can be held in a flame or shaken without burning the fingers.'},
 'intensive-condenser': {'category': 'condensers',
                         'name': 'Intensive condenser',
                         'aliases': ['Double-surface condenser',
                                     'Jacketed coil condenser',
                                     'Liebig-Dimroth condenser'],
                         'description': 'A condenser that combines a Liebig water jacket with a Dimroth '
                                        'cooling coil inside, so the vapour is cooled from both sides. It '
                                        'condenses even diethyl ether. It is expensive and, full of water, '
                                        'heavy, so it must be clamped especially firmly.'},
 'anschutz-adapter': {'category': 'adapters',
                      'name': 'Anschütz adapter',
                      'aliases': ['Anschuetz adapter', 'Anschütz head', 'Two-neck adapter, straight'],
                      'description': 'An adapter with two parallel joints on top, fitted into one neck of a '
                                     'flask. On a three-neck flask it gives a fourth opening, so a liquid '
                                     'can be added to a stirred, refluxing mixture while its temperature is '
                                     'measured.'},
 'three-neck-adapter': {'category': 'adapters',
                        'name': 'Three-neck adapter',
                        'aliases': ['Three-way adapter', 'Triple adapter', 'Three-joint head'],
                        'description': 'An adapter that turns a single neck into three parallel openings. '
                                       'For small flasks it replaces a three-neck flask: reagents are added '
                                       'through the condenser and the temperature is followed in the outer '
                                       'bath.'},
 'stirrer-motor': {'category': 'bench',
                   'name': 'Overhead stirrer',
                   'aliases': ['Stirrer motor', 'Overhead stirring motor', 'Laboratory stirrer'],
                   'description': 'An electric motor clamped above the flask that turns a stirrer shaft. The '
                                  'speed is set with a knob; the motor must line up exactly with the shaft, '
                                  'which is coupled to it with a flexible joint. Before switching on, turn '
                                  'the stirrer by hand to check that it runs freely. Ordinary motors spark, '
                                  'so near flammable vapours a water or air turbine is used instead.'},
 'stirrer-bearing': {'category': 'bench',
                     'name': 'Stirrer bearing',
                     'aliases': ['Stirrer guide', 'Stirrer seal', 'KPG stirrer', 'Stirrer gland'],
                     'description': 'The seal through which a stirrer shaft enters a flask neck. A '
                                    'precision-ground glass sleeve (a KPG stirrer) runs with a little '
                                    'special grease and should not turn faster than about 600 rpm; a '
                                    'screw-cap bearing with a PTFE seal holds a vacuum even while the shaft '
                                    'turns.'},
 'ultrasonic-bath': {'category': 'bench',
                     'name': 'Ultrasonic bath',
                     'aliases': ['Sonicator', 'Ultrasonic cleaner', 'Sonication bath'],
                     'description': 'A steel tank of water shaken by ultrasound. A flask stood in it is '
                                    'sonicated: solids break up, dissolve faster and react more readily — it '
                                    'helps, for example, to start a Grignard reaction or a reduction with an '
                                    'alkali metal. It also cleans glassware.'},
 'shaker': {'category': 'bench',
            'name': 'Laboratory shaker',
            'aliases': ['Shaker', 'Shaking machine', 'Orbital shaker', 'Flask shaker'],
            'description': 'A machine that shakes flasks or bottles for hours. It keeps heavy solids such as '
                           'zinc dust or sodium amalgam moving through a liquid and is used for reactions in '
                           'shaken autoclaves; the vessels must be clamped very firmly.'},
 'rotameter': {'category': 'measuring',
               'name': 'Rotameter',
               'aliases': ['Gas flowmeter', 'Variable-area flowmeter', 'Float flowmeter'],
               'description': 'A vertical glass tube that widens towards the top, with a small float inside. '
                              'Gas flowing up lifts the float until it balances; the height on the scale '
                              'shows the flow rate.'},
 'woulfe-bottle': {'category': 'vacuum',
                   'name': 'Woulfe bottle',
                   'aliases': ['Woulff bottle', 'Safety bottle', 'Two-neck bottle', 'Three-neck bottle'],
                   'description': 'A thick-walled bottle with two or three necks, used as a safety trap '
                                  'between a water-jet pump and the apparatus. If the water pressure drops, '
                                  'water sucked back from the pump is caught here instead of in the flask or '
                                  'manometer, and a tap on it lets air in before the pump is turned off.'},
 'gas-cylinder': {'category': 'vacuum',
                  'name': 'Gas cylinder',
                  'aliases': ['Compressed gas cylinder', 'Gas bottle', 'Steel cylinder'],
                  'description': 'A steel bottle of compressed or liquefied gas. The colour of the body and '
                                 'the thread of the valve show the gas — hydrogen and other flammable gases '
                                 'have left-hand threads. Cylinders are chained upright to a wall, kept away '
                                 'from heat, and the gas is taken off only through a pressure regulator.'},
 'gas-regulator': {'category': 'vacuum',
                   'name': 'Pressure regulator',
                   'aliases': ['Gas regulator',
                               'Cylinder regulator',
                               'Reducing valve',
                               'Pressure-reducing valve'],
                   'description': 'The valve screwed onto a gas cylinder that turns its high pressure into a '
                                  'steady low pressure. One gauge shows the cylinder pressure, the other the '
                                  'delivered pressure, and a shut-off valve sets the flow. Regulators for '
                                  'oxygen must be kept free of oil and grease.'},
 'hot-plate': {'category': 'bench',
               'name': 'Hot plate',
               'aliases': ['Electric hot plate', 'Hotplate', 'Electric heater'],
               'description': 'An electric heating plate with a temperature control, used to heat baths and '
                              'flat-bottomed vessels. A plate with an exposed heating coil counts as an open '
                              'flame, and flammable liquids must not be heated directly on it.'},
 'wire-gauze': {'category': 'bench',
                'name': 'Wire gauze',
                'aliases': ['Gauze mat', 'Ceramic-centred gauze', 'Asbestos gauze', 'Wire mesh'],
                'description': 'A square of wire mesh with a heat-resistant centre, laid on a tripod between '
                               'the flame and the vessel. It spreads the heat so the glass is not heated at '
                               'one spot, and with it a burner becomes the simplest air bath.'},
 'water-bath': {'category': 'bench',
                'name': 'Water bath',
                'aliases': ['Heating bath', 'Thermostatic water bath', 'Bain-marie'],
                'description': 'A tank of water kept warm by an electric heater, for heating up to 100 °C. '
                               'Water responds quickly, so the temperature can be held very precisely, and a '
                               'level regulator connected to the tap keeps it topped up. It must never be '
                               'used with sodium, potassium, metal hydrides or anything else that reacts '
                               'with water.'},
 'oil-bath': {'category': 'bench',
              'name': 'Oil bath',
              'aliases': ['Silicone oil bath', 'Heating bath, oil', 'Glycol bath'],
              'description': 'A dish of silicone oil (or of polyethylene glycol) heated on a hot plate, for '
                             'temperatures above 100 °C — silicone oil to about 250 °C. A thermometer always '
                             'stands in it. A drop of water makes hot oil foam and spit, so the condenser is '
                             'fitted with a paper collar; hot oil is wiped off the flask straight after '
                             'use.'},
 'boiling-chips': {'category': 'bench',
                   'name': 'Boiling chips',
                   'aliases': ['Boiling stones', 'Anti-bumping granules', 'Porous pot'],
                   'description': 'Small pieces of unglazed, fired porcelain dropped into a liquid before it '
                                  'is heated. Their pores release tiny bubbles on which the liquid boils '
                                  'smoothly, preventing superheating and sudden violent boiling. They are '
                                  'never added to a liquid that is already hot, and each chip works only '
                                  'once: once cooled, its pores fill with liquid.'},
 'circulator': {'category': 'bench',
                'name': 'Circulating thermostat',
                'aliases': ['Cryostat', 'Refrigerated circulator', 'Chiller', 'Thermostat'],
                'description': 'A bath with a pump, heater and refrigeration unit that sends a liquid at a '
                               'set temperature through the jacket of a reaction vessel or a condenser. '
                               'Low-temperature models (cryostats) hold down to about −80 °C.'},
 'heat-gun': {'category': 'tools',
              'name': 'Heat gun',
              'aliases': ['Hot-air gun', 'Hair dryer', 'Heat blower'],
              'description': 'A hand-held blower of hot air. It dries glassware, melts a solid that has set '
                             'in a condenser, and chases the last drops of a fore-run out of a microscale '
                             'distillation head.'},
 'drying-oven': {'category': 'vacuum',
                 'name': 'Drying oven',
                 'aliases': ['Oven', 'Laboratory oven', 'Drying cabinet'],
                 'description': 'A heated cabinet for drying glassware and solids that do not decompose on '
                                'heating. Even small amounts of flammable liquids must not be evaporated in '
                                'it.'},
 'fume-hood': {'category': 'tools',
               'name': 'Fume hood',
               'aliases': ['Fume cupboard', 'Hood', 'Extraction hood'],
               'description': 'A ventilated cabinet with a sliding glass front where work with toxic, smelly '
                              'or flammable substances is done. Air is drawn in past the operator and away '
                              'through the duct, so vapours never reach the room; reagents that give off '
                              'poisonous fumes are stored on a shelf inside it.'},
 'autoclave': {'category': 'vacuum',
               'name': 'Autoclave',
               'aliases': ['Pressure reactor', 'Rocking autoclave', 'Steel autoclave', 'Parr reactor'],
               'description': 'A thick steel vessel with a bolted lid, a pressure gauge, a valve and a well '
                              'for a thermometer, for reactions at high pressure — up to about 350 atm and '
                              '350 °C. It is heated in an electric furnace and rocked or stirred, used in '
                              'special rooms, and never cooled with water while hot.'},
 'glass-autoclave': {'category': 'vacuum',
                     'name': 'Glass pressure reactor',
                     'aliases': ['Glass autoclave', 'Pressure-rated glass reactor'],
                     'description': 'A glass reaction vessel, from about 100 mL, inside a steel safety '
                                    'shield, for moderate pressures — up to about 10 bar at 100 °C. Unlike a '
                                    'steel autoclave it lets the reaction be watched; it is stirred '
                                    'magnetically.'},
 'water-aspirator': {'category': 'vacuum',
                     'name': 'Water aspirator',
                     'aliases': ['Water-jet pump', 'Water pump', 'Filter pump', 'Aspirator'],
                     'description': 'A glass or plastic jet on a water tap: water rushing through a narrow '
                                    'nozzle drags air with it and sucks out the apparatus. Its vacuum is '
                                    'limited by the vapour pressure of water, 8–15 mm Hg, and it uses a lot '
                                    'of water. It is always connected through a safety bottle, and air is '
                                    'let in before the tap is turned off.'},
 'diaphragm-pump': {'category': 'vacuum',
                    'name': 'Diaphragm pump',
                    'aliases': ['Membrane pump', 'Membrane vacuum pump', 'Oil-free vacuum pump'],
                    'description': 'An electric vacuum pump in which a flexing membrane moves the gas, with '
                                   'no oil and no water. It is made of corrosion-resistant materials, '
                                   'reaches about 2–80 mbar, and collects the pumped solvents in a built-in '
                                   'separator — which is why it is replacing the water aspirator.'},
 'rotary-vane-pump': {'category': 'vacuum',
                      'name': 'Rotary vane pump',
                      'aliases': ['Oil pump', 'Rotary oil pump', 'Vacuum pump'],
                      'description': 'An oil-sealed pump in which an off-centre rotor compresses the gas and '
                                     'pushes it out, giving a vacuum of 0.01–1 mm Hg. Corrosive and easily '
                                     'condensed vapours ruin the oil, so a cold trap or a gas-ballast valve '
                                     'is fitted in front of it.'},
 'diffusion-pump': {'category': 'vacuum',
                    'name': 'Diffusion pump',
                    'aliases': ['Oil diffusion pump', 'Mercury diffusion pump', 'High-vacuum pump'],
                    'description': 'A pump for high vacuum, below 10⁻³ mm Hg, in which a jet of boiling oil '
                                   'or mercury vapour sweeps gas molecules towards an oil pump behind it. It '
                                   'needs cooling water, and a flow monitor linked to the heater is a '
                                   'sensible protection.'},
 'mcleod-gauge': {'category': 'measuring',
                  'name': 'McLeod gauge',
                  'aliases': ['Compression gauge', 'Gaede gauge', 'Vacuum compression gauge'],
                  'description': 'A mercury gauge for rough-to-medium vacuum, 1–10⁻³ mm Hg. Tilting it traps '
                                 'a known volume of the gas and squeezes it with mercury into a narrow tube, '
                                 'and the compressed volume on the scale gives the original pressure. It '
                                 'reads correctly only when no condensable vapour is present.'},
 'three-way-stopcock': {'category': 'closures',
                        'name': 'Three-way stopcock',
                        'aliases': ['Three-way tap', 'T-bore stopcock', 'Three-way valve'],
                        'description': 'A stopcock with a T-shaped bore and three outlets. Turning it '
                                       'connects any two of them, so one tap can switch an apparatus between '
                                       'a pump and air, or between vacuum and inert gas.'},
 'drying-column': {'category': 'vacuum',
                   'name': 'Drying column',
                   'aliases': ['Drying tower', 'Gas drying column', 'Drying train'],
                   'description': 'A wide upright tube packed with a solid drying agent through which a gas '
                                  'is passed. Phosphorus pentoxide is mixed with glass wool or pumice so it '
                                  'does not cake; several columns in a row, each with a different drying '
                                  'agent, make a drying train.'},
 'hickman-head': {'category': 'distillation',
                  'name': 'Hickman still head',
                  'aliases': ['Hickman head', 'Hickman–Hinkle head', 'Microscale still head', 'Collar head'],
                  'description': 'A small still head for microscale distillation. Vapour condenses on the '
                                 'walls and runs down into a collar round the inside, from which the '
                                 'distillate is drawn off with a pipette or syringe — through a side port in '
                                 'the Hickman–Hinkle version.'},
 'hot-filtration-funnel': {'category': 'funnels',
                           'name': 'Hot-filtration funnel',
                           'aliases': ['Heated funnel', 'Hot-water funnel', 'Jacketed filter funnel'],
                           'description': 'A funnel inside a jacket of hot water or steam, or with an '
                                          'electric heater, so a hot solution can be filtered without '
                                          'crystals forming in the funnel. The stem is short and wide so '
                                          'that it does not block.'},
 'filter-paper': {'category': 'funnels',
                  'name': 'Filter paper',
                  'aliases': ['Fluted filter paper',
                              'Folded filter',
                              'Filter circle',
                              'Qualitative filter paper'],
                  'description': 'Paper made to let liquids pass and hold solids back. A plain circle lies '
                                 'flat in a Büchner funnel; a pleated (fluted) one sits in a glass funnel '
                                 'and filters faster. Strong acids, alkalis and oxidants destroy it.'},
 'centrifuge': {'category': 'measuring',
                'name': 'Centrifuge',
                'aliases': ['Laboratory centrifuge', 'Benchtop centrifuge'],
                'description': 'A machine that spins tubes or cups at a few thousand rpm, so a solid settles '
                               'firmly at the bottom and the liquid can be poured off. It separates small '
                               'amounts of solid without loss and helps where a precipitate would clog a '
                               'filter. Opposite cups must be balanced to the same weight.'},
 'spinning-band-column': {'category': 'distillation',
                          'name': 'Spinning band column',
                          'aliases': ['Spinning-band distillation column', 'Rotating band column'],
                          'description': 'A narrow column with a PTFE or metal band spinning inside it at a '
                                         'few thousand rpm. The band throws the returning liquid onto the '
                                         'wall and mixes it with the vapour, giving many theoretical plates '
                                         'with a tiny hold-up — for fine separations of small amounts.'},
 'empty-column': {'category': 'distillation',
                  'name': 'Empty column',
                  'aliases': ['Open tube column', 'Hollow column', 'Unpacked column'],
                  'description': 'A plain empty tube used as a fractionating column. Its hold-up and '
                                 'pressure drop are tiny, so it suits vacuum and semimicro distillations, '
                                 'but it separates only weakly.'},
 'jacketed-column': {'category': 'distillation',
                     'name': 'Vacuum-jacketed column',
                     'aliases': ['Silvered column', 'Column with vacuum jacket', 'Insulated column'],
                     'description': 'A fractionating column inside a silvered, evacuated glass jacket, like '
                                    'a Dewar flask. The jacket stops the column losing heat, so it works '
                                    'close to the ideal adiabatic conditions and separates as well as it '
                                    'can.'},
 'liquid-extractor': {'category': 'distillation',
                      'name': 'Liquid–liquid extractor',
                      'aliases': ['Perforator', 'Continuous liquid extractor', 'Kutscher–Steudel extractor'],
                      'description': 'An apparatus that extracts a compound out of a solution continuously '
                                     'with only a little solvent: condensed solvent drips through the '
                                     'solution, picks up the compound and overflows back into the boiling '
                                     'flask. It can extract compounds with a partition coefficient below '
                                     '1.5. There are versions for solvents lighter and heavier than the '
                                     'solution.'},
 'uv-lamp': {'category': 'chromatography',
             'name': 'UV lamp',
             'aliases': ['TLC lamp', 'UV hand lamp', '254 nm lamp', 'UV viewing cabinet'],
             'description': 'A lamp giving ultraviolet light at 254 and 365 nm, for looking at TLC plates. '
                            'On a plate with a fluorescent indicator, compounds that absorb UV show as dark '
                            'spots on a glowing background; others glow themselves. Never look into the '
                            'lamp.'},
 'fraction-collector': {'category': 'chromatography',
                        'name': 'Fraction collector',
                        'aliases': ['Automatic fraction collector', 'Fraction collecting rack'],
                        'description': 'A machine that collects the liquid coming out of a column in a row '
                                       'of tubes, moving on to the next tube after a set number of drops or '
                                       'a set time.'},
 'hplc': {'category': 'instruments',
          'name': 'HPLC system',
          'aliases': ['HPLC', 'High-performance liquid chromatograph', 'Liquid chromatograph'],
          'description': 'An instrument that pumps a solvent at 50–500 bar through a short steel column '
                         'packed with very fine particles. The sample is injected into the flow, the '
                         'separated compounds are seen by a detector — usually UV — and appear as peaks on '
                         'the chromatogram.'},
 'gas-chromatograph': {'category': 'instruments',
                       'name': 'Gas chromatograph',
                       'aliases': ['GC', 'Gas chromatography instrument', 'GC oven'],
                       'description': 'An instrument in which a carrier gas sweeps a vaporised sample '
                                      'through a long column in a heated oven. The components leave at '
                                      'different times and are recorded by a detector — a flame-ionisation '
                                      'or thermal-conductivity detector, or a mass spectrometer.'},
 'thiele-tube': {'category': 'instruments',
                 'name': 'Thiele tube',
                 'aliases': ['Thiele melting point apparatus', 'Melting point tube, Thiele'],
                 'description': 'A glass tube with a looped side arm, filled with oil, for measuring a '
                                'melting point. A thermometer with the sample capillary attached hangs in '
                                'it, and heating the side arm makes the oil circulate by itself, so the '
                                'sample warms evenly.'},
 'melting-point-apparatus': {'category': 'instruments',
                             'name': 'Melting point apparatus',
                             'aliases': ['Melting point instrument', 'Mel-Temp', 'Melting point block'],
                             'description': 'An electrically heated metal block with holes for capillaries '
                                            'and a thermometer and a magnifier to watch through. It measures '
                                            'melting points above 250 °C that an oil bath cannot reach, and '
                                            'several samples at once.'},
 'ebulliometer': {'category': 'instruments',
                  'name': 'Ebulliometer',
                  'aliases': ['Boiling point apparatus', 'Cottrell ebulliometer'],
                  'description': 'An apparatus for measuring a boiling point exactly: the liquid is boiled '
                                 'under reflux and the vapour–liquid mixture is pumped over the thermometer '
                                 'bulb, without heat loss or superheating. It needs several millilitres of '
                                 'liquid.'},
 'abbe-refractometer': {'category': 'instruments',
                        'name': 'Abbe refractometer',
                        'aliases': ['Refractometer', 'Abbe', 'Refractive index meter'],
                        'description': 'An instrument that measures the refractive index of a few drops of '
                                       'liquid pressed between two prisms, to four decimal places. It works '
                                       'in daylight but gives the value for the sodium D line; the prisms '
                                       'are held at constant temperature, usually 20 °C.'},
 'polarimeter': {'category': 'instruments',
                 'name': 'Polarimeter',
                 'aliases': ['Polarimeter tube', 'Automatic polarimeter'],
                 'description': 'An instrument that measures how far an optically active compound turns the '
                                'plane of polarised light. Light passes a polariser, a tube of the solution '
                                'and a rotating analyser; the angle read off gives the specific rotation.'},
 'saccharimeter': {'category': 'instruments',
                   'name': 'Saccharimeter',
                   'aliases': ['Sugar polarimeter'],
                   'description': 'A polarimeter made to measure the sugar content of solutions, with a '
                                  'scale in sugar degrees instead of angles.'},
 'cuvette': {'category': 'instruments',
             'name': 'Cuvette',
             'aliases': ['Cell', 'Spectrophotometer cell', 'Quartz cuvette', 'Cuvet'],
             'description': 'A small square tube of glass, quartz or plastic with flat, clear sides, usually '
                            '1 cm across, that holds a solution in the beam of a spectrometer. Quartz is '
                            'needed for ultraviolet light, which glass absorbs.'},
 'uv-vis-spectrometer': {'category': 'instruments',
                         'name': 'UV–Vis spectrophotometer',
                         'aliases': ['UV spectrometer', 'Spectrophotometer', 'UV-Vis'],
                         'description': 'An instrument that shines ultraviolet and visible light through a '
                                        'solution in a cuvette and records how much is absorbed at each '
                                        'wavelength. Double-beam models compare the sample with a reference '
                                        'cell of pure solvent.'},
 'ir-spectrometer': {'category': 'instruments',
                     'name': 'IR spectrometer',
                     'aliases': ['FTIR', 'Infrared spectrometer', 'FT-IR spectrometer'],
                     'description': 'An instrument that records which infrared wavelengths a compound '
                                    'absorbs; each functional group has its own bands. Liquids are measured '
                                    'as a thin film between salt plates, solids pressed into a potassium '
                                    'bromide disc.'},
 'nmr-spectrometer': {'category': 'instruments',
                      'name': 'NMR spectrometer',
                      'aliases': ['NMR', 'NMR magnet', 'Nuclear magnetic resonance spectrometer'],
                      'description': 'An instrument built around a large superconducting magnet. A sample in '
                                     'an NMR tube is lowered into it and irradiated with radio waves; the '
                                     'nuclei ¹H and ¹³C absorb at frequencies that depend on their '
                                     'surroundings, which reveals the structure of the molecule.'},
 'mass-spectrometer': {'category': 'instruments',
                       'name': 'Mass spectrometer',
                       'aliases': ['MS', 'Mass spec', 'GC-MS'],
                       'description': 'An instrument that turns molecules into ions — usually by electron '
                                      'impact — separates them by mass-to-charge ratio and counts them. The '
                                      'molecular ion gives the molar mass and the fragments hint at the '
                                      'structure; it is often coupled to a gas chromatograph.'},
 'diffractometer': {'category': 'instruments',
                    'name': 'X-ray diffractometer',
                    'aliases': ['Single-crystal diffractometer', 'Four-circle diffractometer', 'XRD'],
                    'description': 'An instrument that turns a single crystal in an X-ray beam and measures '
                                   'the reflections. From their positions and intensities a computer '
                                   'calculates where every atom sits — the whole structure of the molecule '
                                   'at once.'},
 'boss-head': {'category': 'bench',
               'name': 'Boss head',
               'aliases': ['Bosshead', 'Clamp holder', 'Double clamp', 'Right-angle clamp holder'],
               'description': 'A small metal block with two screws at right angles that fixes a clamp or a '
                              'ring to the rod of a support stand at any height. It is fitted with its open '
                              'side facing up, so that a loosened clamp cannot slip out and drop the '
                              'apparatus.'},
 'graduated-receiver': {'category': 'distillation',
                        'name': 'Graduated receiver',
                        'aliases': ['Graduated distillation receiver',
                                    'Graduated collecting tube',
                                    'Distilling receiver, graduated'],
                        'description': 'A narrow receiver with a volume scale and a ground joint, put under '
                                       'the condenser in place of a flask. The volume of distillate can be '
                                       'read off at any moment, which is how a boiling curve — temperature '
                                       'against volume distilled — is recorded.'},
 'teclu-burner': {'category': 'bench',
                  'name': 'Teclu burner',
                  'aliases': ['Teclu', 'Teclu gas burner'],
                  'description': 'A gas burner with a conical tube that widens towards the bottom and a '
                                 'screw disc underneath for setting the air intake. It mixes gas and air '
                                 'better than a Bunsen burner and gives a hotter flame, but it is used in '
                                 'just the same way — and never for heating flammable liquids.'}}

DESCRIPTIONS = {'round-bottom-flask': {'description': 'The standard vessel for running a reaction. Its curved bottom '
                                       'spreads heat evenly and lets the liquid swirl without corners where '
                                       'solid can settle, and the ground-glass neck takes a condenser or a '
                                       'stopper. Almost anything that is heated, stirred or distilled starts '
                                       'here. Under vacuum only round-bottom flasks are used, because a flat '
                                       'base can be crushed by the air outside. For a distillation fill it '
                                       'no more than half full under vacuum and two-thirds at normal '
                                       'pressure.'},
 'two-neck-flask': {'description': 'A round-bottom flask with a second opening, so something can be added or '
                                   'measured while the first neck is occupied. Usually the middle neck '
                                   'carries a condenser and the side neck a thermometer, a gas line or a '
                                   'dropping funnel. On small flasks angled side necks are easier to work '
                                   'with than parallel ones, leaving room for a stirrer and a condenser side '
                                   'by side.'},
 'three-neck-flask': {'description': 'Three openings on one flask: typically a condenser in the middle, a '
                                     'thermometer or inert-gas line on one side and an addition funnel on '
                                     'the other. It is the workhorse for reactions that have to be stirred, '
                                     'heated and fed at the same time. An Anschütz adapter on one neck adds '
                                     'a fourth opening when a thermometer is needed as well.'},
 'pear-shaped-flask': {'description': 'A flask that tapers to a point, so the last few millilitres collect '
                                      'in a narrow tip instead of spreading over a wide floor. That makes it '
                                      'the flask of choice for evaporating a small sample down and '
                                      'recovering it afterwards. Pear-shaped flasks also make good '
                                      'distilling flasks and receivers, and 5–10 mL ones are the everyday '
                                      'flask of microscale work.'},
 'erlenmeyer-flask': {'description': 'The cone-shaped flask: narrow at the neck, wide at the base. The shape '
                                     'makes it stable and easy to swirl without splashing, which is why it '
                                     'is used for titrations, for dissolving and mixing, and for storing '
                                     'solutions under a stopper. Closed with a ground-glass stopper it is '
                                     'the right container for volatile, flammable solvents, which would '
                                     'evaporate from a beaker. Like every flat-bottomed vessel it must never '
                                     'be put under vacuum.'},
 'filtering-flask': {'description': 'A thick-walled conical flask with a side arm for a vacuum hose. A '
                                    'Büchner funnel sits in the neck, the pump pulls the liquid through the '
                                    'filter paper, and the filtrate collects below. The heavy wall matters: '
                                    'a thin flask under vacuum can implode. It is connected to a water-jet '
                                    'pump only through a safety bottle (a Woulfe bottle), so that water '
                                    'cannot be sucked back into the filtrate.'},
 'dewar-flask': {'description': 'A double-walled vessel with a vacuum between the walls, which blocks almost '
                                'all heat flow. It holds liquid nitrogen and dry-ice baths for hours. A '
                                'domestic thermos works on exactly the same principle. The gap is pumped '
                                'down to below 10⁻⁵ mm Hg and the walls are silvered. Thin evacuated glass '
                                'can implode, so a Dewar is wrapped in tape or cloth or kept in a wire or '
                                'wooden case, and it must be completely dry before liquid nitrogen goes in.'},
 'beaker': {'description': 'The plain, straight-sided cup of the laboratory. Its graduations are rough, so '
                           'it is for mixing, dissolving, heating and holding liquids — never for measuring '
                           'a volume you intend to trust. Low-boiling and flammable solvents are not kept in '
                           'a beaker: from its wide open top they evaporate quickly.'},
 'test-tube': {'description': 'A narrow glass tube, closed and rounded at one end. The quickest place to try '
                              'a small reaction, warm a sample or watch for a colour change; a rack holds a '
                              'row of them upright. Screw-cap versions store samples. For semimicro work '
                              'short, wide tubes (about 15 mm across and 60–80 mm long) are used.'},
 'watch-glass': {'description': 'A round, slightly curved disc of glass, like the glass of an old pocket '
                                'watch. It covers a beaker to keep dust out while vapour escapes, holds a '
                                'little solid for weighing or drying, and lets a drop of solution evaporate '
                                'where the residue can be seen. Rubbing a drop of an oily product on it with '
                                'a little volatile solvent is one way to make it crystallise.'},
 'rubber-stopper': {'description': 'A tapered plug of rubber for a flask or a test tube without a '
                                   'ground-glass joint. Bored through, it holds a thermometer, a glass tube '
                                   'or a funnel stem. Rubber swells in many organic solvents, so it belongs '
                                   'to aqueous work and to teaching labs. Halogens and strong acids attack '
                                   'rubber as well. In modern set-ups a screw connection with a PTFE seal '
                                   'often takes its place.'},
 'vacuum-tubing': {'description': 'Flexible tubing that connects glassware to a pump, a gas line or a water '
                                  'tap. Tubing for vacuum has thick walls so it does not collapse flat when '
                                  'the air is pumped out. Thin latex or silicone tubing is fine for cooling '
                                  'water. For chlorine, hydrogen bromide, phosgene or ozone, PVC or '
                                  'polyethylene tubing is used instead of rubber; warmed briefly in boiling '
                                  'water, it slips easily onto a glass tube.'},
 'glass-stopper': {'description': 'A ground-glass plug that closes a joint. Glass on glass seals tightly '
                                  'with no plastic or rubber for a solvent to attack, which is why stoppered '
                                  'flasks are used for storing reactive solutions. A stuck stopper can often '
                                  'be freed by rocking it, by warming the outer joint briefly in a smoky '
                                  'flame while the stopper stays cool, or by tapping it with a small wooden '
                                  'mallet.'},
 'vacuum-grease': {'description': 'A thick silicone paste smeared thinly on ground-glass joints and '
                                  'stopcocks. It makes them airtight under vacuum and keeps them turning '
                                  'freely. Use a thin band at the top of the joint only, because excess '
                                  'grease creeps into the reaction. A correctly greased joint looks clear '
                                  'all the way round. Petroleum jelly is enough at normal pressure; for '
                                  'vacuum, silicone or Apiezon greases are used, and water-soluble greases '
                                  'wash off easily.'},
 'air-condenser': {'description': 'A plain tube with no water jacket, cooled by the air around it. For '
                                  'solvents that boil high enough that is cooling enough, and with no hoses '
                                  'it is simpler and safer, especially for a reaction left running '
                                  'overnight. Air cooling is enough only for liquids boiling above about 150 '
                                  '°C.'},
 'liebig-condenser': {'description': 'A straight inner tube inside a water jacket: the classic condenser. '
                                     'Vapour passes down the middle, cooling water flows around it, and the '
                                     'vapour turns back into liquid. This is the standard condenser for a '
                                     'simple distillation. It is used mainly as a downward condenser up to '
                                     'about 160 °C — with running water for liquids boiling below 120 °C and '
                                     'standing water between 120 and 160 °C. As a reflux condenser it is '
                                     'weak.'},
 'allihn-condenser': {'description': 'A condenser whose inner tube is a chain of bulbs. They add surface and '
                                     'hold the returning liquid a moment longer, which makes this the '
                                     'traditional choice for reflux — boiling a reaction for hours without '
                                     'losing solvent. The bulbs make the vapour flow turbulent, so it cools '
                                     'far better than a Liebig condenser; it is used only for reflux.'},
 'coil-condenser': {'description': 'A glass spiral runs down the middle of a water jacket, and the vapour '
                                   'travels through the spiral itself, so it meets a long cooled path in a '
                                   'short piece of glass. It is a condenser for distillation: stood upright '
                                   'for reflux, the returning liquid gathers in the narrow coils and can '
                                   'block them. Stood strictly upright it is the most efficient downward '
                                   'condenser, especially for low-boiling liquids; it must never be tilted.'},
 'dimroth-condenser': {'description': 'A condenser turned inside out: cooling water runs through a glass '
                                      'coil in the middle, and the vapour rises around the coil inside the '
                                      'outer tube. Both water connections are at the top. The coil packs in '
                                      'a large cold surface while the returning liquid runs freely down past '
                                      'it, which makes the Dimroth one of the most efficient reflux '
                                      'condensers. Its outside stays at room temperature, so no dew forms on '
                                      'it; but very low boilers such as ether can creep up the outer wall '
                                      'past the coil.'},
 'cold-finger-condenser': {'description': 'A finger of glass cooled from the inside and dipped into the '
                                          'vapour. Whatever touches it condenses on its outer surface and '
                                          'drips back. Cold fingers are used for reflux in tight spaces and '
                                          'for collecting sublimed solids. Put in through a stopper or a '
                                          'piece of tubing, it leaves the apparatus open. The water flow '
                                          'must never stop: a condenser that runs dry can start a fire.'},
 'drying-tube-adapter': {'description': 'A small tube of drying agent fitted to the top of an apparatus. Air '
                                        'can move in and out as things heat and cool, but the moisture in it '
                                        'is caught on the way — the simple protection for a reaction that '
                                        'water would spoil. It is filled with calcium chloride or soda lime '
                                        'between plugs of glass wool. Blow through a filled tube before use '
                                        'to check that gas still passes.'},
 'claisen-adapter': {'description': 'A Y-shaped adapter that turns one flask neck into two. It is the '
                                    'quickest way to give a single-neck flask room for both a condenser and '
                                    'a thermometer, or a stirrer and an addition funnel. In a vacuum '
                                    'distillation one neck carries the boiling capillary and the other the '
                                    'thermometer, and the bend keeps froth from reaching the condenser.'},
 'distilling-head': {'description': 'The piece that sits on the boiling flask and turns the vapour towards '
                                    'the condenser, with an opening on top for a thermometer. Reading the '
                                    'vapour temperature there is how you know which component is coming '
                                    'over. The thermometer bulb must sit just below the side arm, so that '
                                    'the vapour bathes it completely.'},
 'vacuum-takeoff-adapter': {'description': 'The bend that carries the distillate from the condenser down '
                                           'into the receiving flask, with a side port for the vacuum line. '
                                           'Its bore should be at least 5–6 mm wide, or a vacuum '
                                           'distillation is held back.'},
 'cow-receiver': {'description': 'A rotating receiver with several flasks hanging from it. Turning the cow '
                                 'brings a fresh flask under the outlet, so one fraction after another can '
                                 'be collected without breaking the vacuum. It is cheaper and more '
                                 'vacuum-tight than a receiver with taps, but it can collect only as many '
                                 'fractions as it has flasks.'},
 'vigreux-column': {'description': 'A tube with rows of indentations pointing inwards, fitted between the '
                                   'flask and the still head. Vapour condenses on them and re-evaporates '
                                   'over and over, and each of those cycles enriches it in the lower-boiling '
                                   'component. That is what separates two liquids whose boiling points are '
                                   'close. Its hold-up and pressure drop are small, so it suits vacuum and '
                                   'semimicro distillations, though its efficiency is modest.'},
 'short-path-apparatus': {'description': 'Boiling flask, condenser and receiver joined over the shortest '
                                         'possible distance. Little surface means little material lost on '
                                         'the way, so it is used for small or precious samples, and under '
                                         'vacuum for compounds that would decompose at their normal boiling '
                                         'point. Because the evaporating and condensing surfaces are so '
                                         'close, the distillate runs as a thin film; it is the method for '
                                         'heat-sensitive, high-boiling substances.'},
 'kugelrohr-bulb': {'description': 'One of a chain of bulbs used to distil small amounts over a very short '
                                   'path. The sample is heated in an oven while the chain rotates, and each '
                                   'fraction condenses in the next, cooler bulb — with almost no glassware '
                                   'for it to be lost on. It is excellent for separating liquids and '
                                   'low-melting solids from polymeric and tarry residues.'},
 'rotary-evaporator': {'description': 'An instrument for removing solvent from a solution quickly and '
                                      'gently. The flask spins, half dipped in a warm water bath, so the '
                                      'liquid spreads into a thin film; under vacuum the solvent boils far '
                                      'below its normal boiling point, condenses on a cooled coil and runs '
                                      'into a receiving flask. Almost every organic product is concentrated '
                                      'on one. Start the rotation first, then the vacuum, and only then warm '
                                      'the bath, or the solution foams. Low-boiling solvents are not fully '
                                      'caught by a water-cooled condenser, so the receiver is chilled as '
                                      'well.'},
 'dean-stark-trap': {'description': 'A graduated side tube with a tap, fitted between a reaction flask and a '
                                    'reflux condenser. The solvent — usually toluene — boils off together '
                                    'with the water the reaction makes; both condense and drip into the '
                                    'tube, where the heavier water sinks and the solvent overflows back into '
                                    'the flask. Taking the water out drives the reaction to completion, and '
                                    'the scale shows how far it has got. For solvents heavier than water, '
                                    'such as chloroform or carbon tetrachloride, a different trap is used, '
                                    'in which the solvent collects at the bottom.'},
 'soxhlet-extractor': {'description': 'An extractor that washes a solid with fresh, clean solvent over and '
                                      'over by itself. Solvent boils below, condenses above, fills the '
                                      'chamber holding the sample and siphons back when full — leaving the '
                                      'extracted material in the flask and running unattended for hours. The '
                                      'solid in the thimble must be heavier than the solvent. Unlike a '
                                      'simple flow-through extractor, the siphon empties the chamber in '
                                      'pulses.'},
 'separatory-funnel': {'description': 'A pear-shaped funnel with a stopcock, for separating two liquids that '
                                      'do not mix. Shaking moves a compound into whichever solvent dissolves '
                                      'it better; the layers settle and the lower one is run off through the '
                                      'tap. This extraction is one of the most-used operations in organic '
                                      'chemistry. Fill it no more than two-thirds, turn it tap-up and open '
                                      'the tap to let the vapour out before shaking hard. The lower layer '
                                      'leaves through the tap, the upper one through the top.'},
 'buchner-funnel': {'description': 'A porcelain funnel with a flat, perforated plate across its wide top. A '
                                   'disc of filter paper lies on the plate, the funnel sits in a filter '
                                   'flask on a rubber collar, and suction pulls the liquid through. It is '
                                   'the fast way to collect a solid and the usual last step of a '
                                   'precipitation. Glass funnels with a sintered disc in place of the plate '
                                   'and paper are fritted filter funnels. The filter flask is evacuated '
                                   'through a safety bottle; the cake is pressed down with a flat glass '
                                   'stopper and washed with small portions of cold solvent while the vacuum '
                                   'is off.'},
 'fritted-filter-funnel': {'description': 'A funnel with a disc of fused glass instead of paper. The frit '
                                          'comes in graded porosities, does not tear or react, and can be '
                                          'washed and used again — which matters when the liquid would '
                                          'attack paper or must not pick up fibres. Porosities No. 2 and 3 '
                                          'are the usual ones. A frit is required when strong acids, alkalis '
                                          'or oxidants would destroy paper, and for samples meant for '
                                          'analysis.'},
 'hirsch-funnel': {'description': 'The small version of a Büchner funnel, with sloping sides and a filter '
                                  'plate only a centimetre or two across. It is for collecting a few '
                                  'milligrams of crystals by suction filtration without losing them on a '
                                  'large filter. It is used with a suction test tube rather than a filter '
                                  'flask.'},
 'thermometer': {'description': 'A sealed glass tube with a bulb of liquid at the bottom and a temperature '
                                'scale up the stem. The liquid expands as it warms and climbs the scale; in '
                                'the lab it measures baths, reactions and the vapour in a distillation head. '
                                'When part of the mercury column sticks out of the heated liquid, the '
                                'reading needs an emergent-stem correction.'},
 'gas-washing-bottle': {'description': 'A bottle in which gas is bubbled through a liquid on its way past — '
                                       'to dry it, to wash out an impurity, or to trap something harmful '
                                       'before it reaches the room. The head is held on with metal springs, '
                                       'an empty safety bottle is put before and after it, and a bottle of '
                                       'acid is never placed directly next to one of alkali.'},
 'bubbler': {'description': 'A small vessel of oil in the gas line. Gas leaving the apparatus bubbles out '
                            'through the oil, so the flow can be seen and counted, and the oil stops air '
                            'coming back the other way. With a chosen liquid and height of liquid it also '
                            'keeps a slight overpressure in a closed apparatus.'},
 'vacuum-trap': {'description': 'A cold trap in the line ahead of a vacuum pump. Solvent vapour freezes on '
                                'its cold wall instead of reaching the pump oil, which protects the pump and '
                                'keeps the vacuum deep. It is cooled in a Dewar with dry ice and ethanol or '
                                'with liquid nitrogen. Liquid air, which grows richer in oxygen as it '
                                'stands, must never be used to cool organic substances.'},
 'glass-stopcock': {'description': 'The traditional tap: a ground glass plug in a ground glass barrel, '
                                   'sealed with a film of grease. Cheap, chemically inert and still standard '
                                   'on high-vacuum glassware, though the grease has to be renewed. A fine '
                                   'notch filed along the bore makes it possible to let in air very '
                                   'gradually, for example to set the pressure of a vacuum line.'},
 'desiccator': {'description': 'A heavy glass pot with a greased, tight-fitting lid and a perforated plate '
                               'inside. A drying agent sits below the plate and samples above it, so they '
                               'dry — or stay dry — in air with no water in it. Versions with a tap in the '
                               'lid can be put under vacuum. A vacuum desiccator is wrapped in a towel '
                               'before it is evacuated. The air inlet inside ends in a capillary pointing '
                               'upwards, so the incoming air does not scatter the sample, and glass rings on '
                               'the bottom stop sulfuric acid from splashing.'},
 'sublimator': {'description': 'A vessel with a cold finger above the sample. Under vacuum a solid that '
                               'sublimes passes straight to vapour and re-forms as crystals on the cold '
                               'surface — a purification that never involves a solvent. The cold finger '
                               'should be as close to the sample as possible, and the apparatus is opened '
                               'gently, after warming the joint, so the crystals do not fall off.'},
 'chromatography-column': {'description': 'A vertical glass tube packed with silica gel, with a tap at the '
                                          'bottom. The mixture is loaded on top and solvent pushed through; '
                                          'compounds travel at different speeds and come out one after '
                                          'another. This is how most organic products are purified. A loose '
                                          'plug of cotton or glass wool (or a sieve plate) holds the '
                                          'packing, which is poured in as a slurry. The solvent must never '
                                          'fall below the top of the packing, or the packing cracks.'},
 'tlc-tank': {'description': 'A flat glass chamber with a lid, for thin-layer chromatography. A little '
                             'solvent lies in the bottom, the plate stands in it, and the solvent climbs the '
                             'plate by capillary action and separates the spots as it goes. It is the '
                             'quickest way to see whether a reaction has finished. Its walls are lined with '
                             'filter paper, so the air inside is saturated with solvent vapour before the '
                             'plate goes in.'},
 'pressure-vessel': {'description': 'A heavy-walled tube that can be sealed and heated well above the '
                                    'boiling point of its contents. Holding the solvent liquid under its own '
                                    'pressure lets a reaction run far hotter than open glassware allows; the '
                                    'thick wall and the screw seal are what make that safe. The classic form '
                                    'is a thick-walled Duran ampoule sealed in a flame, good for 20–30 atm '
                                    'and 400 °C; it is heated inside an iron jacket in a special furnace and '
                                    'opened only after cooling.'},
 'magnetic-stirrer': {'description': 'A flat plate with a spinning magnet inside. It turns a stir bar in the '
                                     'flask on top without anything passing through the glass; most models '
                                     'also heat the plate. The bar has to lie flat on the bottom, so it '
                                     'works best in flat-bottomed vessels and small flasks.'},
 'bunsen-burner': {'description': 'A metal tube on a heavy base that burns gas from the bench tap. A collar '
                                  'at the bottom lets in air: closed, the flame is yellow and cool; open, it '
                                  'turns into a hot, roaring blue cone. Flammable liquids are never heated '
                                  'over an open flame.'},
 'support-stand': {'description': 'A heavy metal base with an upright rod. Clamps and rings fixed to the rod '
                                  'hold flasks, condensers, funnels and burettes, and whole apparatus is '
                                  'built up around it. A reaction apparatus is best clamped to a single '
                                  'stand; the bosses are fixed with the open side facing up.'},
 'clamp': {'description': 'Adjustable jaws on an arm, fixed to a stand with a boss head. It grips the neck '
                          'of a flask or the body of a condenser and holds it in place — almost every set-up '
                          'on the bench hangs from clamps. Its jaws are lined with cork or rubber and '
                          'tightened only enough to hold the glass without straining it.'},
 'lab-jack': {'description': 'A flat platform on a scissor mechanism, raised or lowered by turning a knob. '
                             'It holds a heating bath or stirrer under a flask, and can be wound down to '
                             'drop the heat away quickly. A heat source has to be removable at any moment, '
                             'and a lab jack is the usual way to do it.'},
 'mortar-and-pestle': {'description': 'A thick porcelain bowl and a club-shaped grinder. Grinding a solid '
                                      'between them turns lumps and crystals into a fine powder that '
                                      'dissolves or reacts faster. Dry ice is crushed in a metal mortar, not '
                                      'a porcelain one.'},
 'safety-goggles': {'description': 'Close-fitting protective glasses worn at all times in the lab. They keep '
                                   'splashes, flying glass and dust out of the eyes — the one piece of '
                                   'equipment that is never optional. They are mandatory for any work under '
                                   'vacuum or pressure and when a melting point is measured.'},
 'pasteur-pipette': {'description': 'A short glass tube drawn out to a long thin tip, used with a rubber '
                                    'bulb to move small amounts of liquid drop by drop. It has no scale — it '
                                    'is for transferring, not measuring — and is usually thrown away after '
                                    'use. It is easily drawn out from a 12–15 cm glass tube, and it is worth '
                                    'calibrating at 0.5, 1, 1.5 and 2 mL.'},
 'immersion-well': {'description': 'A double-walled quartz or glass tube that holds a UV lamp and dips into '
                                   'the reaction. Light shines outward into the solution while cooling water '
                                   'between the walls stops the lamp from boiling it. Used to drive '
                                   'reactions with light (photochemistry). Never look at the lit lamp. '
                                   'Without an immersion lamp, the flask can be lit from outside by a 500 W '
                                   'photolamp, though the reaction then runs more slowly.'},
 'evaporating-dish': {'description': 'A shallow porcelain bowl with a pouring lip. Heating a solution in it '
                                     'drives off the solvent and leaves the dissolved solid behind; '
                                     'porcelain takes direct heat that would crack ordinary glass. Covered '
                                     'with an upturned glass funnel, it becomes the simplest sublimation '
                                     'apparatus.'}}

COMMONS = {'Ground glass joint open.jpg': {'credit': 'Phasmatisnox, CC BY-SA 3.0, via Wikimedia Commons',
                                 'url': 'https://commons.wikimedia.org/wiki/File:Ground_glass_joint_open.jpg'},
 'Ground glass joint closed.jpg': {'credit': 'Phasmatisnox, CC BY-SA 3.0, via Wikimedia Commons',
                                   'url': 'https://commons.wikimedia.org/wiki/File:Ground_glass_joint_closed.jpg'},
 'Tubing clamp-single 1.jpg': {'credit': 'Nadina Wiórkiewicz, CC BY-SA 3.0, via Wikimedia Commons',
                               'url': 'https://commons.wikimedia.org/wiki/File:Tubing_clamp-single_1.jpg'},
 'Tubing clamp-single 2.jpg': {'credit': 'Nadina Wiórkiewicz, CC BY-SA 3.0, via Wikimedia Commons',
                               'url': 'https://commons.wikimedia.org/wiki/File:Tubing_clamp-single_2.jpg'},
 'Tubing clamp-single 3.jpg': {'credit': 'Nadina Wiórkiewicz, CC BY-SA 3.0, via Wikimedia Commons',
                               'url': 'https://commons.wikimedia.org/wiki/File:Tubing_clamp-single_3.jpg'},
 'Fedolemez.jpg': {'credit': 'Szőcs Tamás, CC BY-SA 3.0, via Wikimedia Commons',
                   'url': 'https://commons.wikimedia.org/wiki/File:Fedolemez.jpg'},
 'Glass slide.jpg': {'credit': 'Whispyhistory, CC BY-SA 4.0, via Wikimedia Commons',
                     'url': 'https://commons.wikimedia.org/wiki/File:Glass_slide.jpg'},
 'Spitzkolben.png': {'credit': 'MediaLab TH Köln, CC BY-SA 4.0, via Wikimedia Commons',
                     'url': 'https://commons.wikimedia.org/wiki/File:Spitzkolben.png'},
 '50ml Falcon tubes-01.jpg': {'credit': 'Lilly_M, CC BY-SA 3.0, via Wikimedia Commons',
                              'url': 'https://commons.wikimedia.org/wiki/File:50ml_Falcon_tubes-01.jpg'},
 'Zentrifugenglas.jpg': {'credit': 'Gmhofmann, public domain, via Wikimedia Commons',
                         'url': 'https://commons.wikimedia.org/wiki/File:Zentrifugenglas.jpg'},
 '25ml tube.jpg': {'credit': 'Karbohut, CC BY-SA 4.0, via Wikimedia Commons',
                   'url': 'https://commons.wikimedia.org/wiki/File:25ml_tube.jpg'},
 'Pharmacy-bottles-blue hg.jpg': {'credit': 'Hannes Grobe, CC BY-SA 4.0, via Wikimedia Commons',
                                  'url': 'https://commons.wikimedia.org/wiki/File:Pharmacy-bottles-blue_hg.jpg'},
 'Bottle, apothecary (AM 629318-1).jpg': {'credit': 'Auckland Museum, CC BY 4.0, via Wikimedia Commons',
                                          'url': 'https://commons.wikimedia.org/wiki/File:Bottle,_apothecary_(AM_629318-1).jpg'},
 'Reagenzglasständer Zucker-Museum.jpg': {'credit': 'FA2010, public domain, via Wikimedia Commons',
                                          'url': 'https://commons.wikimedia.org/wiki/File:Reagenzglasst%C3%A4nder_Zucker-Museum.jpg'},
 '3D printed test tube rack in use.jpg': {'credit': 'Frank Markesteijn, CC BY-SA 4.0, via Wikimedia Commons',
                                          'url': 'https://commons.wikimedia.org/wiki/File:3D_printed_test_tube_rack_in_use.jpg'},
 'Test Tube Holder2 2015.JPG': {'credit': 'Nacharee.jung, CC BY-SA 4.0, via Wikimedia Commons',
                                'url': 'https://commons.wikimedia.org/wiki/File:Test_Tube_Holder2_2015.JPG'},
 'Two small test tubes held in spring clamps.jpg': {'credit': 'Amitchell125, CC BY-SA 3.0, via Wikimedia '
                                                              'Commons',
                                                    'url': 'https://commons.wikimedia.org/wiki/File:Two_small_test_tubes_held_in_spring_clamps.jpg'},
 'Vorsicht beim Erhitzen von Flüssigkeiten im Reagenzglas.jpg': {'credit': 'B.Lachner, CC0, via Wikimedia '
                                                                           'Commons',
                                                                 'url': 'https://commons.wikimedia.org/wiki/File:Vorsicht_beim_Erhitzen_von_Fl%C3%BCssigkeiten_im_Reagenzglas.jpg'},
 'Intensivkuehler.jpg': {'credit': 'Armin Kübelbeck, CC BY-SA 3.0, via Wikimedia Commons',
                         'url': 'https://commons.wikimedia.org/wiki/File:Intensivkuehler.jpg'},
 'RZR 2051 control.jpg': {'credit': 'Evaporation Expert, CC BY-SA 4.0, via Wikimedia Commons',
                          'url': 'https://commons.wikimedia.org/wiki/File:RZR_2051_control.jpg'},
 'Mechanical stirrer engine.jpg': {'credit': 'Polimerek, CC BY-SA 3.0, via Wikimedia Commons',
                                   'url': 'https://commons.wikimedia.org/wiki/File:Mechanical_stirrer_engine.jpg'},
 'Bandelin-sonorex hg.jpg': {'credit': 'Hannes Grobe, CC BY 3.0, via Wikimedia Commons',
                             'url': 'https://commons.wikimedia.org/wiki/File:Bandelin-sonorex_hg.jpg'},
 'Ultrasonic bath 1.jpg': {'credit': 'Karelj, public domain, via Wikimedia Commons',
                           'url': 'https://commons.wikimedia.org/wiki/File:Ultrasonic_bath_1.jpg'},
 'Cuves ultrasons.jpg': {'credit': 'MHC TECHNOLOGY, CC BY-SA 4.0, via Wikimedia Commons',
                         'url': 'https://commons.wikimedia.org/wiki/File:Cuves_ultrasons.jpg'},
 '19112007040.jpg': {'credit': 'Karel Schmiedberger ml., public domain, via Wikimedia Commons',
                     'url': 'https://commons.wikimedia.org/wiki/File:19112007040.jpg'},
 'Velkokapacitni trepacka - shaker.jpg': {'credit': 'Karel Schmiedberger ml., CC BY 3.0, via Wikimedia '
                                                    'Commons',
                                          'url': 'https://commons.wikimedia.org/wiki/File:Velkokapacitni_trepacka_-_shaker.jpg'},
 'Laboratory microbiological shaker with cultures-01.jpg': {'credit': 'Matylda Sęk, CC BY-SA 3.0, via '
                                                                      'Wikimedia Commons',
                                                            'url': 'https://commons.wikimedia.org/wiki/File:Laboratory_microbiological_shaker_with_cultures-01.jpg'},
 'Flowmeter float.JPG': {'credit': 'Cjp24, CC BY-SA 3.0, via Wikimedia Commons',
                         'url': 'https://commons.wikimedia.org/wiki/File:Flowmeter_float.JPG'},
 'Rotameter.jpg': {'credit': 'unknown author, public domain, via Wikimedia Commons',
                   'url': 'https://commons.wikimedia.org/wiki/File:Rotameter.jpg'},
 'Flow-tube-meter hg.jpg': {'credit': 'Hannes Grobe, CC BY-SA 3.0, via Wikimedia Commons',
                            'url': 'https://commons.wikimedia.org/wiki/File:Flow-tube-meter_hg.jpg'},
 'Woulfe bottle 01.jpg': {'credit': 'Steffen 962, CC0, via Wikimedia Commons',
                          'url': 'https://commons.wikimedia.org/wiki/File:Woulfe_bottle_01.jpg'},
 'Woulfe bottle 02.jpg': {'credit': 'Steffen 962, CC0, via Wikimedia Commons',
                          'url': 'https://commons.wikimedia.org/wiki/File:Woulfe_bottle_02.jpg'},
 'Woulfesche Flasche Glas.jpg': {'credit': 'Struppi, CC BY-SA 4.0, via Wikimedia Commons',
                                 'url': 'https://commons.wikimedia.org/wiki/File:Woulfesche_Flasche_Glas.jpg'},
 '2008-07-24 Bundle of compressed gas bottles.jpg': {'credit': 'Ildar Sagdejev (Specious), CC BY-SA 4.0, via '
                                                               'Wikimedia Commons',
                                                     'url': 'https://commons.wikimedia.org/wiki/File:2008-07-24_Bundle_of_compressed_gas_bottles.jpg'},
 'Gas cylinder ammonia.jpg': {'credit': 'Masur, public domain, via Wikimedia Commons',
                              'url': 'https://commons.wikimedia.org/wiki/File:Gas_cylinder_ammonia.jpg'},
 'P3230006 (7322939).jpg': {'credit': 'Robert Cudmore from Marseille, France, CC BY-SA 2.0, via Wikimedia '
                                      'Commons',
                            'url': 'https://commons.wikimedia.org/wiki/File:P3230006_(7322939).jpg'},
 'Gas regulator.jpg': {'credit': 'Rifleman 82, public domain, via Wikimedia Commons',
                       'url': 'https://commons.wikimedia.org/wiki/File:Gas_regulator.jpg'},
 'A nitrogen gas cylinder with pressure-relief devices.jpg': {'credit': 'Seaborg, CC BY-SA 3.0, via '
                                                                        'Wikimedia Commons',
                                                              'url': 'https://commons.wikimedia.org/wiki/File:A_nitrogen_gas_cylinder_with_pressure-relief_devices.jpg'},
 'Pressure regulator by AGA.jpg': {'credit': 'Cjp24, CC BY-SA 3.0, via Wikimedia Commons',
                                   'url': 'https://commons.wikimedia.org/wiki/File:Pressure_regulator_by_AGA.jpg'},
 'Hot plate 2015.JPG': {'credit': 'Athikhun.suw, CC BY-SA 4.0, via Wikimedia Commons',
                        'url': 'https://commons.wikimedia.org/wiki/File:Hot_plate_2015.JPG'},
 'Laboratory hot plate.JPG': {'credit': 'Jeffrey M. Vinocur, CC BY 2.5, via Wikimedia Commons',
                              'url': 'https://commons.wikimedia.org/wiki/File:Laboratory_hot_plate.JPG'},
 '12.5cm by 12.5cm Wire Gauze.jpg': {'credit': 'U5780138, CC BY-SA 4.0, via Wikimedia Commons',
                                     'url': 'https://commons.wikimedia.org/wiki/File:12.5cm_by_12.5cm_Wire_Gauze.jpg'},
 '15cm by 15cm Wire Gauze.jpg': {'credit': 'U5780138, CC BY-SA 4.0, via Wikimedia Commons',
                                 'url': 'https://commons.wikimedia.org/wiki/File:15cm_by_15cm_Wire_Gauze.jpg'},
 'Wire Gauze.jpg': {'credit': 'U5780138, CC BY-SA 4.0, via Wikimedia Commons',
                    'url': 'https://commons.wikimedia.org/wiki/File:Wire_Gauze.jpg'},
 'Bain-marie laboratoire.JPG': {'credit': 'unknown author, public domain, via Wikimedia Commons',
                                'url': 'https://commons.wikimedia.org/wiki/File:Bain-marie_laboratoire.JPG'},
 'Circulating water bath 2015.jpg': {'credit': 'Athikhun.suw, CC BY-SA 4.0, via Wikimedia Commons',
                                     'url': 'https://commons.wikimedia.org/wiki/File:Circulating_water_bath_2015.jpg'},
 'Wasserbad.jpg': {'credit': 'Karbohut, CC BY-SA 4.0, via Wikimedia Commons',
                   'url': 'https://commons.wikimedia.org/wiki/File:Wasserbad.jpg'},
 'Oil bath.jpg': {'credit': 'Sonal Shinde, CC BY-SA 4.0, via Wikimedia Commons',
                  'url': 'https://commons.wikimedia.org/wiki/File:Oil_bath.jpg'},
 'Siedesteinchen.jpg': {'credit': 'Carsten Niehaus, public domain, via Wikimedia Commons',
                        'url': 'https://commons.wikimedia.org/wiki/File:Siedesteinchen.jpg'},
 'Siedesteinen auf Uhrglas.jpg': {'credit': 'B.Lachner, CC0, via Wikimedia Commons',
                                  'url': 'https://commons.wikimedia.org/wiki/File:Siedesteinen_auf_Uhrglas.jpg'},
 'ThermoFlex 900-Recirculating Chiller.jpg': {'credit': 'Nadina Wiórkiewicz, CC BY-SA 3.0, via Wikimedia '
                                                        'Commons',
                                              'url': 'https://commons.wikimedia.org/wiki/File:ThermoFlex_900-Recirculating_Chiller.jpg'},
 'Hot air gun (1).jpg': {'credit': 'Suyash Dwivedi, CC BY-SA 4.0, via Wikimedia Commons',
                         'url': 'https://commons.wikimedia.org/wiki/File:Hot_air_gun_(1).jpg'},
 'Hot air gun (2).jpg': {'credit': 'Suyash Dwivedi, CC BY-SA 4.0, via Wikimedia Commons',
                         'url': 'https://commons.wikimedia.org/wiki/File:Hot_air_gun_(2).jpg'},
 'Heat Gun.JPG': {'credit': 'Jmdestefanis, CC BY-SA 3.0, via Wikimedia Commons',
                  'url': 'https://commons.wikimedia.org/wiki/File:Heat_Gun.JPG'},
 'Trockenschrank.jpg': {'credit': 'unknown author, CC BY 2.5, via Wikimedia Commons',
                        'url': 'https://commons.wikimedia.org/wiki/File:Trockenschrank.jpg'},
 'Drying owen 1.jpg': {'credit': 'Karelj, public domain, via Wikimedia Commons',
                       'url': 'https://commons.wikimedia.org/wiki/File:Drying_owen_1.jpg'},
 'Drying owen 2.jpg': {'credit': 'Karelj, public domain, via Wikimedia Commons',
                       'url': 'https://commons.wikimedia.org/wiki/File:Drying_owen_2.jpg'},
 'Fume-hood.jpg': {'credit': 'Giovanna Canu, Sofia Gambaro, Francesca Cirisano, CNR-ICMATE, CC BY 4.0, via '
                             'Wikimedia Commons',
                   'url': 'https://commons.wikimedia.org/wiki/File:Fume-hood.jpg'},
 'Fume hood.jpg': {'credit': 'unknown author, public domain, via Wikimedia Commons',
                   'url': 'https://commons.wikimedia.org/wiki/File:Fume_hood.jpg'},
 'Fume hood MB.jpg': {'credit': 'Miha Bukleski, CC BY 4.0, via Wikimedia Commons',
                      'url': 'https://commons.wikimedia.org/wiki/File:Fume_hood_MB.jpg'},
 'Figure-1-High-pressure-reactors-and-control-reactors.jpg': {'credit': 'Martina Schedler et al., CC BY 4.0, '
                                                                        'via Wikimedia Commons',
                                                              'url': 'https://commons.wikimedia.org/wiki/File:Figure-1-High-pressure-reactors-and-control-reactors.jpg'},
 'Glass Pressure Reactor.jpg': {'credit': 'Rudyher27, CC BY-SA 4.0, via Wikimedia Commons',
                                'url': 'https://commons.wikimedia.org/wiki/File:Glass_Pressure_Reactor.jpg'},
 'Aspirator sample1.jpg': {'credit': 'GOKLuLe 盧樂, CC BY-SA 3.0, via Wikimedia Commons',
                           'url': 'https://commons.wikimedia.org/wiki/File:Aspirator_sample1.jpg'},
 'CIglass aspirator 3.jpg': {'credit': 'GOKLuLe 盧樂, CC BY-SA 3.0, via Wikimedia Commons',
                             'url': 'https://commons.wikimedia.org/wiki/File:CIglass_aspirator_3.jpg'},
 'Diaphragm pump.JPG': {'credit': 'Agne27, CC BY-SA 3.0, via Wikimedia Commons',
                        'url': 'https://commons.wikimedia.org/wiki/File:Diaphragm_pump.JPG'},
 'Edwards E2M2 2-Stage Rotary Vane Vacuum Pump (15957733526).jpg': {'credit': 'Kitmondo Marketplace, CC BY '
                                                                              '2.0, via Wikimedia Commons',
                                                                    'url': 'https://commons.wikimedia.org/wiki/File:Edwards_E2M2_2-Stage_Rotary_Vane_Vacuum_Pump_(15957733526).jpg'},
 'High-vacuum pump.jpg': {'credit': 'University of Dundee Museum Services, CC BY-SA 4.0, via Wikimedia '
                                    'Commons',
                          'url': 'https://commons.wikimedia.org/wiki/File:High-vacuum_pump.jpg'},
 'Öl-Rotations-Vakuumpumpe der Firma Vacuubrand Wertheim - LABW - Staatsarchiv Wertheim S-N 70 G 3173.jpg': {'credit': 'Landesarchiv '
                                                                                                                       'Baden-Württemberg, '
                                                                                                                       'CC '
                                                                                                                       'BY '
                                                                                                                       '4.0, '
                                                                                                                       'via '
                                                                                                                       'Wikimedia '
                                                                                                                       'Commons',
                                                                                                             'url': 'https://commons.wikimedia.org/wiki/File:%C3%96l-Rotations-Vakuumpumpe_der_Firma_Vacuubrand_Wertheim_-_LABW_-_Staatsarchiv_Wertheim_S-N_70_G_3173.jpg'},
 'Me holding a mercury based diffusion pump (for size comparison).jpg': {'credit': 'LetsGame999, CC BY-SA '
                                                                                   '4.0, via Wikimedia '
                                                                                   'Commons',
                                                                         'url': 'https://commons.wikimedia.org/wiki/File:Me_holding_a_mercury_based_diffusion_pump_(for_size_comparison).jpg'},
 'A simplified oil diffusion pump.jpg': {'credit': 'Antigng, CC BY-SA 4.0, via Wikimedia Commons',
                                         'url': 'https://commons.wikimedia.org/wiki/File:A_simplified_oil_diffusion_pump.jpg'},
 'M6 Diffusion Pump.jpg': {'credit': 'Kkmurray, CC BY 3.0, via Wikimedia Commons',
                           'url': 'https://commons.wikimedia.org/wiki/File:M6_Diffusion_Pump.jpg'},
 'McLeod gauge.jpg': {'credit': 'Ytrottier, CC BY 2.5, via Wikimedia Commons',
                      'url': 'https://commons.wikimedia.org/wiki/File:McLeod_gauge.jpg'},
 'McLeod gauge 01.jpg': {'credit': 'Ytrottier, Amada44, CC BY 2.5, via Wikimedia Commons',
                         'url': 'https://commons.wikimedia.org/wiki/File:McLeod_gauge_01.jpg'},
 'Paper filters-laboratory 1.jpg': {'credit': 'Nadina Wiórkiewicz, CC BY-SA 3.0, via Wikimedia Commons',
                                    'url': 'https://commons.wikimedia.org/wiki/File:Paper_filters-laboratory_1.jpg'},
 'Paper filters-laboratory 3.jpg': {'credit': 'Nadina Wiórkiewicz, CC BY-SA 3.0, via Wikimedia Commons',
                                    'url': 'https://commons.wikimedia.org/wiki/File:Paper_filters-laboratory_3.jpg'},
 'Heraeus Multifuge 3SR centrifuge 1.jpg': {'credit': 'Nadina Wiórkiewicz, CC BY-SA 3.0, via Wikimedia '
                                                      'Commons',
                                            'url': 'https://commons.wikimedia.org/wiki/File:Heraeus_Multifuge_3SR_centrifuge_1.jpg'},
 'Heraeus Multifuge 3SR centrifuge 3.jpg': {'credit': 'Nadina Wiórkiewicz, CC BY-SA 3.0, via Wikimedia '
                                                      'Commons',
                                            'url': 'https://commons.wikimedia.org/wiki/File:Heraeus_Multifuge_3SR_centrifuge_3.jpg'},
 'Beckman-Coulter preparative centrifuge Avanti J25-01.jpg': {'credit': 'Matylda Sęk, CC BY-SA 3.0, via '
                                                                        'Wikimedia Commons',
                                                              'url': 'https://commons.wikimedia.org/wiki/File:Beckman-Coulter_preparative_centrifuge_Avanti_J25-01.jpg'},
 'Distillation bande tournante 100 6504.jpg': {'credit': 'Jflm, CC BY-SA 3.0, via Wikimedia Commons',
                                               'url': 'https://commons.wikimedia.org/wiki/File:Distillation_bande_tournante_100_6504.jpg'},
 'Bande tournante 100 6499.jpg': {'credit': 'Jflm, CC BY-SA 3.0, via Wikimedia Commons',
                                  'url': 'https://commons.wikimedia.org/wiki/File:Bande_tournante_100_6499.jpg'},
 'UV cabinet for thin layer chromatography.jpg': {'credit': 'Seawind60, CC BY-SA 4.0, via Wikimedia Commons',
                                                  'url': 'https://commons.wikimedia.org/wiki/File:UV_cabinet_for_thin_layer_chromatography.jpg'},
 'UV-handlamp hg.jpg': {'credit': 'Hannes Grobe, CC BY-SA 3.0, via Wikimedia Commons',
                        'url': 'https://commons.wikimedia.org/wiki/File:UV-handlamp_hg.jpg'},
 "Wood's UV lamp.JPG": {'credit': 'Seawind60, CC BY-SA 4.0, via Wikimedia Commons',
                        'url': 'https://commons.wikimedia.org/wiki/File:Wood%27s_UV_lamp.JPG'},
 'Fraction collector - sampler LAMBDA OMNICOLL.jpg': {'credit': 'LAMBDA CZ s.r.o, CC BY-SA 4.0, via '
                                                                'Wikimedia Commons',
                                                      'url': 'https://commons.wikimedia.org/wiki/File:Fraction_collector_-_sampler_LAMBDA_OMNICOLL.jpg'},
 'Fraction Collector Tube Rack.jpg': {'credit': 'David J Morgan from Cambridge, UK, CC BY-SA 2.0, via '
                                                'Wikimedia Commons',
                                      'url': 'https://commons.wikimedia.org/wiki/File:Fraction_Collector_Tube_Rack.jpg'},
 'HPLC to ICP-MS.JPG': {'credit': 'Superchilum, CC BY-SA 3.0, via Wikimedia Commons',
                        'url': 'https://commons.wikimedia.org/wiki/File:HPLC_to_ICP-MS.JPG'},
 'Gas chromatographs with functional detectors in CAFIA laboratory, Czech Republic.jpg': {'credit': 'Sarka '
                                                                                                    'Na '
                                                                                                    'kopci, '
                                                                                                    'CC '
                                                                                                    'BY-SA '
                                                                                                    '4.0, '
                                                                                                    'via '
                                                                                                    'Wikimedia '
                                                                                                    'Commons',
                                                                                          'url': 'https://commons.wikimedia.org/wiki/File:Gas_chromatographs_with_functional_detectors_in_CAFIA_laboratory,_Czech_Republic.jpg'},
 'Gas chromatograph for GCxGC analyzes connected to a QTOF mass detector and GC-IRMS interface, in CAFIA laboratory, Czech Republic.png': {'credit': 'Sarka '
                                                                                                                                                     'Na '
                                                                                                                                                     'kopci, '
                                                                                                                                                     'CC '
                                                                                                                                                     'BY-SA '
                                                                                                                                                     '4.0, '
                                                                                                                                                     'via '
                                                                                                                                                     'Wikimedia '
                                                                                                                                                     'Commons',
                                                                                                                                           'url': 'https://commons.wikimedia.org/wiki/File:Gas_chromatograph_for_GCxGC_analyzes_connected_to_a_QTOF_mass_detector_and_GC-IRMS_interface,_in_CAFIA_laboratory,_Czech_Republic.png'},
 'Thiele Tube.jpg': {'credit': 'Iain George from Calgary, Canada, CC BY-SA 2.0, via Wikimedia Commons',
                     'url': 'https://commons.wikimedia.org/wiki/File:Thiele_Tube.jpg'},
 'MEL-TEMP melting point instrument.jpg': {'credit': 'Rifleman 82, public domain, via Wikimedia Commons',
                                           'url': 'https://commons.wikimedia.org/wiki/File:MEL-TEMP_melting_point_instrument.jpg'},
 'Gallenkamp Melting Point Apparatus.jpg': {'credit': 'Iain George from Calgary, Canada, CC BY-SA 2.0, via '
                                                      'Wikimedia Commons',
                                            'url': 'https://commons.wikimedia.org/wiki/File:Gallenkamp_Melting_Point_Apparatus.jpg'},
 'Ebulliometro.jpg': {'credit': 'Livio Brandellero, CC BY-SA 4.0, via Wikimedia Commons',
                      'url': 'https://commons.wikimedia.org/wiki/File:Ebulliometro.jpg'},
 'Ebulliometer for measuring wine alcohol.JPG': {'credit': 'Agne27, CC BY-SA 3.0, via Wikimedia Commons',
                                                 'url': 'https://commons.wikimedia.org/wiki/File:Ebulliometer_for_measuring_wine_alcohol.JPG'},
 'Abbe Refractometer in JXTCM.jpg': {'credit': '丰泽一号, CC BY-SA 4.0, via Wikimedia Commons',
                                     'url': 'https://commons.wikimedia.org/wiki/File:Abbe_Refractometer_in_JXTCM.jpg'},
 'Refractometre ABBE 2009 jflm.jpg': {'credit': 'Jflm, CC BY-SA 3.0, via Wikimedia Commons',
                                      'url': 'https://commons.wikimedia.org/wiki/File:Refractometre_ABBE_2009_jflm.jpg'},
 'Automatic Polarimeter with Filling Funnel.jpg': {'credit': 'Margarete Platzer, CC BY-SA 4.0, via Wikimedia '
                                                             'Commons',
                                                   'url': 'https://commons.wikimedia.org/wiki/File:Automatic_Polarimeter_with_Filling_Funnel.jpg'},
 'Modular circular polarimeter.jpg': {'credit': 'Gingkoaceae, CC BY-SA 4.0, via Wikimedia Commons',
                                      'url': 'https://commons.wikimedia.org/wiki/File:Modular_circular_polarimeter.jpg'},
 'Soviet portable polarimeter in its case.jpg': {'credit': 'Siarhei Besarab, CC BY-SA 4.0, via Wikimedia '
                                                           'Commons',
                                                 'url': 'https://commons.wikimedia.org/wiki/File:Soviet_portable_polarimeter_in_its_case.jpg'},
 'Polarimeter Saccharimeter-UNIL 603.867-IMG 2052-white.jpg': {'credit': 'Rama, CC BY-SA 3.0, via Wikimedia '
                                                                         'Commons',
                                                               'url': 'https://commons.wikimedia.org/wiki/File:Polarimeter_Saccharimeter-UNIL_603.867-IMG_2052-white.jpg'},
 'Saccharimeter Zucker-Museum.jpg': {'credit': 'FA2010, public domain, via Wikimedia Commons',
                                     'url': 'https://commons.wikimedia.org/wiki/File:Saccharimeter_Zucker-Museum.jpg'},
 'Saccharimeter c1906 Zucker-Museum.jpg': {'credit': 'FA2010, public domain, via Wikimedia Commons',
                                           'url': 'https://commons.wikimedia.org/wiki/File:Saccharimeter_c1906_Zucker-Museum.jpg'},
 'Cuvette.jpg': {'credit': 'Jeffrey M. Vinocur, CC BY 2.5, via Wikimedia Commons',
                 'url': 'https://commons.wikimedia.org/wiki/File:Cuvette.jpg'},
 '分光液槽.jpg': {'credit': 'GOKLuLe, CC BY-SA 3.0, via Wikimedia Commons',
              'url': 'https://commons.wikimedia.org/wiki/File:%E5%88%86%E5%85%89%E6%B6%B2%E6%A7%BD.jpg'},
 'Cuvette with penny.jpg': {'credit': 'Jeffrey M. Vinocur, CC BY 2.5, via Wikimedia Commons',
                            'url': 'https://commons.wikimedia.org/wiki/File:Cuvette_with_penny.jpg'},
 'DU640 spectrophotometer.jpg': {'credit': 'TimVickers, public domain, via Wikimedia Commons',
                                 'url': 'https://commons.wikimedia.org/wiki/File:DU640_spectrophotometer.jpg'},
 'Spektrofotometri.jpg': {'credit': 'Skorpion87, public domain, via Wikimedia Commons',
                          'url': 'https://commons.wikimedia.org/wiki/File:Spektrofotometri.jpg'},
 'Wiki21039722.jpg': {'credit': 'Wiki210397, CC BY-SA 4.0, via Wikimedia Commons',
                      'url': 'https://commons.wikimedia.org/wiki/File:Wiki21039722.jpg'},
 'FTIR spectrometer.png': {'credit': 'Wang F. et al., CC BY 4.0, via Wikimedia Commons',
                           'url': 'https://commons.wikimedia.org/wiki/File:FTIR_spectrometer.png'},
 'FTIR Spectrometer + ATR.jpg': {'credit': 'Keshavana, CC BY-SA 4.0, via Wikimedia Commons',
                                 'url': 'https://commons.wikimedia.org/wiki/File:FTIR_Spectrometer_%2B_ATR.jpg'},
 'FTIR 3000 1.jpg': {'credit': 'Kkmurray, CC BY-SA 3.0, via Wikimedia Commons',
                     'url': 'https://commons.wikimedia.org/wiki/File:FTIR_3000_1.jpg'},
 'Bruker 300 MHz NMR Spectrometer.jpg': {'credit': 'Lihan Yao, CC BY 2.0, via Wikimedia Commons',
                                         'url': 'https://commons.wikimedia.org/wiki/File:Bruker_300_MHz_NMR_Spectrometer.jpg'},
 'Bruker Avance DPX 250 NMR Spectrometer.jpg': {'credit': 'Chrumps, CC BY-SA 4.0, via Wikimedia Commons',
                                                'url': 'https://commons.wikimedia.org/wiki/File:Bruker_Avance_DPX_250_NMR_Spectrometer.jpg'},
 'NMR Bruker Avance II 700.jpg': {'credit': 'Chrumps, CC BY-SA 4.0, via Wikimedia Commons',
                                  'url': 'https://commons.wikimedia.org/wiki/File:NMR_Bruker_Avance_II_700.jpg'},
 'Model 21-103 Mass Spectrometer in use at Exxon analytical research laboratory 1974.jpeg': {'credit': 'Science '
                                                                                                       'History '
                                                                                                       'Institute, '
                                                                                                       'public '
                                                                                                       'domain, '
                                                                                                       'via '
                                                                                                       'Wikimedia '
                                                                                                       'Commons',
                                                                                             'url': 'https://commons.wikimedia.org/wiki/File:Model_21-103_Mass_Spectrometer_in_use_at_Exxon_analytical_research_laboratory_1974.jpeg'},
 'HR-ICP-MS, high-resolution inductively coupled plasma ionization mass spectrometer used for multi-element analysis, in CAFIA laboratory, Czech Republic.png': {'credit': 'Sarka '
                                                                                                                                                                           'Na '
                                                                                                                                                                           'kopci, '
                                                                                                                                                                           'CC '
                                                                                                                                                                           'BY-SA '
                                                                                                                                                                           '4.0, '
                                                                                                                                                                           'via '
                                                                                                                                                                           'Wikimedia '
                                                                                                                                                                           'Commons',
                                                                                                                                                                 'url': 'https://commons.wikimedia.org/wiki/File:HR-ICP-MS,_high-resolution_inductively_coupled_plasma_ionization_mass_spectrometer_used_for_multi-element_analysis,_in_CAFIA_laboratory,_Czech_Republic.png'},
 'EA-IRMS, isotope ratio mass spectrometer with elemental analyzer for the determination of isotope ratios of stable isotopes in wines, spirits, honey and natural sweeteners, in CAFIA laboratory.jpg': {'credit': 'Sarka '
                                                                                                                                                                                                                    'Na '
                                                                                                                                                                                                                    'kopci, '
                                                                                                                                                                                                                    'CC '
                                                                                                                                                                                                                    'BY-SA '
                                                                                                                                                                                                                    '4.0, '
                                                                                                                                                                                                                    'via '
                                                                                                                                                                                                                    'Wikimedia '
                                                                                                                                                                                                                    'Commons',
                                                                                                                                                                                                          'url': 'https://commons.wikimedia.org/wiki/File:EA-IRMS,_isotope_ratio_mass_spectrometer_with_elemental_analyzer_for_the_determination_of_isotope_ratios_of_stable_isotopes_in_wines,_spirits,_honey_and_natural_sweeteners,_in_CAFIA_laboratory.jpg'},
 'Scxrd.jpg': {'credit': 'Anjali Merin, CC BY-SA 4.0, via Wikimedia Commons',
               'url': 'https://commons.wikimedia.org/wiki/File:Scxrd.jpg'},
 'Equi-inclination 3-circle diffractometer.jpg': {'credit': 'unknown author, CC BY-SA 4.0, via Wikimedia '
                                                            'Commons',
                                                  'url': 'https://commons.wikimedia.org/wiki/File:Equi-inclination_3-circle_diffractometer.jpg'},
 'Teclu burner.jpg': {'credit': 'jasonwoodhead23, CC BY 2.0, via Wikimedia Commons',
                      'url': 'https://commons.wikimedia.org/wiki/File:Teclu_burner.jpg'},
 'Brulilo Teclu.JPG': {'credit': 'Walber, CC BY-SA 3.0, via Wikimedia Commons',
                       'url': 'https://commons.wikimedia.org/wiki/File:Brulilo_Teclu.JPG'},
 'Teclu Burner in museum.png': {'credit': 'Wirtualne Muzeum Gazonictwa, public domain, via Wikimedia Commons',
                                'url': 'https://commons.wikimedia.org/wiki/File:Teclu_Burner_in_museum.png'}}

NO_PHOTO = {'glass-tubing': 'на Commons только заготовки и газоразрядные трубки, чистого фото лабораторной трубки нет',
 'graduated-test-tube': 'единственное фото (коническая градуированная пробирка) уже использовано в карточке '
                        '«Центрифужная пробирка»',
 'bulb-air-condenser': 'найдены только снимки шарикового (водяного) холодильника Аллина — спутается с '
                       'существующей карточкой',
 'stadeler-condenser': 'нет фото ни на Commons, ни в магазине',
 'flange-reaction-vessel': 'нет фото',
 'thermometer-with-joint': 'отдельного фото нет; добавлено в описание карточки «Термометр»',
 'rod-thermometer': 'отдельного фото нет; добавлено в описание карточки «Термометр»',
 'hershberg-stirrer': 'нет фото',
 'homogenizer': 'на Commons только гомогенизаторы Даунса (ручные) и стомахеры',
 'flowmeter-capillary': 'нет фото (только гравюры)',
 'gas-meter': 'нет фото лабораторных газовых часов',
 'needle-valve': 'только промышленные вентили и чертежи в разрезе',
 'bunsen-valve': 'нет фото',
 'air-bath': 'нет фото',
 'metal-bath': 'нет фото бани (только слитки сплава Вуда)',
 'sand-bath': 'нет фото',
 'hydrogenation-apparatus': 'нет фото аппарата Парра или установки для гидрирования',
 'mercury-manometer': 'только медицинские тонометры и барометры',
 'sodium-press': 'нет фото',
 'ketyl-still': 'в магазине есть «куб для перегонки растворителя», но он спутается с карточкой «Насадка куба '
                'для растворителя»',
 'filter-pipette': 'нет фото',
 'filter-nail': 'нет фото',
 'filter-stick': 'нет фото',
 'anschutz-thiele-adapter': 'нет фото',
 'sabre-flask': 'нет фото',
 'antifoam-trap': 'в магазине это «насадки против брызг» — они уже есть в квизе',
 'steam-generator': 'нет фото',
 'bubble-cap-column': 'только схемы и промышленные колонны',
 'reflux-head': 'нет фото',
 'glass-helices': 'снимки есть только вместе с другими насадками (карточка «Насадки для колонок»)',
 'mesh-packing': 'то же, входит в карточку «Насадки для колонок»',
 'glass-bead-column': 'нет фото',
 'fischer-column': 'нет фото',
 'hahn-head': 'нет фото',
 'flow-extractor': 'нет фото',
 'craig-apparatus': 'нет фото',
 'tlc-sprayer': 'нашлась только камера для опрыскивания, самого распылителя нет',
 'mplc': 'нет фото',
 'hot-stage-microscope': 'нет фото микроскопа Кофлера/Бётиуса'}

NEW_CATEGORIES = [
    {"slug": "instruments", "image": "polarimeter-1.jpg", "name": "Instruments",
     "description": "Instruments for measuring melting points, refractive index, optical rotation and spectra, and for chromatography.", "sort_order": 125},
]
