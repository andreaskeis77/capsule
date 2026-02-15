
```markdown
<!-- FILE: ontology_part_05_materials_sustainability_certifications.md -->
# Part 05 – Materialien, Nachhaltigkeit, Zertifikate
version: "0.9.0"
date: "2026-01-12"
scope: "Material-Lexikon inkl. Synonyme, Eigenschaften (1..5), Sustainability-Score (1..5), Pflege-/Risiko-Hinweise"
toc:
  - materials
  - certifications
  - sustainability_scoring_heuristic

```yaml
materials:
  # Pflanzlich (plant)
  - id: mat_cotton
    label_de: "Baumwolle"
    label_en: "Cotton"
    synonyms: ["CO", "Cotton"]
    group: plant
    properties: {breathability: 4, warmth: 2, stretch: 1, wrinkle: 3, durability: 4, odor: 3, pilling_risk: 2}
    sustainability: {score_1to5: 3, notes_de: "Besser bei Bio/Fairtrade; konventionell wasser-/pestizidintensiv.", typical_certifications: [cert_gots, cert_fairtrade_cotton, cert_oeko_tex_100]}
    care_risks: ["Einlaufen bei heißer Wäsche", "Farbverlust bei dunklen Farben"]
    common_blends: ["Baumwolle+Elasthan (Stretch)", "Baumwolle+Polyester (pflegeleichter, weniger atmungsaktiv)"]

  - id: mat_organic_cotton
    label_de: "Bio-Baumwolle"
    label_en: "Organic Cotton"
    synonyms: ["Organic Cotton"]
    group: plant
    properties: {breathability: 4, warmth: 2, stretch: 1, wrinkle: 3, durability: 4, odor: 3, pilling_risk: 2}
    sustainability: {score_1to5: 4, notes_de: "Bessere Agrarpraktiken; ideal mit GOTS.", typical_certifications: [cert_gots, cert_oeko_tex_100]}
    care_risks: ["Einlaufen möglich"]
    common_blends: ["Bio-Baumwolle+Elasthan"]

  - id: mat_linen
    label_de: "Leinen"
    label_en: "Linen"
    synonyms: ["Flachs", "LI", "Linen"]
    group: plant
    properties: {breathability: 5, warmth: 2, stretch: 1, wrinkle: 5, durability: 4, odor: 4, pilling_risk: 1}
    sustainability: {score_1to5: 4, notes_de: "Oft geringerer Wasserbedarf; knittert stark (Feature, kein Fehler).", typical_certifications: [cert_oeko_tex_100]}
    care_risks: ["Knitteranfällig", "kann steif wirken ohne Weichspüler"]
    common_blends: ["Leinen+Baumwolle", "Leinen+Viskose"]

  - id: mat_hemp
    label_de: "Hanf"
    label_en: "Hemp"
    synonyms: ["Hemp"]
    group: plant
    properties: {breathability: 4, warmth: 2, stretch: 1, wrinkle: 4, durability: 5, odor: 4, pilling_risk: 1}
    sustainability: {score_1to5: 4, notes_de: "Robust; häufig gute Öko-Bilanz.", typical_certifications: [cert_oeko_tex_100]}
    care_risks: ["Anfangs steifer Griff"]
    common_blends: ["Hanf+Baumwolle"]

  # Regenerierte Zellulose (regenerated)
  - id: mat_viscose
    label_de: "Viskose"
    label_en: "Viscose"
    synonyms: ["Rayon", "CV", "Viscose", "Rayon"]
    group: regenerated
    properties: {breathability: 4, warmth: 2, stretch: 1, wrinkle: 4, durability: 3, odor: 3, pilling_risk: 2}
    sustainability: {score_1to5: 3, notes_de: "Stark abhängig von Herstellprozess/Forstwirtschaft; Lyocell meist besser.", typical_certifications: [cert_oeko_tex_100]}
    care_risks: ["Schwächer im nassen Zustand", "kann einlaufen/verziehen"]
    common_blends: ["Viskose+Polyester", "Viskose+Elasthan"]

  - id: mat_lyocell
    label_de: "Lyocell"
    label_en: "Lyocell"
    synonyms: ["TENCEL", "CL", "Lyocell"]
    group: regenerated
    properties: {breathability: 4, warmth: 2, stretch: 1, wrinkle: 3, durability: 4, odor: 4, pilling_risk: 2}
    sustainability: {score_1to5: 4, notes_de: "Geschlossener Lösungsmittelkreislauf (typisch) -> oft bessere Bilanz.", typical_certifications: [cert_oeko_tex_100]}
    care_risks: ["Schonend waschen, Pilling möglich bei Reibung"]
    common_blends: ["Lyocell+Baumwolle", "Lyocell+Elasthan"]

  - id: mat_modal
    label_de: "Modal"
    label_en: "Modal"
    synonyms: ["CMD", "Modal"]
    group: regenerated
    properties: {breathability: 4, warmth: 2, stretch: 2, wrinkle: 2, durability: 3, odor: 4, pilling_risk: 2}
    sustainability: {score_1to5: 3, notes_de: "Weich, oft aus Buchenholz; Prozess variiert.", typical_certifications: [cert_oeko_tex_100]}
    care_risks: ["Schonwaschgang empfohlen"]
    common_blends: ["Modal+Elasthan"]

  # Synthetik (synthetic)
  - id: mat_polyester
    label_de: "Polyester"
    label_en: "Polyester"
    synonyms: ["PES", "Polyester"]
    group: synthetic
    properties: {breathability: 2, warmth: 2, stretch: 1, wrinkle: 1, durability: 4, odor: 2, pilling_risk: 3}
    sustainability: {score_1to5: 2, notes_de: "Langlebig, aber fossilbasiert; recyceltes Polyester besser.", typical_certifications: [cert_oeko_tex_100, cert_bluesign]}
    care_risks: ["Geruchsbindung", "Mikroplastikabrieb", "statische Aufladung"]
    common_blends: ["Polyester+Baumwolle", "Polyester+Viskose", "Polyester+Elasthan"]

  - id: mat_recycled_polyester
    label_de: "Recyceltes Polyester"
    label_en: "Recycled Polyester"
    synonyms: ["rPES", "recycled polyester"]
    group: synthetic
    properties: {breathability: 2, warmth: 2, stretch: 1, wrinkle: 1, durability: 4, odor: 2, pilling_risk: 3}
    sustainability: {score_1to5: 3, notes_de: "Besser als neu, aber weiterhin Kunststoff; Abrieb bleibt Thema.", typical_certifications: [cert_oeko_tex_100, cert_bluesign]}
    care_risks: ["Geruchsbindung", "Mikroplastikabrieb"]
    common_blends: ["rPES+Elasthan"]

  - id: mat_polyamide
    label_de: "Polyamid"
    label_en: "Polyamide"
    synonyms: ["PA", "Nylon", "Polyamide"]
    group: synthetic
    properties: {breathability: 2, warmth: 2, stretch: 1, wrinkle: 1, durability: 5, odor: 2, pilling_risk: 3}
    sustainability: {score_1to5: 2, notes_de: "Sehr robust; recycelte Varianten besser.", typical_certifications: [cert_oeko_tex_100, cert_bluesign]}
    care_risks: ["Geruchsbindung", "Mikroplastikabrieb"]
    common_blends: ["PA+Elasthan (Activewear)", "PA+Wolle (Strumpfwaren)"]

  - id: mat_elastane
    label_de: "Elasthan"
    label_en: "Elastane"
    synonyms: ["EL", "Spandex", "Lycra"]
    group: synthetic
    properties: {breathability: 1, warmth: 1, stretch: 5, wrinkle: 1, durability: 3, odor: 2, pilling_risk: 2}
    sustainability: {score_1to5: 1, notes_de: "Kleiner Anteil ok; erschwert Recycling bei hohen Anteilen.", typical_certifications: [cert_oeko_tex_100]}
    care_risks: ["Hitzeempfindlich", "Alterung durch Chlor/UV"]
    common_blends: ["Baumwolle+Elasthan", "PA+Elasthan", "PES+Elasthan"]

  - id: mat_acrylic
    label_de: "Acryl"
    label_en: "Acrylic"
    synonyms: ["PAN", "Acrylic"]
    group: synthetic
    properties: {breathability: 1, warmth: 3, stretch: 2, wrinkle: 1, durability: 3, odor: 2, pilling_risk: 4}
    sustainability: {score_1to5: 1, notes_de: "Fossilbasiert, pilling-anfällig.", typical_certifications: [cert_oeko_tex_100]}
    care_risks: ["Pilling", "statisch"]
    common_blends: ["Acryl+Wolle"]

  # Tierisch (animal)
  - id: mat_wool
    label_de: "Schurwolle"
    label_en: "Virgin Wool"
    synonyms: ["WO", "Virgin Wool", "Schurwolle"]
    group: animal
    properties: {breathability: 4, warmth: 5, stretch: 2, wrinkle: 2, durability: 4, odor: 4, pilling_risk: 3}
    sustainability: {score_1to5: 4, notes_de: "Langlebig, reparierbar; Tierwohl/Standard wichtig (z. B. RWS).", typical_certifications: [cert_rws, cert_oeko_tex_100]}
    care_risks: ["Filzen bei Wärme/Reibung", "Mottenrisiko"]
    common_blends: ["Wolle+Polyamid (haltbarer)", "Wolle+Kaschmir"]

  - id: mat_merino
    label_de: "Merinowolle"
    label_en: "Merino Wool"
    synonyms: ["Merino"]
    group: animal
    properties: {breathability: 5, warmth: 5, stretch: 2, wrinkle: 2, durability: 4, odor: 5, pilling_risk: 3}
    sustainability: {score_1to5: 4, notes_de: "Sehr gute Geruchsneutralität; Standard/Tierwohl beachten.", typical_certifications: [cert_rws]}
    care_risks: ["Pilling bei Feinstrick", "Filzen bei falscher Wäsche"]
    common_blends: ["Merino+Polyamid (Socken)"]

  - id: mat_cashmere
    label_de: "Kaschmir"
    label_en: "Cashmere"
    synonyms: ["Cashmere"]
    group: animal
    properties: {breathability: 4, warmth: 5, stretch: 2, wrinkle: 2, durability: 3, odor: 4, pilling_risk: 4}
    sustainability: {score_1to5: 3, notes_de: "Luxusfaser; Qualität/Tierhaltung variiert stark.", typical_certifications: []}
    care_risks: ["Pilling", "empfindlich, Handwäsche/Schonprogramm"]
    common_blends: ["Wolle+Kaschmir"]

  - id: mat_silk
    label_de: "Seide"
    label_en: "Silk"
    synonyms: ["SE", "Silk"]
    group: animal
    properties: {breathability: 4, warmth: 3, stretch: 1, wrinkle: 3, durability: 3, odor: 3, pilling_risk: 1}
    sustainability: {score_1to5: 3, notes_de: "Hochwertig, pflegeintensiv; soziale Standards variieren.", typical_certifications: [cert_oeko_tex_100]}
    care_risks: ["Wasserflecken", "Sonne kann ausbleichen", "Reinigung häufig empfohlen"]
    common_blends: ["Seide+Viskose"]

  - id: mat_leather
    label_de: "Leder"
    label_en: "Leather"
    synonyms: ["Leder", "Glattleder", "Nappa"]
    group: animal
    properties: {breathability: 3, warmth: 3, stretch: 2, wrinkle: 2, durability: 5, odor: 4, pilling_risk: 1}
    sustainability: {score_1to5: 3, notes_de: "Sehr langlebig; Gerbprozess kritisch, LWG als Indikator.", typical_certifications: [cert_lwg]}
    care_risks: ["Austrocknung ohne Pflege", "Wasserflecken", "Farbabrieb"]
    common_blends: ["Leder+Textil (Sneaker)"]

  - id: mat_suede
    label_de: "Veloursleder"
    label_en: "Suede"
    synonyms: ["Suede", "Wildleder"]
    group: animal
    properties: {breathability: 3, warmth: 3, stretch: 2, wrinkle: 2, durability: 4, odor: 4, pilling_risk: 1}
    sustainability: {score_1to5: 3, notes_de: "Wie Leder; Pflege wichtig.", typical_certifications: [cert_lwg]}
    care_risks: ["Schmutzempfindlich", "Imprägnierung nötig"]
    common_blends: []

  # Spezial/Materialeffekte
  - id: mat_sequins
    label_de: "Pailletten"
    label_en: "Sequins"
    synonyms: ["Sequins", "Paillettenstoff"]
    group: blend
    properties: {breathability: 1, warmth: 2, stretch: 1, wrinkle: 1, durability: 3, odor: 2, pilling_risk: 2}
    sustainability: {score_1to5: 1, notes_de: "Meist Kunststoff/Verbund -> schwer zu recyceln; Anlass-Teil.", typical_certifications: []}
    care_risks: ["Vision-Farbfehler durch Reflexion", "Empfindlich, oft Handwäsche"]
    common_blends: ["Pailletten auf Polyester/Netz"]

