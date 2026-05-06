"""Règles de cumul / exclusion mutuelle entre aides.

Beaucoup de dispositifs Bpifrance financent les MÊMES dépenses (R&D
prototypage, dépenses d'innovation pré-industrielle…). Les empiler dans une
recommandation donne un total irréaliste car ils ne sont pas cumulables sur
une même assiette.

Principe : on regroupe les aides en "familles" qui se substituent les unes
aux autres. Dans le top 5, on garde au plus UNE aide par famille — celle
qui maximise le score.

Source : doctrine Bpifrance (catalogue offres + guide cumul) et règlement
RGEC 651/2014. Mises à jour 2025-2026.
"""

from __future__ import annotations

# Familles d'aides mutuellement exclusives sur les mêmes dépenses.
# Une famille = liste de motifs (substring lowercase) qui matchent les noms
# d'aides du catalogue.
FAMILLES_EXCLUSIVES: dict[str, list[str]] = {
    # Aides BPI à l'innovation entreprise (pré-industrialisation)
    # API, Avance Innovation, Prêt Innovation R&D financent la même phase
    # avec des modalités différentes (subv vs avance vs prêt) — pas cumulables
    # sur une même assiette de dépenses.
    "bpi_innovation_pre_industriel": [
        "aide pour le développement de l'innovation",
        "aide à l'innovation",
        "avance innovation",
        "prêt innovation r&d",
        "prêt innovation rd",
        "api innovation",
        "adi innovation",
    ],
    # Bourses BFT et BFTE — non cumulables entre elles (et avec ADI/API
    # sur les mêmes dépenses)
    "bpi_bourses_creation": [
        "bourse french tech",
        "bourse french tech emergence",
        "bft emergence",
    ],
    # Diagnostics Bpifrance — chacun couvre un thème différent, mais on
    # ne propose pas plus de 2 diagnostics dans le top 5
    "bpi_diags": [
        "diag décarbon",
        "diag data ia",
        "diag ia",
        "diag cyber",
        "diag adaptation",
        "diag biodiversité",
        "diag éco",
    ],
    # AAP France 2030 généraux — un AAP par projet (pas plusieurs en même
    # temps sur la même thématique)
    "france_2030_aap_general": [
        "france 2030 - appel à projets \"projets d'innovation\"",
        "france 2030 - appel à projets « projets d'innovation »",
        "i-démo",
        "france 2030 - démontrer la valeur",
    ],
    # AAP IA spécifiques
    "france_2030_ia": [
        "pionniers de l'intelligence artificielle",
        "pionniers de l'ia",
        "booster ia",
    ],
    # Crédits d'impôt — chacun automatique, mais pas cumulables sur les
    # MÊMES dépenses : une dépense déclarée en CIR ne peut pas l'être en CII
    "credits_impot": [
        "crédit d'impôt recherche",
        "crédit d'impôt innovation",
        "cir",
        "cii",
        "crédit d'impôt en faveur de la recherche collaborative",
        "cico",
    ],
    # Statuts JEI / JEC / JEII — un seul statut à la fois
    "statuts_jei": [
        "jeune entreprise innovante",
        "jeune entreprise de croissance",
        "jeune entreprise d'innovation à impact",
        "jei -",
        "jeii -",
        "jec -",
    ],
    # Prêts d'honneur — non cumulables entre eux
    "prets_honneur": [
        "prêt d'honneur",
        "pret d'honneur",
    ],
}


def famille_de(nom_aide: str) -> str | None:
    """Retourne la famille (clé) à laquelle appartient une aide, ou None."""
    nom = nom_aide.lower()
    for famille, motifs in FAMILLES_EXCLUSIVES.items():
        for motif in motifs:
            if motif in nom:
                return famille
    return None


def filtrer_par_familles(
    aides_scored: list[tuple[float, dict]],
    max_par_famille: dict[str, int] | None = None,
) -> list[dict]:
    """Garde, parmi les aides scorées, au plus N par famille.

    Args:
        aides_scored: liste [(score, aide), ...] triée par score décroissant
        max_par_famille: surcharge du nombre max par famille (défaut: 1, sauf
        diags = 2 et credits_impot = 2 — CIR + CII souvent cumulables si
        dépenses distinctes, à signaler à l'utilisateur)

    Returns:
        Liste d'aides filtrées (sans le score), ordre préservé.
    """
    if max_par_famille is None:
        max_par_famille = {
            "bpi_diags": 2,
            "credits_impot": 2,  # CIR + CII admis si dépenses distinctes
            "statuts_jei": 1,
        }

    seen_count: dict[str, int] = {}
    out = []
    for score, aide in aides_scored:
        fam = famille_de(aide.get("nom", ""))
        if fam is None:
            out.append(aide)
            continue
        n_max = max_par_famille.get(fam, 1)
        if seen_count.get(fam, 0) < n_max:
            seen_count[fam] = seen_count.get(fam, 0) + 1
            out.append(aide)
        # sinon : on supprime cette aide (déjà couverte par une plus prioritaire)

    return out


def aides_alternatives(aide: dict, catalogue: list[dict]) -> list[dict]:
    """Pour une aide donnée, liste les autres aides de sa famille
    qu'on pourrait considérer en remplacement (utile pour le rapport :
    "envisager aussi telle ou telle alternative")."""
    fam = famille_de(aide.get("nom", ""))
    if fam is None:
        return []
    return [
        a for a in catalogue
        if a.get("nom") != aide.get("nom") and famille_de(a.get("nom", "")) == fam
    ]


# Note pour le scoring : quand on a appliqué la déduplication par famille,
# on signale à l'utilisateur que d'autres aides de la même famille existent
# mais qu'elles ne se cumulent pas. Cela évite l'effet "trop beau pour être
# vrai" et améliore la crédibilité du rapport.
