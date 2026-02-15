
```markdown
<!-- FILE: ontology_part_04_attributes_value_sets_core.md -->
# Part 04 – Attribute-Lexikon (attribute) & Value-Sets (Grundstruktur)
version: "0.9.0"
date: "2026-01-12"
scope: "DB-Felder (= Wahrheit) + zentrale Enums"
toc:
  - attributes
  - value_sets (Kern)

```yaml
attributes:
  # 1) Identität & Herkunft
  - id: attr_brand
    label_de: "Marke"
    description_de: "Hersteller-/Markenname (normalisiert über brand-Verzeichnis)."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["exakt Markenname", "Brand-Logo", "Text: 'Marke: ...'"]
    negative_patterns: ["Kragenformen", "Passformen", "Materialien ohne Markenbezug"]
    extraction_priority: 5
    common_source_fields: ["Marke", "Brand", "Hersteller", "Label"]

  - id: attr_model_name
    label_de: "Modell-/Produktname"
    description_de: "Produktlinie/Modellbezeichnung (z. B. 'Luxor', 'Level Five')."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["Groß-/Kleinschreibung gemischt", "oft in Titel/Headline"]
    negative_patterns: ["reine Kategoriebegriffe wie 'Hemd'"]
    extraction_priority: 3
    common_source_fields: ["Produktname", "Artikelname", "Titel"]

  - id: attr_shop
    label_de: "Shop/Plattform"
    description_de: "Bezugsquelle (z. B. Zalando, OTTO, Amazon, hessnatur)."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["Domain/Shopname", "Marketplace"]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Shop", "Verkäufer", "Händler"]

  - id: attr_url
    label_de: "Produkt-URL"
    description_de: "Quelle für Web-Import."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["http(s)://..."]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["URL", "Link"]

  - id: attr_sku
    label_de: "Artikelnummer/SKU"
    description_de: "Interne Artikelnummer, EAN, Style-ID."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["Alphanumerisch", "EAN-13", "Style-ID"]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Artikelnummer", "SKU", "EAN", "Style"]

  # 2) Größen & Maße
  - id: attr_size_system
    label_de: "Größensystem"
    description_de: "Wie die Größe kodiert ist (alpha, EU numerisch, W/L, Schuhgrößen etc.)."
    data_type: "enum"
    unit: null
    allowed_values: "vs_size_system"
    value_patterns: ["S/M/L/XL", "EU 46/48", "W32/L34", "Schuh 42", "One Size"]
    negative_patterns: []
    extraction_priority: 5
    common_source_fields: ["Größe", "Size", "Größenangabe"]

  - id: attr_size_label_raw
    label_de: "Größe (raw)"
    description_de: "Originaltext der Größe aus Quelle/Etikett."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["beliebiger Text"]
    negative_patterns: []
    extraction_priority: 5
    common_source_fields: ["Größe", "Size", "Label"]

  - id: attr_size_normalized
    label_de: "Größe (normalisiert)"
    description_de: "Kanonische Größe passend zu attr_size_system."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["alpha_l", "eu_48", "w32_l34", "shoe_eu_42"]
    negative_patterns: []
    extraction_priority: 5
    common_source_fields: ["intern berechnet"]

  - id: attr_body_measurements_cm
    label_de: "Körper-/Artikelmaße (cm)"
    description_de: "Objekt mit Maßen (z. B. Brust, Taille, Hüfte, Hals, Innenbein, Armlänge)."
    data_type: "object"
    unit: "cm"
    allowed_values: null
    value_patterns: ["{chest: 100, waist: 84, ...}"]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Größentabelle", "Maße", "Size guide"]

  - id: attr_special_size_type
    label_de: "Sondergrößentyp"
    description_de: "petite/short/regular/long/tall/plus/maternity."
    data_type: "enum"
    unit: null
    allowed_values: "vs_special_size_type"
    value_patterns: ["Short", "Long", "Tall", "Petite", "Plus", "Umstand"]
    negative_patterns: []
    extraction_priority: 3
    common_source_fields: ["Größenwahl", "Längen", "Sondergrößen"]

  # 3) Farben & Muster
  - id: attr_color_primary
    label_de: "Primärfarbe"
    description_de: "Dominante Farbe (präziser Name)."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["navy", "schwarz", "hellblau", "cognac"]
    negative_patterns: ["Materialien", "Marken"]
    extraction_priority: 4
    common_source_fields: ["Farbe", "Color", "Farbname"]

  - id: attr_color_secondary
    label_de: "Sekundärfarbe"
    description_de: "Zweite dominante Farbe (falls relevant)."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["weiß", "gold", "rot"]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Farbe", "Color"]

  - id: attr_color_family
    label_de: "Farbfamilie"
    description_de: "Kontrollierte grobe Farbgruppe."
    data_type: "enum"
    unit: null
    allowed_values: "vs_color_family"
    value_patterns: ["schwarz/weiß/blau/rot/grün/braun/beige/grau/bunt/metallic/pastell"]
    negative_patterns: []
    extraction_priority: 4
    common_source_fields: ["Farbe", "Color", "Filter: Farbe"]

  - id: attr_multicolor_flag
    label_de: "Mehrfarbig-Flag"
    description_de: "true, wenn mehrere dominante Farben oder starkes Muster."
    data_type: "boolean"
    unit: null
    allowed_values: null
    value_patterns: ["true/false"]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Mehrfarbig", "Multicolor"]

  - id: attr_color_confidence
    label_de: "Farb-Konfidenz"
    description_de: "0..1, für Vision-Korrekturen (z. B. Pailletten)."
    data_type: "number"
    unit: null
    allowed_values: null
    value_patterns: ["0.0 - 1.0"]
    negative_patterns: []
    extraction_priority: 1
    common_source_fields: ["intern berechnet"]

  - id: attr_pattern
    label_de: "Muster"
    description_de: "Kontrolliertes Muster/Print."
    data_type: "enum"
    unit: null
    allowed_values: "vs_pattern"
    value_patterns: ["uni", "gestreift", "kariert", "floral", "gepunktet", "animal", "print", "meliert", "used", "jacquard"]
    negative_patterns: []
    extraction_priority: 3
    common_source_fields: ["Muster", "Print", "Pattern", "Details"]

  # 4) Materialien
  - id: attr_material_main
    label_de: "Hauptmaterial"
    description_de: "Material mit höchstem Anteil."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["Baumwolle", "Schurwolle", "Polyester", "Leder"]
    negative_patterns: []
    extraction_priority: 4
    common_source_fields: ["Material", "Oberstoff"]

  - id: attr_material_composition
    label_de: "Materialzusammensetzung"
    description_de: "Array aus Materialanteilen in Prozent."
    data_type: "array"
    unit: "percent"
    allowed_values: null
    value_patterns: ["[{material_id: mat_cotton, percent: 98}, {material_id: mat_elastane, percent: 2}]"]
    negative_patterns: []
    extraction_priority: 5
    common_source_fields: ["Material & Pflegehinweise", "Material", "Composition", "Oberstoff"]

  - id: attr_lining_material
    label_de: "Futter/Innenmaterial"
    description_de: "Material des Futters (wenn vorhanden)."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["Viskosefutter", "Polyesterfutter"]
    negative_patterns: []
    extraction_priority: 3
    common_source_fields: ["Futter", "Innenfutter", "Lining"]

  - id: attr_upper_material
    label_de: "Obermaterial (Schuhe)"
    description_de: "Material des Schuh-Uppers."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["Glattleder", "Veloursleder", "Textil", "Synthetik"]
    negative_patterns: []
    extraction_priority: 4
    common_source_fields: ["Obermaterial", "Upper"]

  - id: attr_sole_material
    label_de: "Sohlenmaterial"
    description_de: "Material der Sohle."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["Gummi", "TPR", "PU", "Leder"]
    negative_patterns: []
    extraction_priority: 3
    common_source_fields: ["Sohle", "Outsole"]

  - id: attr_stretch_percent
    label_de: "Stretch-Anteil (%)"
    description_de: "Optionaler Stretch-Anteil (oder aus Elasthan ableitbar)."
    data_type: "number"
    unit: "percent"
    allowed_values: null
    value_patterns: ["0-30"]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Stretch", "Elasthan", "Spandex"]

  # 5) Pflege
  - id: attr_care_instructions_text
    label_de: "Pflegehinweise (Text)"
    description_de: "Textuelle Pflegehinweise aus Etikett/Shop."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["Schonwaschgang", "nicht trocknergeeignet", "chemische Reinigung"]
    negative_patterns: []
    extraction_priority: 4
    common_source_fields: ["Pflegehinweise", "Care instructions", "Material & Pflegehinweise"]

  - id: attr_iron_allowed
    label_de: "Bügeln erlaubt"
    description_de: "true/false nach Pflegeetikett."
    data_type: "boolean"
    unit: null
    allowed_values: null
    value_patterns: []
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Pflegehinweise", "Symbole"]

  - id: attr_tumble_dry_allowed
    label_de: "Trockner erlaubt"
    description_de: "true/false nach Pflegeetikett."
    data_type: "boolean"
    unit: null
    allowed_values: null
    value_patterns: []
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Pflegehinweise", "Symbole"]

  - id: attr_dry_clean_only
    label_de: "Nur chemische Reinigung"
    description_de: "true, wenn 'chemische Reinigung' gefordert."
    data_type: "boolean"
    unit: null
    allowed_values: null
    value_patterns: ["Text: 'chemische Reinigung'", "dry clean only"]
    negative_patterns: []
    extraction_priority: 3
    common_source_fields: ["Pflegehinweise", "Care"]

  # 6) Passform & Schnitt (Auswahl; Details in Part 06)
  - id: attr_fit_type
    label_de: "Passform (Fit)"
    description_de: "Slim/Regular/Comfort/Modern/Oversized/etc."
    data_type: "enum"
    unit: null
    allowed_values: "vs_fit_type"
    value_patterns: ["slim fit", "regular fit", "comfort fit", "modern fit", "oversized"]
    negative_patterns: []
    extraction_priority: 4
    common_source_fields: ["Passform", "Fit", "Schnitt"]

  - id: attr_rise
    label_de: "Bundhöhe (Rise)"
    description_de: "low/mid/high."
    data_type: "enum"
    unit: null
    allowed_values: "vs_rise"
    value_patterns: ["high waist", "mid rise", "low rise"]
    negative_patterns: []
    extraction_priority: 3
    common_source_fields: ["Bundhöhe", "Rise", "High Waist"]

  - id: attr_leg_shape
    label_de: "Beinform"
    description_de: "skinny/slim/straight/tapered/wide/bootcut/flared."
    data_type: "enum"
    unit: null
    allowed_values: "vs_leg_shape"
    value_patterns: ["skinny", "straight", "wide leg", "bootcut"]
    negative_patterns: []
    extraction_priority: 3
    common_source_fields: ["Schnitt", "Leg", "Fit"]

  - id: attr_collar_type
    label_de: "Kragenform"
    description_de: "Kragenform bei Hemden/Blusen/Polos."
    data_type: "enum"
    unit: null
    allowed_values: "vs_collar_type"
    value_patterns: ["Kent", "Global Kent", "Haifisch", "Button-Down", "Stehkragen"]
    negative_patterns: ["Markenliste"]
    extraction_priority: 4
    common_source_fields: ["Kragen", "Collar", "Details"]

  - id: attr_neckline
    label_de: "Ausschnitt"
    description_de: "Rundhals/V/Boat/etc."
    data_type: "enum"
    unit: null
    allowed_values: "vs_neckline"
    value_patterns: ["Rundhals", "V-Ausschnitt", "U-Boot", "Herz", "Carré"]
    negative_patterns: []
    extraction_priority: 3
    common_source_fields: ["Ausschnitt", "Neckline"]

  - id: attr_sleeve_length
    label_de: "Ärmellänge"
    description_de: "ärmellos/kurz/3-4/lang."
    data_type: "enum"
    unit: null
    allowed_values: "vs_sleeve_length"
    value_patterns: ["Kurzarm", "Langarm", "ärmellos", "3/4"]
    negative_patterns: []
    extraction_priority: 4
    common_source_fields: ["Ärmel", "Sleeve"]

  - id: attr_cuff_type
    label_de: "Manschettenart"
    description_de: "Sportmanschette/Kombimanschette/etc."
    data_type: "enum"
    unit: null
    allowed_values: "vs_cuff_type"
    value_patterns: ["Kombimanschette", "Sportmanschette", "Umschlagmanschette"]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Manschette", "Cuff"]

  - id: attr_silhouette
    label_de: "Silhouette/Form"
    description_de: "A-Linie/Etui/Schlauch/Fit&Flare/Empire/etc."
    data_type: "enum"
    unit: null
    allowed_values: "vs_silhouette"
    value_patterns: ["A-Linie", "Etui", "Schlauch", "Fit & Flare", "Empire"]
    negative_patterns: []
    extraction_priority: 3
    common_source_fields: ["Schnitt", "Silhouette", "Passform"]

  - id: attr_length_category
    label_de: "Längenkategorie"
    description_de: "kurz/knielang/midi/lang/maxi."
    data_type: "enum"
    unit: null
    allowed_values: "vs_length_category"
    value_patterns: ["kurz", "midi", "maxi", "knielang"]
    negative_patterns: []
    extraction_priority: 3
    common_source_fields: ["Länge", "Length"]

  # 7) Funktionen
  - id: attr_function_waterproof
    label_de: "Wasserdicht"
    description_de: "true, wenn wasserdicht (nicht nur wasserabweisend)."
    data_type: "boolean"
    unit: null
    allowed_values: null
    value_patterns: ["wasserdicht", "waterproof"]
    negative_patterns: ["wasserabweisend (separat)"]
    extraction_priority: 3
    common_source_fields: ["Funktion", "Features", "Details"]

  - id: attr_function_breathable
    label_de: "Atmungsaktiv"
    description_de: "true, wenn als atmungsaktiv ausgewiesen."
    data_type: "boolean"
    unit: null
    allowed_values: null
    value_patterns: ["atmungsaktiv", "breathable"]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Funktion", "Features"]

  - id: attr_function_windproof
    label_de: "Winddicht"
    description_de: "true, wenn winddicht."
    data_type: "boolean"
    unit: null
    allowed_values: null
    value_patterns: ["winddicht", "windproof"]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Funktion", "Features"]

  - id: attr_season
    label_de: "Saison"
    description_de: "SS/FW/all-season."
    data_type: "enum"
    unit: null
    allowed_values: "vs_season"
    value_patterns: ["Sommer", "Winter", "Ganzjahr", "Übergang"]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Saison", "Season"]

  - id: attr_activity
    label_de: "Aktivität (Sport/Outdoor)"
    description_de: "Running/Trekking/Ski/etc."
    data_type: "enum"
    unit: null
    allowed_values: "vs_activity"
    value_patterns: ["Running", "Trekking", "Ski", "Yoga", "Training"]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Sportart", "Activity"]

  # 8) Nachhaltigkeit
  - id: attr_certifications
    label_de: "Zertifikate"
    description_de: "Array mit Zertifikaten (IDs)."
    data_type: "array"
    unit: null
    allowed_values: null
    value_patterns: ["[cert_gots, cert_oeko_tex_100]"]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Nachhaltigkeit", "Zertifikate", "Labels"]

  - id: attr_sustainability_score_1to5
    label_de: "Nachhaltigkeits-Score (1..5)"
    description_de: "Transparenter Score aus Material + Zertifikaten (Heuristik)."
    data_type: "number"
    unit: null
    allowed_values: null
    value_patterns: ["1-5"]
    negative_patterns: []
    extraction_priority: 1
    common_source_fields: ["intern berechnet"]

  - id: attr_longevity_notes
    label_de: "Hinweise zur Langlebigkeit"
    description_de: "Kurznotiz zu Haltbarkeit/Reparatur."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: []
    negative_patterns: []
    extraction_priority: 1
    common_source_fields: ["intern/Notizen"]

  # Zusätzliche allgemeine Attribute (kompakt)
  - id: attr_closure_type
    label_de: "Verschlussart"
    description_de: "Knopf, Reißverschluss, Schnürung, Schlupf, Klett."
    data_type: "enum"
    unit: null
    allowed_values: "vs_closure_type"
    value_patterns: ["Knopf", "Reißverschluss", "Schnürung", "Klett", "Schlupf"]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Verschluss", "Closure", "Details"]

  - id: attr_hood
    label_de: "Kapuze"
    description_de: "true, wenn Kapuze vorhanden."
    data_type: "boolean"
    unit: null
    allowed_values: null
    value_patterns: ["Kapuze", "hood"]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Details", "Features"]

  - id: attr_occasion
    label_de: "Anlass"
    description_de: "Business/Casual/Formal/Outdoor/Party/Workwear."
    data_type: "enum"
    unit: null
    allowed_values: "vs_occasion"
    value_patterns: ["Business", "Casual", "Formal", "Outdoor", "Party"]
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Anlass", "Style", "Occasion"]

  - id: attr_style
    label_de: "Stil"
    description_de: "Streetwear, Classic, Minimal, etc. (kontrolliert)."
    data_type: "enum"
    unit: null
    allowed_values: "vs_style"
    value_patterns: ["Classic", "Streetwear", "Minimal", "Preppy", "Athleisure"]
    negative_patterns: []
    extraction_priority: 1
    common_source_fields: ["Style", "Look"]

  # Schuh-spezifische Attribute (Auswahl)
  - id: attr_toe_shape
    label_de: "Schuhspitzenform"
    description_de: "rund/spitz/mandel/eckig."
    data_type: "enum"
    unit: null
    allowed_values: "vs_toe_shape"
    value_patterns: ["rund", "spitz", "eckig"]
    negative_patterns: []
    extraction_priority: 1
    common_source_fields: ["Details"]

  - id: attr_heel_height_cm
    label_de: "Absatzhöhe (cm)"
    description_de: "Absatzhöhe für Schuhe."
    data_type: "number"
    unit: "cm"
    allowed_values: null
    value_patterns: ["0-15"]
    negative_patterns: []
    extraction_priority: 1
    common_source_fields: ["Absatzhöhe", "Heel height"]

  - id: attr_shaft_height
    label_de: "Schaft-/Stiefelhöhe"
    description_de: "Kurz/mittel/hoch oder cm."
    data_type: "enum"
    unit: null
    allowed_values: "vs_shaft_height"
    value_patterns: ["kurz", "mittel", "hoch"]
    negative_patterns: []
    extraction_priority: 1
    common_source_fields: ["Schaft", "Shaft"]

  - id: attr_sole_profile
    label_de: "Sohlenprofil"
    description_de: "glatt/leicht/profil/stark."
    data_type: "enum"
    unit: null
    allowed_values: "vs_sole_profile"
    value_patterns: ["glatt", "profil", "starkes Profil"]
    negative_patterns: []
    extraction_priority: 1
    common_source_fields: ["Sohle", "Profil"]

  # Accessoire-Attribute (Auswahl)
  - id: attr_length_cm
    label_de: "Länge (cm)"
    description_de: "Gürtel/Schal etc."
    data_type: "number"
    unit: "cm"
    allowed_values: null
    value_patterns: []
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Länge"]

  - id: attr_width_cm
    label_de: "Breite (cm)"
    description_de: "Gürtelbreite etc."
    data_type: "number"
    unit: "cm"
    allowed_values: null
    value_patterns: []
    negative_patterns: []
    extraction_priority: 2
    common_source_fields: ["Breite"]

  - id: attr_buckle_material
    label_de: "Schnallenmaterial"
    description_de: "Metall/legiert/etc."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["Edelstahl", "Messing", "Zinklegierung"]
    negative_patterns: []
    extraction_priority: 1
    common_source_fields: ["Schnalle"]

  - id: attr_case_material
    label_de: "Uhrengehäuse-Material"
    description_de: "Material des Gehäuses."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["Edelstahl", "Titan", "Kunststoff"]
    negative_patterns: []
    extraction_priority: 1
    common_source_fields: ["Gehäuse"]

  - id: attr_strap_material
    label_de: "Armband-Material"
    description_de: "Leder/Metall/Silikon/Textil."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["Leder", "Edelstahl", "Silikon", "NATO-Band"]
    negative_patterns: []
    extraction_priority: 1
    common_source_fields: ["Armband"]

  - id: attr_water_resistance
    label_de: "Wasserdichtigkeit (Uhr)"
    description_de: "z. B. 3 ATM, 5 ATM, 10 ATM."
    data_type: "string"
    unit: null
    allowed_values: null
    value_patterns: ["ATM", "bar", "m"]
    negative_patterns: []
    extraction_priority: 1
    common_source_fields: ["Wasserdichtigkeit", "Water resistance"]

  - id: attr_touchscreen_compatible
    label_de: "Touchscreen-kompatibel"
    description_de: "true bei Touchscreen-Handschuhen."
    data_type: "boolean"
    unit: null
    allowed_values: null
    value_patterns: ["touch", "touchscreen", "smartphone"]
    negative_patterns: []
    extraction_priority: 1
    common_source_fields: ["Feature", "Details"]

