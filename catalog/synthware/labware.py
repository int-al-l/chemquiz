"""Photos from the Synthware shop at labware-shop.com, chosen by eye.

labware-shop.com sells the same Synthware glassware as chengduglassware.com,
with sharper, cleaner photographs, and also stocks common bench items
(clamps, septa, O-rings, tubing...). tools/fetch_labware_shop.py downloads it;
build.py reads the photos from <folder>/labware/images/.

A stem "lw:<file>" is <folder>/labware/images/<file>.jpg. Lists here replace
the card's list in curate.PHOTOS: Synthware first, then any Wikimedia Commons
photo worth keeping. The same rules as curate.py apply -- clean product shots
only (no drawings, rulers, captions or the shop's red disclaimer text), and
nothing that could be mistaken for another card.

Left out on purpose, because a photo would fit two cards: rotavap spider
adapter (looks like a cow receiver), graduated distillation receiver (a
concentrator tube), liquid-liquid extractor (a Soxhlet), boss head (it is in
the clamp photos), glass Büchner funnels (they are fritted funnels) and the
shop's "inlet adapters" (they don't match the straight/bent inlet cards).
"""


def _card(category, name, aliases, description):
    return {"category": category, "name": name, "aliases": aliases, "description": description}


PHOTOS = {
    # --- existing cards: sharper Synthware photos ------------------------------
    'round-bottom-flask': [
        '5688_0',
        '5688_1',
        'lw:flask-round-bottom-spherical-joint_0',
        'lw:flask-round-bottom-spherical-joint_3',
    ],
    'two-neck-flask': [
        'lw:flask-two-neck-angled-13_0',
        'lw:flask-two-neck-angled-13_1',
        'lw:flask-two-neck-angled-7_0',
        'lw:flask-two-neck-angled-6_0',
        'lw:flask-two-neck-angled-4_1',
        'lw:flask-two-neck-angled-3_0',
    ],
    'three-neck-flask': [
        'lw:flask-three-neck-vertical-12_2',
        'lw:flask-three-neck-small-angled-11_0',
        'lw:flask-three-neck-vertical-11_0',
        'lw:flask-three-neck-vertical-11_1',
        'lw:flask-three-neck-small-angled-10_1',
        'lw:flask-three-neck-small-angled-8_0',
    ],
    'erlenmeyer-flask': [
        'lw:flask-erlenmeyer-3_0',
        'lw:flask-erlenmeyer-2_2',
        'lw:flask-erlenmeyer-1_1',
        'lw:flask-erlenmeyer_1',
        'lw:flask-erlenmeyer-wide-neck_2',
    ],
    'filtering-flask': [
        'lw:flask-filtering-with-joint-glass-side-arm-3_0',
        'lw:flask-filtering-with-joint-glass-side-arm-3_2',
        'lw:flask-filtering-with-joint-glass-side-arm-2_1',
        'lw:flask-filtering-with-joint-glass-side-arm-1_0',
        'lw:flask-filtering-with-joint-glass-side-arm-1_2',
    ],
    'jacketed-reaction-flask': [
        'lw:flask-round-bottom-3-neck-vertical-full-jacketed-2_0',
        'lw:flask-round-bottom-3-neck-vertical-full-jacketed-1_2',
        'lw:flask-round-bottom-3-neck-vertical-full-jacketed-1_0',
        'lw:flask-round-bottom-3-neck-vertical-half-jacketed-1_1',
        'lw:flask-round-bottom-3-neck-vertical-half-jacketed_1',
    ],
    'bottom-outlet-flask': [
        'lw:flask-three-neck-vertical-bottom-valve-center-joint-29-42-side-joint-24-40_0',
        'lw:flask-three-neck-vertical-bottom-valve-1_0',
        'lw:flask-three-neck-vertical-bottom-valve-1_1',
        '14181_0',
    ],
    'dewar-flask': [
        '1648_0',
        '1648_2',
        '1659_0',
        'lw:flask-dewar-wide-mouth-metal-and-plastic-housing-with-cover_2',
        'lw:flask-dewar-wide-mouth-metal-and-plastic-housing-with-cover_3',
    ],
    'beaker': [
        'lw:beaker-heavy-wall-double-scaled_0',
        'lw:beaker-heavy-wall-double-scaled_1',
        'lw:beaker-heavy-wall-double-scaled_2',
        'lw:beaker-heavy-wall-double-scaled_3',
    ],
    'pressure-vessel': [
        'lw:pressure-vessel-heavy-wall-gas-vacuum-connector-with-o-ring_1',
        'lw:pressure-vessel-heavy-wall-gas-vacuum-connector-with-o-ring_3',
        'lw:pressure-flask-round-bottom-thick-wall_0',
        'lw:pressure-vessel-heavy-wall-with-o-ring-2_0',
        'lw:pressure-vessel-heavy-wall-with-o-ring-2_1',
    ],
    'crystallizing-dish': [
        'lw:dish-crystallization_0',
        'lw:dish-crystallization_1',
        'lw:dish-crystallization_2',
        'lw:dish-crystallization_3',
    ],
    'kuderna-danish-flask': [
        'lw:kd-distillation-apparatus_0',
        'lw:kd-distillation-apparatus_2',
        'lw:kuderna-danish-flask_0',
        'lw:kuderna-danish-flask_1',
        'lw:kuderna-danish-flask_2',
    ],
    'jacketed-beaker': [
        'lw:beaker-tall-form-jacketed-removable-hose_0',
        'lw:beaker-tall-form-jacketed-removable-hose_1',
        'lw:beaker-short-form-jacketed-removable-hose_0',
    ],
    'reagent-bottle': [
        'lw:reagent-bottle-gl45-threaded_1',
        'lw:reagent-bottle-gl45-threaded_2',
        'lw:reagent-bottle-gl45-threaded_3',
        'lw:reagent-bottle-gl45-threaded_0',
    ],
    'peptide-synthesis-vessel': [
        'lw:peptide-synthesis-vessel-solid-phase-t-bore-teflon-stopcock-1_0',
        'lw:peptide-synthesis-vessel-solid-phase-t-bore-teflon-stopcock-1_2',
        'lw:peptide-synthesis-vessel-solid-phase-t-bore-teflon-stopcock_1',
        'lw:peptide-synthesis-vessel-solid-phase-1_2',
        'lw:peptide-synthesis-vessel-solid-phase_0',
        'lw:peptide-synthesis-vessel-solid-phase-t-bore-vacuum-1_3',
    ],
    'flat-bottom-flask': [
        'lw:flask-flat-bottom-4_1',
        'lw:flask-flat-bottom-4_2',
        'lw:flask-flat-bottom-3_1',
        'lw:flask-flat-bottom-2_3',
        'lw:flask-flat-bottom-4_0',
    ],
    'liebig-condenser': [
        'lw:condenser-distrllation-removale-hose-connections-1_1',
        'lw:condenser-west-removable-hose-connections-2_0',
        'lw:condenser-west-removable-hose-connections_0',
        'lw:condenser-west-removable-hose-connections-1_1',
        'lw:condenser-distrllation-removale-hose-connections-1_0',
    ],
    'coil-condenser': [
        'lw:condenser-graham-removable-hose-connections-3_1',
        'lw:condenser-graham-removable-hose-connections-3_2',
        'lw:condenser-graham-removable-hose-connections-2_0',
        'lw:condenser-graham-removable-hose-connections_1',
        'lw:condenser-graham-2_1',
        'wm:Graham (spiral) condenser-small.jpg',
        'wm:Graham condenser.jpg',
    ],
    'dimroth-condenser': [
        'lw:condenser-reflux-removable-hose-connections-4_0',
        'lw:condenser-reflux-removable-hose-connections_0',
        'lw:condenser-reflux-large-cooling-capacity_0',
        'lw:condenser-reflux_0',
        'lw:condenser-reflux-1_1',
        'wm:Dimrothkühler.jpg',
        'wm:Dimroth kuehler.jpg',
    ],
    'allihn-condenser': [
        'lw:condenser-allihn-removable-hose-connections-3_1',
        'lw:condenser-allihn-removable-hose-connections_0',
        'lw:condenser-allihn-3_1',
        'lw:condenser-allihn-2_1',
        'lw:condenser-allihn_1',
        'lw:condenser-allihn_2',
    ],
    'friedrichs-condenser': [
        'lw:condenser-friedrichs-removable-hose-connections_0',
        'lw:condenser-friedrichs-removable-hose-connections_1',
        'lw:condenser-friedrichs_0',
        'lw:condenser-friedrichs_2',
        'lw:condenser-friedrichs-1_0',
    ],
    'cold-finger-condenser': [
        'lw:condenser-cold-finger-with-drip-tip-2_0',
        'lw:condenser-cold-finger-with-drip-tip-2_1',
        'lw:condenser-cold-finger-with-drip-tip-1_0',
        'lw:condenser-cold-finger-with-drip-tip_0',
        'lw:condenser-cold-finger-short-form-1_1',
    ],
    'dewar-condenser': [
        'lw:condenser-dewar-micro-2_0',
        'lw:condenser-dewar-micro-1_0',
        'lw:condenser-dewar-micro_0',
        'lw:condenser-dewar-micro_1',
    ],
    'rotary-evaporator-condenser': [
        'lw:condenser-for-rotary-evaporators-rotary-evaporator-condenser-diagonal-style_0',
        'lw:condenser-for-rotary-evaporator-vertical-style_0',
        '4959_1',
    ],
    'air-condenser': [
        'lw:conderser-air-cooling-3_1',
        'lw:conderser-air-cooling-3_2',
        'lw:conderser-air-cooling-2_0',
        'lw:conderser-air-cooling-1_0',
    ],
    'vigreux-column': [
        'lw:column-distilling-vigreux-4_0',
        'lw:column-distilling-vigreux-4_1',
        'lw:column-distilling-vigreux-1_1',
        'lw:column-distilling-vigreux_0',
        'lw:column-distilling-vigreux-2_0',
    ],
    'distilling-head': [
        'lw:adapter-distillation-connecting_0',
        'lw:adapter-distillation-connecting_2',
        'lw:adapter-distillation-connecting-top-plastic-cap_2',
        '8434_0',
    ],
    'short-path-apparatus': [
        'lw:distilling-head-short-path-for-vorlatile-distillants_1',
        'lw:distilling-head-short-path-for-vorlatile-solvents_1',
        'lw:distillation-apparatus-short-path-vacuum-jacketed-1_0',
        'lw:distillation-apparatus-microscale-vigreux_0',
        'lw:distillation-apparatus-microscale_0',
        'lw:distillation-short-path-with-24-20-joint_0',
    ],
    'cow-receiver': [
        'lw:distillation-cow-receiver_0',
        'lw:distillation-cow-receiver_1',
        'lw:distillation-receiver-with-hose-connection-1_1',
        'lw:distillation-receiver-with-hose-connection-1_3',
        'lw:distillation-receiver-without-hose-connection_1',
        '14573_0',
    ],
    'kugelrohr-bulb': [
        'lw:distilling-bulb-kugelror_0',
        'lw:distilling-bulb-kugelror_2',
        'lw:distilling-bulb-kugelror_3',
    ],
    'snyder-column': [
        'lw:snyder-distillation-column_0',
        '15285_0',
    ],
    'glass-funnel': [
        'lw:funnel-micro_1',
        '15725_0',
        'wm:Analysentrichter.png',
        'wm:Funnel MET DP234124.jpg',
    ],
    'powder-funnel': [
        'lw:funnel-power-60-offset_0',
        'lw:funnel-power-60-offset_1',
        'lw:funnel-power-60-offset_2',
        'lw:funnel-power_0',
    ],
    'fritted-filter-funnel': [
        'lw:filter-funnel-buchner-inner-joint-17_0',
        'lw:filter-funnel-buchner-inner-joint-14_0',
        'lw:filter-funnel-buchner-inner-joint-20_1',
    ],
    'fritted-filter-tube': [
        'lw:filter-tube-fritted-disc-3_0',
        'lw:filter-tube-fritted-disc-3_2',
        'lw:filter-tube-fritted-disc-2_0',
        'lw:filter-tube-fritted-disc-2_1',
        'lw:filter-tube-fritted-disc-2_3',
    ],
    'separatory-funnel': [
        'lw:funnel-separatory-squibb-glass-stopcock-4_0',
        'lw:funnel-separatory-squibb-glass-stopcock-4_1',
        'lw:funnel-separatory-squibb-glass-stopcock-2_0',
        'lw:funnel-separatory-squibb-glass-stopcock-1_0',
        'lw:funnel-separatory-squibb-glass-stopcock_0',
        'lw:funnel-separatory-glass-stopper-14_0',
    ],
    'pressure-equalizing-funnel': [
        'lw:funnel-pressure-equalizing-double-glass-stopcock-no-scale-3_0',
        'lw:funnel-pressure-equalizing-double-teflon-stopcock-4_0',
        'lw:funnel-pressure-equalizing-double-teflon-stopcock-3_0',
        'lw:funnel-pressure-equalizing-double-glass-stopcock-no-scale-2_1',
        'lw:funnel-pressure-equalizing-double-teflon-stopcock-no-scale-2_1',
        'lw:funnel-pressure-equalizing-double-glass-stopcock-2_1',
    ],
    'reducing-adapter': [
        'lw:adapter-enlarging_0',
        'lw:adapter-enlarging_2',
        'lw:adapter-enlarging_3',
        'lw:adapter-reducing_1',
        'lw:adapter-reducing_3',
    ],
    'ball-socket-adapter': [
        'lw:adapter-with-ball-joint_0',
        'lw:adapter-with-ball-joint_1',
        'lw:adapter-with-ball-socket_0',
        'lw:adapter-with-ball-socket_1',
        'lw:adapter-with-ball-socket_2',
    ],
    'thermometer-adapter': [
        'lw:adapter-inlet-or-thermometer_0',
        'lw:adapter-inlet-or-thermometer_1',
        'lw:adapter-inlet-or-thermometer_2',
        'lw:adapter-inlet-or-thermometer_3',
        '4625_0',
    ],
    'thermowell': [
        'lw:adapter-for-thermometer-2_0',
        'lw:adapter-for-thermometer-2_2',
        'lw:adapter-for-thermometer_2',
        '8939_0',
    ],
    'vacuum-gas-adapter': [
        'lw:adapter-vacuum-innert-gas-90_0',
        'lw:adapter-vacuum-innert-gas-90_2',
        'lw:adapter-vacuum-or-argon_1',
        'lw:adapter-vacuum-or-argon_3',
    ],
    'claisen-adapter': [
        'lw:adapter-claisen-two-neck_1',
        'lw:adapter-claisen-two-neck_3',
        'lw:adapter-claisen-three-neck_1',
    ],
    'vacuum-takeoff-adapter': [
        'lw:adapter-vacuum-take-off-short-stem_1',
        'lw:adapter-vacuum-take-off-short-stem_2',
        'lw:adapter-vacuum-take-off-short-stem_3',
        'lw:adapter-vacuum-take-off-long-stem_0',
        '8808_0',
    ],
    'stopcock-vacuum-adapter': [
        'lw:adapter-vacuum-glass-stopcock-90_0',
        'lw:adapter-vacuum-glass-stopcock-90_2',
        'lw:adapter-flow-control-metering-stopcock-90%C2%BA_0',
        'lw:adapter-bent-90-outer-joint-ptfe-stopcock_1',
        'lw:adapter-straight-vacuum-ptfe-stopcock_1',
        'lw:adapter-bent-90-outer-joint-glass-stopcock_1',
        'lw:adapter-straight-outer-joint-glass-stopcock_1',
    ],
    'drying-tube-adapter': [
        'lw:adapter-drying-tube-75_0',
        'lw:adapter-drying-tube-75_1',
        'lw:adapter-drying-tube-75_3',
        'lw:adapter-drying-tube-straight-1_0',
        'lw:adapter-drying-tube-straight_0',
        'lw:adapter-drying-tube-u-shaped_1',
    ],
    'anti-splash-adapter': [
        'lw:adapter-anti-splash-modified_0',
        'lw:adapter-anti-splash-modified_1',
        'lw:adapter-anti-splash-with-fritted-disc-1_0',
        'lw:adapter-anti-splash_1',
        'lw:adapter-anti-climb_0',
        'lw:adapter-anti-splash-modified-ellipse_0',
        'lw:adapter-anti-splash-ellipse_0',
    ],
    'kjeldahl-trap': [
        'lw:adapter-kjeldahl-trap_0',
        'lw:adapter-kjeldahl-trap_1',
        'lw:adapter-kjeldahl-trap_2',
        'lw:adapter-kjeldahl-trap-glass-side-arm_0',
        'lw:adapter-kjeldahl-trap-glass-side-arm_1',
    ],
    'concentrator-tube': [
        'lw:concentrator-tube-graduated_0',
        'lw:concentrator-tube-graduated_1',
        'lw:concentrator-tube-graduated_2',
    ],
    'filtration-apparatus': [
        'lw:filtration-apparatus-47mm-stainless-steel-complete-support-assembly_1',
        'lw:filtration-apparatus-47mm-stainless-steel-complete-support-assembly_2',
        'lw:filtration-apparatus-47mm-sintered-glass-complete-support-assembly_2',
    ],
    'schlenk-flask': [
        'lw:flask-reaction-teflon-stopper-2_3',
        'lw:flask-reaction-teflon-stopper-1_2',
        'lw:flask-reaction-teflon-stopper_1',
        'lw:flask-reaction-glass-stopper-2_3',
        'lw:flask-reaction-glass-stopper-1_1',
        'lw:flask-reaction-high-vacuum-valve-2_1',
    ],
    'schlenk-tube': [
        'lw:flask-reaction-tube-teflon-stopcock-6_0',
        'lw:flask-reaction-tube-teflon-stopcock-5_1',
        'lw:flask-reaction-tube-glass-stopcock-5_0',
        'lw:flask-reaction-tube-teflon-stopcock-4_0',
        'lw:flask-reaction-tube-glass-stopcock-4_1',
        'lw:flask-reaction-tube-glass-stopcock-with-hook-1_2',
        'lw:flask-reaction-tube-glass-stopcock_1',
    ],
    'vacuum-manifold': [
        'lw:manifold-nitrogen-argon-line-teflon-right-hose_0',
        'lw:manifold-vacuum-single-high-vacuum-valves-left-hose_1',
        'lw:manifold-vacuum-single-teflon-stopcocks-2-side-hose_1',
        'lw:manifold-vacuum-inert-gas-all-glass-6_1',
        'lw:manifold-double-hollow-glass-stopcocks-both-side_2',
        'lw:manifold-vacuum-single-teflon-stopcock-left-hose-right-joint_0',
    ],
    'vacuum-trap': [
        'lw:vacuum-trap-with-hose-connector_0',
        'lw:vacuum-trap-without-joint_0',
        'lw:vacuum-trap-without-joint_1',
        'lw:vacuum-trap-2_0',
        'lw:vacuum-trap-2_1',
        'lw:vacuum-trap-15-ball-joint_0',
    ],
    'bubbler': [
        'lw:bubbler-mineral-oil-anti-blow-back-conical_0',
        'lw:bubbler-mineral-oil-anti-blow-back_0',
        'lw:bubbler-mineral-oil_0',
        'lw:adapter-with-mineral-oil-bubbler_0',
        'lw:adapter-with-mineral-oil-bubbler_3',
    ],
    'gas-washing-bottle': [
        'lw:bottle-gas-washing-porous-tube-with-hook_0',
        'lw:bottle-gas-washing-straight-tube-with-hook_0',
        'lw:bottle-gas-washing-straight-tube-with-hook_2',
        'lw:bottle-gas-washing-fritted-2_0',
    ],
    'sublimator': [
        'lw:sublimation-apparatus-valve-modified_0',
        'lw:sublimation-apparatus-1_0',
        'lw:sublimation-apparatus_1',
        'lw:sublimator-with-2mm-glass-stopcock_0',
        '34040_0',
    ],
    'solvent-still-head': [
        'lw:distilling-head-solvent_0',
        'lw:distilling-head-solvent_1',
        'lw:distilling-head-solvent_2',
        'lw:solvent-still-with-high-vacuum-valves_2',
        'lw:solvent-still-high-vacuum-valves_1',
    ],
    'high-vacuum-valve': [
        'lw:valve-high-vacuum-ptfe-o-ring-90_0',
        'lw:valve-high-vacuum-ptfe-o-ring-90_1',
        'lw:valve-high-vacuum-ptfe-o-ring-90_2',
        'lw:valve-high-vacuum-ptfe-o-ring_2',
    ],
    'chromatography-column': [
        'lw:column-chromatography-fritted-disc-5_0',
        'lw:chromatography-column-fritted-disc-spherical-joints-1_1',
        'lw:chromatography-column-spherical-joints-1_1',
        '20984_0',
    ],
    'chromatography-column-reservoir': [
        'lw:column-chromatography-with-reservoir-with-hook-1_0',
        'lw:column-chromatography-with-reservoir-with-hook-1_1',
        '27704_0',
    ],
    'chromatography-reservoir': [
        'lw:chromatography-reservoir-upper-and-lower-hook_0',
        'lw:chromatography-reservoir-upper-and-lower-hook_1',
        'lw:chromatography-reservoir_0',
        'lw:chromatography-reservoir_1',
        'lw:chromatography-reservoir-with-ball-socket_0',
        'lw:reservoir-chromatography-rodaviss-joints_0',
    ],
    'tlc-tank': [
        'lw:tank-thin-layer-chromatography-rectangular-groove_1',
        'lw:tank-thin-layer-chromatography-rectangular-groove_2',
        'lw:tank-thin-layer-chromatography-rectangular-flat_0',
        'lw:tank-thin-layer-chromatography-rectangular-flat_1',
        'lw:tank-thin-layer-chromatography-rectangular-groove_0',
    ],
    'glass-stopper': [
        'lw:stopper-penny-head-glass-hollow-1_0',
        'lw:stopper-penny-head-glass-hollow-1_1',
        'lw:stopper-penny-head-glass-hollow-1_2',
        'lw:stopper-glass-flsk-length-pennyhead_0',
        'lw:stopper-glass-flsk-length-pennyhead_2',
        'lw:stopper-glass-flsk-length-pennyhead_3',
    ],
    'ptfe-stopper': [
        'lw:stopcock-replacement-plug-1-5-teflon-double-oblique-bore_0',
        'lw:stopcock-replacement-plug-1-5-teflon-t-bore_0',
        'lw:stopcock-replacement-plug-1-5-teflon-metering-valve_0',
        'lw:stopcock-replacement-plug-1-5-teflon-straight-bore_0',
        'lw:stopcock-replacement-plug-1-5-teflon-double-oblique-bore_1',
    ],
    'ptfe-stopcock': [
        'lw:stopcock-1-5-teflon-metering-valve_0',
        'lw:stopcock-1-5-teflon-metering-valve_1',
        'lw:stopcock-teflon-straight-bore_0',
        'lw:stopcock-teflon-straight-bore_1',
        '6666_0',
    ],
    'glass-stopcock': [
        'lw:stopcock-glass-high-vacuum-straight-bore_0',
        '13356_0',
        '16172_0',
    ],
    'joint-clip': [
        'lw:joint-clip-standad-taper-joint_0',
        'lw:joint-clip-standad-taper-joint_1',
        'lw:joint-clip-standad-taper-joint_2',
        'lw:joint-clip-standad-taper-joint_3',
        'wm:Keck clips.jpg',
    ],
    'septum': [
        'lw:septum-stopper-sleeve-type-soft_0',
        'lw:septum-stopper-sleeve-type-soft_1',
        'lw:septum-stopper-sleeve-type-hard_2',
        'lw:septum-silicone-rubber-sleeve-type-hard_0',
        'wm:Rubberseptum.jpg',
    ],
    'soxhlet-extractor': [
        'lw:extractor-soxhlet_0',
        'lw:extractor-soxhlet_1',
        'lw:extractor-soxhlet_2',
        'lw:extractor-soxhlet_3',
        'wm:Soxhlet-Extraktor.png',
    ],
    'volumetric-flask': [
        'lw:high-precision-thick-walled-volumetric-flask-with-constant-a-grade-and-coding_0',
        'lw:flask-volumetric-clear-pp-stopper-non-certified_1',
        'lw:flask-volumetric-clear-pp-stopper-certified_2',
        'lw:flask-volumetric-clear-glass-stopper-certified_2',
        'lw:flask-volumetric-amber-pp-stopper-non-certified_0',
        'lw:flask-volumetric-amber-glass-stopper-certified_1',
        'wm:Brand volumetric flask 100ml.jpg',
    ],
    'test-tube': [
        'wm:Test tube blue background.jpg',
        'wm:Glass tube with screw cap 1.jpg',
        'lw:test-tube-heavy-wall_0',
        'lw:test-tube-heavy-wall_1',
        'lw:test-tube-heavy-wall_2',
        'lw:test-tube-heavy-wall_3',
    ],
    'burette': [
        'lw:burette-clear-high-vacuum-valve-ptfe-stopcock_0',
        'lw:burette-amber-ptfe-stopcock_0',
        'lw:burette-clear-ptfe-stopcock_0',
        'lw:burette-clear-ptfe-stopcock_2',
        'wm:50 mL Buret.jpg',
    ],
    'desiccator': [
        'lw:desiccator-clear_0',
        'lw:desiccator-amber_0',
        'lw:desiccator-amber-vacuum_0',
        'lw:desiccator-clear-vacuum_0',
        'wm:Exsikkator.png',
    ],
    'drying-pistol': [
        'lw:drying-chamber-abderhalden_0',
        'wm:Trockenpistole Abderhalden 02.jpg',
        'wm:Abderhalden drying pistol.jpg',
    ],
    'nmr-tube': [
        '5457_0',
        'lw:nmr-tubes-with-cap-high-flow_0',
    ],
    'clamp': [
        'wm:Metal laboratory clamp-02.jpg',
        'wm:Universal clamp.jpg',
        'lw:three-finger-double-adjust-able-clamp-small_0',
        'lw:three-finger-double-adjust-able-clamp-large_0',
        'lw:four-finger-clamp-shank-chromed_0',
    ],
    'support-stand': [
        'wm:Retort stand.jpg',
        'wm:Ringstand with a ring clamp.jpg',
        'lw:laboratory-stand-rectangular-1_0',
    ],
    # --- new cards ---------------------------------------------------------------
    'evaporating-flask': [
        'lw:flask-evaporation-2_1',
        'lw:flask-evaporation-1_2',
        'lw:flask-evaporation_1',
        'lw:flask-evaporation-3_3',
        'lw:flask-evaporation-1_0',
    ],
    'four-neck-flask': [
        'lw:flask-round-bottom-5-neck-vertical-4_0',
        'lw:flask-round-bottom-5-neck-vertical-4_1',
        'lw:flask-round-bottom-5-neck-vertical-2_0',
        'lw:flask-round-bottom-5-neck-vertical-2_1',
        'lw:flask-round-bottom-5-neck-vertical-3_0',
    ],
    'freeze-drying-flask': [
        'lw:bottle-for-freeze-dryer_0',
        'lw:bottle-for-freeze-dryer_1',
        'lw:bottle-for-freeze-dryer_3',
    ],
    'immersion-well': [
        'lw:immersion-well-photochemical-quartz-without-joint_0',
        'lw:reaction-vessel-photochemical-internal-thread_0',
    ],
    'hirsch-funnel': [
        'lw:filter-funnel-hirsch-1_0',
        'lw:filter-funnel-hirsch_0',
        'lw:filter-funnel-hirsch-glass-sintered_0',
    ],
    'weighing-funnel': [
        'lw:funnel-weighing_0',
        'lw:funnel-weighing_1',
        'lw:funnel-weighing_2',
    ],
    'addition-funnel': [
        'lw:funnel-separatory-cylinder-graduated-3_1',
        'lw:funnel-separatory-cylinder-graduated-2_1',
        'lw:funnel-separatory-cylinder-graduated_1',
        'lw:funnel-separatory-cylinder-graduated_3',
        'lw:funnel-separatory-cylinder-graduated-2_2',
    ],
    'gooch-crucible': [
        'lw:crucible-gooch-low-form-1_0',
        'lw:crucible-gooch-low-form-1_1',
    ],
    'column-packing': [
        'lw:distilling-column-packing_0',
    ],
    'extraction-thimble': [
        'lw:extraction-thimble-glass-1_0',
        'lw:extraction-thimble-glass-1_1',
        'lw:extraction-thimble-glass-1_2',
    ],
    'strauss-flask': [
        'lw:flask-high-vacuum-valve-flat-bottom-modified_0',
        'lw:flask-high-vacuum-valve-flat-bottom-modified_1',
        'lw:flask-high-vacuum-valve-flat-bottom-1_0',
        'lw:flask-high-vacuum-valve-flat-bottom-1_1',
        'lw:flask-high-vacuum-valve-round-bottom-1_1',
        'lw:flask-high-vacuum-valve-round-bottom_0',
    ],
    'filter-ball': [
        'lw:filter-ball-sintered_0',
        'lw:filter-ball-sintered_2',
    ],
    'check-valve': [
        'lw:check-valve_0',
    ],
    'cannula': [
        'lw:cannula-stainless-steel-3_0',
    ],
    'vacuum-grease': [
        'lw:vacuum-silicone-grease-7501_0',
    ],
    'vacuum-tubing': [
        'lw:silicone-tubings_0',
        'lw:latex-tubings_0',
        'lw:rubber-tubings-vacuum_0',
    ],
    'flow-control-adapter': [
        'lw:chromatography-flow-control-adapter_0',
        'lw:chromatography-flow-control-adapter_1',
        'lw:flow-control-adapter-chromatogaphy-rodaviss-joint_0',
    ],
    'silica-gel': [
        'lw:silica-gel-300-400-mesh_0',
    ],
    'o-ring': [
        'lw:o-ring-viton-anti-corrosive-2_0',
        'lw:o-ring-viton-anti-polarity-2_0',
        'lw:o-ring-viton-anti-polarity-1_0',
        'lw:o-ring-viton-2_0',
    ],
    'gl-screw-cap': [
        'lw:cap-compression-nylon-with-hole-2_0',
        'lw:cap-compression-nylon-with-hole-1_0',
        'lw:cap-compression-nylon-with-hole_0',
        'lw:cap-nylon-screw-thread-no-o-ring_1',
    ],
    'ptfe-sleeve': [
        'lw:sleeve-teflon-ribbed-with-gripping-ring_0',
    ],
    'hose-connector': [
        'lw:removable-hose-connection-gl-thread-straight_0',
        'lw:removable-hose-connection-gl-thread-straight_1',
    ],
    'pipette-bulb': [
        'lw:pasteur-pipette-bulb-red_0',
    ],
    'craig-tube': [
        'lw:tube-craig-recrystallization-complete_0',
    ],
    'ball-joint-clamp': [
        'lw:clamp-pinch-stainless-steel-spherical_0',
        'lw:clamp-pinch-stainless-steel-spherical_1',
        'lw:clamp-pinch-stainless-steel-spherical_2',
        'lw:clamp-pinch-stainless-steel-spherical_3',
    ],
    'overhead-stirrer': [
        'lw:stirring-rod-for-overhead-stirrer-teflon-anchor_0',
        'lw:stirring-rod-for-overhead-stirrer-teflon-anchor_1',
        'lw:stirring-rod-for-overhead-stirrer-teflon-anchor_2',
    ],
    'nmr-tube-washer': [
        'lw:nmr-tube-washer_0',
    ],
    'brush': [
        'lw:nmr-tube-brush-nylon_2',
        'lw:nmr-tube-brush-nylon_3',
        'lw:pig-bristle-brush_2',
        'lw:pig-bristle-brush_3',
    ],
    'glass-cutter': [
        'lw:glass-cutter-natural-diamond_0',
    ],
    'vial-decapper': [
        'lw:manual-de-capper-%CF%8611mm_0',
    ],
    'finger-protector': [
        'lw:silicone-finger-protector-heat-protection-2_0',
    ],
}

