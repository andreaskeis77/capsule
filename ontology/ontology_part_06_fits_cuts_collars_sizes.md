<!-- FILE: ontology_part_06_fits_cuts_collars_sizes.md -->
# Part 06 – Fits/Cuts, Kragen, Größen-Systeme & Normalisierung (präzise, RAG-tauglich)
version: "1.0.0"
date: "2026-01-13"
scope: "Fit/Cut-Lexikon + Kragen/Manschetten-Detaillexikon + robuste Größen-Normalisierung inkl. Hemd-Kragenweite & Sonderarmlängen"
toc:
  - intent_and_design_principles
  - value_set_extensions_recommended
  - fit_cut_lexicon
  - collar_cuff_neckline_detail_lexicon
  - size_systems_and_normalization_playbook
  - disambiguation_rules_high_impact
  - schema_patch_recommended

```yaml
intent_and_design_principles:
  goals:
    - "Extraktion stabilisieren: Begriffe wie 'Global Kent' immer als Kragenform (attr_collar_type), nie als Marke (attr_brand)."
    - "Größen-Ambiguitäten reduzieren: '39/40' bei Hemden ist Kragenweite/Halsumfang (cm), NICHT Konfektionsgröße."
    - "RAG-freundlich: Alles ist als klare Listen/Objekte strukturiert und leicht nach JSON zu überführen."
    - "Regel-basiert + tolerant: Raw-Werte nie verlieren; Normalisierung nur, wenn Kontext/Pattern robust."
  invariants:
    - "attr_size_label_raw wird immer befüllt, wenn irgendeine Größe in der Quelle steht."
    - "attr_size_system wird gesetzt, sobald das System eindeutig ist; sonst 'other' und nur raw speichern."
    - "Mehrdimensionale Größen (z. B. Hemd: Kragenweite + Ärmellänge + ggf. alpha) sollen getrennt gespeichert werden (siehe schema_patch)."

# ------------------------------------------------------------
# (A) VALUE-SET EXTENSIONS (für Part 04 übernehmen)
# ------------------------------------------------------------
value_set_extensions_recommended:
  vs_size_system:
    add_values:
      - value: shirt_collar_cm
        synonyms_de: ["Kragenweite", "Halsweite", "Halsumfang", "collar size"]
        notes_de: "Hemd/Bluse: Kragenweite in cm, oft als 37/38, 39/40 etc."
      - value: shirt_sleeve_variant
        synonyms_de: ["Extra langer Arm", "Extra kurzer Arm", "Super-Extra langer Arm"]
        notes_de: "Nicht die generische Ärmel-Länge (Kurzarm/Langarm), sondern Sonderlängen-Variante."
      - value: bra_band_cup
        synonyms_de: ["75B", "80C", "band/cup"]
        notes_de: "BH: Unterbrustzahl + Cup-Buchstabe."
      - value: belt_length_cm
        synonyms_de: ["Gürtel 90", "Belt 95 cm"]
        notes_de: "Gürtel-Länge in cm; stark kontextabhängig."
      - value: hat_circumference_cm
        synonyms_de: ["Mütze 58", "Hutgröße 56"]
        notes_de: "Kopfumfang/ Hutgröße in cm."
      - value: gloves_numeric
        synonyms_de: ["Handschuhgröße 7", "8.5", "9"]
        notes_de: "Handschuhe oft numerisch (europäisch), ohne Bezug zu Konfektionsgrößen."
      - value: shoe_mondopoint_mm
        synonyms_de: ["Mondopoint", "280/110"]
        notes_de: "Schuhe nach Fußlänge/-breite in mm (ISO Mondopoint)."
      - value: ring_size
        synonyms_de: ["Ringgröße 56", "Ring size"]
        notes_de: "Schmuck, optional."
      - value: other
        synonyms_de: ["unklar", "freitext"]
        notes_de: "Fallback, wenn System nicht eindeutig."

  vs_leg_shape:
    add_values:
      - value: barrel
        synonyms_de: ["Barrel Leg", "Tonnenform"]
        notes_de: "Weit an Hüfte/Oberschenkel, zum Saum wieder enger."
      - value: carrot
        synonyms_de: ["Carrot", "Karotte"]
        notes_de: "Oben weiter, stark zulaufend."
      - value: culotte
        synonyms_de: ["Culotte"]
        notes_de: "Weit & oft wadenlang (Länge separat)."
      - value: jogger
        synonyms_de: ["Jogger", "Cuff pant", "Bündchenhose"]
        notes_de: "Bündchen am Saum, sportlich."
      - value: boyfriend
        synonyms_de: ["Boyfriend"]
        notes_de: "Locker, hüftig."
      - value: mom
        synonyms_de: ["Mom Jeans", "Mom"]
        notes_de: "Hohe Taille + lockerer Sitz; Leg-Shape meist tapered/straight."
    notes_de: "Wenn ihr Enums strikt halten wollt: erst übernehmen, wenn in eurer Datenbasis relevant."

  vs_collar_type:
    add_values:
      - value: grandad_band
        synonyms_de: ["Grandad", "Band collar", "Stehkragen (Hemd, ohne Umschlag)"]
        notes_de: "Achtung: 'Stehkragen' wird oft auch für Mandarin genutzt."
      - value: wing_tip
        synonyms_de: ["Kläppchenkragen", "Wing collar"]
        notes_de: "Festlich/Smoking."
      - value: club
        synonyms_de: ["Clubkragen", "Rounded collar"]
        notes_de: "Abgerundete Kragenspitzen."
      - value: tab
        synonyms_de: ["Tabkragen", "Tab collar"]
        notes_de: "Mit Lasche; meist mit Krawatte."
      - value: pin
        synonyms_de: ["Pinnkragen", "Pin collar"]
        notes_de: "Mit Kragennadel."
      - value: hidden_button_down
        synonyms_de: ["Hidden Button-Down", "verdeckter Button-Down"]
        notes_de: "Buttons unter Kragen verdeckt."
      - value: tuxedo_bib
        synonyms_de: ["Smokinghemd (Plastron/Bib)"]
        notes_de: "Eher Feature/Front—nur setzen, wenn explizit im Text."
    notes_de: "Global Kent, New Kent, Kent, Haifisch/Spread, Button-Down, Cutaway, Mandarin, Polo, Camp existieren bereits (Part 04)."

  vs_cuff_type:
    add_values:
      - value: barrel
        synonyms_de: ["Knopfmanschette", "Barrel cuff"]
        notes_de: "Standard-Knopfmanschette; wenn ihr 'sport' als Standard nutzt, könnt ihr das mappen."
      - value: naples
        synonyms_de: ["Neapolitan cuff"]
        notes_de: "Selten; optional."

  vs_sleeve_length:
    notes_de: "Kurzarm/Langarm/3-4/ärmellos ist ok. Sonderlängen bitte über neues Attribut/Value-Set (siehe schema_patch) abbilden."

# ------------------------------------------------------------
# (B) FIT/CUT LEXIKON
# - Jede Einheit mappt sauber auf bestehende Attribute/Enums.
# - Wo das Enum (noch) nicht existiert: note + empfohlenes Enum in extensions.
# ------------------------------------------------------------
fit_cut_lexicon:
  # ---------- General fit ----------
  - id: fc_fit_super_slim
    domain: general_fit
    label_de: "Super Slim / Body Fit"
    synonyms_de: ["extra slim", "body fit", "super slim fit"]
    maps_to:
      attribute: attr_fit_type
      enum: vs_fit_type.super_slim
    description_de: "Sehr körpernah, oft bei Businesshemden/Anzügen als modische Linie."
    conflicts_with: ["fc_fit_oversized", "fc_fit_comfort"]

  - id: fc_fit_slim
    domain: general_fit
    label_de: "Slim Fit"
    synonyms_de: ["schmal", "körpernah", "tailliert"]
    maps_to:
      attribute: attr_fit_type
      enum: vs_fit_type.slim
    description_de: "Körpernah, aber weniger extrem als Super Slim."
    conflicts_with: ["fc_fit_oversized", "fc_fit_comfort"]

  - id: fc_fit_modern
    domain: general_fit
    label_de: "Modern Fit"
    synonyms_de: ["moderne Passform"]
    maps_to:
      attribute: attr_fit_type
      enum: vs_fit_type.modern
    description_de: "Zwischen Slim und Regular; häufig in Business-Sortimenten."
    conflicts_with: ["fc_fit_oversized"]

  - id: fc_fit_regular
    domain: general_fit
    label_de: "Regular Fit"
    synonyms_de: ["klassisch", "normal"]
    maps_to:
      attribute: attr_fit_type
      enum: vs_fit_type.regular
    description_de: "Klassischer Standardschnitt."
    conflicts_with: []

  - id: fc_fit_comfort
    domain: general_fit
    label_de: "Comfort Fit"
    synonyms_de: ["bequem", "weit", "comfort"]
    maps_to:
      attribute: attr_fit_type
      enum: vs_fit_type.comfort
    description_de: "Mehr Weite, besonders im Brust-/Taillenbereich."
    conflicts_with: ["fc_fit_slim", "fc_fit_super_slim"]

  - id: fc_fit_relaxed
    domain: general_fit
    label_de: "Relaxed Fit"
    synonyms_de: ["relaxed"]
    maps_to:
      attribute: attr_fit_type
      enum: vs_fit_type.relaxed
    description_de: "Locker, aber nicht bewusst oversized."
    conflicts_with: ["fc_fit_super_slim"]

  - id: fc_fit_oversized
    domain: general_fit
    label_de: "Oversized"
    synonyms_de: ["loose", "extra weit", "boxy (oft)"]
    maps_to:
      attribute: attr_fit_type
      enum: vs_fit_type.oversized
    description_de: "Bewusst groß/locker geschnitten."
    conflicts_with: ["fc_fit_slim", "fc_fit_super_slim"]

  - id: fc_fit_athletic
    domain: general_fit
    label_de: "Athletic Fit"
    synonyms_de: ["athletic", "für Sportler"]
    maps_to:
      attribute: attr_fit_type
      enum: vs_fit_type.athletic
    description_de: "Mehr Raum an Brust/Oberschenkel; Taille oft moderat."
    conflicts_with: ["fc_fit_super_slim"]

  # ---------- Pants: leg shape ----------
  - id: fc_pants_skinny
    domain: pants
    label_de: "Skinny"
    synonyms_de: ["sehr eng", "skinny fit"]
    maps_to:
      attribute: attr_leg_shape
      enum: vs_leg_shape.skinny
    description_de: "Eng über Oberschenkel und Wade."
    conflicts_with: ["fc_pants_wide_leg", "fc_pants_flared", "fc_pants_bootcut"]

  - id: fc_pants_slim
    domain: pants
    label_de: "Slim"
    synonyms_de: ["slim leg"]
    maps_to:
      attribute: attr_leg_shape
      enum: vs_leg_shape.slim
    description_de: "Schmal, aber nicht hauteng."
    conflicts_with: ["fc_pants_wide_leg"]

  - id: fc_pants_straight
    domain: pants
    label_de: "Straight"
    synonyms_de: ["gerades Bein"]
    maps_to:
      attribute: attr_leg_shape
      enum: vs_leg_shape.straight
    description_de: "Gleichmäßige Weite vom Oberschenkel bis Saum."
    conflicts_with: []

  - id: fc_pants_tapered
    domain: pants
    label_de: "Tapered"
    synonyms_de: ["zulaufend"]
    maps_to:
      attribute: attr_leg_shape
      enum: vs_leg_shape.tapered
    description_de: "Oben mehr Raum, nach unten schmaler."
    conflicts_with: ["fc_pants_bootcut", "fc_pants_flared"]

  - id: fc_pants_wide_leg
    domain: pants
    label_de: "Wide Leg"
    synonyms_de: ["weit", "wide"]
    maps_to:
      attribute: attr_leg_shape
      enum: vs_leg_shape.wide
    description_de: "Weites Bein; bei fließenden Stoffen häufig."
    conflicts_with: ["fc_pants_skinny", "fc_pants_slim"]

  - id: fc_pants_bootcut
    domain: pants
    label_de: "Bootcut"
    synonyms_de: ["leicht ausgestellt"]
    maps_to:
      attribute: attr_leg_shape
      enum: vs_leg_shape.bootcut
    description_de: "Ab Knie leicht weiter."
    conflicts_with: ["fc_pants_tapered"]

  - id: fc_pants_flared
    domain: pants
    label_de: "Flared / Schlaghose"
    synonyms_de: ["Schlag", "flare"]
    maps_to:
      attribute: attr_leg_shape
      enum: vs_leg_shape.flared
    description_de: "Deutlich ausgestellt ab Knie."
    conflicts_with: ["fc_pants_skinny", "fc_pants_tapered"]

  # (Optional Erweiterungen – nur nutzbar, wenn vs_leg_shape erweitert wurde)
  - id: fc_pants_barrel
    domain: pants
    label_de: "Barrel Leg"
    synonyms_de: ["Tonnenform", "barrel"]
    maps_to:
      attribute: attr_leg_shape
      enum: vs_leg_shape.barrel
    description_de: "Weit an Hüfte/Oberschenkel, zum Saum wieder enger."
    conflicts_with: ["fc_pants_skinny"]
    notes_de: "Benötigt vs_leg_shape.barrel (siehe extensions)."

  - id: fc_pants_culotte
    domain: pants
    label_de: "Culotte"
    synonyms_de: ["culotte"]
    maps_to:
      attribute: attr_leg_shape
      enum: vs_leg_shape.culotte
    description_de: "Weites Bein; Länge meist wadenlang (Länge separat via attr_length_category)."
    conflicts_with: []
    notes_de: "Benötigt vs_leg_shape.culotte (siehe extensions)."

  # ---------- Dresses/Skirts: silhouette ----------
  - id: fc_silhouette_sheath
    domain: dresses_skirts
    label_de: "Schlauchform / Sheath"
    synonyms_de: ["sheath", "schmal", "schlauch"]
    maps_to:
      attribute: attr_silhouette
      enum: vs_silhouette.sheath
    description_de: "Gerade bis leicht figurbetont, ohne starke Weite."
    conflicts_with: ["fc_silhouette_a_line"]

  - id: fc_silhouette_pencil
    domain: dresses_skirts
    label_de: "Bleistift / Pencil"
    synonyms_de: ["pencil", "bleistiftrock", "etui (teils)"]
    maps_to:
      attribute: attr_silhouette
      enum: vs_silhouette.pencil
    description_de: "Figurbetont, meist schmal zulaufend."
    conflicts_with: ["fc_silhouette_a_line"]

  - id: fc_silhouette_a_line
    domain: dresses_skirts
    label_de: "A-Linie"
    synonyms_de: ["a line", "A-Form"]
    maps_to:
      attribute: attr_silhouette
      enum: vs_silhouette.a_line
    description_de: "Oben schmaler, nach unten weiter."
    conflicts_with: ["fc_silhouette_pencil"]

  - id: fc_silhouette_fit_flare
    domain: dresses_skirts
    label_de: "Fit & Flare"
    synonyms_de: ["fit and flare", "oben eng unten weit"]
    maps_to:
      attribute: attr_silhouette
      enum: vs_silhouette.fit_flare
    description_de: "Tailliert, Rockteil ausgestellt."
    conflicts_with: []

  - id: fc_silhouette_empire
    domain: dresses_skirts
    label_de: "Empire"
    synonyms_de: ["empire waist"]
    maps_to:
      attribute: attr_silhouette
      enum: vs_silhouette.empire
    description_de: "Hoch angesetzte Taille unter der Brust."
    conflicts_with: []

  - id: fc_silhouette_wrap
    domain: dresses_skirts
    label_de: "Wickel (Wrap)"
    synonyms_de: ["wrap", "wickelkleid", "wickelrock"]
    maps_to:
      attribute: attr_silhouette
      enum: vs_silhouette.wrap
    description_de: "Überlappung/Bindung; Silhouette kann variieren."
    conflicts_with: []

# ------------------------------------------------------------
# (C) DETAIL-LEXIKON: KRAGEN / MANSCHETTEN / AUSSCHNITTE
# - Fokus: saubere Mappings + Synonyme + Warnhinweise.
# ------------------------------------------------------------
collar_cuff_neckline_detail_lexicon:
  collars:
    - id: term_collar_kent
      label_de: "Kentkragen"
      synonyms_de: ["Kent"]
      maps_to:
        attribute: attr_collar_type
        enum: vs_collar_type.kent
      notes_de: "Klassiker."

    - id: term_collar_global_kent
      label_de: "Global Kent"
      synonyms_de: ["Global-Kent-Kragen", "weltoffener Global Kent"]
      maps_to:
        attribute: attr_collar_type
        enum: vs_collar_type.global_kent
      notes_de:
        - "Immer Kragenform, nie Marke."
        - "Als moderne Kent-Variante häufig in Businesshemden."

    - id: term_collar_new_kent
      label_de: "New Kent"
      synonyms_de: ["New-Kent-Kragen"]
      maps_to:
        attribute: attr_collar_type
        enum: vs_collar_type.new_kent
      notes_de: "Zwischen Kent und Haifisch (hybrid)."

    - id: term_collar_haifisch_spread
      label_de: "Haifisch / Spread"
      synonyms_de: ["Haifischkragen", "Spread"]
      maps_to:
        attribute: attr_collar_type
        enum: vs_collar_type.spread_haifisch
      notes_de: "Weit auseinander stehende Kragenspitzen."

    - id: term_collar_cutaway
      label_de: "Cutaway"
      synonyms_de: ["Cutaway-Kragen"]
      maps_to:
        attribute: attr_collar_type
        enum: vs_collar_type.cutaway
      notes_de: "Oft sehr weit gespreizt (teilweise nahe Haifisch)."

    - id: term_collar_button_down
      label_de: "Button-Down"
      synonyms_de: ["BD", "Button Down"]
      maps_to:
        attribute: attr_collar_type
        enum: vs_collar_type.button_down
      notes_de: "Kragenenden per Knopf fixiert (casual)."

    - id: term_collar_mandarin
      label_de: "Stehkragen / Mandarin"
      synonyms_de: ["Mandarin", "Stehkragen"]
      maps_to:
        attribute: attr_collar_type
        enum: vs_collar_type.mandarin
      notes_de:
        - "Achtung: 'Stehkragen' wird auch für Grandad/Band genutzt -> Kontext prüfen."

    - id: term_collar_camp
      label_de: "Reverskragen / Camp Collar"
      synonyms_de: ["Camp Collar", "Kuba-Kragen"]
      maps_to:
        attribute: attr_collar_type
        enum: vs_collar_type.camp
      notes_de: "Sommerhemd/Resort."

    - id: term_collar_polo
      label_de: "Polokragen"
      synonyms_de: ["polo collar"]
      maps_to:
        attribute: attr_collar_type
        enum: vs_collar_type.polo
      notes_de: "Für Poloshirts."

    # Erweiterungen
    - id: term_collar_wing_tip
      label_de: "Kläppchenkragen / Wing collar"
      synonyms_de: ["wing", "wingtip collar", "Kläppchen"]
      maps_to:
        attribute: attr_collar_type
        enum: vs_collar_type.wing_tip
      notes_de: "Festlich/Smoking (optional, wenn übernommen)."

    - id: term_collar_grandad_band
      label_de: "Grandad / Band collar"
      synonyms_de: ["Bandkragen", "Grandad"]
      maps_to:
        attribute: attr_collar_type
        enum: vs_collar_type.grandad_band
      notes_de: "Stehkragen ohne Umschlag (optional)."

  cuffs:
    - id: term_cuff_sport
      label_de: "Sportmanschette"
      synonyms_de: ["knöpfbar", "Sport cuff"]
      maps_to:
        attribute: attr_cuff_type
        enum: vs_cuff_type.sport
      notes_de: "Standardknopfmanschette (je nach Datenquelle)."

    - id: term_cuff_combi
      label_de: "Kombimanschette"
      synonyms_de: ["combi", "Kombi"]
      maps_to:
        attribute: attr_cuff_type
        enum: vs_cuff_type.combi
      notes_de: "Knopf ODER Manschettenknopf möglich."

    - id: term_cuff_french
      label_de: "Umschlagmanschette / French cuff"
      synonyms_de: ["French cuff", "Doppelmanschette"]
      maps_to:
        attribute: attr_cuff_type
        enum: vs_cuff_type.french
      notes_de: "Benötigt Manschettenknöpfe."

  necklines:
    - id: term_neckline_crew
      label_de: "Rundhals"
      synonyms_de: ["Crew"]
      maps_to:
        attribute: attr_neckline
        enum: vs_neckline.crew

    - id: term_neckline_v
      label_de: "V-Ausschnitt"
      synonyms_de: ["V-neck"]
      maps_to:
        attribute: attr_neckline
        enum: vs_neckline.v_neck

    - id: term_neckline_turtleneck
      label_de: "Rollkragen"
      synonyms_de: ["Turtleneck"]
      maps_to:
        attribute: attr_neckline
        enum: vs_neckline.turtleneck

# ------------------------------------------------------------
# (D) GRÖSSEN: SYSTEME + NORMALISIERUNG
# - EN-13402/ISO-Denke: Maße als Körperdimensionen; Labels können variieren.
# - Hemden: Kragenweite/Halsumfang ist eine eigene Achse.
# ------------------------------------------------------------
size_systems_and_normalization_playbook:
  principles:
    - "1) Immer raw behalten: attr_size_label_raw = exakt aus Quelle/Label."
    - "2) Kontext vor Konversion: Erst item_type/category prüfen, dann size_system."
    - "3) Bei Unsicherheit: size_system='other', normalized leer lassen, nur raw + ggf. body_measurements."
    - "4) Mehrdimensionale Größen separat speichern (schema_patch empfohlen)."
    - "5) Wenn Größentabelle vorhanden: Maße in attr_body_measurements_cm übernehmen; diese sind oft zuverlässiger als Label-Konversion."
  body_measurement_keys_canonical:
    # orientiert an gängigen Size-Guides / EN-13402-Dimensionen
    - key: neck_girth
      unit: cm
      examples: ["37", "39-40"]
      notes: "Hemdkragenweite/Halsumfang."
    - key: chest_girth
      unit: cm
      examples: ["100", "122"]
      notes: "Brustumfang."
    - key: bust_girth
      unit: cm
      examples: ["88", "96"]
      notes: "Damen: Oberweite."
    - key: waist_girth
      unit: cm
      examples: ["84", "98"]
      notes: "Taillenumfang."
    - key: hip_girth
      unit: cm
      examples: ["96", "112"]
      notes: "Hüftumfang."
    - key: body_height
      unit: cm
      examples: ["176"]
      notes: "Körpergröße."
    - key: inside_leg
      unit: cm
      examples: ["82", "86"]
      notes: "Innenbeinlänge."
    - key: sleeve_length
      unit: cm
      examples: ["66.5"]
      notes: "Ärmellänge (Definition je Marke unterschiedlich) – daher immer Quelle/Typ notieren, wenn möglich."
    - key: foot_length
      unit: mm
      examples: ["280", "297"]
      notes: "Mondopoint (optional, ISO)."
    - key: foot_width
      unit: mm
      examples: ["110"]
      notes: "Mondopoint (optional, ISO)."

  patterns:
    alpha_sizes:
      detect_examples: ["XXS", "XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", "5XL", "6XL"]
      normalized_rule: "alpha_{lowercase}"
      normalized_examples: ["alpha_xs", "alpha_m", "alpha_3xl"]
      notes:
        - "Achtung: 'M' kann auch Maßeinheit sein -> nur im Feld 'Größe' oder in klarer Size-Auswahl interpretieren."

    numeric_eu_apparel:
      detect_examples: ["32", "34", "36", "38", "40", "42", "44", "46", "48", "50", "52", "54", "56"]
      normalized_rule: "eu_{number}"
      notes:
        - "Nur, wenn Kontext Bekleidung (cat_apparel) und NICHT Hemdkragenweite/Hut/BH/Handschuh."

    jeans_waist_inseam_inch:
      detect_examples: ["W32/L34", "W 32 L 34", "32W/34L", "32/34 (nur im Hosen-Kontext)", "W31 L32"]
      parse:
        waist_in: "W"
        inseam_in: "L"
      normalized_rule: "w{waist}_l{inseam}"
      normalized_examples: ["w32_l34", "w31_l32"]
      notes:
        - "Wenn '32/34' ohne W/L: nur als W/L interpretieren, wenn item_type Hose/Jeans ODER Quelle klar Jeans."

    shoe_eu:
      detect_examples: ["36", "37", "38", "39", "40", "41", "42", "42.5", "43", "44", "45", "46", "47"]
      normalized_rule: "shoe_eu_{value}"
      notes:
        - "Bei adidas/ähnlich kommen Bruchteile wie '43 1/3', '42 2/3' vor -> raw behalten + optional shoe_eu_43_1_3."

    shoe_mondopoint:
      detect_examples: ["280/110", "270", "295 (mm)", "27.0 (MP)"]
      normalized_rule: "mp_{foot_length_mm}_{optional_width_mm}"
      normalized_examples: ["mp_280_110", "mp_270"]
      notes:
        - "Mondopoint basiert auf Fußlänge (und optional Breite) in mm; sehr robust, wenn vorhanden."

    shirt_collar_cm:
      # Kernfix für euer Projekt
      detect_examples: ["37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "37/38", "39/40", "41-42", "43 - 44"]
      detect_context_clues:
        - "Kragenweite"
        - "Halsweite"
        - "Halsumfang"
        - "collar"
        - "neck"
        - "bei Hemd/Bluse (item_type) implizit"
      parse_rules:
        - "Wenn token 'NN/NN' oder 'NN-NN' -> range_low=N1, range_high=N2."
        - "Wenn single 'NN' -> range_low=NN, range_high=NN."
        - "Zusätzlich: wenn Quelle Doppelgrößen nutzt (z. B. 39/40), kann alpha_size gleich bleiben; der Unterschied ist primär die Halsweite."
      normalized_rule:
        single: "collar_cm_{n}"
        range: "collar_cm_{n1}_{n2}"
      normalized_examples: ["collar_cm_39", "collar_cm_39_40"]
      storage_guidance:
        - "Wenn Hemd nur Kragenweite auswählbar: attr_size_system=shirt_collar_cm + attr_size_normalized=collar_cm_.."
        - "Wenn Hemd sowohl alpha (M) als auch Kragenweite (39/40) zeigt: PRIMARY size bleibt alpha, SECONDARY wird collar_cm (schema_patch empfohlen)."
        - "Immer zusätzlich attr_body_measurements_cm.neck_girth befüllen (single oder range)."

    shirt_sleeve_variant:
      detect_examples: ["Extra langer Arm", "super-extra langer Arm", "Extra kurzer Arm", "Kurzarm", "Langarm"]
      mapping:
        - "Kurzarm/Langarm/3-4/ärmellos -> attr_sleeve_length (vs_sleeve_length)."
        - "Extra langer Arm / Extra kurzer Arm / super-extra langer Arm -> attr_sleeve_length_variant (NEU, siehe schema_patch)."
      notes:
        - "Ein Hemd kann gleichzeitig Langarm sein UND 'Extra langer Arm' (Variante)."

    bra_band_cup:
      detect_examples: ["70A", "75B", "80C", "85D", "90E", "75 DD"]
      normalized_rule: "bra_{band}_{cup}"
      normalized_examples: ["bra_75_b", "bra_80_c"]
      notes:
        - "Nur bei item_type BH/Bralette/Bikini-Top mit Cup."
        - "Cup kann D/DD/E etc. sein -> raw behalten, wenn komplex."

    belt_length_cm:
      detect_examples: ["90", "95", "100", "105", "110", "120"]
      detect_context_clues: ["Gürtel", "belt", "Bundweite Gürtel"]
      normalized_rule: "belt_cm_{n}"
      notes:
        - "Zahl ohne Kontext niemals als Gürtel interpretieren."

    hat_circumference_cm:
      detect_examples: ["54", "56", "58", "60"]
      detect_context_clues: ["Hut", "Mütze", "Cap", "Kopfumfang"]
      normalized_rule: "hat_cm_{n}"

    gloves_numeric:
      detect_examples: ["7", "7.5", "8", "8.5", "9", "10", "11"]
      detect_context_clues: ["Handschuh", "glove"]
      normalized_rule: "glove_{n}"

  shirt_size_association_helpers:
    # Hilfslogik, wenn ihr aus Kragenweite eine alpha-Größe ableiten wollt (optional, low/medium confidence).
    collar_range_to_alpha:
      - collar_cm_range: "37-38"
        alpha: "S"
      - collar_cm_range: "39-40"
        alpha: "M"
      - collar_cm_range: "41-42"
        alpha: "L"
      - collar_cm_range: "43-44"
        alpha: "XL"
      - collar_cm_range: "45-46"
        alpha: "XXL"
      - collar_cm_range: "47-48"
        alpha: "3XL"
    notes_de:
      - "Diese Zuordnung ist in vielen deutschsprachigen Hemden-Größentabellen üblich; trotzdem als 'derived' kennzeichnen."
      - "Wenn Hersteller explizite Größentabelle vorliegt: Hersteller-Tabelle gewinnt."

# ------------------------------------------------------------
# (E) HIGH-IMPACT DISAMBIGUATION RULES (Kurz, wirkungsvoll)
# ------------------------------------------------------------
disambiguation_rules_high_impact:
  # 1) Global Kent etc.
  collar_terms_never_brand:
    - "Global Kent"
    - "New Kent"
    - "Kentkragen"
    - "Haifischkragen"
    - "Button-Down"
    - "Kläppchenkragen"
    - "Reverskragen"
    - "Camp Collar"

  # 2) Hemd-Kragenweite vs Konfektionsgröße
  shirt_collar_vs_eu_size:
    rule: "Wenn ein zweistelliges Token 36..54 erscheint UND Kontext=Hemd/Bluse ODER 'Kragenweite/Halsweite/Halsumfang' -> als shirt_collar_cm behandeln, nicht numeric_eu."
    examples:
      - input: "Größe 39/40"
        context: "Hemd"
        output: "size_system=shirt_collar_cm, normalized=collar_cm_39_40, body_measurements.neck_girth=39-40"
      - input: "M (39/40)"
        context: "Hemd"
        output: "primary alpha=M, secondary collar_cm_39_40 (schema_patch), body_measurements.neck_girth=39-40"

  # 3) '42' harte Ambiguität (Schuh vs Bekleidung)
  size_42_disambiguation:
    rule: "Token '42' ohne weitere Hinweise -> Kontext entscheidet: footwear => shoe_eu, apparel => numeric_eu; sonst other."
    tie_breakers:
      - "Wenn Begriffe wie 'Sneaker', 'Schuh', 'Boot', 'Sohle' => shoe_eu"
      - "Wenn Begriffe wie 'Hose', 'Sakko', 'Kleid' => numeric_eu"
      - "Wenn Begriffe wie 'Kragenweite' => shirt_collar_cm"

  # 4) Sonderarmlängen nicht als eigene Hauptgröße verwechseln
  sleeve_variant_handling:
    rule: "Extra langer/kürzerer Arm ist keine Größe, sondern ein Variant-Attribut."
    action: "Mappe auf attr_sleeve_length_variant (neu) + sleeve_length (short/long) wenn ableitbar."

  # 5) Mondopoint vs EU-Schuhgröße
  mondopoint_precedence:
    rule: "Wenn Mondopoint (mm) vorhanden: als primärere, präzisere Größeninfo speichern (shoe_mondopoint_mm) und EU-Schuhgröße nur sekundär."
    notes_de: "Mondopoint basiert direkt auf Fußlänge/-breite."

# ------------------------------------------------------------
# (F) SCHEMA PATCH (empfohlen, um Mehrdimensionen sauber zu speichern)
# ------------------------------------------------------------
schema_patch_recommended:
  add_attributes:
    - id: attr_size_secondary_system
      label_de: "Größensystem (sekundär)"
      description_de: "Optional: zweite Größenachse (z. B. Hemd: alpha + Kragenweite)."
      data_type: "enum"
      allowed_values: "vs_size_system"
      extraction_priority: 3

    - id: attr_size_secondary_label_raw
      label_de: "Größe (sekundär, raw)"
      description_de: "Originaltext der sekundären Größe."
      data_type: "string"
      extraction_priority: 3

    - id: attr_size_secondary_normalized
      label_de: "Größe (sekundär, normalisiert)"
      description_de: "Kanonische sekundäre Größe passend zu attr_size_secondary_system."
      data_type: "string"
      extraction_priority: 3

    - id: attr_sleeve_length_variant
      label_de: "Ärmellängen-Variante"
      description_de: "Sonderlängen bei Hemden: extra_lang / super_extra_lang / extra_kurz / normal."
      data_type: "enum"
      allowed_values: "vs_sleeve_length_variant"
      extraction_priority: 3

  add_value_sets:
    - id: vs_sleeve_length_variant
      description_de: "Sonderarmlängen (Hemden) – zusätzlich zu Kurzarm/Langarm."
      values:
        - value: normal
          synonyms_de: ["normal", "Standard"]
          notes_de: ""
        - value: extra_long
          synonyms_de: ["Extra langer Arm"]
          notes_de: ""
        - value: super_extra_long
          synonyms_de: ["Super-extra langer Arm", "super extra langer Arm"]
          notes_de: ""
        - value: extra_short
          synonyms_de: ["Extra kurzer Arm"]
          notes_de: ""

  migration_notes:
    - "Wenn ihr schema_patch nicht wollt: dann collar_cm ausschließlich in attr_body_measurements_cm.neck_girth ablegen und primary size als alpha/numeric belassen."
    - "Für RAG/SQL ist schema_patch stark empfohlen, weil Hemden real häufig mehrere Größenachsen parallel ausweisen."