certifications:
  - id: cert_gots
    label: "GOTS"
    scope: textile
    meaning_de: "Global Organic Textile Standard – Bio-Fasern + Umwelt-/Sozialkriterien entlang der Lieferkette."
    typical_claim_phrases_de: ["GOTS", "GOTS-zertifiziert", "organic textile standard"]
    fraud_risk_notes_de: "Achte auf Zertifikatsnummer/Label-Nachweis."

  - id: cert_oeko_tex_100
    label: "OEKO-TEX Standard 100"
    scope: chemical
    meaning_de: "Schadstoffgeprüfte Textilien – Fokus auf Chemikaliengrenzwerte im Endprodukt."
    typical_claim_phrases_de: ["OEKO-TEX", "Standard 100", "schadstoffgeprüft"]
    fraud_risk_notes_de: "Sagt nichts über Bio-Anbau oder Löhne aus."

  - id: cert_fairtrade_cotton
    label: "Fairtrade Cotton"
    scope: social
    meaning_de: "Fairtrade-Standards für Baumwolle – soziale/ökonomische Kriterien."
    typical_claim_phrases_de: ["Fairtrade Cotton", "Fairtrade-Baumwolle"]
    fraud_risk_notes_de: "Umfang prüfen (nur Baumwolle vs. gesamtes Produkt)."

  - id: cert_bluesign
    label: "bluesign"
    scope: chemical
    meaning_de: "Chemikalien- und Prozessstandard für Textilproduktion (Input Stream)."
    typical_claim_phrases_de: ["bluesign", "bluesign approved"]
    fraud_risk_notes_de: "Gilt oft für Materialien/Komponenten, nicht zwingend das ganze Produkt."

  - id: cert_rws
    label: "RWS"
    scope: animal
    meaning_de: "Responsible Wool Standard – Tierwohl und Landmanagement für Wolle."
    typical_claim_phrases_de: ["RWS", "Responsible Wool Standard"]
    fraud_risk_notes_de: "Auf Scope achten (Merino/Wolle)."

  - id: cert_lwg
    label: "LWG"
    scope: leather
    meaning_de: "Leather Working Group – Bewertung von Gerbereien (Umwelt/Prozess)."
    typical_claim_phrases_de: ["LWG", "Leather Working Group"]
    fraud_risk_notes_de: "Nicht jedes Leder im Produkt muss LWG sein."

sustainability_scoring_heuristic:
  description_de: "Heuristik für attr_sustainability_score_1to5 (transparent, anpassbar)."
  steps:
    - "Base = material.sustainability.score_1to5 des Hauptmaterials"
    - "+1 wenn mind. 1 starkes Zertifikat vorhanden (GOTS, RWS, bluesign, LWG) – max 5"
    - "-1 wenn material_composition >80% (mat_polyester oder mat_acrylic) und keine Zertifikate – min 1"
    - "Optional +1 wenn reparierbar (Leder/Schurwolle) und Pflegehinweise vorhanden"