value_sets:
  - id: vs_size_system
    description_de: "Größensysteme"
    values:
      - value: alpha
        synonyms_de: ["S/M/L/XL", "Buchstabengröße"]
        notes_de: "z. B. S, M, L, XL, XXL"
      - value: numeric_eu
        synonyms_de: ["EU", "Konfektionsgröße"]
        notes_de: "z. B. 34-54"
      - value: waist_inseam
        synonyms_de: ["W/L", "W32/L34", "inch"]
        notes_de: "Taille/Innenbein"
      - value: shoe_eu
        synonyms_de: ["EU Schuhgröße"]
        notes_de: "z. B. 36-47"
      - value: shoe_uk
        synonyms_de: ["UK"]
        notes_de: ""
      - value: shoe_us
        synonyms_de: ["US"]
        notes_de: ""
      - value: one_size
        synonyms_de: ["One Size", "OS", "Einheitsgröße"]
        notes_de: ""
      - value: kids
        synonyms_de: ["Kindergröße", "116", "128"]
        notes_de: "oft Körpergröße in cm"

  - id: vs_special_size_type
    description_de: "Sondergrößen/Längen"
    values:
      - value: petite
        synonyms_de: ["Kurzgröße", "Petite"]
        notes_de: ""
      - value: short
        synonyms_de: ["Short", "kurz"]
        notes_de: "häufig bei W/L"
      - value: regular
        synonyms_de: ["Regular", "normal"]
        notes_de: ""
      - value: long
        synonyms_de: ["Long", "lang"]
        notes_de: ""
      - value: tall
        synonyms_de: ["Tall", "extra lang"]
        notes_de: ""
      - value: plus
        synonyms_de: ["Plus Size", "Große Größen"]
        notes_de: ""
      - value: maternity
        synonyms_de: ["Umstandsmode", "Maternity"]
        notes_de: ""

  - id: vs_color_family
    description_de: "Farbfamilien (kontrolliert)"
    values:
      - value: black
        synonyms_de: ["schwarz"]
        notes_de: ""
      - value: white
        synonyms_de: ["weiß", "offwhite", "creme"]
        notes_de: ""
      - value: grey
        synonyms_de: ["grau", "anthrazit"]
        notes_de: ""
      - value: blue
        synonyms_de: ["blau", "navy", "jeansblau"]
        notes_de: ""
      - value: red
        synonyms_de: ["rot", "bordeaux"]
        notes_de: ""
      - value: green
        synonyms_de: ["grün", "oliv", "khaki"]
        notes_de: ""
      - value: brown
        synonyms_de: ["braun", "cognac"]
        notes_de: ""
      - value: beige
        synonyms_de: ["beige", "sand", "camel"]
        notes_de: ""
      - value: yellow_orange
        synonyms_de: ["gelb", "orange", "senf"]
        notes_de: ""
      - value: purple_pink
        synonyms_de: ["lila", "pink", "magenta"]
        notes_de: ""
      - value: metallic
        synonyms_de: ["silber", "gold", "metallic"]
        notes_de: "Achtung: Reflexion kann Vision täuschen"
      - value: multicolor
        synonyms_de: ["bunt", "mehrfarbig"]
        notes_de: ""

  - id: vs_pattern
    description_de: "Muster/Print"
    values:
      - value: solid
        synonyms_de: ["uni", "einfarbig"]
        notes_de: ""
      - value: striped
        synonyms_de: ["gestreift"]
        notes_de: ""
      - value: checked
        synonyms_de: ["kariert", "karo"]
        notes_de: ""
      - value: floral
        synonyms_de: ["blumen", "floral"]
        notes_de: ""
      - value: polka_dot
        synonyms_de: ["gepunktet", "punkte"]
        notes_de: ""
      - value: animal
        synonyms_de: ["leo", "zebra", "animal print"]
        notes_de: ""
      - value: print
        synonyms_de: ["print", "grafisch", "logo"]
        notes_de: ""
      - value: melange
        synonyms_de: ["meliert"]
        notes_de: ""
      - value: used
        synonyms_de: ["used", "washed", "destroyed"]
        notes_de: "oft Denim"
      - value: jacquard
        synonyms_de: ["jacquard"]
        notes_de: ""

  - id: vs_fit_type
    description_de: "Passformen (generisch)"
    values:
      - value: slim
        synonyms_de: ["Slim Fit", "körpernah"]
        notes_de: ""
      - value: super_slim
        synonyms_de: ["Super Slim", "extra slim", "body fit"]
        notes_de: ""
      - value: regular
        synonyms_de: ["Regular Fit", "klassisch"]
        notes_de: ""
      - value: modern
        synonyms_de: ["Modern Fit"]
        notes_de: "zwischen slim und regular"
      - value: comfort
        synonyms_de: ["Comfort Fit", "bequem", "weit"]
        notes_de: ""
      - value: oversized
        synonyms_de: ["Oversized", "loose"]
        notes_de: ""
      - value: athletic
        synonyms_de: ["Athletic Fit"]
        notes_de: "mehr Raum an Oberschenkel/Brust"
      - value: relaxed
        synonyms_de: ["Relaxed Fit"]
        notes_de: ""

  - id: vs_rise
    description_de: "Bundhöhe"
    values:
      - value: low
        synonyms_de: ["Low Rise", "niedrig"]
        notes_de: ""
      - value: mid
        synonyms_de: ["Mid Rise", "normal"]
        notes_de: ""
      - value: high
        synonyms_de: ["High Rise", "High Waist", "hoch"]
        notes_de: ""

  - id: vs_leg_shape
    description_de: "Beinform (Hosen)"
    values:
      - value: skinny
        synonyms_de: ["Skinny"]
        notes_de: ""
      - value: slim
        synonyms_de: ["Slim"]
        notes_de: ""
      - value: straight
        synonyms_de: ["Straight", "gerade"]
        notes_de: ""
      - value: tapered
        synonyms_de: ["Tapered", "zulaufend"]
        notes_de: ""
      - value: wide
        synonyms_de: ["Wide Leg", "weit"]
        notes_de: ""
      - value: bootcut
        synonyms_de: ["Bootcut"]
        notes_de: ""
      - value: flared
        synonyms_de: ["Flared", "Schlaghose"]
        notes_de: ""

  - id: vs_collar_type
    description_de: "Kragenformen (Hemden/Blusen/Polos)"
    values:
      - value: kent
        synonyms_de: ["Kentkragen", "Kent"]
        notes_de: ""
      - value: global_kent
        synonyms_de: ["Global Kent"]
        notes_de: "Immer Kragenform, nie Marke"
      - value: new_kent
        synonyms_de: ["New Kent"]
        notes_de: ""
      - value: spread_haifisch
        synonyms_de: ["Haifisch", "Spread"]
        notes_de: ""
      - value: button_down
        synonyms_de: ["Button-Down"]
        notes_de: ""
      - value: cutaway
        synonyms_de: ["Cutaway"]
        notes_de: ""
      - value: mandarin
        synonyms_de: ["Stehkragen", "Mandarin"]
        notes_de: ""
      - value: polo
        synonyms_de: ["Polokragen"]
        notes_de: ""
      - value: camp
        synonyms_de: ["Reverskragen", "Camp Collar"]
        notes_de: "häufig bei Sommerhemden"

  - id: vs_neckline
    description_de: "Ausschnitte"
    values:
      - value: crew
        synonyms_de: ["Rundhals"]
        notes_de: ""
      - value: v_neck
        synonyms_de: ["V-Ausschnitt"]
        notes_de: ""
      - value: boat
        synonyms_de: ["U-Boot", "Boat"]
        notes_de: ""
      - value: scoop
        synonyms_de: ["U-Ausschnitt", "Scoop"]
        notes_de: ""
      - value: square
        synonyms_de: ["Carré", "Square"]
        notes_de: ""
      - value: turtleneck
        synonyms_de: ["Rollkragen"]
        notes_de: ""

  - id: vs_sleeve_length
    description_de: "Ärmellängen"
    values:
      - value: sleeveless
        synonyms_de: ["ärmellos"]
        notes_de: ""
      - value: short
        synonyms_de: ["Kurzarm"]
        notes_de: ""
      - value: three_quarter
        synonyms_de: ["3/4", "dreiviertel"]
        notes_de: ""
      - value: long
        synonyms_de: ["Langarm"]
        notes_de: ""

  - id: vs_cuff_type
    description_de: "Manschetten"
    values:
      - value: sport
        synonyms_de: ["Sportmanschette"]
        notes_de: ""
      - value: combi
        synonyms_de: ["Kombimanschette"]
        notes_de: "Knopf oder Manschettenknopf möglich"
      - value: french
        synonyms_de: ["Umschlagmanschette", "French cuff"]
        notes_de: "Manschettenknöpfe"

  - id: vs_silhouette
    description_de: "Silhouetten (Kleider/Röcke)"
    values:
      - value: sheath
        synonyms_de: ["Schlauch", "Sheath"]
        notes_de: ""
      - value: pencil
        synonyms_de: ["Etui", "Bleistift"]
        notes_de: ""
      - value: a_line
        synonyms_de: ["A-Linie"]
        notes_de: ""
      - value: fit_flare
        synonyms_de: ["Fit & Flare"]
        notes_de: ""
      - value: empire
        synonyms_de: ["Empire"]
        notes_de: ""
      - value: wrap
        synonyms_de: ["Wickel", "Wrap"]
        notes_de: ""

  - id: vs_length_category
    description_de: "Längen (generisch)"
    values:
      - value: mini
        synonyms_de: ["mini", "kurz"]
        notes_de: ""
      - value: knee
        synonyms_de: ["knielang"]
        notes_de: ""
      - value: midi
        synonyms_de: ["midi"]
        notes_de: ""
      - value: maxi
        synonyms_de: ["maxi", "lang"]
        notes_de: ""

  - id: vs_season
    description_de: "Saison"
    values:
      - value: ss
        synonyms_de: ["Sommer", "Spring/Summer"]
        notes_de: ""
      - value: fw
        synonyms_de: ["Winter", "Fall/Winter"]
        notes_de: ""
      - value: all_season
        synonyms_de: ["Ganzjahr", "All-season"]
        notes_de: ""

  - id: vs_activity
    description_de: "Aktivität (Sport/Outdoor)"
    values:
      - value: training
        synonyms_de: ["Training", "Gym"]
        notes_de: ""
      - value: running
        synonyms_de: ["Running", "Laufen"]
        notes_de: ""
      - value: hiking_trekking
        synonyms_de: ["Trekking", "Wandern"]
        notes_de: ""
      - value: ski_snow
        synonyms_de: ["Ski", "Snow"]
        notes_de: ""
      - value: yoga
        synonyms_de: ["Yoga", "Pilates"]
        notes_de: ""
      - value: cycling
        synonyms_de: ["Radfahren", "Cycling"]
        notes_de: ""

  - id: vs_closure_type
    description_de: "Verschlussarten"
    values:
      - value: button
        synonyms_de: ["Knopf", "Knopfleiste"]
        notes_de: ""
      - value: zipper
        synonyms_de: ["Reißverschluss", "Zip"]
        notes_de: ""
      - value: lace
        synonyms_de: ["Schnürung", "Schnürsenkel"]
        notes_de: ""
      - value: slip_on
        synonyms_de: ["Schlupf", "Slip-on"]
        notes_de: ""
      - value: velcro
        synonyms_de: ["Klett", "Velcro"]
        notes_de: ""
      - value: buckle
        synonyms_de: ["Schnalle"]
        notes_de: ""

  - id: vs_occasion
    description_de: "Anlass"
    values:
      - value: business
        synonyms_de: ["Business", "Office"]
        notes_de: ""
      - value: casual
        synonyms_de: ["Casual", "Freizeit"]
        notes_de: ""
      - value: formal
        synonyms_de: ["Formal", "Gala", "Black Tie"]
        notes_de: ""
      - value: outdoor
        synonyms_de: ["Outdoor"]
        notes_de: ""
      - value: party
        synonyms_de: ["Party", "Abend"]
        notes_de: ""
      - value: workwear
        synonyms_de: ["Workwear", "Arbeitskleidung"]
        notes_de: ""

  - id: vs_style
    description_de: "Stil (kontrolliert, grob)"
    values:
      - value: classic
        synonyms_de: ["klassisch"]
        notes_de: ""
      - value: minimal
        synonyms_de: ["minimal", "clean"]
        notes_de: ""
      - value: streetwear
        synonyms_de: ["streetwear"]
        notes_de: ""
      - value: preppy
        synonyms_de: ["preppy"]
        notes_de: ""
      - value: athleisure
        synonyms_de: ["athleisure"]
        notes_de: ""
      - value: boho
        synonyms_de: ["boho"]
        notes_de: ""
      - value: vintage
        synonyms_de: ["vintage", "retro"]
        notes_de: ""

  - id: vs_toe_shape
    description_de: "Schuhspitzenform"
    values:
      - value: round
        synonyms_de: ["rund"]
        notes_de: ""
      - value: pointed
        synonyms_de: ["spitz"]
        notes_de: ""
      - value: square
        synonyms_de: ["eckig"]
        notes_de: ""

  - id: vs_shaft_height
    description_de: "Schaft-Höhe"
    values:
      - value: low
        synonyms_de: ["kurz"]
        notes_de: "Stiefelette"
      - value: mid
        synonyms_de: ["mittel"]
        notes_de: ""
      - value: high
        synonyms_de: ["hoch"]
        notes_de: "Stiefel"

  - id: vs_sole_profile
    description_de: "Sohlenprofil"
    values:
      - value: smooth
        synonyms_de: ["glatt"]
        notes_de: ""
      - value: light
        synonyms_de: ["leichtes Profil"]
        notes_de: ""
      - value: profiled
        synonyms_de: ["profil"]
        notes_de: ""
      - value: heavy
        synonyms_de: ["starkes Profil"]
        notes_de: ""
