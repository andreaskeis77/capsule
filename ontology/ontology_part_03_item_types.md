<!-- FILE: ontology_part_03_item_types.md -->
# Part 03 – Item Types & Varianten (item_type) — REWRITE
version: "0.9.1"
date: "2026-01-13"
scope: "Konkrete Kleidungsstücke/Schuhe/Accessoires inkl. praxisnaher Varianten + Normalisierungshinweise (Item-Type vs. Attribute)."
toc:
  - Designprinzipien (Item-Type vs. Modifier)
  - item_types (YAML)

## Designprinzipien (wichtig für Extraktion & Fehlerreduktion)

### 1) Item-Type = „Was ist es strukturell?“ (Kern-Nomen/Produktart)
Beispiele (Item-Type):
- „Jeans“, „Chino“, „Blazer“, „Sakko“, „Bomberjacke“, „Hardshell“, „Sneaker“, „Oxford“, „Gürtel“, „Uhr“.

### 2) Modifier = Attribute (nicht als Brand/Item-Type speichern)
Typische Modifier (als Attribute modellieren):
- Material/Gewebe: „Baumwolle“, „Leinen“, „Wolle“, „Kaschmir“, „Leder“, „Velours“, „Denim“, „Jersey“, „Strick“, „Cord“
  -> attr_material_composition (+ ggf. attr_upper_material/attr_sole_material bei Schuhen)
- Länge: „kurz“, „lang“, „3/4“, „mini/midi/maxi“
  -> attr_length_category
- Passform/Cut: „Slim“, „Regular“, „Wide Leg“, „Straight“, „Tapered“, „Oversized“
  -> attr_fit_type, attr_leg_shape (bei Hosen)
- Anlass/Style: „Business“, „Casual“, „Festlich“, „Outdoor“, „Functional“
  -> attr_occasion, attr_style, (Sport/Outdoor zusätzlich: attr_activity)
- Kragen/Details: „Global Kent“, „Button-Down“, „Haifisch“
  -> attr_collar_type (niemals brand)

### 3) Wenn ein Begriff im Handel eine eigene Produktart ist, darf er eigener Item-Type sein
Beispiele:
- „Jeans“ (Denim-Hosen als Produktart) -> it_jeans
- „Chino“ (Twill, smart casual als Produktart) -> it_chino
- „Oxford/Derby/Loafer“ (klassische Schuharten) -> eigene Item-Types

---