NEW_CARDS = {
    'evaporating-flask': _card(
        'flasks', 'Evaporating flask', ['Rotavap flask', 'Rotary evaporator flask'],
        'A round flask with one wide ground joint, made to hang on a rotary evaporator. It spins '
        'in a warm bath under vacuum, and the solvent boils off from a thin film spread over the '
        'inside wall. Never fill it more than half full, or the solution bumps up into the '
        'machine.'),
    'four-neck-flask': _card(
        'flasks', 'Four-neck flask', ['Four-necked round-bottom flask', 'Multi-neck flask'],
        'A round-bottom flask with four necks, for reactions that need many things at once: a '
        'stirrer in the middle, and a condenser, a thermometer and a dropping funnel in the side '
        'necks. Counting the necks is the quickest way to tell it from its two- and three-neck '
        'relatives.'),
    'freeze-drying-flask': _card(
        'flasks', 'Freeze-drying flask', ['Lyophilization flask', 'Freeze dryer bottle'],
        'A wide glass jar with a black lid that plugs onto a freeze dryer. A frozen solution '
        'inside loses its water straight from ice to vapour under deep vacuum, leaving a dry, '
        'fluffy powder. Used for proteins, sugars and other things that heat would spoil.'),
    'immersion-well': _card(
        'flasks', 'Photochemical immersion well', ['Photoreactor', 'Immersion well', 'Photochemical reactor'],
        'A double-walled quartz or glass tube that holds a UV lamp and dips into the reaction. '
        'Light shines outward into the solution while cooling water between the walls stops the '
        'lamp from boiling it. Used to drive reactions with light (photochemistry). Never look at '
        'the lit lamp.'),
    'hirsch-funnel': _card(
        'funnels', 'Hirsch funnel', ['Small filter funnel'],
        'The small version of a Büchner funnel, with sloping sides and a filter plate only a '
        'centimetre or two across. It is for collecting a few milligrams of crystals by suction '
        'filtration without losing them on a large filter.'),
    'weighing-funnel': _card(
        'funnels', 'Weighing funnel', ['Weighing scoop', 'Powder scoop funnel'],
        'A small glass scoop with a spout. The solid is weighed straight into it, then poured '
        'through the spout into a narrow flask neck, and a rinse of solvent carries the last '
        'grains in, so nothing is lost between the balance and the flask.'),
    'addition-funnel': _card(
        'funnels', 'Graduated addition funnel', ['Cylindrical addition funnel', 'Graduated dropping funnel'],
        'A tall graduated cylinder with a tap at the bottom and a ground joint below it. It sits '
        'in a flask neck and adds a liquid drop by drop, and the scale shows how much has gone '
        'in. It has no side tube, so the top must be left open or vented. The closed version, '
        'with the side tube, is the pressure-equalizing funnel.'),
    'gooch-crucible': _card(
        'funnels', 'Fritted Gooch crucible', ['Gooch crucible', 'Filter crucible', 'Sintered crucible'],
        'A small cup with a sintered-glass bottom, used for quantitative analysis. A precipitate '
        'is filtered into it by suction, dried in an oven and weighed, crucible and all. The gain '
        'in weight is the mass of the precipitate.'),
    'column-packing': _card(
        'distillation', 'Column packing', ['Raschig rings', 'Distillation packing', 'Glass helices'],
        'Short glass tubes or rings poured into a distillation column. They give rising vapour '
        'and falling liquid a large surface to meet on, and each meeting is like one more small '
        'distillation. That sharpens the separation of liquids whose boiling points are close.'),
    'extraction-thimble': _card(
        'distillation', 'Extraction thimble', ['Soxhlet thimble', 'Glass thimble'],
        'A cup with a porous glass bottom that holds the solid inside a Soxhlet extractor. Hot '
        'solvent soaks through it again and again, washing out what dissolves, while the solid '
        'itself stays in the cup. Paper thimbles do the same job once and are thrown away.'),
    'strauss-flask': _card(
        'vacuum', 'Strauss flask', ['Solvent storage flask', 'Solvent transfer flask'],
        'A round flask with a sealed Teflon screw valve on a side arm, for keeping dry, degassed '
        'solvents or air-sensitive solutions. The valve closes tight enough to hold a vacuum or '
        'argon for weeks, and the flask is filled and emptied through a vacuum line.'),
    'filter-ball': _card(
        'vacuum', 'Sintered filter ball', ['In-line gas filter', 'Fritted filter bulb'],
        'A glass bulb with a porous glass disc across its middle, fitted into a gas or vacuum '
        'line. Gas passes through the disc but dust and fine powder do not, so nothing gets '
        'sucked into the pump or blown into the reaction.'),
    'check-valve': _card(
        'vacuum', 'Check valve', ['Non-return valve', 'One-way valve'],
        'A valve that lets gas flow in one direction only. Pressure lifts a small glass or Teflon '
        'seat and gas passes. If the flow reverses, the seat drops back and closes, so air or oil '
        'cannot be sucked back into the apparatus.'),
    'cannula': _card(
        'vacuum', 'Cannula', ['Double-tipped needle', 'Transfer needle'],
        'A long, thin, flexible steel tube pointed at both ends. One end goes through the septum '
        'of one flask and the other through the septum of another, and a little gas pressure '
        'pushes the liquid across. Air-sensitive liquids move from flask to flask this way '
        'without ever meeting air.'),
    'vacuum-grease': _card(
        'vacuum', 'Vacuum grease', ['Silicone grease', 'Joint grease', 'High-vacuum grease'],
        'A thick silicone paste smeared thinly on ground-glass joints and stopcocks. It makes '
        'them airtight under vacuum and keeps them turning freely. Use a thin band at the top of '
        'the joint only, because excess grease creeps into the reaction.'),
    'vacuum-tubing': _card(
        'vacuum', 'Vacuum tubing', ['Rubber tubing', 'Thick-walled tubing', 'Hose'],
        'Flexible tubing that connects glassware to a pump, a gas line or a water tap. Tubing for '
        'vacuum has thick walls so it does not collapse flat when the air is pumped out. Thin '
        'latex or silicone tubing is fine for cooling water.'),
    'flow-control-adapter': _card(
        'chromatography', 'Flow control adapter', ['Column flow adapter', 'Pressure adapter'],
        'A cap for the top of a chromatography column, with a gas inlet and a fine needle valve. '
        'Gentle air or nitrogen pressure pushes the solvent through the silica faster (flash '
        'chromatography), and the valve sets how fast.'),
    'silica-gel': _card(
        'chromatography', 'Silica gel', ['Chromatography silica', 'SiO2'],
        'A fine white powder of porous silicon dioxide, the most common stationary phase in '
        'column chromatography. Polar compounds stick to it more strongly and come off the column '
        'later. The mesh number gives the grain size. Weigh and pour it in a fume hood and never '
        'breathe the dust.'),
    'o-ring': _card(
        'closures', 'O-ring', ['Sealing ring', 'Viton O-ring'],
        'A rubber ring with a round cross-section that seals a joint when squeezed between two '
        'surfaces. O-ring joints and Teflon valves rely on them. Viton and other materials are '
        'chosen to survive the solvents they will meet.'),
    'gl-screw-cap': _card(
        'closures', 'GL screw cap', ['GL cap', 'Screw cap with hole', 'Compression cap'],
        'A plastic cap for glass with a GL screw thread. Some are solid and simply close a '
        'bottle. Others have a hole in the top and a seal inside, so a tube, thermometer or hose '
        'can pass through and be clamped airtight.'),
    'ptfe-sleeve': _card(
        'closures', 'PTFE joint sleeve', ['Teflon sleeve', 'Joint sleeve'],
        'A thin Teflon liner slipped over a ground-glass joint before it is assembled. It seals '
        'without grease and stops the joint from seizing, so nothing sticks and no grease gets '
        'into the product.'),
    'hose-connector': _card(
        'closures', 'Hose connector', ['Hose barb', 'Removable hose connection'],
        'A ribbed nozzle that rubber or plastic tubing is pushed onto. Removable versions screw '
        'onto a GL thread, so a broken one is swapped out and the glassware is saved.'),
    'pipette-bulb': _card(
        'measuring', 'Pipette bulb', ['Pasteur pipette bulb', 'Rubber bulb', 'Teat'],
        'A small rubber bulb pushed onto the top of a Pasteur pipette. Squeeze it, dip the tip '
        'into the liquid and let go slowly, and the liquid is drawn up. Larger pipettes use a '
        'bigger bulb or a filler, never the mouth.'),
    'craig-tube': _card(
        'tubes', 'Craig tube', ['Craig recrystallization tube'],
        'A small tube with a loosely fitting glass plug, for recrystallizing a few milligrams. '
        'Crystals form in the tube, the plug goes in, and the tube is spun upside down in a '
        'centrifuge. The liquid is flung past the plug and the crystals stay behind.'),
    'ball-joint-clamp': _card(
        'bench', 'Ball joint clamp', ['Pinch clamp', 'Spherical joint clamp'],
        'A spring clamp with two jaws shaped to grip a ball-and-socket joint. It holds the ball '
        'tight in its socket while still letting the joint swivel, which makes vacuum lines and '
        'traps easier to connect.'),
    'overhead-stirrer': _card(
        'bench', 'Overhead stirrer paddle', ['Stirrer shaft', 'Anchor stirrer', 'Stirrer paddle'],
        'A long Teflon-coated rod with a paddle at the end, turned by a motor mounted above the '
        'flask. It stirs thick mixtures and large volumes that a magnetic stir bar cannot move. A '
        'stirrer bearing in the middle neck keeps it straight and sealed.'),
    'nmr-tube-washer': _card(
        'tools', 'NMR tube washer', ['NMR tube cleaner'],
        'A glass stand that NMR tubes are turned upside down onto. Solvent is pulled through each '
        'tube by vacuum and rinses it inside, which is much gentler than scrubbing these thin, '
        'expensive tubes with a brush.'),
    'brush': _card(
        'tools', 'Test tube brush', ['Glassware brush', 'Bottle brush'],
        'A twisted-wire brush with bristles, for scrubbing the inside of test tubes, flasks and '
        'burettes with soapy water. Brushes come in many sizes. Choose one that fits, because the '
        'wire tip can scratch or crack glass.'),
    'glass-cutter': _card(
        'tools', 'Glass cutter', ['Diamond glass cutter', 'Tube cutter'],
        'A tool with a diamond or hard-metal tip that scores a line across glass tubing or an '
        'ampoule neck. The glass then snaps cleanly along the scratch. Wrap the tube in a cloth '
        'when you break it.'),
    'vial-decapper': _card(
        'tools', 'Vial decapper', ['Crimp cap remover', 'Decrimper'],
        'Pliers that open the metal crimp caps sealed onto GC and sample vials. They tear the '
        'aluminium collar off in one squeeze, so nobody has to pry at a sharp edge with a '
        'spatula.'),
    'finger-protector': _card(
        'tools', 'Heat-resistant finger protector', ['Silicone finger grip', 'Heat protection grip'],
        'A silicone grip slipped over the fingers for picking up hot flasks and beakers. Silicone '
        "stays cool enough on the outside to hold, doesn't slip on glass, and lets you feel what "
        'you are gripping better than a thick glove.'),
}
