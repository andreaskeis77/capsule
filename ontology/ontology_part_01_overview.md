<!-- FILE: ontology_part_01_overview.md -->
# Mode-Ontologie für Capsule-Wardrobe-RAG (lokal)
version: "0.9.0"
date: "2026-01-12"
scope: "Bekleidung, Schuhe, Accessoires, Sport/Outdoor; deutsch+englische Synonyme; DB-Attribut-Lexikon; Disambiguation-Regeln"
toc:
  - 1. Konventionen (IDs, Slugs, Synonyme)
  - 2. Core Model (Entity-Typen & Beziehungen)
  - 3. Normalisierungsprinzipien (Größen, Farben, Materialien)
  - 4. Referenzen auf Parts

## 1) Konventionen
### 1.1 IDs / Slugs
- Alle `id` sind `lower_snake_case`, ASCII, ohne Umlaute (ä->ae, ö->oe, ü->ue, ß->ss).
- Präfixe:
  - Kategorien: `cat_...`
  - Item-Types: `it_...`
  - Attribute: `attr_...`
  - Value-Sets: `vs_...`
  - Materialien: `mat_...`
  - Fits/Cuts: `fc_...`
  - Brands: `br_...`
  - Shops: `shop_...`
  - Zertifikate: `cert_...`
  - Regeln: `rule_###`

### 1.2 Synonyme
- `synonyms_de` und `label_en` dienen der Suche/Normalisierung.
- Materialkürzel als Synonyme (z. B. `PES -> Polyester`, `EL -> Elasthan`).

### 1.3 JSON-nahe Struktur
- Jede Entität ist ein Objekt mit stabiler Key-Reihenfolge.
- Arrays sind geordnet, keine Tabellen nötig.

## 2) Core Model – Entity-Typen (Schema-Definition)
> Die konkreten Instanzen folgen in den nächsten Parts.

```yaml
entity_schemas:
  category:
    keys_in_order: [id, label_de, label_en, description_de, parent_id, gender_target, typical_attributes, examples]
  item_type:
    keys_in_order: [id, label_de, label_en, category_id, synonyms_de, variants, allowed_material_groups, required_attributes, optional_attributes, disambiguation_hints]
  attribute:
    keys_in_order: [id, label_de, description_de, data_type, unit, allowed_values, value_patterns, negative_patterns, extraction_priority, common_source_fields]
  value_set:
    keys_in_order: [id, description_de, values]
  material:
    keys_in_order: [id, label_de, label_en, synonyms, group, properties, sustainability, care_risks, common_blends]
  fit_cut:
    keys_in_order: [id, domain, label_de, synonyms_de, description_de, conflicts_with, related_attributes]
  brand:
    keys_in_order: [id, label, tier, common_categories, known_confusions]
  shop:
    keys_in_order: [id, label, shop_type, typical_facets, mapping_hints]
  certification:
    keys_in_order: [id, label, scope, meaning_de, typical_claim_phrases_de, fraud_risk_notes_de]
  rules:
    keys_in_order: [id, if, then, confidence_adjustment, examples]
