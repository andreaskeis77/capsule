
```markdown
<!-- FILE: ontology_part_02_taxonomy.md -->
# Part 02 – Kategorienhierarchie (category)
version: "0.9.0"
date: "2026-01-12"
scope: "Hierarchie der Mode-Kategorien (5 Ebenen wo sinnvoll)"
toc:
  - Kategorien (YAML)

```yaml
categories:
  # Root
  - id: cat_apparel
    label_de: "Bekleidung"
    label_en: "Apparel"
    description_de: "Alle tragbaren Textil-/Lederwaren inkl. Unterwäsche und Sport/Outdoor."
    parent_id: null
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_brand, attr_size_system, attr_size_label_raw, attr_color_family, attr_material_composition]
    examples: ["Hemd", "Bluse", "Hose", "Kleid"]

  - id: cat_footwear
    label_de: "Schuhe"
    label_en: "Footwear"
    description_de: "Schuhe aller Art inkl. Einlagen-relevanter Maße."
    parent_id: null
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_brand, attr_size_system, attr_size_label_raw, attr_material_composition, attr_closure_type]
    examples: ["Sneaker", "Lederschuh", "Stiefel"]

  - id: cat_accessories
    label_de: "Accessoires"
    label_en: "Accessories"
    description_de: "Nicht primär-bekleidende Ergänzungen (Gürtel, Uhr, Mütze, Tasche etc.)."
    parent_id: null
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_brand, attr_color_family, attr_material_composition]
    examples: ["Gürtel", "Uhr", "Handschuhe", "Schal"]

  # Apparel Level 1
  - id: cat_apparel_outerwear
    label_de: "Oberbekleidung"
    label_en: "Outerwear"
    description_de: "Jacken, Mäntel, Sakkos/Blazer, Westen."
    parent_id: cat_apparel
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_fit_type, attr_season, attr_lining_material, attr_function_waterproof]
    examples: ["Mantel", "Blazer", "Funktionsjacke"]

  - id: cat_apparel_tops
    label_de: "Oberteile"
    label_en: "Tops"
    description_de: "T-Shirts, Hemden/Blusen, Strick, Hoodies."
    parent_id: cat_apparel
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_neckline, attr_sleeve_length, attr_collar_type, attr_fit_type]
    examples: ["Hemd", "Bluse", "Pullover"]

  - id: cat_apparel_bottoms
    label_de: "Unterteile"
    label_en: "Bottoms"
    description_de: "Hosen, Shorts, Röcke."
    parent_id: cat_apparel
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_rise, attr_leg_shape, attr_length_category, attr_fit_type]
    examples: ["Jeans", "Chino", "Rock"]

  - id: cat_apparel_dresses_jumpsuits
    label_de: "Kleider & Einteiler"
    label_en: "Dresses & Jumpsuits"
    description_de: "Kleider, Jumpsuits, Overalls."
    parent_id: cat_apparel
    gender_target: [women, unisex, kids]
    typical_attributes: [attr_silhouette, attr_length_category, attr_neckline, attr_sleeve_length]
    examples: ["Etuikleid", "Jumpsuit"]

  - id: cat_apparel_underwear
    label_de: "Unterwäsche & Socken"
    label_en: "Underwear & Hosiery"
    description_de: "Unterwäsche, Socken/Strümpfe, BHs, Shapewear."
    parent_id: cat_apparel
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_size_system, attr_material_composition, attr_stretch_percent]
    examples: ["Boxershorts", "Slip", "Socken"]

  - id: cat_apparel_sleepwear
    label_de: "Nachtwäsche"
    label_en: "Sleepwear"
    description_de: "Pyjamas, Nachthemden, Loungewear."
    parent_id: cat_apparel
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_fit_type, attr_material_composition, attr_season]
    examples: ["Pyjama", "Nachthemd"]

  - id: cat_apparel_sport_outdoor
    label_de: "Sport & Outdoor"
    label_en: "Sport & Outdoor"
    description_de: "Funktionsbekleidung, Baselayer, Trekking, Running, Ski."
    parent_id: cat_apparel
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_function_waterproof, attr_function_breathable, attr_season, attr_activity]
    examples: ["Funktionsjacke", "Laufshirt", "Trekkinghose"]

  # Outerwear Level 2-5 (Beispiele mit Tiefe)
  - id: cat_outerwear_jackets
    label_de: "Jacken"
    label_en: "Jackets"
    description_de: "Kurze bis mittellange Oberbekleidung."
    parent_id: cat_apparel_outerwear
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_closure_type, attr_hood, attr_lining_material]
    examples: ["Jeansjacke", "Bomberjacke"]

  - id: cat_outerwear_jackets_casual
    label_de: "Freizeitjacken"
    label_en: "Casual Jackets"
    description_de: "Alltag/Street, weniger formal."
    parent_id: cat_outerwear_jackets
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_style, attr_fit_type]
    examples: ["Bomber", "Jeansjacke"]

  - id: cat_outerwear_jackets_casual_bomber
    label_de: "Bomberjacken"
    label_en: "Bomber Jackets"
    description_de: "Kurze Jacken mit Bündchen."
    parent_id: cat_outerwear_jackets_casual
    gender_target: [women, men, unisex]
    typical_attributes: [attr_cuff_style, attr_ribbed_hem]
    examples: ["Bomber aus Nylon", "Wollbomber"]

  - id: cat_outerwear_jackets_outdoor
    label_de: "Outdoorjacken"
    label_en: "Outdoor Jackets"
    description_de: "Wetterschutz, Funktionalität."
    parent_id: cat_outerwear_jackets
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_function_waterproof, attr_function_windproof, attr_layer_system]
    examples: ["Hardshell", "Softshell"]

  - id: cat_outerwear_jackets_outdoor_hardshell
    label_de: "Hardshell-Jacken"
    label_en: "Hardshell Jackets"
    description_de: "Wasserdicht, winddicht, atmungsaktiv (Membran)."
    parent_id: cat_outerwear_jackets_outdoor
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_membrane, attr_seam_sealed, attr_water_column_mm]
    examples: ["3-Lagen-Hardshell", "2.5-Lagen-Jacke"]

  - id: cat_outerwear_coats
    label_de: "Mäntel"
    label_en: "Coats"
    description_de: "Längere Oberbekleidung, oft wärmer."
    parent_id: cat_apparel_outerwear
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_length_category, attr_lining_material, attr_season]
    examples: ["Wollmantel", "Trenchcoat"]

  - id: cat_outerwear_blazers_suits
    label_de: "Sakkos, Blazer & Anzüge"
    label_en: "Blazers, Suits"
    description_de: "Formelle bis semi-formelle Oberteile."
    parent_id: cat_apparel_outerwear
    gender_target: [women, men, unisex]
    typical_attributes: [attr_lapel_type, attr_occasion, attr_fit_type]
    examples: ["Sakko", "Blazer", "Anzug"]

  - id: cat_outerwear_blazers_suits_blazer
    label_de: "Blazer"
    label_en: "Blazers"
    description_de: "Einzelnes formelles Oberteil."
    parent_id: cat_outerwear_blazers_suits
    gender_target: [women, men, unisex]
    typical_attributes: [attr_lapel_type, attr_button_count, attr_fit_type]
    examples: ["Business-Blazer", "Casual-Blazer"]

  - id: cat_outerwear_blazers_suits_sakko_festlich
    label_de: "Festliche Sakkos"
    label_en: "Formal Blazers"
    description_de: "Sakkos für Anlässe (Hochzeit, Gala)."
    parent_id: cat_outerwear_blazers_suits
    gender_target: [men, unisex]
    typical_attributes: [attr_occasion, attr_fabric_shine, attr_lapel_type]
    examples: ["Smoking-Sakko", "Gala-Sakko"]

  - id: cat_outerwear_vests
    label_de: "Westen"
    label_en: "Vests"
    description_de: "Ärmellose Oberbekleidung (formal/Stepp)."
    parent_id: cat_apparel_outerwear
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_lining_material, attr_fill_material, attr_fill_weight_g]
    examples: ["Anzugweste", "Steppweste"]

  # Tops Level 2
  - id: cat_tops_tshirts
    label_de: "T-Shirts & Tops"
    label_en: "T-Shirts & Tops"
    description_de: "Kurzarm/ärmellos, meist Jersey."
    parent_id: cat_apparel_tops
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_neckline, attr_sleeve_length, attr_fit_type]
    examples: ["Rundhals T-Shirt", "Tanktop"]

  - id: cat_tops_shirts_blouses
    label_de: "Hemden & Blusen"
    label_en: "Shirts & Blouses"
    description_de: "Gewebte Oberteile mit Knopfleiste (typisch)."
    parent_id: cat_apparel_tops
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_collar_type, attr_cuff_type, attr_fit_type]
    examples: ["Businesshemd", "Bluse"]

  - id: cat_tops_knitwear
    label_de: "Strick & Pullover"
    label_en: "Knitwear"
    description_de: "Gestrickt/gewirkt, wärmend."
    parent_id: cat_apparel_tops
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_material_composition, attr_neckline, attr_season]
    examples: ["Pullover", "Cardigan"]

  - id: cat_tops_hoodies_sweat
    label_de: "Sweatshirts & Hoodies"
    label_en: "Sweatshirts & Hoodies"
    description_de: "Sweatware, oft Baumwollmix."
    parent_id: cat_apparel_tops
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_hood, attr_fit_type, attr_style]
    examples: ["Hoodie", "Crewneck"]

  # Bottoms Level 2-4
  - id: cat_bottoms_trousers
    label_de: "Hosen"
    label_en: "Trousers"
    description_de: "Lange Hosen (Jeans, Chinos, Stoffhosen)."
    parent_id: cat_apparel_bottoms
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_rise, attr_leg_shape, attr_closure_type, attr_fit_type]
    examples: ["Jeans", "Chino"]

  - id: cat_bottoms_trousers_denim
    label_de: "Jeans"
    label_en: "Jeans"
    description_de: "Denim-Hosen."
    parent_id: cat_bottoms_trousers
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_wash, attr_leg_shape, attr_rise]
    examples: ["Straight Jeans", "Skinny Jeans"]

  - id: cat_bottoms_trousers_chino
    label_de: "Chinos"
    label_en: "Chinos"
    description_de: "Baumwoll-Twill-Hosen, smart casual."
    parent_id: cat_bottoms_trousers
    gender_target: [women, men, unisex]
    typical_attributes: [attr_leg_shape, attr_rise, attr_occasion]
    examples: ["Slim Chino", "Regular Chino"]

  - id: cat_bottoms_trousers_suit
    label_de: "Anzughosen"
    label_en: "Suit Trousers"
    description_de: "Teil eines Anzugs / formelle Hosen."
    parent_id: cat_bottoms_trousers
    gender_target: [women, men, unisex]
    typical_attributes: [attr_occasion, attr_crease, attr_fit_type]
    examples: ["Wollanzughose"]

  - id: cat_bottoms_shorts
    label_de: "Shorts"
    label_en: "Shorts"
    description_de: "Kurze Hosen."
    parent_id: cat_apparel_bottoms
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_length_category, attr_fit_type, attr_occasion]
    examples: ["Jeansshorts", "Bermuda"]

  - id: cat_bottoms_skirts
    label_de: "Röcke"
    label_en: "Skirts"
    description_de: "Röcke verschiedener Formen."
    parent_id: cat_apparel_bottoms
    gender_target: [women, unisex, kids]
    typical_attributes: [attr_silhouette, attr_length_category, attr_waistband_style]
    examples: ["Bleistiftrock", "A-Linien-Rock"]

  # Dresses/Jumpsuits
  - id: cat_dresses
    label_de: "Kleider"
    label_en: "Dresses"
    description_de: "Kleider (Sommer, Business, Abend)."
    parent_id: cat_apparel_dresses_jumpsuits
    gender_target: [women, unisex, kids]
    typical_attributes: [attr_silhouette, attr_length_category, attr_occasion]
    examples: ["Etuikleid", "Sommerkleid"]

  - id: cat_jumpsuits
    label_de: "Jumpsuits & Overalls"
    label_en: "Jumpsuits & Overalls"
    description_de: "Einteiler mit Hosenbein."
    parent_id: cat_apparel_dresses_jumpsuits
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_closure_type, attr_fit_type, attr_occasion]
    examples: ["Jumpsuit", "Overall"]

  # Footwear Level 1-3
  - id: cat_shoes_sneaker
    label_de: "Sneaker"
    label_en: "Sneakers"
    description_de: "Sportlich/Alltag."
    parent_id: cat_footwear
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_sole_material, attr_upper_material, attr_closure_type]
    examples: ["Ledersneaker", "Stoffsneaker"]

  - id: cat_shoes_leather
    label_de: "Lederschuhe (klassisch)"
    label_en: "Leather Shoes"
    description_de: "Business/klassisch (Derby, Oxford, Loafer)."
    parent_id: cat_footwear
    gender_target: [women, men, unisex]
    typical_attributes: [attr_toe_shape, attr_heel_height_cm, attr_upper_material]
    examples: ["Oxford", "Derby", "Loafer"]

  - id: cat_shoes_boots
    label_de: "Stiefel & Stiefeletten"
    label_en: "Boots"
    description_de: "Hohe/halbhohe Schuhe, oft saisonal."
    parent_id: cat_footwear
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_shaft_height, attr_lining_material, attr_sole_profile]
    examples: ["Chelsea Boots", "Winterstiefel"]

  - id: cat_shoes_sandals
    label_de: "Sandalen"
    label_en: "Sandals"
    description_de: "Offene Schuhe."
    parent_id: cat_footwear
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_closure_type, attr_upper_material]
    examples: ["Riemchensandale", "Badesandale"]

  # Accessories Level 1-3 (Auswahl)
  - id: cat_acc_belts
    label_de: "Gürtel"
    label_en: "Belts"
    description_de: "Gürtel aus Leder/Textil."
    parent_id: cat_accessories
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_length_cm, attr_width_cm, attr_buckle_material]
    examples: ["Ledergürtel", "Textilgürtel"]

  - id: cat_acc_watches
    label_de: "Uhren"
    label_en: "Watches"
    description_de: "Armbanduhren."
    parent_id: cat_accessories
    gender_target: [women, men, unisex]
    typical_attributes: [attr_case_material, attr_strap_material, attr_water_resistance]
    examples: ["Quarzuhr", "Automatik"]

  - id: cat_acc_hats
    label_de: "Mützen & Hüte"
    label_en: "Hats"
    description_de: "Kopfbedeckungen."
    parent_id: cat_accessories
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_material_composition, attr_season]
    examples: ["Beanie", "Cap", "Fedora"]

  - id: cat_acc_gloves
    label_de: "Handschuhe"
    label_en: "Gloves"
    description_de: "Handschuhe aus Leder/Wolle/etc."
    parent_id: cat_accessories
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_material_composition, attr_lining_material, attr_touchscreen_compatible]
    examples: ["Lederhandschuh", "Strickhandschuh"]

  - id: cat_acc_bags
    label_de: "Taschen"
    label_en: "Bags"
    description_de: "Handtaschen, Rucksäcke, Shopper, Koffer."
    parent_id: cat_accessories
    gender_target: [women, men, unisex, kids]
    typical_attributes: [attr_volume_l, attr_strap_type, attr_closure_type]
    examples: ["Rucksack", "Shopper", "Umhängetasche"]
