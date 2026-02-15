<!-- FILE: ontology_part_07_brands_shops.md -->
# Part 07 – Brands & Shops (für RAG-Extraktion, Shop-Facets, Brand-Disambiguation)
version: "1.0.0"
date: "2026-01-13"
scope: "Shop-Verzeichnis (inkl. Facets/Attribute-Mapping) + Brand-Katalog (breit, RAG-tauglich) + Ambiguitäten"
toc:
  - intent_and_principles
  - shop_facet_canonicalization
  - shops_catalog
  - brand_detection_playbook
  - brand_groups
  - brands_catalog
  - top_brand_shop_ambiguities

```yaml
intent_and_principles:
  why_this_part_exists:
    - "Shops strukturieren Produktdaten unterschiedlich. Wir normalisieren Shop-Facets → Ontologie-Attribute."
    - "Brands sind ein eigenes Lexikon ('Wahrheit') und werden nie aus Attributen abgeleitet."
    - "Marketplace-Shops (Amazon etc.) sind besonders fehleranfällig: Shop != Brand."
  invariants:
    - "attr_shop wird aus Domain/Quelle gesetzt (URL, Rechnung, PDF-Header), nicht aus Produkttext."
    - "attr_brand wird nur gesetzt, wenn Brand-Quelle hoch genug ist (Label/OCR, EAN, Titel-Brand-Feld, Shop-Metadaten)."
    - "Shop-Facets dürfen Attribute setzen (fit/material/care/etc.), aber niemals Brand, außer Shop liefert ein explizites Brand-Feld."
  id_conventions:
    shop_prefix: "shop_"
    brand_prefix: "br_"
    allowed_chars: "a-z0-9_"
    examples:
      - "shop_uniqlo (nicht: shop_unqlo)"
      - "br_hugo_boss (optional), br_boss, br_hugo"

# ------------------------------------------------------------
# (A) Shop-Facet-Kanonisierung: Shop-Begriffe → Ontologie-Attribute
# ------------------------------------------------------------
shop_facet_canonicalization:
  canonical_facets:
    # Jede Facet-Definition beschreibt: (a) typische Shop-Labels, (b) Ziel-Attribut(e),
    # (c) Parsing-Hinweise / Prioritäten.
    - facet_id: facet_size
      labels_de: ["Größe", "Groesse", "Konfektionsgröße", "Schuhgröße", "Jeansgröße", "Sondergrößen"]
      labels_en: ["Size", "Sizing", "Special sizes"]
      maps_to:
        - attr: attr_size_label_raw
          notes: "Immer raw übernehmen."
        - attr: attr_size_system
          notes: "Nur setzen, wenn Kontext/Pattern eindeutig (siehe Part 06)."
        - attr: attr_size_normalized
          notes: "Nur bei robustem Parse."
        - attr: attr_size_secondary_label_raw
          notes: "Optional (Schema Patch empfohlen), wenn 2. Größenachse existiert (z. B. Hemd: M + 39/40)."
    - facet_id: facet_fit_cut
      labels_de: ["Passform", "Fit", "Schnitt", "Weite", "Beinform"]
      labels_en: ["Fit", "Cut", "Leg", "Silhouette"]
      maps_to:
        - attr: attr_fit_type
        - attr: attr_leg_shape
        - attr: attr_silhouette
        - attr: attr_rise
      notes: "Fit/Cut nie als Brand interpretieren."
    - facet_id: facet_material_composition
      labels_de: ["Material", "Zusammensetzung", "Oberstoff", "Material Oberstoff", "Futter", "Wattierung"]
      labels_en: ["Material", "Composition", "Outer fabric", "Lining", "Filling"]
      maps_to:
        - attr: attr_material_composition
          notes: "Prefer Prozentangaben + Komponenten. Synonyme über Part 05/09 normalisieren."
        - attr: attr_material_main
          notes: "Aus Composition ableiten, wenn möglich."
    - facet_id: facet_care
      labels_de: ["Pflegehinweise", "Pflege", "Care instructions", "Waschen", "Bügeln", "Trocknen"]
      labels_en: ["Care", "Care instructions", "Washing instructions"]
      maps_to:
        - attr: attr_care_instructions_text
          notes: "Freitext + Symbole (falls verfügbar) speichern; nicht über-interpretieren."
    - facet_id: facet_color
      labels_de: ["Farbe", "Farbton", "Color"]
      labels_en: ["Color"]
      maps_to:
        - attr: attr_color_primary
        - attr: attr_color_family
        - attr: attr_multicolor_flag
      notes: "Vision-Farbe vs Text-Farbe: bei Glanz/Pailletten confidence reduzieren (Part 09)."
    - facet_id: facet_pattern
      labels_de: ["Muster", "Print", "Dessins", "Karo", "Streifen"]
      labels_en: ["Pattern", "Print"]
      maps_to:
        - attr: attr_pattern_type
    - facet_id: facet_length
      labels_de: ["Länge", "Gesamtlänge", "Rocklänge", "Beininnenlänge", "Kurzgröße", "Langgröße"]
      labels_en: ["Length", "Inseam"]
      maps_to:
        - attr: attr_length_category
        - attr: attr_inseam_length_cm
        - attr: attr_special_size_type
      notes: "Kurz-/Langgröße ≠ Short/Long Sleeve."
    - facet_id: facet_collar_neckline
      labels_de: ["Kragen", "Kragenart", "Ausschnitt", "Halsform"]
      labels_en: ["Collar", "Neckline"]
      maps_to:
        - attr: attr_collar_type
        - attr: attr_neckline
    - facet_id: facet_sleeve
      labels_de: ["Ärmellänge", "Arm", "Kurzarm", "Langarm"]
      labels_en: ["Sleeve length"]
      maps_to:
        - attr: attr_sleeve_length
        - attr: attr_sleeve_length_variant
    - facet_id: facet_features_function
      labels_de: ["Funktion", "Eigenschaften", "Technologie", "Besonderes Material", "Wasserabweisend", "Atmungsaktiv"]
      labels_en: ["Features", "Technology", "Water-repellent", "Breathable"]
      maps_to:
        - attr: attr_activity
        - attr: attr_water_resistance
        - attr: attr_breathability
        - attr: attr_wind_resistance
        - attr: attr_insulation_type
      notes: "Finish/Technologien (z. B. DWR) nicht als Material verwechseln."
    - facet_id: facet_sustainability
      labels_de: ["Nachhaltigkeit", "Zertifikate", "Bio", "Recycelt", "Ausgezeichnete Qualität"]
      labels_en: ["Sustainability", "Certified", "Organic", "Recycled"]
      maps_to:
        - attr: attr_certifications
        - attr: attr_sustainability_score_1to5
      notes: "Zertifikate als IDs (cert_*) speichern; Freitext zusätzlich erlauben."

  facet_priority_order:
    # Wenn mehrere Shops dasselbe Feld anbieten, gewinnt meist:
    - "Explizite Shop-Detailsektion (Material & Pflegehinweise) > Filter/Facet > Freitextbeschreibung > Vision"
    - "Prozent-Komposition > Materialwort ohne Prozent"
    - "Größentabelle/Measurements > Label-Konversion"

# ------------------------------------------------------------
# (B) Shops-Katalog: Fokus + typische Facets + Extraktionsanker
# ------------------------------------------------------------
shops_catalog:
  - id: shop_zalando
    label: "Zalando"
    shop_type: retailer_marketplace
    primary_region: ["DE", "AT", "CH", "EU"]
    catalog_focus: ["cat_apparel", "cat_footwear", "cat_accessories", "cat_sport_outdoor"]
    content_anchors:
      # Strings, die beim Parsen von HTML/PDF helfen
      - "Material & Pflegehinweise"
      - "Größe & Passform"
      - "Passform:"
      - "Schnitt:"
    typical_facets: ["facet_size", "facet_fit_cut", "facet_material_composition", "facet_care", "facet_color", "facet_pattern", "facet_length", "facet_collar_neckline", "facet_sleeve", "facet_sustainability"]
    data_quality_notes:
      - "Produktseiten enthalten oft strukturierte Blöcke (Material/Pflege + Größe/Passform)."
      - "Model-Maße können im Text vorkommen; als Hinweis nutzen, aber nicht als Body-Measures des Besitzers speichern."
    extraction_hints:
      - "Wenn 'Passform: weit'/'normal'/'eng' vorhanden → attr_fit_type oder attr_leg_shape (je nach Item)."
      - "Care instructions häufig als Textliste (maschinenwäsche, handwäsche, nicht trocknergeeignet)."

  - id: shop_zalando_lounge
    label: "Zalando Lounge"
    shop_type: offprice_retailer
    primary_region: ["DE", "AT", "CH", "EU"]
    catalog_focus: ["cat_apparel", "cat_footwear", "cat_accessories"]
    content_anchors: ["Größentabellen", "Körpermaße", "Größenberater"]
    typical_facets: ["facet_size", "facet_fit_cut", "facet_material_composition", "facet_care", "facet_color", "facet_pattern"]
    data_quality_notes: ["Größentabellen als Orientierung; Herstellerangaben können variieren."]
    extraction_hints: ["Wenn Größentabelle vorhanden: body_measurements bevorzugen."]

  - id: shop_aboutyou
    label: "ABOUT YOU"
    shop_type: retailer_marketplace
    primary_region: ["DE", "AT", "EU"]
    catalog_focus: ["cat_apparel", "cat_footwear", "cat_accessories"]
    content_anchors: ["Sondergrößen", "Größentabelle", "Größenberater"]
    typical_facets: ["facet_size", "facet_fit_cut", "facet_material_composition", "facet_care", "facet_color", "facet_pattern", "facet_length", "facet_sustainability"]
    data_quality_notes:
      - "Sondergrößen/Petite/Tall kommen als Filter/Meta vor."
    extraction_hints:
      - "Sondergrößen → attr_special_size_type (petite/tall/maternity/plus)."

  - id: shop_breuninger
    label: "BREUNINGER"
    shop_type: department_store
    primary_region: ["DE", "CH", "EU"]
    catalog_focus: ["cat_apparel", "cat_footwear", "cat_accessories", "cat_apparel_formal"]
    content_anchors: ["Welche Größe passt mir?", "Grössenberater"]
    typical_facets: ["facet_size", "facet_fit_cut", "facet_material_composition", "facet_care", "facet_color", "facet_pattern", "facet_sustainability"]
    data_quality_notes:
      - "Größenberater kann zusätzliche Struktur liefern; Luxus-/Premium-Marken stark vertreten."
    extraction_hints:
      - "Brand häufig zuverlässig als explizites Feld vorhanden; trotzdem nicht aus Fließtext 'BOSS Lederjacken' blind übernehmen."

  - id: shop_peek_cloppenburg
    label: "Peek & Cloppenburg"
    shop_type: department_store
    primary_region: ["DE", "EU"]
    catalog_focus: ["cat_apparel", "cat_footwear", "cat_accessories"]
    content_anchors: ["Größen & Passformen", "Material & Pflege"]
    typical_facets: ["facet_size", "facet_fit_cut", "facet_material_composition", "facet_care", "facet_color", "facet_pattern", "facet_sustainability"]
    data_quality_notes: ["Kategorie-/Ratgeberseiten spiegeln oft die Struktur der Produktdetails wider."]

  - id: shop_otto
    label: "OTTO"
    shop_type: retailer_marketplace
    primary_region: ["DE"]
    catalog_focus: ["cat_apparel", "cat_footwear", "cat_accessories", "cat_sport_outdoor"]
    content_anchors: ["Material", "Pflegehinweise", "Passform", "Größe"]
    typical_facets: ["facet_size", "facet_fit_cut", "facet_material_composition", "facet_care", "facet_color", "facet_pattern", "facet_length", "facet_features_function", "facet_sustainability"]
    data_quality_notes:
      - "Marketplace-Charakter: Brand-Qualität variiert je nach Seller."
    extraction_hints:
      - "Brand nur aus explizitem Brand-Feld oder Label/OCR; nicht aus Seller-Name."

  - id: shop_amazon_fashion
    label: "Amazon Fashion"
    shop_type: marketplace
    primary_region: ["DE", "EU", "Global"]
    catalog_focus: ["cat_apparel", "cat_footwear", "cat_accessories"]
    content_anchors: ["Material", "Pflegehinweise", "Passform", "Muster"]
    typical_facets: ["facet_size", "facet_fit_cut", "facet_material_composition", "facet_care", "facet_color", "facet_pattern", "facet_features_function", "facet_sustainability"]
    data_quality_notes:
      - "Sehr heterogene Datenqualität (Seller-Uploads)."
      - "Filter wie 'Pflegehinweise'/'Material' existieren, aber Produktseiten können inkonsistent sein."
    extraction_hints:
      - "Brand-Confidence: OCR(Label) > 'Marke:' Feld > Titel-Brand-Prefix > Bulletpoints."
      - "Wenn Brand unklar: leave attr_brand empty, set brand_confidence low."

  - id: shop_bonprix
    label: "bonprix"
    shop_type: retailer
    primary_region: ["DE", "AT", "CH", "EU"]
    catalog_focus: ["cat_apparel", "cat_accessories"]
    content_anchors: ["Passform", "Länge", "Ärmellänge", "Kragenart", "Besonderes Material", "Funktionen"]
    typical_facets: ["facet_size", "facet_fit_cut", "facet_material_composition", "facet_care", "facet_color", "facet_pattern", "facet_length", "facet_collar_neckline", "facet_sleeve", "facet_features_function", "facet_sustainability"]
    data_quality_notes:
      - "Viele strukturierte Bullet-Felder (Passform/Länge/Kragenart)."
    extraction_hints:
      - "'Besonderes Material' kann Finish/Technologie enthalten (z. B. wasserabweisend) → facet_features_function."

  - id: shop_hessnatur
    label: "hessnatur"
    shop_type: specialist_sustainable
    primary_region: ["DE", "EU"]
    catalog_focus: ["cat_apparel", "cat_accessories", "cat_baby_kids_optional"]
    content_anchors: ["GOTS", "Ausgezeichnete Qualität", "Material", "Pflege"]
    typical_facets: ["facet_size", "facet_fit_cut", "facet_material_composition", "facet_care", "facet_color", "facet_pattern", "facet_sustainability"]
    data_quality_notes:
      - "Nachhaltigkeitskennzeichnungen sind zentral; Zertifikate oft explizit markiert."
    extraction_hints:
      - "GOTS/IVN/OEKO-TEX etc. → attr_certifications (cert_*)."

  - id: shop_hm
    label: "H&M"
    shop_type: fast_fashion_retailer
    primary_region: ["Global", "EU"]
    catalog_focus: ["cat_apparel", "cat_accessories"]
    content_anchors: ["Materialien", "Zusammensetzung"]
    typical_facets: ["facet_size", "facet_fit_cut", "facet_material_composition", "facet_care", "facet_color", "facet_pattern", "facet_sustainability"]
    data_quality_notes: ["Material-Komposition häufig nach Bauteilen (Bündchen/Äußere Schicht)."]
    extraction_hints:
      - "Bauteil-Komposition in attr_material_composition als Liste speichern (component_name + %)."

  - id: shop_canda
    label: "C&A"
    shop_type: value_retailer
    primary_region: ["DE", "EU"]
    catalog_focus: ["cat_apparel", "cat_accessories"]
    content_anchors: ["Größenberater", "Größensysteme"]
    typical_facets: ["facet_size", "facet_fit_cut", "facet_material_composition", "facet_care", "facet_color", "facet_pattern", "facet_sustainability"]
    data_quality_notes: ["Größenberater/Tabellen häufig vorhanden (gute Body-Measure Quelle)."]

  - id: shop_uniqlo
    label: "UNIQLO"
    shop_type: retailer_brand
    primary_region: ["EU", "Global"]
    catalog_focus: ["cat_apparel", "cat_accessories"]
    content_anchors: ["Size Chart", "Check my size", "Care label"]
    typical_facets: ["facet_size", "facet_fit_cut", "facet_material_composition", "facet_care", "facet_color", "facet_pattern", "facet_features_function"]
    data_quality_notes:
      - "Maßtabellen auf Produktseite; Messabweichungen (1–2 cm) möglich."
    extraction_hints:
      - "Wenn Size Chart vorhanden: Maße als body_measurements speichern (source=shop_size_chart)."

  # --- Luxus / internationale Plattformen (kürzer, aber hilfreich fürs RAG) ---
  - id: shop_farfetch
    label: "FARFETCH"
    shop_type: luxury_marketplace
    primary_region: ["Global", "EU"]
    catalog_focus: ["cat_apparel", "cat_footwear", "cat_accessories"]
    typical_facets: ["facet_size", "facet_material_composition", "facet_care", "facet_color", "facet_sustainability"]
    data_quality_notes: ["Boutique-abhängige Daten; häufig gute Designer-Brand-Felder."]

  - id: shop_mytheresa
    label: "Mytheresa"
    shop_type: luxury_retailer
    primary_region: ["EU", "Global"]
    catalog_focus: ["cat_apparel", "cat_footwear", "cat_accessories"]
    typical_facets: ["facet_size", "facet_material_composition", "facet_care", "facet_color"]
    data_quality_notes: ["Hoch strukturierte Designer-Produktdaten."]

  - id: shop_net_a_porter
    label: "NET-A-PORTER"
    shop_type: luxury_retailer
    primary_region: ["Global"]
    catalog_focus: ["cat_apparel", "cat_footwear", "cat_accessories"]
    typical_facets: ["facet_size", "facet_material_composition", "facet_care", "facet_color"]
    data_quality_notes: ["Gute Detailbeschreibungen; Maße/Model-Info häufig enthalten (nicht als Nutzermaße speichern)."]

  - id: shop_mr_porter
    label: "MR PORTER"
    shop_type: luxury_retailer
    primary_region: ["Global"]
    catalog_focus: ["cat_apparel", "cat_footwear", "cat_accessories"]
    typical_facets: ["facet_size", "facet_fit_cut", "facet_material_composition", "facet_care", "facet_color"]
    data_quality_notes: ["Herren-Fokus; Fit-Infos oft gut."]

  # --- Secondhand (optional fürs Projekt, aber praktisch) ---
  - id: shop_vinted
    label: "Vinted"
    shop_type: secondhand_marketplace
    primary_region: ["EU"]
    catalog_focus: ["cat_apparel", "cat_footwear", "cat_accessories"]
    typical_facets: ["facet_size", "facet_color", "facet_pattern", "facet_material_composition"]
    data_quality_notes:
      - "User-generated content, hohe Varianz; Bilder/Vision besonders wichtig, aber fehleranfällig."
    extraction_hints:
      - "Condition/Zustand optional separat (falls euer Schema es hat); nicht in material/care mischen."

  - id: shop_vestiaire_collective
    label: "Vestiaire Collective"
    shop_type: secondhand_luxury_marketplace
    primary_region: ["EU", "Global"]
    catalog_focus: ["cat_apparel", "cat_footwear", "cat_accessories"]
    typical_facets: ["facet_size", "facet_color", "facet_material_composition"]
    data_quality_notes: ["Luxus-Secondhand; Brand-Felder oft vorhanden, aber Beschreibung variiert."]

# ------------------------------------------------------------
# (C) Brand-Detection Playbook (kurz, aber entscheidend)
# ------------------------------------------------------------
brand_detection_playbook:
  preferred_sources_ranked:
    - source: "label_ocr_primary"
      confidence: 0.95
      examples: ["Nackenlabel", "Innenlabel", "geprägtes Leder-Branding", "Uhrenboden/Schließe"]
    - source: "shop_explicit_brand_field"
      confidence: 0.90
      examples: ["Shop-Feld 'Marke'/'Brand' als eigenes Metadatenfeld"]
    - source: "barcode_ean_lookup"
      confidence: 0.85
      examples: ["EAN/GTIN → Brand"]
    - source: "product_title_prefix"
      confidence: 0.70
      examples: ["BOSS Hemd ...", "adidas Sneaker ..."]
    - source: "free_text_mentions"
      confidence: 0.40
      examples: ["'inspiriert von ...', 'passt zu BOSS ...'"]
  normalization_rules:
    - "Casefold + Trim + entferne Rechtsformzusätze (GmbH/AG) für Brand-Matching."
    - "Diakritika normalisieren (é → e), Bindestriche/Spaces tolerant behandeln."
    - "Wenn Token gleichzeitig Attribut sein kann (z. B. 'Kent', 'Oxford'), niemals als Brand matchen."
  brand_confidence_policy:
    - "Wenn keine Quelle ≥ 0.70: attr_brand leer lassen und stattdessen brand_candidate_text + confidence speichern (falls euer Schema das erlaubt)."

# ------------------------------------------------------------
# (D) Brand-Gruppen (Defaults zur Reduktion von Wiederholungen)
# ------------------------------------------------------------
brand_groups:
  luxury_designer:
    tier: luxury
    tags: ["designer", "runway_optional"]
    default_categories: ["cat_apparel", "cat_footwear", "cat_accessories"]
  premium_business:
    tier: premium
    tags: ["business", "smart_casual"]
    default_categories: ["cat_apparel", "cat_accessories"]
  sport_athleisure:
    tier: mid
    tags: ["sport", "performance"]
    default_categories: ["cat_sport_outdoor", "cat_footwear", "cat_accessories"]
  outdoor_technical:
    tier: mid
    tags: ["outdoor", "technical"]
    default_categories: ["cat_sport_outdoor", "cat_footwear", "cat_accessories"]
  sustainable_focused:
    tier: mid
    tags: ["sustainable", "certifications_common"]
    default_categories: ["cat_apparel", "cat_accessories", "cat_footwear"]
  denim_specialist:
    tier: mid
    tags: ["denim"]
    default_categories: ["cat_apparel"]
  value_fast_fashion:
    tier: budget
    tags: ["trend", "fast_fashion"]
    default_categories: ["cat_apparel", "cat_accessories"]

# ------------------------------------------------------------
# (E) Brands-Katalog (breit, RAG-tauglich; >150 Marken)
# - Felder: id, label, group (optional), tier (override), common_categories (override), known_confusions
# ------------------------------------------------------------
brands_catalog:
  # --- DE/Business Hemden & Formalwear ---
  - {id: br_olymp, label: "OLYMP", group: premium_business, known_confusions: ["Global Kent ist Kragenform, keine Marke."]}
  - {id: br_eterna, label: "ETERNA", group: premium_business}
  - {id: br_seidensticker, label: "Seidensticker", group: premium_business}
  - {id: br_van_laack, label: "van Laack", group: premium_business}
  - {id: br_jake_s, label: "Jake*s", tier: mid, common_categories: ["cat_apparel", "cat_accessories"], known_confusions: ["Stern/Zeichen in OCR kann fehlen."]}
  - {id: br_windsor, label: "Windsor", group: premium_business}
  - {id: br_digel, label: "DIGEL", group: premium_business}
  - {id: br_eduard_dressler, label: "Eduard Dressler", group: premium_business}
  - {id: br_carl_gross, label: "Carl Gross", group: premium_business}
  - {id: br_wilvorst, label: "Wilvorst", group: premium_business}
  - {id: br_henk_ter_horst, label: "Henk ter Horst", tier: mid, common_categories: ["cat_apparel", "cat_accessories"]}
  - {id: br_eagle_no7, label: "EAGLE No. 7", tier: mid, common_categories: ["cat_apparel"], known_confusions: ["No. 7 kann als Größe fehlinterpretiert werden."]}
  - {id: br_stenstroms, label: "Stenströms", group: premium_business}
  - {id: br_charvet, label: "Charvet", group: luxury_designer}
  - {id: br_turnbull_asser, label: "Turnbull & Asser", group: luxury_designer}

  # --- Boss/Hugo usw. ---
  - {id: br_boss, label: "BOSS", group: premium_business, known_confusions: ["Wort 'Boss' (Chef) ≠ Marke, nur bei Label/Titel sicher."]}
  - {id: br_hugo, label: "HUGO", group: premium_business}
  - {id: br_hugo_boss, label: "HUGO BOSS", group: premium_business, known_confusions: ["Manchmal steht nur 'BOSS' auf Label."]}

  # --- Sport / Performance ---
  - {id: br_adidas, label: "adidas", group: sport_athleisure}
  - {id: br_nike, label: "Nike", group: sport_athleisure}
  - {id: br_puma, label: "PUMA", group: sport_athleisure}
  - {id: br_asics, label: "ASICS", group: sport_athleisure}
  - {id: br_new_balance, label: "New Balance", group: sport_athleisure}
  - {id: br_under_armour, label: "Under Armour", group: sport_athleisure}
  - {id: br_reebok, label: "Reebok", group: sport_athleisure}
  - {id: br_hoka, label: "HOKA", group: sport_athleisure}
  - {id: br_brooks, label: "Brooks", group: sport_athleisure}
  - {id: br_on_running, label: "On", group: sport_athleisure, known_confusions: ["'on' als Präposition; nur als Brand matchen, wenn Kontext Sport/Logo eindeutig."]}
  - {id: br_salomon, label: "Salomon", group: outdoor_technical}

  # --- Outdoor/Technical ---
  - {id: br_patagona, label: "Patagonia", group: outdoor_technical}
  - {id: br_the_north_face, label: "The North Face", group: outdoor_technical}
  - {id: br_arcteryx, label: "Arc'teryx", group: outdoor_technical, known_confusions: ["Apostroph/Zeichen in OCR kann fehlen."]}
  - {id: br_vaude, label: "VAUDE", group: outdoor_technical}
  - {id: br_jack_wolfskin, label: "Jack Wolfskin", group: outdoor_technical}
  - {id: br_mammut, label: "Mammut", group: outdoor_technical}
  - {id: br_fjallraven, label: "Fjällräven", group: outdoor_technical, known_confusions: ["Umlaut/diacritics in OCR."]}
  - {id: br_columbia, label: "Columbia", group: outdoor_technical}
  - {id: br_merrell, label: "Merrell", group: outdoor_technical}
  - {id: br_helly_hansen, label: "Helly Hansen", group: outdoor_technical}
  - {id: br_icebreaker, label: "Icebreaker", group: outdoor_technical}

  # --- Denim Spezialisten ---
  - {id: br_levis, label: "Levi's", group: denim_specialist, known_confusions: ["Apostroph fehlt in OCR."]}
  - {id: br_lee, label: "Lee", group: denim_specialist, known_confusions: ["Kurz/ambig, nur matchen wenn Denim-Kontext."]}
  - {id: br_wrangler, label: "Wrangler", group: denim_specialist}
  - {id: br_diesel, label: "DIESEL", group: denim_specialist}
  - {id: br_g_star_raw, label: "G-Star RAW", group: denim_specialist, known_confusions: ["Bindestrich/Space Varianten."]}
  - {id: br_replay, label: "REPLAY", group: denim_specialist}
  - {id: br_nudie_jeans, label: "Nudie Jeans", group: denim_specialist}
  - {id: br_kings_of_indigo, label: "Kings of Indigo", group: denim_specialist}

  # --- Sustainable Focus (Auswahl) ---
  - {id: br_hessnatur, label: "hessnatur", group: sustainable_focused}
  - {id: br_armedangels, label: "ARMEDANGELS", group: sustainable_focused}
  - {id: br_knowledgecotton_apparel, label: "KnowledgeCotton Apparel", group: sustainable_focused}
  - {id: br_people_tree, label: "People Tree", group: sustainable_focused}
  - {id: br_veja, label: "VEJA", group: sustainable_focused}
  - {id: br_allbirds, label: "Allbirds", group: sustainable_focused}
  - {id: br_reformation, label: "Reformation", group: sustainable_focused}

  # --- Fast Fashion / High Street ---
  - {id: br_hm, label: "H&M", group: value_fast_fashion}
  - {id: br_zara, label: "Zara", group: value_fast_fashion}
  - {id: br_mango, label: "Mango", group: value_fast_fashion}
  - {id: br_canda, label: "C&A", group: value_fast_fashion}
  - {id: br_uniqlo, label: "UNIQLO", group: value_fast_fashion}
  - {id: br_reserved, label: "Reserved", group: value_fast_fashion}
  - {id: br_bershka, label: "Bershka", group: value_fast_fashion}
  - {id: br_pull_and_bear, label: "Pull&Bear", group: value_fast_fashion}
  - {id: br_stradivarius, label: "Stradivarius", group: value_fast_fashion}
  - {id: br_primark, label: "Primark", group: value_fast_fashion}

  # --- Contemporary / Smart Casual ---
  - {id: br_marc_o_polo, label: "Marc O'Polo", tier: mid, common_categories: ["cat_apparel", "cat_accessories"], known_confusions: ["Apostroph/Format-Varianten."]}
  - {id: br_tom_tailor, label: "TOM TAILOR", tier: mid, common_categories: ["cat_apparel", "cat_accessories"]}
  - {id: br_esprit, label: "Esprit", tier: mid, common_categories: ["cat_apparel", "cat_accessories"]}
  - {id: br_s_oliver, label: "s.Oliver", tier: mid, common_categories: ["cat_apparel", "cat_accessories"], known_confusions: ["Punkt/Case-Varianten."]}
  - {id: br_selected, label: "SELECTED", tier: mid, common_categories: ["cat_apparel"], known_confusions: ["Wort 'selected' in Text ≠ Brand, nur wenn eindeutig."]}
  - {id: br_only, label: "ONLY", tier: mid, common_categories: ["cat_apparel"], known_confusions: ["Wort 'only' sehr ambig."]}
  - {id: br_vero_moda, label: "Vero Moda", tier: mid, common_categories: ["cat_apparel"]}
  - {id: br_jack_and_jones, label: "Jack & Jones", tier: mid, common_categories: ["cat_apparel"]}
  - {id: br_cos, label: "COS", tier: mid, common_categories: ["cat_apparel"], known_confusions: ["'cos' als Mathematik/Abkürzung; nur matchen wenn Shop/Label-Kontext."]}
  - {id: br_arket, label: "ARKET", tier: mid, common_categories: ["cat_apparel", "cat_accessories"]}

  # --- Schuhe / Lederwaren ---
  - {id: br_birkenstock, label: "BIRKENSTOCK", tier: mid, common_categories: ["cat_footwear"]}
  - {id: br_dr_martens, label: "Dr. Martens", tier: mid, common_categories: ["cat_footwear"], known_confusions: ["Punkt/Space-Varianten."]}
  - {id: br_clarks, label: "Clarks", tier: mid, common_categories: ["cat_footwear"]}
  - {id: br_ecco, label: "ECCO", tier: mid, common_categories: ["cat_footwear"]}
  - {id: br_geox, label: "GEOX", tier: mid, common_categories: ["cat_footwear"]}
  - {id: br_gabor, label: "Gabor", tier: mid, common_categories: ["cat_footwear"]}
  - {id: br_tamaris, label: "Tamaris", tier: mid, common_categories: ["cat_footwear"]}
  - {id: br_vans, label: "Vans", tier: mid, common_categories: ["cat_footwear", "cat_accessories"]}
  - {id: br_converse, label: "Converse", tier: mid, common_categories: ["cat_footwear"]}
  - {id: br_common_projects, label: "Common Projects", group: luxury_designer, common_categories: ["cat_footwear"]}

  # --- Strümpfe / Hosiery ---
  - {id: br_falke, label: "FALKE", tier: premium, common_categories: ["cat_apparel_underwear", "cat_accessories"]}
  - {id: br_wolford, label: "Wolford", tier: premium, common_categories: ["cat_apparel_underwear", "cat_accessories"]}
  - {id: br_kunert, label: "KUNERT", tier: mid, common_categories: ["cat_apparel_underwear", "cat_accessories"]}
  - {id: br_hudson, label: "Hudson", tier: mid, common_categories: ["cat_apparel_underwear", "cat_accessories"]}

  # --- Luxus/Designer (Auswahl, erweiterbar) ---
  - {id: br_gucci, label: "Gucci", group: luxury_designer}
  - {id: br_prada, label: "Prada", group: luxury_designer}
  - {id: br_louis_vuitton, label: "Louis Vuitton", group: luxury_designer}
  - {id: br_chanel, label: "Chanel", group: luxury_designer}
  - {id: br_dior, label: "Dior", group: luxury_designer}
  - {id: br_burberry, label: "Burberry", group: luxury_designer}
  - {id: br_moncler, label: "Moncler", group: luxury_designer}
  - {id: br_canada_goose, label: "Canada Goose", group: luxury_designer}
  - {id: br_saint_laurent, label: "Saint Laurent", group: luxury_designer}
  - {id: br_balenciaga, label: "Balenciaga", group: luxury_designer}
  - {id: br_givenchy, label: "Givenchy", group: luxury_designer}
  - {id: br_fendi, label: "Fendi", group: luxury_designer}
  - {id: br_valentino, label: "Valentino", group: luxury_designer}
  - {id: br_stella_mccartney, label: "Stella McCartney", group: luxury_designer}

  # --- Uhren (Accessoires; optional, aber praktisch) ---
  - {id: br_casio, label: "Casio", tier: mid, common_categories: ["cat_accessories", "cat_accessories_watches_optional"]}
  - {id: br_seiko, label: "Seiko", tier: mid, common_categories: ["cat_accessories", "cat_accessories_watches_optional"]}
  - {id: br_tissot, label: "Tissot", tier: premium, common_categories: ["cat_accessories", "cat_accessories_watches_optional"]}
  - {id: br_omega, label: "Omega", group: luxury_designer, common_categories: ["cat_accessories_watches_optional"]}
  - {id: br_rolex, label: "Rolex", group: luxury_designer, common_categories: ["cat_accessories_watches_optional"]}
  - {id: br_apple, label: "Apple", tier: premium, common_categories: ["cat_accessories_watches_optional"], known_confusions: ["Watch-Brand vs Hersteller; nur bei Smartwatch."]}
  - {id: br_garmin, label: "Garmin", tier: premium, common_categories: ["cat_accessories_watches_optional"], known_confusions: ["Outdoor/GPS; häufig Smartwatch."]}

  # --- Amazon Eigenmarken (relevant fürs RAG) ---
  - {id: br_amazon_essentials, label: "Amazon Essentials", tier: budget, common_categories: ["cat_apparel", "cat_accessories"], known_confusions: ["Nicht = Amazon (Shop)."]}
  - {id: br_find, label: "FIND", tier: budget, common_categories: ["cat_apparel"], known_confusions: ["Wort 'find' extrem ambig."]}

  # --- (Weitere Brands: bewusst als lange Liste, ohne Wiederholung von Feldern) ---
  - {id: br_joop, label: "JOOP!", group: premium_business, known_confusions: ["Ausrufezeichen kann in OCR fehlen."]}
  - {id: br_lacoste, label: "Lacoste", tier: premium, common_categories: ["cat_apparel", "cat_accessories", "cat_footwear"]}
  - {id: br_polo_ralph_lauren, label: "Polo Ralph Lauren", tier: premium, common_categories: ["cat_apparel", "cat_accessories"], known_confusions: ["'Polo' allein kann Item sein."]}
  - {id: br_ralph_lauren, label: "Ralph Lauren", tier: premium, common_categories: ["cat_apparel", "cat_accessories"]}
  - {id: br_calvin_klein, label: "Calvin Klein", tier: premium, common_categories: ["cat_apparel", "cat_apparel_underwear", "cat_accessories"]}
  - {id: br_tommy_hilfiger, label: "Tommy Hilfiger", tier: premium, common_categories: ["cat_apparel", "cat_accessories", "cat_footwear"]}
  - {id: br_gant, label: "GANT", tier: premium, common_categories: ["cat_apparel", "cat_accessories"]}
  - {id: br_barbour, label: "Barbour", tier: premium, common_categories: ["cat_apparel", "cat_accessories"]}
  - {id: br_stone_island, label: "Stone Island", group: luxury_designer}
  - {id: br_cp_company, label: "C.P. Company", group: luxury_designer, known_confusions: ["Punkte können fehlen."]}
  - {id: br_massimo_dutti, label: "Massimo Dutti", tier: mid, common_categories: ["cat_apparel", "cat_accessories"]}
  - {id: br_weekday, label: "Weekday", tier: mid, common_categories: ["cat_apparel"]}
  - {id: br_levi_strauss_signature, label: "Signature by Levi Strauss & Co.", tier: budget, common_categories: ["cat_apparel"], known_confusions: ["Langer Name, OCR bricht ab."]}

  # Hinweis: Der Katalog ist absichtlich offen erweiterbar.
  # Empfohlen: künftig pro Nutzer-Schrank häufige Brands als "hot list" zusätzlich pflegen.

# ------------------------------------------------------------
# (F) Top Ambiguitäten: Brand vs Shop vs Attribut (Kurzliste)
# ------------------------------------------------------------
top_brand_shop_ambiguities:
  - ambiguity: "Global Kent"
    correct_field: "attr_collar_type"
    never: ["attr_brand"]
    hint: "Wenn 'Kent' im Hemd-Kontext → collar_type; niemals Brand."
  - ambiguity: "Amazon Essentials"
    correct_field: "attr_brand"
    never: ["attr_shop=Amazon Essentials"]
    hint: "Shop bleibt Amazon; Brand ist Amazon Essentials."
  - ambiguity: "On"
    correct_field: "attr_brand"
    hint: "Nur bei Sport/Logo/Schuh-Kontext; sonst ignorieren."
  - ambiguity: "Selected / Only / Find"
    correct_field: "attr_brand"
    hint: "Nur matchen, wenn Shop-Brand-Feld oder Label/OCR; im Fließtext sehr ambig."



**Web-basierte Qualitätsanker (für die Shop-Facet-Logik in Part 07):**  
- Zalando-Produktseiten zeigen strukturierte Blöcke wie **„Material & Pflegehinweise“** sowie **Fit/Passform** und Größen-/Model-Infos. :contentReference[oaicite:0]{index=0}  
- ABOUT YOU arbeitet u. a. mit **Sondergrößen** und verweist auf **Größentabellen/Größenberater**. :contentReference[oaicite:1]{index=1}  
- Breuninger bietet einen expliziten **Größenberater** („Welche Größe passt mir?“) auf Produktseiten. :contentReference[oaicite:2]{index=2}  
- bonprix nutzt viele strukturierte Felder wie **Passform, Länge, Ärmellänge, Kragenart** und teils „Besonderes Material“. :contentReference[oaicite:3]{index=3}  
- hessnatur markiert **GOTS**-zertifizierte Artikel auf Produkt-/Qualitätsseiten sichtbar. :contentReference[oaicite:4]{index=4}
::contentReference[oaicite:5]{index=5}

