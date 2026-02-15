rules_meta:
  engine: "post_extraction_normalizer"
  default_source_precedence: ["label", "shop_structured", "shop_text", "notes", "vision"]
  default_conflict_strategy: "prefer_higher_source_precedence"
  default_language: "de"
  notes:
    - "Regeln dürfen Felder setzen, überschreiben, Kandidaten entfernen oder Konfidenzen anpassen."
    - "Regeln referenzieren Attribute/Value-Sets aus Part 04 sowie Typen/Kategorien aus Part 02/03."

rules:

  # =========================================================
  # A) HARD GUARDS: NIE ALS MARKE INTERPRETIEREN
  # =========================================================

  - id: rule_0001
    name: "Guard: Kragenformen niemals als Marke"
    priority: 100
    scope:
      fields: [attr_brand]
    match:
      tokens_any:
        - "Kent" - "Kentkragen" - "Global Kent" - "New Kent"
        - "Haifisch" - "Spread" - "Button-Down" - "Button Down"
        - "Stehkragen" - "Mandarin" - "Polokragen" - "Camp Collar" - "Reverskragen"
    actions:
      - op: remove_candidate
        field: attr_brand
        value_from_match: true
      - op: add_debug
        message: "Removed collar tokens from brand candidates."
    examples:
      - input: "OLYMP Luxor Modern Fit Global Kent"
        expected: "attr_brand=OLYMP; attr_collar_type=global_kent"

  - id: rule_0002
    name: "Guard: Passformen niemals als Marke"
    priority: 100
    scope:
      fields: [attr_brand]
    match:
      tokens_any:
        - "Slim Fit" - "Regular Fit" - "Modern Fit" - "Comfort Fit"
        - "Oversized" - "Relaxed Fit" - "Athletic Fit"
        - "Skinny" - "Straight" - "Wide Leg" - "Bootcut" - "Flared" - "Tapered"
    actions:
      - op: remove_candidate
        field: attr_brand
        value_from_match: true
      - op: add_debug
        message: "Removed fit/cut tokens from brand candidates."

  - id: rule_0003
    name: "Guard: Materialbegriffe niemals als Marke"
    priority: 98
    scope:
      fields: [attr_brand]
    match:
      tokens_any:
        - "Baumwolle" - "Cotton" - "Schurwolle" - "Wolle" - "Merino"
        - "Seide" - "Leinen" - "Kaschmir" - "Viskose" - "Lyocell" - "Modal"
        - "Polyester" - "Polyamid" - "Elasthan" - "Acryl"
        - "Leder" - "Veloursleder" - "Nubuk" - "Kunstleder" - "PU"
        - "Denim" - "Jeans" - "Cord" - "Twill" - "Jersey" - "Fleece"
    actions:
      - op: remove_candidate
        field: attr_brand
        value_from_match: true

  - id: rule_0004
    name: "Guard: Shop-Namen niemals als Marke (außer definierte Eigenmarken)"
    priority: 98
    scope:
      fields: [attr_brand]
    match:
      tokens_any: ["Zalando", "OTTO", "bonprix", "Amazon", "About You"]
    actions:
      - op: remove_candidate
        field: attr_brand
        value_from_match: true
      - op: add_debug
        message: "Removed shop tokens from brand candidates (marketplaces/retailers)."

  # =========================================================
  # B) BRAND & SHOP NORMALIZATION (BASISREGELN)
  # =========================================================

  - id: rule_0101
    name: "Shop aus URL-Domain normalisieren"
    priority: 95
    scope:
      fields: [attr_shop, attr_url]
    match:
      regex_any:
        - "(?i)https?://([^/]+)"
    actions:
      - op: normalize_shop_from_domain
        source_field: attr_url
        domain_map:
          "zalando.": "Zalando"
          "otto.": "OTTO"
          "amazon.": "Amazon"
          "bonprix.": "bonprix"
          "hessnatur.": "hessnatur"
          "aboutyou.": "ABOUT YOU"
          "adidas.": "adidas"
          "boss.": "BOSS"
      - op: add_debug
        message: "Normalized shop from URL domain."

  - id: rule_0102
    name: "Eigenmarken: Amazon Essentials, Zalando Essentials korrekt als Brand"
    priority: 94
    scope:
      fields: [attr_brand, attr_shop]
    match:
      regex_any:
        - "(?i)amazon\\s+essentials"
        - "(?i)zalando\\s+essentials"
        - "(?i)about\\s+you\\s+essentials"
    actions:
      - op: set
        field: attr_brand
        value_from_match: true
      - op: normalize_brand
        field: attr_brand
        canonical_map:
          "amazon essentials": "Amazon Essentials"
          "zalando essentials": "Zalando Essentials"
          "about you essentials": "ABOUT YOU Essentials"
      - op: add_debug
        message: "Detected retailer private-label brand."

  - id: rule_0103
    name: "BOSS/HUGO BOSS Normalisierung"
    priority: 92
    scope:
      fields: [attr_brand]
    match:
      regex_any:
        - "(?i)\\bhugo\\s+boss\\b"
        - "(?i)\\bboss\\b"
    actions:
      - op: normalize_brand
        field: attr_brand
        canonical_map:
          "hugo boss": "HUGO BOSS"
          "boss": "BOSS"

  - id: rule_0104
    name: "OLYMP/ETERNA immer Brand (wenn als Token vorhanden)"
    priority: 92
    scope:
      fields: [attr_brand]
    match:
      regex_any:
        - "(?i)\\bolymp\\b"
        - "(?i)\\beterna\\b"
    actions:
      - op: set_if_empty
        field: attr_brand
        value_from_match: true
      - op: normalize_brand
        field: attr_brand
        canonical_map:
          "olymp": "OLYMP"
          "eterna": "ETERNA"

  - id: rule_0105
    name: "Marke darf nicht gleich Shop sein (Fallback)"
    priority: 90
    scope:
      fields: [attr_brand, attr_shop]
    match:
      always: true
    conditions:
      if_equals:
        - [attr_brand, attr_shop]
    actions:
      - op: unset
        field: attr_brand
      - op: add_debug
        message: "Brand identical to shop; removed brand (unless private-label rule fired)."

  # =========================================================
  # C) KRAGEN / FIT / SCHNITT: KONKRETE ZUORDNUNG
  # =========================================================

  - id: rule_0201
    name: "Global Kent → collar_type"
    priority: 89
    scope:
      fields: [attr_collar_type, attr_brand]
    match:
      regex_any: ["(?i)global\\s*-?\\s*kent"]
    actions:
      - op: set
        field: attr_collar_type
        value: global_kent
      - op: remove_candidate
        field: attr_brand
        value: "Global Kent"

  - id: rule_0202
    name: "New Kent → collar_type"
    priority: 88
    scope:
      fields: [attr_collar_type]
    match:
      regex_any: ["(?i)new\\s*-?\\s*kent"]
    actions:
      - op: set
        field: attr_collar_type
        value: new_kent

  - id: rule_0203
    name: "Kent/Kentkragen → collar_type"
    priority: 87
    scope:
      fields: [attr_collar_type]
    match:
      regex_any: ["(?i)kent(\\s*kragen)?"]
    conditions:
      any_of:
        - item_type_in: [it_shirt_dress, it_blouse]
        - category_in: [cat_tops_shirts_blouses]
    actions:
      - op: set_if_empty
        field: attr_collar_type
        value: kent

  - id: rule_0204
    name: "Haifisch/Spread → collar_type"
    priority: 87
    scope:
      fields: [attr_collar_type]
    match:
      regex_any: ["(?i)haifisch", "(?i)\\bspread\\b"]
    conditions:
      any_of:
        - item_type_in: [it_shirt_dress, it_blouse]
        - category_in: [cat_tops_shirts_blouses]
    actions:
      - op: set
        field: attr_collar_type
        value: spread_haifisch

  - id: rule_0205
    name: "Button-Down → collar_type"
    priority: 87
    scope:
      fields: [attr_collar_type]
    match:
      regex_any: ["(?i)button\\s*-?\\s*down"]
    conditions:
      any_of:
        - item_type_in: [it_shirt_dress]
        - category_in: [cat_tops_shirts_blouses]
    actions:
      - op: set
        field: attr_collar_type
        value: button_down

  - id: rule_0206
    name: "Stehkragen/Mandarin → collar_type"
    priority: 86
    scope:
      fields: [attr_collar_type]
    match:
      regex_any: ["(?i)stehkragen", "(?i)mandarin"]
    actions:
      - op: set
        field: attr_collar_type
        value: mandarin

  - id: rule_0210
    name: "Fit tokens → attr_fit_type (kontrolliert)"
    priority: 85
    scope:
      fields: [attr_fit_type]
    match:
      regex_any:
        - "(?i)\\bsuper\\s*slim\\b|\\bbody\\s*fit\\b"
        - "(?i)\\bslim\\s*fit\\b"
        - "(?i)\\bmodern\\s*fit\\b"
        - "(?i)\\bregular\\s*fit\\b"
        - "(?i)\\bcomfort\\s*fit\\b"
        - "(?i)\\bover\\s*sized\\b|\\boversized\\b"
        - "(?i)\\brelaxed\\s*fit\\b"
        - "(?i)\\bathletic\\s*fit\\b"
    actions:
      - op: map_regex_to_enum
        target_field: attr_fit_type
        mapping:
          "(?i)super\\s*slim|body\\s*fit": super_slim
          "(?i)slim\\s*fit": slim
          "(?i)modern\\s*fit": modern
          "(?i)regular\\s*fit": regular
          "(?i)comfort\\s*fit": comfort
          "(?i)oversized|over\\s*sized": oversized
          "(?i)relaxed\\s*fit": relaxed
          "(?i)athletic\\s*fit": athletic

  - id: rule_0211
    name: "Beinform tokens → attr_leg_shape"
    priority: 84
    scope:
      fields: [attr_leg_shape]
    match:
      regex_any:
        - "(?i)\\bskinny\\b"
        - "(?i)\\bstraight\\b|\\bgerade\\b"
        - "(?i)\\btapered\\b|\\bzulaufend\\b"
        - "(?i)\\bwide\\s*leg\\b|\\bweit\\b"
        - "(?i)\\bbootcut\\b"
        - "(?i)\\bflared\\b|\\bschlag\\b"
    conditions:
      category_in: [cat_bottoms_trousers_jeans, cat_bottoms_skirts, cat_bottoms_shorts]
    actions:
      - op: map_regex_to_enum
        target_field: attr_leg_shape
        mapping:
          "(?i)skinny": skinny
          "(?i)straight|gerade": straight
          "(?i)tapered|zulaufend": tapered
          "(?i)wide\\s*leg|weit": wide
          "(?i)bootcut": bootcut
          "(?i)flared|schlag": flared

  # =========================================================
  # D) GRÖSSEN-DISAMBIGUATION (42 ist NICHT immer EU-Konfektion)
  # =========================================================

  - id: rule_0301
    name: "W/L (W32/L34) → size_system=waist_inseam"
    priority: 83
    scope:
      fields: [attr_size_system, attr_size_label_raw, attr_size_normalized]
    match:
      regex_any:
        - "(?i)\\bW\\s*\\d{2}\\s*/\\s*L\\s*\\d{2}\\b"
        - "(?i)\\bW\\d{2}\\s*L\\d{2}\\b"
    actions:
      - op: set
        field: attr_size_system
        value: waist_inseam
      - op: normalize_size_wl
        source_field: attr_size_label_raw
        target_field: attr_size_normalized
      - op: add_debug
        message: "Detected W/L sizing."

  - id: rule_0302
    name: "One Size/OS → size_system=one_size"
    priority: 83
    scope:
      fields: [attr_size_system, attr_size_normalized]
    match:
      regex_any: ["(?i)\\bone\\s*size\\b", "(?i)\\bOS\\b", "(?i)einheitsgr(o|ö)ße"]
    actions:
      - op: set
        field: attr_size_system
        value: one_size
      - op: set
        field: attr_size_normalized
        value: one_size

  - id: rule_0303
    name: "Kindergröße (z.B. 116/128) → size_system=kids"
    priority: 82
    scope:
      fields: [attr_size_system, attr_size_label_raw, attr_size_normalized]
    match:
      regex_any: ["(?i)\\b(\\d{3})\\b"]
    conditions:
      all_of:
        - category_in: [cat_kids]
        - regex_capture_range:
            group: 1
            min: 80
            max: 176
    actions:
      - op: set
        field: attr_size_system
        value: kids
      - op: normalize_size_kids_height_cm
        source_field: attr_size_label_raw
        target_field: attr_size_normalized

  - id: rule_0304
    name: "Schuhgröße EU (Kontext footwear) → size_system=shoe_eu"
    priority: 82
    scope:
      fields: [attr_size_system, attr_size_label_raw, attr_size_normalized]
    match:
      regex_any: ["(?i)\\b(3[4-9]|4[0-9]|5[0-1])\\b", "(?i)\\bEU\\s*(3[4-9]|4[0-9]|5[0-1])\\b"]
    conditions:
      category_in: [cat_footwear]
    actions:
      - op: set
        field: attr_size_system
        value: shoe_eu
      - op: normalize_size_shoe_eu
        source_field: attr_size_label_raw
        target_field: attr_size_normalized

  - id: rule_0305
    name: "Schuhgröße UK/US explizit → size_system=shoe_uk|shoe_us"
    priority: 82
    scope:
      fields: [attr_size_system, attr_size_label_raw, attr_size_normalized]
    match:
      regex_any:
        - "(?i)\\bUK\\s*\\d{1,2}(\\.5)?\\b"
        - "(?i)\\bUS\\s*\\d{1,2}(\\.5)?\\b"
    actions:
      - op: normalize_shoe_uk_us
        source_field: attr_size_label_raw
        target_fields:
          size_system: attr_size_system
          normalized: attr_size_normalized

  - id: rule_0306
    name: "EU-Konfektionsgröße (Kontext Kleidung, nicht footwear) → numeric_eu"
    priority: 81
    scope:
      fields: [attr_size_system, attr_size_label_raw, attr_size_normalized]
    match:
      regex_any: ["(?i)\\b(3[0-9]|4[0-9]|5[0-8])\\b"]
    conditions:
      not_category_in: [cat_footwear]
    actions:
      - op: set_if_empty
        field: attr_size_system
        value: numeric_eu
      - op: normalize_size_eu_numeric
        source_field: attr_size_label_raw
        target_field: attr_size_normalized

  - id: rule_0307
    name: "Alpha sizes (S/M/L/XL/XXL) → size_system=alpha"
    priority: 81
    scope:
      fields: [attr_size_system, attr_size_label_raw, attr_size_normalized]
    match:
      regex_any: ["(?i)\\b(XXXL|XXL|XL|L|M|S|XS)\\b"]
    actions:
      - op: set
        field: attr_size_system
        value: alpha
      - op: normalize_size_alpha
        source_field: attr_size_label_raw
        target_field: attr_size_normalized

  - id: rule_0308
    name: "Hemd/Bluse: 39/40 oder 41/42 etc. als Halsweite in cm speichern"
    priority: 80
    scope:
      fields: [attr_body_measurements_cm, attr_size_system]
    match:
      regex_any: ["(?i)\\b(3\\d|4\\d)\\s*/\\s*(3\\d|4\\d)\\b"]
    conditions:
      category_in: [cat_tops_shirts_blouses]
    actions:
      - op: set_in_object_avg
        field: attr_body_measurements_cm
        key: neck
        from_regex_groups: [1, 2]
      - op: set_if_empty
        field: attr_size_system
        value: numeric_eu
      - op: add_debug
        message: "Interpreted 39/40 style as collar circumference range; stored avg in body_measurements_cm.neck."

  # =========================================================
  # E) MATERIAL & KOMPOSITION: ABBREVIATIONS, LEDER VS. KUNSTLEDER, etc.
  # =========================================================

  - id: rule_0401
    name: "Material-Abkürzungen normalisieren (PES/PA/EL/CO/WO/VI/LI/SE)"
    priority: 79
    scope:
      fields: [attr_material_composition, attr_material_main]
    match:
      regex_any:
        - "(?i)\\bPES\\b|\\bPA\\b|\\bEL\\b|\\bEA\\b|\\bCO\\b|\\bWO\\b|\\bWV\\b|\\bVI\\b|\\bCV\\b|\\bLI\\b|\\bSE\\b"
    actions:
      - op: expand_material_abbreviations_in_text
        source_fields: [attr_material_composition, attr_care_instructions_text]
        abbreviation_map:
          "PES": "Polyester"
          "PA": "Polyamid"
          "EL": "Elasthan"
          "EA": "Elasthan"
          "CO": "Baumwolle"
          "WO": "Wolle"
          "WV": "Schurwolle"
          "VI": "Viskose"
          "CV": "Viskose"
          "LI": "Leinen"
          "SE": "Seide"

  - id: rule_0402
    name: "Kunstleder/PU/Vegan Leather → nicht als echtes Leder klassifizieren"
    priority: 78
    scope:
      fields: [attr_material_main, attr_upper_material]
    match:
      regex_any:
        - "(?i)kunstleder"
        - "(?i)\\bPU\\b"
        - "(?i)vegan\\s+leather"
        - "(?i)synthetikleder"
    actions:
      - op: set_prefer_existing
        field: attr_material_main
        value: "Kunstleder/PU"
      - op: set_prefer_existing
        field: attr_upper_material
        value: "Synthetik/Kunstleder"
      - op: add_debug
        message: "Detected synthetic leather; avoid mapping to genuine leather."

  - id: rule_0403
    name: "Glattleder/Velours/Nubuk → upper_material (Schuhe) bevorzugen"
    priority: 77
    scope:
      fields: [attr_upper_material, attr_material_main]
    match:
      regex_any:
        - "(?i)glattleder|full\\s*grain"
        - "(?i)velours|suede"
        - "(?i)nubuk|nubuck"
    conditions:
      category_in: [cat_footwear]
    actions:
      - op: map_regex_to_string
        target_field: attr_upper_material
        mapping:
          "(?i)glattleder|full\\s*grain": "Glattleder"
          "(?i)velours|suede": "Veloursleder"
          "(?i)nubuk|nubuck": "Nubukleder"

  - id: rule_0404
    name: "Futter-Hinweise → lining_material"
    priority: 76
    scope:
      fields: [attr_lining_material]
    match:
      regex_any:
        - "(?i)futter\\s*:\\s*([A-Za-zÄÖÜäöüß\\-/ ]+)"
        - "(?i)lining\\s*:\\s*([A-Za-z\\-/ ]+)"
    actions:
      - op: extract_after_label
        target_field: attr_lining_material
        labels_any: ["Futter:", "Innenfutter:", "Lining:"]

  # =========================================================
  # F) FUNKTIONSANGABEN: WASSERDICHT vs. WASSERABWEISEND (DWR)
  # =========================================================

  - id: rule_0501
    name: "Wasserabweisend/DWR ≠ wasserdicht → waterproof=false (wenn fälschlich true)"
    priority: 75
    scope:
      fields: [attr_function_waterproof, attr_longevity_notes]
    match:
      regex_any:
        - "(?i)wasserabweisend"
        - "(?i)water[- ]repellent"
        - "(?i)\\bDWR\\b"
    actions:
      - op: set
        field: attr_function_waterproof
        value: false
      - op: append_text
        field: attr_longevity_notes
        value: "Hinweis: wasserabweisend (z.B. DWR) ist nicht gleich wasserdicht."
      - op: add_debug
        message: "Corrected waterproof confusion: water-repellent/DWR."

  - id: rule_0502
    name: "Wasserdicht/Waterproof explizit → waterproof=true"
    priority: 74
    scope:
      fields: [attr_function_waterproof]
    match:
      regex_any: ["(?i)\\bwasserdicht\\b", "(?i)\\bwaterproof\\b"]
    actions:
      - op: set
        field: attr_function_waterproof
        value: true

  - id: rule_0503
    name: "Winddicht/Atmungsaktiv → entsprechende Flags"
    priority: 74
    scope:
      fields: [attr_function_windproof, attr_function_breathable]
    match:
      regex_any: ["(?i)winddicht|windproof", "(?i)atmungsaktiv|breathable"]
    actions:
      - op: set_if_match
        field: attr_function_windproof
        regex: "(?i)winddicht|windproof"
        value: true
      - op: set_if_match
        field: attr_function_breathable
        regex: "(?i)atmungsaktiv|breathable"
        value: true

  # =========================================================
  # G) PFLEGE: NUR MIT EXISTIERENDEN ATTRIBUTEN (Part 04)
  # =========================================================

  - id: rule_0601
    name: "Chemische Reinigung / Dry clean only → dry_clean_only=true"
    priority: 73
    scope:
      fields: [attr_dry_clean_only]
    match:
      regex_any: ["(?i)chemische\\s+reinigung", "(?i)dry\\s+clean\\s+only"]
    actions:
      - op: set
        field: attr_dry_clean_only
        value: true

  - id: rule_0602
    name: "Nicht bügeln / Do not iron → iron_allowed=false"
    priority: 73
    scope:
      fields: [attr_iron_allowed]
    match:
      regex_any: ["(?i)nicht\\s*b(ü|ue)geln", "(?i)do\\s+not\\s+iron"]
    actions:
      - op: set
        field: attr_iron_allowed
        value: false

  - id: rule_0603
    name: "Nicht trocknergeeignet / Do not tumble dry → tumble_dry_allowed=false"
    priority: 73
    scope:
      fields: [attr_tumble_dry_allowed]
    match:
      regex_any: ["(?i)nicht\\s*trockner", "(?i)do\\s+not\\s+tumble\\s+dry"]
    actions:
      - op: set
        field: attr_tumble_dry_allowed
        value: false

  - id: rule_0604
    name: "Bügelfrei/Easy Iron ist KEINE Marke; nur in care_text notieren"
    priority: 72
    scope:
      fields: [attr_brand, attr_care_instructions_text]
    match:
      regex_any: ["(?i)b(ü|ue)gelfrei", "(?i)non\\s*iron", "(?i)easy\\s*iron"]
    actions:
      - op: remove_candidate
        field: attr_brand
        value_from_match: true
      - op: append_text
        field: attr_care_instructions_text
        value_from_match: true

  # =========================================================
  # H) FARBE & MUSTER: VISION-HALLUZINATIONEN (Pailletten, Metallic, Reflexion)
  # =========================================================

  - id: rule_0701
    name: "Pailletten/Sequins/Glitzer → Farbkonfidenz deckeln, multicolor möglich"
    priority: 71
    scope:
      fields: [attr_color_confidence, attr_multicolor_flag, attr_color_family]
    match:
      regex_any: ["(?i)pailletten", "(?i)sequins", "(?i)glitzer"]
    actions:
      - op: clamp_max
        field: attr_color_confidence
        max: 0.5
      - op: set_if_empty
        field: attr_color_family
        value: metallic
      - op: set_if_source
        field: attr_multicolor_flag
        source: vision
        value: true
      - op: add_debug
        message: "Sequins/glitter: reduce color confidence; may appear multicolor in vision."

  - id: rule_0702
    name: "Metallic-Familie: wenn 'silber/gold/metallic' im Text"
    priority: 70
    scope:
      fields: [attr_color_family]
    match:
      regex_any: ["(?i)\\bmetallic\\b", "(?i)\\bsilber\\b", "(?i)\\bgold\\b"]
    actions:
      - op: set
        field: attr_color_family
        value: metallic

  - id: rule_0703
    name: "Used/Washed/Destroy als Muster (Denim-Kontext)"
    priority: 69
    scope:
      fields: [attr_pattern]
    match:
      regex_any: ["(?i)\\bused\\b", "(?i)washed", "(?i)destroyed", "(?i)stone\\s*wash"]
    conditions:
      any_of:
        - regex_any_in_title: ["(?i)denim", "(?i)jeans"]
        - category_in: [cat_bottoms_trousers_jeans]
    actions:
      - op: set
        field: attr_pattern
        value: used

  - id: rule_0704
    name: "Meliert/Melange → Muster melange"
    priority: 69
    scope:
      fields: [attr_pattern]
    match:
      regex_any: ["(?i)meliert", "(?i)melange"]
    actions:
      - op: set
        field: attr_pattern
        value: melange

  # =========================================================
  # I) FOOTWEAR-SPEZIAL: 'Oxford' ist Schuh ODER Hemdstoff → Kontextregeln
  # =========================================================

  - id: rule_0801
    name: "Oxford im Schuh-Kontext → closure_type=lace (Oxford/Derby-Familie) und NICHT als Hemd-Variante"
    priority: 68
    scope:
      fields: [attr_closure_type, attr_model_name]
    match:
      regex_any: ["(?i)\\boxford\\b"]
    conditions:
      any_of:
        - category_in: [cat_footwear]
        - regex_any_in_title: ["(?i)schuh", "(?i)lace", "(?i)schn(ü|ue)r"]
    actions:
      - op: set_if_empty
        field: attr_closure_type
        value: lace
      - op: add_debug
        message: "Oxford detected in footwear context."

  - id: rule_0802
    name: "Oxford im Hemd-Kontext → NICHT als Schuh interpretieren"
    priority: 68
    scope:
      fields: [attr_closure_type]
    match:
      regex_any: ["(?i)\\boxford\\b"]
    conditions:
      any_of:
        - category_in: [cat_tops_shirts_blouses]
        - regex_any_in_title: ["(?i)hemd", "(?i)shirt", "(?i)bluse"]
    actions:
      - op: unset_if_source
        field: attr_closure_type
        source: vision
      - op: add_debug
        message: "Oxford detected in shirt context; avoided footwear inference."

  - id: rule_0803
    name: "Derby im Schuh-Kontext → closure_type=lace"
    priority: 67
    scope:
      fields: [attr_closure_type]
    match:
      regex_any: ["(?i)\\bderby\\b"]
    conditions:
      category_in: [cat_footwear]
    actions:
      - op: set_if_empty
        field: attr_closure_type
        value: lace

  - id: rule_0804
    name: "Slip-on/Loafer/Schlupfschuh → closure_type=slip_on"
    priority: 67
    scope:
      fields: [attr_closure_type]
    match:
      regex_any: ["(?i)slip\\s*-?\\s*on", "(?i)loafer", "(?i)schlupf"]
    conditions:
      category_in: [cat_footwear]
    actions:
      - op: set
        field: attr_closure_type
        value: slip_on

  - id: rule_0805
    name: "Klett/Velcro → closure_type=velcro"
    priority: 66
    scope:
      fields: [attr_closure_type]
    match:
      regex_any: ["(?i)klett", "(?i)velcro"]
    actions:
      - op: set
        field: attr_closure_type
        value: velcro

  # =========================================================
  # J) UHR/ACCESSOIRE-SPEZIAL: '5 ATM' gehört in water_resistance (Uhr)
  # =========================================================

  - id: rule_0901
    name: "Uhr: Wasserdichtigkeit (ATM/bar/m) → attr_water_resistance"
    priority: 65
    scope:
      fields: [attr_water_resistance]
    match:
      regex_any:
        - "(?i)\\b\\d{1,2}\\s*ATM\\b"
        - "(?i)\\b\\d{1,2}\\s*bar\\b"
        - "(?i)\\b\\d{2,3}\\s*m\\b"
    conditions:
      any_of:
        - item_type_in: [it_watch]
        - category_in: [cat_accessories_watches]
    actions:
      - op: extract_first_match
        target_field: attr_water_resistance
        from_fields: ["raw_text", "title", "description"]

  # =========================================================
  # K) FINAL SAFETY: BRAND-KANDIDATEN VALIDIEREN (Fallback-Heuristik)
  # =========================================================

  - id: rule_0991
    name: "Brand-Candidate Cleanup: wenn brand nur aus Attribut-/Material-/Größenwort besteht → unset"
    priority: 10
    scope:
      fields: [attr_brand]
    match:
      always: true
    conditions:
      brand_in_blacklist_tokens:
        - "Kent" - "Global Kent" - "New Kent"
        - "Slim" - "Regular" - "Modern" - "Comfort" - "Oversized"
        - "Baumwolle" - "Wolle" - "Polyester" - "Viskose" - "Leinen" - "Seide"
        - "S" - "M" - "L" - "XL" - "XXL"
    actions:
      - op: unset
        field: attr_brand
      - op: add_debug
        message: "Brand invalid after cleanup blacklist."

  - id: rule_0992
    name: "Wenn Pflichtattribute fehlen: nur Debug-Hinweis (keine Halluzination)"
    priority: 1
    scope:
      fields: []
    match:
      always: true
    actions:
      - op: add_debug_if_missing_required
        message: "Missing required attributes for item_type; do not invent values."
