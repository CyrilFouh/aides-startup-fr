"""Chargement du catalogue compact embarqué dans le skill."""

from __future__ import annotations

import json
import os
from pathlib import Path


def load_catalogue() -> list[dict]:
    """Charge le catalogue compact (~1700 aides crédibles).

    Le fichier est embarqué dans `data/catalogue_compact.json` à côté du
    SKILL.md. Si la variable d'env AIDES_COMPACT_JSON pointe vers un
    fichier valide, l'utiliser à la place (utile pour fournir une version
    plus à jour sans réinstaller le skill).
    """
    override = os.environ.get("AIDES_COMPACT_JSON")
    if override and Path(override).exists():
        path = Path(override)
    else:
        path = Path(__file__).resolve().parent.parent / "data" / "catalogue_compact.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("aides", data)


# Aides automatiques invisibles dans le catalogue mais à mentionner
# systématiquement quand les conditions sont remplies. Source : fiches enrichies
# `references/fiches_aides_fiscales.md`.
AIDES_AUTOMATIQUES = {
    "JEI": {
        "id": "JEI-2025",
        "nom": "Statut Jeune Entreprise Innovante (JEI)",
        "ticket_min": 50_000,
        "ticket_max": 250_000,
        "natures": ["Allègement fiscal", "Exonération de charges sociales"],
        "lien": "https://www.urssaf.fr/accueil/employeur/beneficier-exonerations/exonerations-secteur-activite/jeunes-entreprises-innovantes.html",
        "criteres_eligibilite": "Entreprise < 8 ans, PME UE, indépendance capital ≥ 50 %, ≥ 20 % de charges en R&D (LFSS 2025)",
        "timeline": "Application immédiate sur DSN",
        "selectivite": "Automatique si critères remplis (mais contrôle URSSAF fréquent)",
        "tip": "Documenter time-sheets R&D des le J1 ; rescrit URSSAF recommandé",
    },
    "JEC": {
        "id": "JEC-2025",
        "nom": "Statut Jeune Entreprise de Croissance (JEC)",
        "ticket_min": 30_000,
        "ticket_max": 150_000,
        "natures": ["Exonération de charges sociales"],
        "lien": "https://entreprendre.service-public.gouv.fr/vosdroits/F31188",
        "criteres_eligibilite": "Critères JEI sauf seuil R&D (5-20 %) + croissance effectif +100 % et +10 ETP",
        "timeline": "Application sur DSN, vérification annuelle",
        "selectivite": "Automatique si critères remplis",
        "tip": "Vérifier les indicateurs de croissance à chaque clôture (perte rétroactive possible)",
    },
    "CIR": {
        "id": "CIR-2025",
        "nom": "Crédit d'Impôt Recherche (CIR)",
        "ticket_min": 30_000,
        "ticket_max": 1_000_000,
        "natures": ["Allègement fiscal"],
        "lien": "https://www.impots.gouv.fr/professionnel/credit-dimpot-recherche",
        "criteres_eligibilite": "Dépenses R&D conformes Frascati (salaires, sous-traitance agréée, amortissements R&D)",
        "timeline": "Déclaré N+1, remboursé sous 6 mois pour PME",
        "selectivite": "Automatique mais contrôle DGFiP fréquent (~1 sur 4 sur 5 ans)",
        "tip": "Forfait fonctionnement passé à 40 % en LF 2025 ; suppression dispositif jeune docteur",
    },
    "CII": {
        "id": "CII-2025",
        "nom": "Crédit d'Impôt Innovation (CII)",
        "ticket_min": 10_000,
        "ticket_max": 80_000,
        "natures": ["Allègement fiscal"],
        "lien": "https://www.impots.gouv.fr/professionnel/credit-dimpot-innovation-cii",
        "criteres_eligibilite": "PME au sens UE, dépenses d'innovation hors R&D pure (design, prototypage)",
        "timeline": "Déclaré N+1, remboursé PME sous 6 mois",
        "selectivite": "Automatique si dépenses justifiées",
        "tip": "Taux abaissé à 20 % en LF 2025 (vs 30 % avant), plafond assiette 400k€ → crédit max 80k€",
    },
    "CICo": {
        "id": "CICo-2025",
        "nom": "Crédit d'impôt Recherche Collaborative (CICo)",
        "ticket_min": 50_000,
        "ticket_max": 3_000_000,
        "natures": ["Allègement fiscal"],
        "lien": "https://www.impots.gouv.fr/professionnel/cico",
        "criteres_eligibilite": "Contrat de collaboration avec ORDC (organisme de recherche et diffusion des connaissances)",
        "timeline": "Déclaré N+1",
        "selectivite": "Automatique si contrat éligible",
        "tip": "Taux 50 % PME (40 % autres), plafond 6 M€ ; cumulable avec CIR sur lots distincts",
    },
    "ACRE": {
        "id": "ACRE",
        "nom": "Aide à la création ou reprise d'entreprise (ACRE)",
        "ticket_min": 5_000,
        "ticket_max": 25_000,
        "natures": ["Exonération de charges sociales"],
        "lien": "https://entreprendre.service-public.gouv.fr/vosdroits/F11677",
        "criteres_eligibilite": "Création/reprise d'entreprise, demandeur d'emploi, jeune <30 ans, RSA, etc.",
        "timeline": "1ʳᵉ année d'activité",
        "selectivite": "Automatique si statut éligible",
        "tip": "À demander dans les 45 jours suivant la création",
    },
}