```yaml
item_types:

  # ------------------------------------------------------------
  # 0) Fallbacks (für Notizen / unspezifische Angaben)
  # ------------------------------------------------------------
  - id: it_top_generic
    label_de: "Oberteil (unspezifisch)"
    label_en: "Top (generic)"
    category_id: cat_apparel_tops
    synonyms_de: ["Oberteil", "Top", "Shirt (generisch)"]
    variants: ["langarm", "kurzarm", "ärmellos"]
    allowed_material_groups: ["plant", "regenerated", "synthetic", "blend", "animal"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_fit_type, attr_color_primary, attr_material_composition, attr_care_instructions_text]
    disambiguation_hints: ["Wenn ein konkreteres Nomen gefunden wird (Hemd/Bluse/Pullover), diesen Item-Type NICHT verwenden."]

  - id: it_bottom_generic
    label_de: "Unterteil (unspezifisch)"
    label_en: "Bottom (generic)"
    category_id: cat_apparel_bottoms
    synonyms_de: ["Unterteil"]
    variants: ["lang", "kurz"]
    allowed_material_groups: ["plant", "regenerated", "synthetic", "blend", "animal"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_fit_type, attr_length_category, attr_color_primary, attr_material_composition]
    disambiguation_hints: ["Wenn Jeans/Chino/Rock/Shorts eindeutig, spezifischen Item-Type nehmen."]

  - id: it_outerwear_generic
    label_de: "Oberbekleidung (unspezifisch)"
    label_en: "Outerwear (generic)"
    category_id: cat_apparel_outerwear
    synonyms_de: ["Jacke (unspezifisch)", "Oberjacke"]
    variants: ["leicht", "gefüttert", "mit Kapuze"]
    allowed_material_groups: ["plant", "regenerated", "synthetic", "blend", "animal"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_fit_type, attr_hood, attr_lining_material, attr_season, attr_material_composition]
    disambiguation_hints: ["Wenn Mantel/Blazer/Bomber/Hardshell etc. erkannt, spezifischen Item-Type nehmen."]

  - id: it_footwear_generic
    label_de: "Schuh (unspezifisch)"
    label_en: "Footwear (generic)"
    category_id: cat_footwear
    synonyms_de: ["Schuh", "Schuhe"]
    variants: ["Leder", "Stoff", "Sneaker", "Stiefel"]
    allowed_material_groups: ["plant", "synthetic", "blend", "animal"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_upper_material, attr_sole_material, attr_closure_type, attr_color_primary]
    disambiguation_hints: ["Wenn Sneaker/Boot/Oxford/Derby etc. erkennbar, spezifischen Item-Type nehmen."]

  - id: it_accessory_generic
    label_de: "Accessoire (unspezifisch)"
    label_en: "Accessory (generic)"
    category_id: cat_accessories
    synonyms_de: ["Accessoire", "Zubehör"]
    variants: ["klein", "tragbar"]
    allowed_material_groups: ["plant", "synthetic", "blend", "animal", "regenerated"]
    required_attributes: [attr_brand]
    optional_attributes: [attr_color_primary, attr_material_composition, attr_size_system, attr_size_label_raw]
    disambiguation_hints: ["Wenn Gürtel/Uhr/Mütze/Tasche/Handschuhe erkennbar, spezifischen Item-Type nehmen."]

  # ------------------------------------------------------------
  # 1) Hemden & Blusen (cat_tops_shirts_blouses)
  # ------------------------------------------------------------
  - id: it_shirt_dress
    label_de: "Businesshemd"
    label_en: "Dress Shirt"
    category_id: cat_tops_shirts_blouses
    synonyms_de: ["Hemd", "Oberhemd", "Business-Hemd"]
    variants: ["Langarmhemd", "Kurzarmhemd", "Oxford-Hemd", "Popeline-Hemd", "Flanellhemd", "Leinenhemd", "Denimhemd", "Bügelfreies Hemd"]
    allowed_material_groups: ["plant", "blend", "regenerated"]
    required_attributes: [attr_brand, attr_collar_type, attr_sleeve_length, attr_fit_type, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_cuff_type, attr_pattern, attr_color_primary, attr_material_composition, attr_care_instructions_text]
    disambiguation_hints: ["Global Kent/Haifisch/Button-Down -> attr_collar_type (niemals brand)."]

  - id: it_shirt_casual
    label_de: "Freizeithemd"
    label_en: "Casual Shirt"
    category_id: cat_tops_shirts_blouses
    synonyms_de: ["Casual Hemd", "Hemd (casual)"]
    variants: ["Flanellhemd", "Cordhemd", "Overshirt (wenn nicht eindeutig Jacke)", "Jeanshemd", "Karohemd"]
    allowed_material_groups: ["plant", "blend", "regenerated"]
    required_attributes: [attr_brand, attr_sleeve_length, attr_fit_type, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_collar_type, attr_pattern, attr_color_primary, attr_material_composition]
    disambiguation_hints: ["Bei dicker, jackenähnlicher Ausführung eher it_overshirt."]

  - id: it_overshirt
    label_de: "Overshirt / Hemdjacke"
    label_en: "Overshirt"
    category_id: cat_tops_shirts_blouses
    synonyms_de: ["Hemdjacke", "Shacket"]
    variants: ["Woll-Overshirt", "Cord-Overshirt", "Quilted Overshirt"]
    allowed_material_groups: ["plant", "animal", "blend", "synthetic", "regenerated"]
    required_attributes: [attr_brand, attr_fit_type, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_closure_type, attr_pocket_style, attr_lining_material, attr_material_composition]
    disambiguation_hints: ["Wenn eindeutig Jacke (gefüttert/Outdoor), eher Outerwear-Item-Types verwenden."]

  - id: it_blouse
    label_de: "Bluse"
    label_en: "Blouse"
    category_id: cat_tops_shirts_blouses
    synonyms_de: ["Damenbluse", "Hemdbluse"]
    variants: ["Schlupfbluse", "Chiffonbluse", "Seidenbluse", "Rüschenbluse", "Oversize-Bluse"]
    allowed_material_groups: ["plant", "regenerated", "synthetic", "blend", "animal"]
    required_attributes: [attr_brand, attr_sleeve_length, attr_fit_type, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_neckline, attr_collar_type, attr_pattern, attr_color_primary, attr_material_composition, attr_care_instructions_text]
    disambiguation_hints: ["Tunika als längere Blusenform -> ggf. it_tunic_top."]

  - id: it_tunic_top
    label_de: "Tunika"
    label_en: "Tunic"
    category_id: cat_tops_shirts_blouses
    synonyms_de: ["Tunikabluse", "Longbluse"]
    variants: ["Sommer-Tunika", "Strand-Tunika"]
    allowed_material_groups: ["plant", "regenerated", "synthetic", "blend", "animal"]
    required_attributes: [attr_brand, attr_length_category, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_sleeve_length, attr_neckline, attr_fit_type, attr_material_composition]
    disambiguation_hints: ["Wenn als Kleid getragen/gelabelt: it_dress."]

  # ------------------------------------------------------------
  # 2) T-Shirts & Tops (cat_tops_tshirts)
  # ------------------------------------------------------------
  - id: it_tshirt
    label_de: "T-Shirt"
    label_en: "T-Shirt"
    category_id: cat_tops_tshirts
    synonyms_de: ["Shirt", "Kurzarmshirt", "Tee"]
    variants: ["Rundhals", "V-Neck", "Print", "Basic", "Oversize", "Funktionsshirt"]
    allowed_material_groups: ["plant", "regenerated", "synthetic", "blend"]
    required_attributes: [attr_brand, attr_neckline, attr_sleeve_length, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_fit_type, attr_pattern, attr_color_primary, attr_material_composition, attr_care_instructions_text]
    disambiguation_hints: ["Jersey -> Material/Gewebe (attr_material_composition), nicht Item-Type."]

  - id: it_longsleeve
    label_de: "Longsleeve"
    label_en: "Long Sleeve Top"
    category_id: cat_tops_tshirts
    synonyms_de: ["Langarmshirt", "Long Sleeve"]
    variants: ["Rundhals-Longsleeve", "Henley (falls so bezeichnet)", "Basic Longsleeve"]
    allowed_material_groups: ["plant", "regenerated", "synthetic", "blend"]
    required_attributes: [attr_brand, attr_neckline, attr_sleeve_length, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_fit_type, attr_color_primary, attr_material_composition]
    disambiguation_hints: ["Wenn Kragen+Knopfleiste wie Hemd: eher Hemd-Item-Type."]

  - id: it_tank_top
    label_de: "Tanktop / Trägertop"
    label_en: "Tank Top"
    category_id: cat_tops_tshirts
    synonyms_de: ["Top (ärmellos)", "Unterhemd (wenn als Unterwäsche)"]
    variants: ["Racerback", "Spaghettiträger (eher Damen)", "Muskelshirt"]
    allowed_material_groups: ["plant", "regenerated", "synthetic", "blend"]
    required_attributes: [attr_brand, attr_neckline, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_fit_type, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Wenn explizit Unterwäsche: it_undershirt."]

  - id: it_polo
    label_de: "Polo-Shirt"
    label_en: "Polo Shirt"
    category_id: cat_tops_tshirts
    synonyms_de: ["Polo", "Poloshirt"]
    variants: ["Kurzarm-Polo", "Langarm-Polo", "Strickpolo"]
    allowed_material_groups: ["plant", "blend", "regenerated", "synthetic"]
    required_attributes: [attr_brand, attr_collar_type, attr_sleeve_length, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_fit_type, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Polokragen -> attr_collar_type."]

  # ------------------------------------------------------------
  # 3) Strick (cat_tops_knitwear)
  # ------------------------------------------------------------
  - id: it_sweater
    label_de: "Pullover"
    label_en: "Sweater"
    category_id: cat_tops_knitwear
    synonyms_de: ["Pulli", "Strickpullover"]
    variants: ["Rundhals", "V-Neck", "Rollkragen", "Troyer (Zip)", "Feinstrick", "Grobstrick"]
    allowed_material_groups: ["animal", "plant", "blend", "synthetic", "regenerated"]
    required_attributes: [attr_brand, attr_neckline, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_fit_type, attr_sleeve_length, attr_material_composition, attr_color_primary, attr_care_instructions_text]
    disambiguation_hints: ["Rollkragen = neckline/kragenform (attr_neckline/collar_type), nicht brand."]

  - id: it_cardigan
    label_de: "Cardigan / Strickjacke"
    label_en: "Cardigan"
    category_id: cat_tops_knitwear
    synonyms_de: ["Strickjacke"]
    variants: ["Button Cardigan", "Zip Cardigan", "Longcardigan"]
    allowed_material_groups: ["animal", "plant", "blend", "synthetic", "regenerated"]
    required_attributes: [attr_brand, attr_closure_type, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_fit_type, attr_material_composition, attr_color_primary, attr_neckline]
    disambiguation_hints: ["Wenn sehr dick + Outdoor: ggf. Outerwear."]

  # ------------------------------------------------------------
  # 4) Sweat & Hoodies (cat_tops_hoodies_sweat)
  # ------------------------------------------------------------
  - id: it_hoodie
    label_de: "Hoodie"
    label_en: "Hoodie"
    category_id: cat_tops_hoodies_sweat
    synonyms_de: ["Kapuzensweat", "Hoody"]
    variants: ["Zip-Hoodie", "Pullover-Hoodie", "Oversize Hoodie"]
    allowed_material_groups: ["plant", "blend", "synthetic", "regenerated"]
    required_attributes: [attr_brand, attr_hood, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_fit_type, attr_style, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Kapuze -> attr_hood = true (falls extrahierbar)."]

  - id: it_sweatshirt
    label_de: "Sweatshirt (Crewneck)"
    label_en: "Sweatshirt"
    category_id: cat_tops_hoodies_sweat
    synonyms_de: ["Crewneck", "Sweater (Sweat)"]
    variants: ["Crewneck", "Raglan", "Half-Zip (Troyer)"]
    allowed_material_groups: ["plant", "blend", "synthetic", "regenerated"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_neckline, attr_fit_type, attr_style, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Troyer meist Half-Zip: attr_closure_type ergänzen."]

  # ------------------------------------------------------------
  # 5) Hosen (cat_bottoms_trousers + Subcats)
  # ------------------------------------------------------------
  - id: it_jeans
    label_de: "Jeans"
    label_en: "Jeans"
    category_id: cat_bottoms_trousers_denim
    synonyms_de: ["Jeanshose", "Denimhose"]
    variants: ["Straight", "Slim", "Skinny", "Tapered", "Bootcut", "Wide Leg", "Raw Denim", "Stonewash", "Selvedge"]
    allowed_material_groups: ["plant", "blend"]
    required_attributes: [attr_brand, attr_leg_shape, attr_rise, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_wash, attr_stretch_percent, attr_material_composition, attr_occasion, attr_color_primary]
    disambiguation_hints: ["W/L (z.B. W32/L34) häufig; Waschung -> attr_wash."]

  - id: it_chino
    label_de: "Chinohose"
    label_en: "Chinos"
    category_id: cat_bottoms_trousers_chino
    synonyms_de: ["Chino"]
    variants: ["Slim Chino", "Regular Chino", "Stretch Chino", "Sommerchino"]
    allowed_material_groups: ["plant", "blend"]
    required_attributes: [attr_brand, attr_leg_shape, attr_rise, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_material_composition, attr_occasion, attr_color_primary]
    disambiguation_hints: ["Twill/Chino -> Typ; Material 'Baumwolle' separat."]

  - id: it_trousers_fabric
    label_de: "Stoffhose"
    label_en: "Trousers"
    category_id: cat_bottoms_trousers
    synonyms_de: ["Bundfaltenhose", "Hose (Stoff)"]
    variants: ["Wollhose", "Baumwollhose", "Leinenhose", "Cordhose", "Culotte", "Palazzo", "Paperbag"]
    allowed_material_groups: ["plant", "animal", "blend", "regenerated", "synthetic"]
    required_attributes: [attr_brand, attr_leg_shape, attr_rise, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_crease, attr_material_composition, attr_occasion, attr_lining_material, attr_color_primary]
    disambiguation_hints: ["Materialadjektiv (Wolle/Leinen/Cord) -> attr_material_composition."]

  - id: it_suit_trousers
    label_de: "Anzughose"
    label_en: "Suit Trousers"
    category_id: cat_bottoms_trousers_suit
    synonyms_de: ["Wollanzughose", "Dress Pants (engl.)"]
    variants: ["Einreiher-Anzughose (Set)", "Zweiteiler", "Dreiteiler"]
    allowed_material_groups: ["animal", "blend", "synthetic", "plant"]
    required_attributes: [attr_brand, attr_occasion, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_crease, attr_leg_shape, attr_rise, attr_lining_material, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Wenn zusammen mit Sakko -> Anzug (Set-Logik in Regeln)."]

  - id: it_cargo_pants
    label_de: "Cargohose"
    label_en: "Cargo Pants"
    category_id: cat_bottoms_trousers
    synonyms_de: ["Cargo"]
    variants: ["Utility", "Ripstop Cargo", "Cargo Jogger"]
    allowed_material_groups: ["plant", "blend", "synthetic"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_leg_shape, attr_rise, attr_pocket_style, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Aufgesetzte Taschen -> attr_pocket_style."]

  - id: it_sweatpants
    label_de: "Jogginghose"
    label_en: "Sweatpants"
    category_id: cat_apparel_sport_outdoor
    synonyms_de: ["Sweathose", "Trackpants (unscharf)"]
    variants: ["Cuffed", "Straight", "Wide", "Tech-Fleece"]
    allowed_material_groups: ["plant", "blend", "synthetic", "regenerated"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_fit_type, attr_leg_shape, attr_style, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Wenn 'Trainingshose'/'Sport' -> attr_activity ergänzen."]

  - id: it_leggings
    label_de: "Leggings"
    label_en: "Leggings"
    category_id: cat_apparel_sport_outdoor
    synonyms_de: ["Tights (Sport)"]
    variants: ["Sportleggings", "Thermo-Leggings", "Kompressionsleggings"]
    allowed_material_groups: ["synthetic", "blend", "regenerated"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_stretch_percent, attr_activity, attr_material_composition, attr_color_primary, attr_length_category]
    disambiguation_hints: ["Kompression als Feature -> eher Hinweistext/Phrase, nicht Farbe."]

  # ------------------------------------------------------------
  # 6) Shorts (cat_bottoms_shorts)
  # ------------------------------------------------------------
  - id: it_shorts
    label_de: "Shorts"
    label_en: "Shorts"
    category_id: cat_bottoms_shorts
    synonyms_de: ["Kurze Hose", "Short", "Bermuda"]
    variants: ["Jeansshorts", "Chino-Shorts", "Bermuda", "Cargo-Shorts", "Sport-Shorts", "Badeshorts", "Leinenshorts"]
    allowed_material_groups: ["plant", "synthetic", "blend", "regenerated"]
    required_attributes: [attr_brand, attr_length_category, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_fit_type, attr_material_composition, attr_occasion, attr_pocket_style, attr_color_primary]
    disambiguation_hints: ["Badeshorts -> ggf. Sport/Outdoor + activity=swim (falls vorhanden)."]

  # ------------------------------------------------------------
  # 7) Röcke (cat_bottoms_skirts)
  # ------------------------------------------------------------
  - id: it_skirt
    label_de: "Rock"
    label_en: "Skirt"
    category_id: cat_bottoms_skirts
    synonyms_de: ["Damenrock"]
    variants: ["Bleistiftrock", "A-Linien-Rock", "Faltenrock", "Wickelrock", "Jeansrock", "Lederrock", "Maxirock", "Minirock", "Midirock"]
    allowed_material_groups: ["plant", "animal", "synthetic", "blend", "regenerated"]
    required_attributes: [attr_brand, attr_silhouette, attr_length_category, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_material_composition, attr_color_primary, attr_waistband_style, attr_occasion]
    disambiguation_hints: ["Bleistift/A-Linie/Falten/Wickel -> attr_silhouette. 'Leder' -> Material, nicht eigener Rock-Typ."]

  # ------------------------------------------------------------
  # 8) Kleider & Einteiler (cat_dresses / cat_jumpsuits)
  # ------------------------------------------------------------
  - id: it_dress
    label_de: "Kleid"
    label_en: "Dress"
    category_id: cat_dresses
    synonyms_de: ["Sommerkleid", "Etuikleid", "Hemdblusenkleid"]
    variants: ["Etuikleid", "A-Linien-Kleid", "Schlauchkleid", "Fit-and-Flare", "Empire-Kleid", "Maxikleid", "Midikleid", "Minikleid", "Strickkleid", "Abendkleid", "Wickelkleid"]
    allowed_material_groups: ["plant", "animal", "synthetic", "blend", "regenerated"]
    required_attributes: [attr_brand, attr_silhouette, attr_length_category, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_neckline, attr_sleeve_length, attr_occasion, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Pailletten/Sequins -> Farberkennung kritisch (Regeln in Part 08)."]

  - id: it_jumpsuit
    label_de: "Jumpsuit/Overall"
    label_en: "Jumpsuit"
    category_id: cat_jumpsuits
    synonyms_de: ["Overall", "Boiler Suit"]
    variants: ["Sommer-Jumpsuit", "Business-Jumpsuit", "Boiler Suit", "Latzoverall"]
    allowed_material_groups: ["plant", "synthetic", "blend", "regenerated"]
    required_attributes: [attr_brand, attr_closure_type, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_fit_type, attr_leg_shape, attr_material_composition, attr_occasion, attr_color_primary]
    disambiguation_hints: ["Einteiler mit Hosenbein; wenn eher Kleid-Form -> it_dress."]

  # ------------------------------------------------------------
  # 9) Unterwäsche & Socken (cat_apparel_underwear)
  # ------------------------------------------------------------
  - id: it_socks
    label_de: "Socken/Strümpfe"
    label_en: "Socks/Hosiery"
    category_id: cat_apparel_underwear
    synonyms_de: ["Socken", "Strümpfe", "Strumpfhose"]
    variants: ["Sneakersocken", "Businesssocken", "Wollsocken", "Kompressionssocken", "Feinstrumpfhose"]
    allowed_material_groups: ["plant", "synthetic", "blend", "animal"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_material_composition, attr_stretch_percent, attr_color_primary]
    disambiguation_hints: ["Denier bei Strumpfhosen; Kompression nicht als Muster/Farbe interpretieren."]

  - id: it_undershirt
    label_de: "Unterhemd"
    label_en: "Undershirt"
    category_id: cat_apparel_underwear
    synonyms_de: ["Achselhemd", "Unterziehshirt"]
    variants: ["Tank-Unterhemd", "T-Shirt-Unterhemd", "Thermo-Unterhemd"]
    allowed_material_groups: ["plant", "blend", "synthetic", "regenerated"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_neckline, attr_material_composition, attr_color_primary, attr_stretch_percent]
    disambiguation_hints: ["Wenn als normales Top getragen (Shop-Kategorie Tops), ggf. it_tank_top/it_tshirt."]

  - id: it_underwear_men
    label_de: "Unterhose (Herren)"
    label_en: "Men's Underwear"
    category_id: cat_apparel_underwear
    synonyms_de: ["Boxershorts", "Slip", "Trunks"]
    variants: ["Boxershorts", "Slip", "Trunks", "Long Johns (lang)"]
    allowed_material_groups: ["plant", "synthetic", "blend", "regenerated"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_material_composition, attr_stretch_percent, attr_color_primary]
    disambiguation_hints: ["Trunks/Boxer/Slip als Varianten, nicht Marken."]

  - id: it_underwear_women
    label_de: "Unterwäsche (Damen)"
    label_en: "Women's Underwear"
    category_id: cat_apparel_underwear
    synonyms_de: ["Slip", "Panty", "String"]
    variants: ["Slip", "Hipster", "String", "Brazilian", "Shapewear"]
    allowed_material_groups: ["plant", "synthetic", "blend", "regenerated", "animal"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_material_composition, attr_stretch_percent, attr_color_primary]
    disambiguation_hints: ["Shapewear als Variante; Details ggf. in Notizen."]

  - id: it_bra
    label_de: "BH"
    label_en: "Bra"
    category_id: cat_apparel_underwear
    synonyms_de: ["Bügel-BH", "Soft-BH", "Bralette"]
    variants: ["Bügel-BH", "Soft-BH", "Bralette", "Sport-BH (auch Sport/Outdoor möglich)"]
    allowed_material_groups: ["synthetic", "blend", "regenerated", "plant", "animal"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_material_composition, attr_stretch_percent, attr_color_primary]
    disambiguation_hints: ["Sport-BH: ggf. it_sports_bra (wenn sportlicher Kontext)."]

  # ------------------------------------------------------------
  # 10) Nachtwäsche (cat_apparel_sleepwear)
  # ------------------------------------------------------------
  - id: it_pajama
    label_de: "Pyjama"
    label_en: "Pajamas"
    category_id: cat_apparel_sleepwear
    synonyms_de: ["Schlafanzug", "Pyjama-Set"]
    variants: ["Kurzpyjama", "Langpyjama", "Flanell-Pyjama", "Seidenpyjama"]
    allowed_material_groups: ["plant", "blend", "synthetic", "regenerated", "animal"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_material_composition, attr_season, attr_fit_type, attr_color_primary]
    disambiguation_hints: ["Loungewear ohne Schlaf-Kontext -> ggf. Tops/Bottoms generisch."]

  - id: it_nightgown
    label_de: "Nachthemd"
    label_en: "Nightgown"
    category_id: cat_apparel_sleepwear
    synonyms_de: ["Nightdress"]
    variants: ["Kurz", "Lang", "Hemdform"]
    allowed_material_groups: ["plant", "blend", "synthetic", "regenerated", "animal"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_length_category, attr_neckline, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Wenn als Kleid im Alltag: it_dress (Kontext!)."]

  # ------------------------------------------------------------
  # 11) Sport & Outdoor (cat_apparel_sport_outdoor)
  # ------------------------------------------------------------
  - id: it_functional_shirt
    label_de: "Funktionsshirt"
    label_en: "Performance Shirt"
    category_id: cat_apparel_sport_outdoor
    synonyms_de: ["Laufshirt", "Sportshirt", "Base Layer Top (unscharf)"]
    variants: ["Kurzarm", "Langarm", "Merino Baselayer", "Schnelltrocknend"]
    allowed_material_groups: ["synthetic", "blend", "regenerated", "animal", "plant"]
    required_attributes: [attr_brand, attr_activity, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_function_breathable, attr_material_composition, attr_color_primary, attr_fit_type]
    disambiguation_hints: ["'schnelltrocknend'/'atmungsaktiv' -> Funktion, nicht Muster/Farbe."]

  - id: it_trekking_pants
    label_de: "Trekkinghose"
    label_en: "Trekking Pants"
    category_id: cat_apparel_sport_outdoor
    synonyms_de: ["Outdoorhose", "Wanderhose"]
    variants: ["Zip-Off", "Softshell-Hose", "Regenhose (Overpant)"]
    allowed_material_groups: ["synthetic", "blend", "plant", "regenerated"]
    required_attributes: [attr_brand, attr_activity, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_leg_shape, attr_function_windproof, attr_function_waterproof, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Zip-Off als Variante; wasserdicht -> attr_function_waterproof."]

  - id: it_hardshell_jacket
    label_de: "Hardshell-Jacke"
    label_en: "Hardshell Jacket"
    category_id: cat_outerwear_jackets_outdoor_hardshell
    synonyms_de: ["Regenjacke (technisch)", "Shelljacke (hardshell)"]
    variants: ["2-Lagen", "2.5-Lagen", "3-Lagen", "mit Pit-Zips"]
    allowed_material_groups: ["synthetic", "blend"]
    required_attributes: [attr_brand, attr_membrane, attr_seam_sealed, attr_water_column_mm, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_layer_system, attr_hood, attr_function_breathable, attr_color_primary, attr_material_composition]
    disambiguation_hints: ["Membran/Nahtversiegelung/Wassersäule -> Hardshell."]

  - id: it_softshell_jacket
    label_de: "Softshell-Jacke"
    label_en: "Softshell Jacket"
    category_id: cat_outerwear_jackets_outdoor
    synonyms_de: ["Softshell"]
    variants: ["mit Fleece-Innen", "hybrid"]
    allowed_material_groups: ["synthetic", "blend"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_function_windproof, attr_function_waterproof, attr_hood, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Softshell oft winddicht/wasserabweisend, aber nicht zwingend wasserdicht."]

  # ------------------------------------------------------------
  # 12) Outerwear – Blazer/Sakko/Coats/Jackets
  # ------------------------------------------------------------
  - id: it_blazer
    label_de: "Blazer"
    label_en: "Blazer"
    category_id: cat_outerwear_blazers_suits_blazer
    synonyms_de: ["Damenblazer", "Blazerjacke"]
    variants: ["Business-Blazer", "Casual-Blazer", "Jersey-Blazer", "Sommerblazer (Leinen)"]
    allowed_material_groups: ["animal", "plant", "synthetic", "blend", "regenerated"]
    required_attributes: [attr_brand, attr_lapel_type, attr_fit_type, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_button_count, attr_lining_material, attr_occasion, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Revers -> attr_lapel_type; 'Sakko' nicht automatisch = Blazer (siehe it_suit_jacket)."]

  - id: it_suit_jacket
    label_de: "Sakko"
    label_en: "Suit Jacket"
    category_id: cat_outerwear_blazers_suits
    synonyms_de: ["Sakko", "Anzugsakko"]
    variants: ["Einreiher", "Zweireiher", "Sommer-Sakko (Leinen)", "Jersey-Sakko"]
    allowed_material_groups: ["animal", "blend", "synthetic", "plant"]
    required_attributes: [attr_brand, attr_lapel_type, attr_fit_type, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_button_count, attr_lining_material, attr_occasion, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Wenn klar Teil eines Anzugs (Set/Anzughose vorhanden) -> attr_occasion=formal + Regeln in Part 08 nutzen."]

  - id: it_tuxedo_jacket
    label_de: "Smoking-Sakko"
    label_en: "Tuxedo Jacket"
    category_id: cat_outerwear_blazers_suits_sakko_festlich
    synonyms_de: ["Smoking", "Dinner Jacket"]
    variants: ["Schalkragen", "Spitzfacon", "mit Satinrevers"]
    allowed_material_groups: ["animal", "blend", "synthetic"]
    required_attributes: [attr_brand, attr_occasion, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_lapel_type, attr_lining_material, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Smoking/Dinner -> festlich; Reversdetails als lapel_type."]

  - id: it_coat
    label_de: "Mantel"
    label_en: "Coat"
    category_id: cat_outerwear_coats
    synonyms_de: ["Wollmantel", "Wintermantel"]
    variants: ["Wollmantel", "Übergangsmantel", "Steppmantel", "Daunenmantel"]
    allowed_material_groups: ["animal", "plant", "synthetic", "blend", "regenerated"]
    required_attributes: [attr_brand, attr_length_category, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_lining_material, attr_season, attr_hood, attr_fit_type, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Trenchcoat als eigener Item-Type: it_trenchcoat."]

  - id: it_trenchcoat
    label_de: "Trenchcoat"
    label_en: "Trench Coat"
    category_id: cat_outerwear_coats
    synonyms_de: ["Trench"]
    variants: ["klassisch", "kurz", "lang"]
    allowed_material_groups: ["plant", "blend", "synthetic", "regenerated"]
    required_attributes: [attr_brand, attr_length_category, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_closure_type, attr_fit_type, attr_lining_material, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Gürtel/Bindegürtel als Detail; nicht als eigener Gürtel-Item-Type speichern."]

  - id: it_jacket_bomber
    label_de: "Bomberjacke"
    label_en: "Bomber Jacket"
    category_id: cat_outerwear_jackets_casual_bomber
    synonyms_de: ["Bomber", "Flight Jacket (unscharf)"]
    variants: ["Nylon-Bomber", "Wollbomber", "gefüttert"]
    allowed_material_groups: ["synthetic", "blend", "animal", "plant", "regenerated"]
    required_attributes: [attr_brand, attr_cuff_style, attr_ribbed_hem, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_fit_type, attr_lining_material, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Bündchen/gerippter Saum typisch."]

  - id: it_jacket_denim
    label_de: "Jeansjacke"
    label_en: "Denim Jacket"
    category_id: cat_outerwear_jackets_casual
    synonyms_de: ["Denimjacke"]
    variants: ["Trucker Jacket", "Oversized Denim Jacket"]
    allowed_material_groups: ["plant", "blend"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_fit_type, attr_closure_type, attr_wash, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Denim -> jeansartig; Waschung möglich."]

  - id: it_jacket_leather
    label_de: "Lederjacke"
    label_en: "Leather Jacket"
    category_id: cat_outerwear_jackets_casual
    synonyms_de: ["Bikerjacke", "Kunstlederjacke"]
    variants: ["Biker", "Bomber-Leder", "Wildleder (Suede)", "Kunstleder"]
    allowed_material_groups: ["animal", "synthetic", "blend"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_closure_type, attr_lining_material, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Wildleder/Velours -> upper/leather type als Materialhinweis, nicht Farbe."]

  - id: it_rain_jacket
    label_de: "Regenjacke (nicht zwingend Hardshell)"
    label_en: "Rain Jacket"
    category_id: cat_outerwear_jackets_outdoor
    synonyms_de: ["Rain Jacket", "Shelljacke (unscharf)"]
    variants: ["packbar", "wasserabweisend", "wasserdicht"]
    allowed_material_groups: ["synthetic", "blend"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_function_waterproof, attr_function_windproof, attr_hood, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Wenn Membran+Wassersäule explizit -> it_hardshell_jacket."]

  - id: it_vest
    label_de: "Weste"
    label_en: "Vest"
    category_id: cat_apparel_outerwear
    synonyms_de: ["Steppweste", "Daunenweste", "Anzugweste"]
    variants: ["Steppweste", "Daunenweste", "Anzugweste"]
    allowed_material_groups: ["synthetic", "blend", "animal", "plant", "regenerated"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_occasion, attr_lining_material, attr_fit_type, attr_material_composition, attr_color_primary]
    disambiguation_hints: ["Anzugweste kann mit Sakko/Anzughose gekoppelt sein (Regeln)."]

  # ------------------------------------------------------------
  # 13) Schuhe (cat_shoes_*)
  # ------------------------------------------------------------
  - id: it_sneaker
    label_de: "Sneaker"
    label_en: "Sneakers"
    category_id: cat_shoes_sneaker
    synonyms_de: ["Turnschuh", "Sportschuh (Alltag)", "Stoffsneaker", "Ledersneaker"]
    variants: ["Low-Top", "High-Top", "Canvas Sneaker", "Leather Sneaker"]
    allowed_material_groups: ["plant", "synthetic", "blend", "animal"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_upper_material, attr_sole_material, attr_closure_type, attr_color_primary]
    disambiguation_hints: ["Stoffschuh -> meist Sneaker; upper_material=textile."]

  - id: it_leather_shoe_classic
    label_de: "Klassischer Lederschuh (generisch)"
    label_en: "Classic Leather Shoe (generic)"
    category_id: cat_shoes_leather
    synonyms_de: ["Lederschuh", "Business-Schuh", "Schnürschuh (klassisch)"]
    variants: ["Oxford", "Derby", "Loafer", "Monkstrap", "Brogue"]
    allowed_material_groups: ["animal", "synthetic", "blend"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_toe_shape, attr_heel_height_cm, attr_upper_material, attr_closure_type, attr_color_primary]
    disambiguation_hints: ["Wenn Oxford/Derby/Loafer explizit -> spezifischen Item-Type nutzen."]

  - id: it_oxford
    label_de: "Oxford-Schuh"
    label_en: "Oxford Shoe"
    category_id: cat_shoes_leather
    synonyms_de: ["Oxford"]
    variants: ["Plain Oxford", "Cap-Toe Oxford", "Brogue Oxford"]
    allowed_material_groups: ["animal", "synthetic", "blend"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_toe_shape, attr_upper_material, attr_heel_height_cm, attr_color_primary]
    disambiguation_hints: ["Oxford wird häufig als Business-Schuh geführt."]

  - id: it_derby
    label_de: "Derby-Schuh"
    label_en: "Derby Shoe"
    category_id: cat_shoes_leather
    synonyms_de: ["Derby"]
    variants: ["Plain Derby", "Brogue Derby"]
    allowed_material_groups: ["animal", "synthetic", "blend"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_toe_shape, attr_upper_material, attr_heel_height_cm, attr_color_primary]
    disambiguation_hints: ["Derby ist klassischer Lederschuh-Typ; oft Schnürung."]

  - id: it_loafer
    label_de: "Loafer"
    label_en: "Loafers"
    category_id: cat_shoes_leather
    synonyms_de: ["Slipper (klassisch)", "Penny Loafer"]
    variants: ["Penny Loafer", "Tassel Loafer"]
    allowed_material_groups: ["animal", "synthetic", "blend"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_toe_shape, attr_upper_material, attr_heel_height_cm, attr_color_primary]
    disambiguation_hints: ["Nicht verwechseln mit Hausschuh (it_slipper_home)."]

  - id: it_boots
    label_de: "Stiefel"
    label_en: "Boots"
    category_id: cat_shoes_boots
    synonyms_de: ["Boot", "Winterstiefel"]
    variants: ["Chelsea Boot", "Schnürstiefel", "Winterboot", "Bikerboot"]
    allowed_material_groups: ["animal", "synthetic", "blend", "plant"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_shaft_height, attr_lining_material, attr_sole_profile, attr_upper_material, attr_color_primary]
    disambiguation_hints: ["Chelsea kann als Variante; bei explizit 'Chelsea' ggf. in Variantenfeld belassen."]

  - id: it_ankle_boots
    label_de: "Stiefelette"
    label_en: "Ankle Boots"
    category_id: cat_shoes_boots
    synonyms_de: ["Ankle Boot", "Bootie"]
    variants: ["Chelsea-Stiefelette", "Absatz-Stiefelette", "Western-Stiefelette"]
    allowed_material_groups: ["animal", "synthetic", "blend"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_shaft_height, attr_heel_height_cm, attr_toe_shape, attr_upper_material, attr_color_primary]
    disambiguation_hints: ["Absatzhöhe -> attr_heel_height_cm."]

  - id: it_sandals
    label_de: "Sandale"
    label_en: "Sandals"
    category_id: cat_shoes_sandals
    synonyms_de: ["Sandalen", "Riemchensandale", "Badesandale"]
    variants: ["Riemchensandale", "Slide", "Badesandale", "Trekkingsandale"]
    allowed_material_groups: ["synthetic", "blend", "plant", "animal"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_upper_material, attr_closure_type, attr_sole_material, attr_color_primary]
    disambiguation_hints: ["Badesandale/Slide oft ohne Verschluss; closure_type entsprechend."]

  - id: it_slipper_home
    label_de: "Hausschuh"
    label_en: "Slippers"
    category_id: cat_footwear
    synonyms_de: ["Pantoffel", "Filzhausschuh"]
    variants: ["Filz", "Lammfell", "offen", "geschlossen"]
    allowed_material_groups: ["animal", "plant", "blend", "synthetic", "regenerated"]
    required_attributes: [attr_brand, attr_size_system, attr_size_label_raw]
    optional_attributes: [attr_upper_material, attr_sole_material, attr_lining_material, attr_color_primary]
    disambiguation_hints: ["Nicht mit Loafer verwechseln (klassischer Lederschuh)."]

  # ------------------------------------------------------------
  # 14) Accessoires (cat_acc_* + cat_accessories)
  # ------------------------------------------------------------
  - id: it_belt
    label_de: "Gürtel"
    label_en: "Belt"
    category_id: cat_acc_belts
    synonyms_de: ["Ledergürtel", "Textilgürtel"]
    variants: ["Ledergürtel", "Flechtgürtel", "Stoffgürtel"]
    allowed_material_groups: ["animal", "synthetic", "blend", "plant"]
    required_attributes: [attr_brand]
    optional_attributes: [attr_size_system, attr_size_label_raw, attr_color_primary, attr_material_composition]
    disambiguation_hints: ["Gürtel am Trenchcoat ist Detail, nicht eigener Gürtel-Record (wenn fest vernäht/mitgeliefert)."]

  - id: it_watch
    label_de: "Uhr"
    label_en: "Watch"
    category_id: cat_acc_watches
    synonyms_de: ["Armbanduhr", "Wristwatch"]
    variants: ["Analog", "Digital", "Smartwatch"]
    allowed_material_groups: ["synthetic", "blend", "animal", "plant"]
    required_attributes: [attr_brand]
    optional_attributes: [attr_color_primary, attr_material_composition]
    disambiguation_hints: ["Metall/Steel ist nicht in Materialgruppen abgebildet; ggf. im Textfeld belassen."]

  - id: it_hat
    label_de: "Mütze/Hut"
    label_en: "Hat/Beanie"
    category_id: cat_acc_hats
    synonyms_de: ["Mütze", "Beanie", "Cap", "Hut"]
    variants: ["Beanie", "Cap", "Basecap", "Strickmütze", "Bucket Hat"]
    allowed_material_groups: ["plant", "animal", "blend", "synthetic", "regenerated"]
    required_attributes: [attr_brand]
    optional_attributes: [attr_size_system, attr_size_label_raw, attr_color_primary, attr_material_composition]
    disambiguation_hints: ["Cap/Basecap -> Variante; Material als attr_material_composition."]

  - id: it_gloves
    label_de: "Handschuhe"
    label_en: "Gloves"
    category_id: cat_acc_gloves
    synonyms_de: ["Lederhandschuhe", "Strickhandschuhe"]
    variants: ["Lederhandschuh", "Strickhandschuh", "Fingerlos", "Fäustling"]
    allowed_material_groups: ["animal", "plant", "blend", "synthetic", "regenerated"]
    required_attributes: [attr_brand]
    optional_attributes: [attr_size_system, attr_size_label_raw, attr_lining_material, attr_color_primary, attr_material_composition]
    disambiguation_hints: ["Lederhandschuh -> Materialhinweis; nicht eigener Handschuh-Typ."]

  - id: it_bag
    label_de: "Tasche"
    label_en: "Bag"
    category_id: cat_acc_bags
    synonyms_de: ["Handtasche", "Umhängetasche", "Rucksack", "Gürteltasche", "Shopper"]
    variants: ["Rucksack", "Umhängetasche", "Handtasche", "Gürteltasche", "Shopper", "Weekender"]
    allowed_material_groups: ["synthetic", "blend", "plant", "animal", "regenerated"]
    required_attributes: [attr_brand]
    optional_attributes: [attr_color_primary, attr_material_composition, attr_size_system, attr_size_label_raw]
    disambiguation_hints: ["Gürteltasche ist Tasche-Variante (nicht Gürtel)."]

  - id: it_scarf
    label_de: "Schal/Tuch"
    label_en: "Scarf"
    category_id: cat_accessories
    synonyms_de: ["Schal", "Tuch", "Stola"]
    variants: ["Winterschal", "Seidentuch", "Strickschal"]
    allowed_material_groups: ["animal", "plant", "blend", "synthetic", "regenerated"]
    required_attributes: [attr_brand]
    optional_attributes: [attr_color_primary, attr_material_composition, attr_care_instructions_text]
    disambiguation_hints: ["Kategorie in Part 02 ist (noch) nicht separat; daher cat_accessories."]

  - id: it_tie
    label_de: "Krawatte/Fliege"
    label_en: "Tie/Bow Tie"
    category_id: cat_accessories
    synonyms_de: ["Krawatte", "Fliege"]
    variants: ["Krawatte", "Fliege", "Strickkrawatte"]
    allowed_material_groups: ["animal", "plant", "blend", "synthetic", "regenerated"]
    required_attributes: [attr_brand]
    optional_attributes: [attr_color_primary, attr_material_composition]
    disambiguation_hints: ["Formell; occasion ggf. ergänzen (attr_occasion)."]
