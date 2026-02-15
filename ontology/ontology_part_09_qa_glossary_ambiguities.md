<!-- FILE: ontology_part_09_qa_glossary_ambiguities.md -->
# Part 09 – QA, Glossar, Top-Ambiguitäten
version: "0.9.0"
date: "2026-01-12"
scope: "Prüfregeln, häufige Verwechslungen, Synonym-Glossar"
toc:
  - qa_checks
  - glossary_synonyms
  - top_20_ambiguities
  - normalization_playbook_addendum

```yaml
qa_checks:
  ids_and_references:
    - "IDs: eindeutig, keine Sonderzeichen, konsistente Präfixe (cat_/it_/attr_/vs_/mat_/fc_/br_/shop_/cert_/rule_)."
    - "Referenzen: jedes *_id zeigt auf existierende Entität (category_id, parent_id, allowed_values, material_id, etc.)."
    - "Keine Dopplungen: keine zwei Objekte mit gleicher id oder gleicher (label_de + category_id) Kombination."
  enums_and_values:
    - "Enums: jedes attribute.allowed_values referenziert existierendes vs_*."
    - "Enum-Values: nur values[].value zulässig; Synonyme landen in values[].synonyms_de."
    - "Fit/Cut Konflikte: wenn conflicts_with gesetzt, sicherstellen dass Gegenseite kompatibel ist (optional: symmetrisch pflegen)."
  materials_and_composition:
    - "Materialanteile: Summe 95..105% tolerieren (Rundung); außerhalb -> warn_flag=true."
    - "material_main: Material mit höchstem Anteil; wenn composition fehlt, material_main darf leer sein."
    - "Kürzel-Normalisierung: PES/PA/EL/WO/CO/CV etc. müssen auf mat_* gemappt werden."
    - "Leder vs Kunstleder: wenn 'PU', 'vegan', 'synthetisch' in Material -> nicht als mat_leather setzen."
  sizes:
    - "Größen: attr_size_label_raw nie leer (wenn Größe vorhanden)."
    - "Größensystem: attr_size_system nie null, wenn size_label_raw vorhanden."
    - "normalized: muss zur Logik von size_system passen (alpha_* / eu_* / w*_l* / shoe_*)."
    - "Ambiguität '42': Kontext cat_footwear -> shoe_eu, sonst numeric_eu; bei Unklarheit -> leave size_system as 'other' + keep raw."
  colors_and_patterns:
    - "Farbe: color_family immer aus vs_color_family; color_primary ist frei-text."
    - "multicolor_flag: true bei >1 dominanter Farbe oder starkem Muster."
    - "Pailletten/Glitzer/Metallic: attr_color_confidence <= 0.5 wenn nur Vision-Quelle; Textquelle kann confidence erhöhen."
  category_logic:
    - "Gender: keine doppelten Bäume; nutze gender_target statt Männer/Frauen-Subtrees."
    - "item_type required_attributes: müssen existierende attr_* sein."
    - "Kragenformen nur für relevante Items (Hemd/Bluse/Polo) oder wenn Text explizit Kragen erwähnt."
  shop_brand_logic:
    - "Shop != Brand: shop_* kommt in attr_shop, Marken in attr_brand."
    - "Wenn Token sowohl Shop als auch Brand sein kann (z. B. 'Zara'): priorisiere attr_brand aus Produkttitel/Label; attr_shop aus Domain."
    - "Marketplace (Amazon) -> Brand nur aus klarer Brand-Quelle (Titel/Label/EAN-DB), nicht aus Bulletpoints allein."

glossary_synonyms:
  materials:
    - term: "Viskose"
      equals: ["Rayon", "CV", "Viscose"]
      map_to: "mat_viscose"
    - term: "Lyocell"
      equals: ["TENCEL", "CL"]
      map_to: "mat_lyocell"
    - term: "Modal"
      equals: ["CMD"]
      map_to: "mat_modal"
    - term: "Schurwolle"
      equals: ["Virgin Wool", "WO"]
      map_to: "mat_wool"
    - term: "Merinowolle"
      equals: ["Merino"]
      map_to: "mat_merino"
    - term: "Polyester"
      equals: ["PES"]
      map_to: "mat_polyester"
    - term: "Recyceltes Polyester"
      equals: ["rPES", "recycled polyester"]
      map_to: "mat_recycled_polyester"
    - term: "Polyamid"
      equals: ["PA", "Nylon", "Polyamide"]
      map_to: "mat_polyamide"
    - term: "Elasthan"
      equals: ["EL", "Spandex", "Lycra", "Elastane"]
      map_to: "mat_elastane"
    - term: "Leinen"
      equals: ["Flachs", "LI", "Linen"]
      map_to: "mat_linen"
    - term: "Leder"
      equals: ["Glattleder", "Nappa", "Leather"]
      map_to: "mat_leather"
    - term: "Veloursleder"
      equals: ["Wildleder", "Suede"]
      map_to: "mat_suede"
    - term: "Pailletten"
      equals: ["Sequins", "Paillettenstoff"]
      map_to: "mat_sequins"

  fits:
    - term: "Body Fit"
      equals: ["Super Slim", "Extra Slim"]
      map_to: "vs_fit_type.super_slim"
    - term: "Comfort Fit"
      equals: ["bequem", "weit"]
      map_to: "vs_fit_type.comfort"
    - term: "Modern Fit"
      equals: ["modern"]
      map_to: "vs_fit_type.modern"
    - term: "Loose Fit"
      equals: ["oversized", "loose"]
      map_to: "vs_fit_type.oversized"
    - term: "Relaxed Fit"
      equals: ["relaxed"]
      map_to: "vs_fit_type.relaxed"

  collars:
    - term: "Global Kent"
      equals: ["Global-Kent-Kragen"]
      map_to: "vs_collar_type.global_kent"
      note: "Immer Kragenform, nie Marke."
    - term: "Haifischkragen"
      equals: ["Spread", "Cutaway (nah)"]
      map_to: "vs_collar_type.spread_haifisch"
    - term: "Button-Down"
      equals: ["BD"]
      map_to: "vs_collar_type.button_down"
    - term: "Stehkragen"
      equals: ["Mandarin"]
      map_to: "vs_collar_type.mandarin"
    - term: "Reverskragen"
      equals: ["Camp Collar"]
      map_to: "vs_collar_type.camp"

  items:
    - term: "Jeanshose"
      equals: ["Jeans", "Denimhose"]
      map_to: "it_jeans"
    - term: "Kurze Hose"
      equals: ["Shorts", "Bermuda"]
      map_to: "it_short"
    - term: "Lederschuh"
      equals: ["Businessschuh", "Oxford (Schuh)"]
      map_to: "it_leather_shoe_classic"
    - term: "Stoffschuh"
      equals: ["Textilsneaker", "Canvas Sneaker"]
      map_to: "it_sneaker"
    - term: "Lederhandschuh"
      equals: ["Handschuh aus Leder"]
      map_to: "it_gloves"

top_20_ambiguities:
  - term: "42"
    risk: "Schuhgröße vs Konfektionsgröße"
    disambiguation_hint: "cat_footwear => shoe_eu; cat_apparel => numeric_eu; sonst raw behalten"
  - term: "M"
    risk: "Medium vs Meter (Maßangabe)"
    disambiguation_hint: "nur im Größenfeld => alpha; sonst Maßeinheit"
  - term: "Polo"
    risk: "Kleidungsstück vs Marken-/Linienname"
    disambiguation_hint: "wenn 'Kragen'/'Shirt'/'Piqué' => item; wenn im Brand-Kontext => brand/line"
  - term: "Oxford"
    risk: "Schuhmodell vs Stoff/Bindung (Oxford cloth)"
    disambiguation_hint: "bei cat_footwear => Schuh; bei Hemd => Stoffart"
  - term: "Kent"
    risk: "Kragenform vs zufälliger Begriff"
    disambiguation_hint: "nur bei Hemd/Bluse oder mit 'Kragen' => collar_type"
  - term: "Chelsea"
    risk: "Bootstil vs Orts-/Namensteil"
    disambiguation_hint: "bei cat_footwear + 'Boot' => Chelsea Boot"
  - term: "Nappa"
    risk: "Lederart vs Marketing"
    disambiguation_hint: "nur wenn klar Leder-Kontext; sonst als Freitext in upper_material"
  - term: "Velours"
    risk: "Veloursleder vs Veloursstoff"
    disambiguation_hint: "wenn 'Leder'/'Wildleder' => mat_suede; sonst Stoff"
  - term: "PU"
    risk: "Kunstleder (Polyurethan) vs unbekannt"
    disambiguation_hint: "PU => kein mat_leather; set synthetic/leather_look note"
  - term: "Vegan Leather"
    risk: "als echtes Leder erkannt"
    disambiguation_hint: "vegan => Kunstleder; material_main nicht Leder"
  - term: "Merino"
    risk: "Wolle vs Produktlinie"
    disambiguation_hint: "wenn %/Materialkomposition => mat_merino"
  - term: "TENCEL"
    risk: "Marke/Produktname vs Material"
    disambiguation_hint: "als Lyocell materialisieren (mat_lyocell)"
  - term: "Softshell/Hardshell"
    risk: "Material vs Kategorie/Funktionslage"
    disambiguation_hint: "outerwear_outdoor => category hint + function attributes"
  - term: "DWR"
    risk: "wasserabweisend vs wasserdicht"
    disambiguation_hint: "DWR != waterproof"
  - term: "ATM"
    risk: "Uhr-Wasserresistenz vs sonst"
    disambiguation_hint: "nur bei it_watch/cat_acc_watches"
  - term: "Denier"
    risk: "Strumpfhose-Dicke vs Produktname"
    disambiguation_hint: "cat_apparel_underwear + 'DEN' => hosiery thickness (optional Feld)"
  - term: "Stretch"
    risk: "Marketing vs echte Elastan-Anteile"
    disambiguation_hint: "wenn EL/Spandex in composition => stretch_percent plausibilisieren"
  - term: "Regular"
    risk: "Größentyp vs Fit"
    disambiguation_hint: "bei Größen/Länge => special_size_type; bei Passform => fit_type"
  - term: "Long"
    risk: "Langgröße vs Ärmel/Artikel-Länge"
    disambiguation_hint: "wenn Größen-Auswahl => special_size_type=long; sonst length_category"
  - term: "Used"
    risk: "Zustand (Secondhand) vs Denim-Waschung"
    disambiguation_hint: "bei Jeans => pattern/finish; bei Secondhand-Quelle => separate condition (optional)"

normalization_playbook_addendum:
  leather_vs_faux:
    triggers_faux: ["PU", "Polyurethan", "Kunstleder", "vegan", "synthetisch"]
    rule: "Wenn triggers_faux im Materialtext -> material_main darf nicht 'Leder' sein; upper_material kann 'Kunstleder' sein."
  metallic_and_sequins_color:
    triggers: ["metallic", "glitzer", "pailletten", "sequins"]
    rule: "Wenn nur Vision-Farbe: set color_confidence<=0.5; bei Text-Farbname => confidence erhöhen (z. B. 0.8)."
  brand_vs_attribute_shortlist:
    brand_tokens_high_conf: ["OLYMP", "ETERNA", "BOSS", "HUGO", "adidas", "Nike"]
    attribute_tokens_never_brand: ["Global Kent", "Kentkragen", "Button-Down", "Haifischkragen", "Stehkragen"]
    rule: "brand_tokens -> attr_brand; attribute_tokens -> attr_collar_type (oder anderes Attribut), niemals attr_brand."
