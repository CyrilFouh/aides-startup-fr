"""Filtrage + scoring des aides selon le profil utilisateur (10 questions).

Usage en bibliothèque :
    from scoring_lead_magnet import build_top5, Profile
    profile = Profile(stade='seed', cofi_max=600_000, ...)
    top5, deuxieme_cercle = build_top5(profile)

Usage CLI :
    python3 scoring_lead_magnet.py --profile-json profile.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_data import AIDES_AUTOMATIQUES, load_catalogue  # noqa: E402
from cumul_rules import filtrer_par_familles, famille_de, aides_alternatives  # noqa: E402


# ===== Grille de cohérence taille / ticket (cf. references/coherence_taille_montant.md) =====

GRILLE_TICKET = {
    # stade : (petit_min, petit_max, moyen_max, gros_max, plafond_credibilite)
    "preseed": (5_000, 30_000, 100_000, 300_000, 500_000),
    "seed": (25_000, 75_000, 300_000, 1_000_000, 2_000_000),
    "serieA": (50_000, 150_000, 700_000, 3_000_000, 5_000_000),
    "serieB": (100_000, 300_000, 1_500_000, 5_000_000, 10_000_000),
    "bootstrap": (5_000, 30_000, 150_000, 500_000, 1_000_000),
    "pme": (30_000, 100_000, 500_000, 2_000_000, 3_000_000),
    "pme_grand": (50_000, 200_000, 1_000_000, 3_000_000, 5_000_000),
    "eti": (200_000, 500_000, 2_000_000, 10_000_000, 20_000_000),
}

# Mapping projets utilisateur -> projets catalogue
PROJET_MAP = {
    "creation": [
        "Financer le lancement de son entreprise",
        "Créer une entreprise innovante",
        "Financer la reprise d'une entreprise",
        "Acheter un fond de commerce",
        "Reprendre une entreprise innovante",
    ],
    "invest_local": [
        "Construction acquisition d'un local, d'un site",
        "Extension, rénovation ou aménagement d'un local, d'un site",
        "Acquérir, aménager un site, un local",
    ],
    "invest_materiel": [
        "Achat/modernisation de machines, équipements",
        "Financer ses investissements matériels",
        "Achats TIC, technologies numériques",
    ],
    "rh": [
        "Embauches, créations de poste",
        "Financer ses embauches",
        "Formation des salariés",
        "Gestion des emplois",
    ],
    "innovation_rd": [
        "Créer une entreprise innovante",
        "Partenariats technologiques, projets collaboratifs",
        "Faisabilité",
        "Investissements d'Avenir et France 2030",
    ],
    "transition_eco": [
        "Economies d'énergie, énergies renouvelables",
        "Gestion des déchets et économie circulaire",
        "Transports, véhicules propres",
        "Pollution de l'eau, de l'air et des sols",
        "Mettre en place un management environnemental - RSE ",
    ],
    "commercial": [
        "Actions de promotion commerciale, communication",
        "Commercialisation",
        "Développer l'offre, lancer de nouveaux produits",
    ],
    "tresorerie": [
        "Renforcer la structure financière, financer la croissance",
        "Financement global",
        "Garantir ses prêts bancaires",
        "Prévenir et gérer les difficultés",
        "Prêts d'honneur",
    ],
    "conseil_etudes": [
        "Etre conseillé et formé",
        "Réaliser une étude, un audit",
        "Etudes, conseils, expertise",
    ],
}

NATURE_MAP = {
    "subvention": ["Subvention"],
    "pret_avance": ["Prêt", "Prêt d'honneur", "Avance remboursable", "Bonification d'intérêt", "Crédit-bail"],
    "fiscal_social": ["Allègement fiscal", "Exonération de charges sociales"],
    "fonds_propres": ["Participation en capital"],
    "garantie": ["Garantie"],
    "accompagnement": ["Accompagnement", "Prix", "Appel à projet"],
}


@dataclass
class Profile:
    """Profil issu des 10 questions."""

    projets: set[str] = field(default_factory=set)
    domaine: str = "1"
    stade: str = "seed"  # preseed, seed, serieA, serieB, bootstrap, pme, pme_grand, eti
    natures: set[str] = field(default_factory=set)
    secteurs: set[str] = field(default_factory=set)
    effectif: str = "2"  # '1' à '6'
    region: str = "France"
    export: bool = False
    innovation: bool = False
    rd_pure: bool = False  # True si R&D au sens Frascati (vs innovation large)
    cofi_max: int = 100_000  # capacité de cofinancement en €
    nom_entreprise: str = "Votre entreprise"
    age_annees: float | None = None  # années d'existence

    @property
    def stade_grille(self) -> tuple[int, int, int, int, int]:
        return GRILLE_TICKET.get(self.stade, GRILLE_TICKET["seed"])


# ===== Filtrage =====

def aide_passes_filter(aide: dict, p: Profile) -> bool:
    """Filtrage dur sur les questions structurées."""
    # Couverture géo : on accepte tout pour ne pas perdre les territoriales
    # qui correspondent à la région de l'utilisateur ; le filtrage région
    # se fait dans aide_passes_region().

    # Domaine : on accepte si match OU si domaine non spécifié
    if p.domaine and aide.get("id_domaine") and aide["id_domaine"] != p.domaine:
        # tolérance : si projet innovation, on accepte aussi domaine 1 (Eco)
        if not (p.innovation and aide["id_domaine"] == "1"):
            return False

    # Effectif
    aide_eff = set(t for t in (aide.get("effectif") or "").split(",") if t)
    if aide_eff and p.effectif not in aide_eff:
        return False

    # Natures
    if p.natures:
        a_natures_hl = set()
        for hl, libs in NATURE_MAP.items():
            if any(lib in aide["natures"] for lib in libs):
                a_natures_hl.add(hl)
        if a_natures_hl and not (a_natures_hl & p.natures):
            return False

    # Projets
    if p.projets:
        a_projets_hl = set()
        for hl, libs in PROJET_MAP.items():
            if any(lib in aide["projets"] for lib in libs):
                a_projets_hl.add(hl)
        if a_projets_hl and not (a_projets_hl & p.projets):
            return False

    return True


def aide_passes_region(aide: dict, p: Profile) -> bool:
    """Filtrage région pour les aides territoriales."""
    if aide.get("couverture_geo") in ("2", "3"):
        return True  # nationale ou européenne
    # territoriale : doit matcher la région
    aide_terrs = set(aide.get("territoires", []))
    if "FRANCE" in aide_terrs:
        return True
    if p.region == "France":
        return True  # pas filtré
    return any(p.region.lower() in t.lower() for t in aide_terrs)


# ===== Scoring =====

def score_aide(aide: dict, p: Profile) -> tuple[float, dict]:
    """Score de crédibilité. Retourne (score, debug_info)."""
    petit_min, petit_max, moyen_max, gros_max, plafond = p.stade_grille

    score = 0.0
    debug = {}

    ticket_max = aide.get("montant_max_eur") or 0
    ticket_min = aide.get("montant_min_eur") or 0

    # 1. Cohérence ticket / stade
    # ticket_min est ce que l'aide refuse de descendre en dessous (ex: 100 k€ minimum)
    # ticket_max est le plafond de l'aide
    # Le ticket réaliste pour le profil = min(ticket_max, plafond_du_stade)
    if ticket_max:
        if ticket_max < petit_min * 0.3:
            score -= 8
            debug["ticket"] = "trop petit"
        elif ticket_min and ticket_min > plafond * 1.5:
            # le minimum exigé est très au-dessus de ce que la boite peut faire
            score -= 6
            debug["ticket"] = "ticket min trop élevé"
        elif petit_max <= ticket_max <= gros_max:
            score += 8
            debug["ticket"] = "cible"
        elif ticket_max < petit_max:
            score += 2
            debug["ticket"] = "petit ok"
        elif ticket_max <= moyen_max:
            score += 6
            debug["ticket"] = "moyen ok"
        elif ticket_max <= plafond * 2:
            # plafond officiel élevé mais ticket réaliste accessible
            score += 4
            debug["ticket"] = "plafond élevé, ticket réaliste OK"
        else:
            score += 1
            debug["ticket"] = "très gros"
    else:
        score += 1  # neutre si on n'a pas le montant

    # 2. Cohérence cofinancement : si l'aide demande typiquement 50% cofi
    # (subvention, avance), on vérifie que le cofi disponible permet d'atteindre
    # un projet de la taille attendue
    if "Subvention" in aide["natures"] or "Avance remboursable" in aide["natures"]:
        # estimation : aide ≈ 50 % du projet → projet ≈ ticket × 2 → cofi requis ≈ ticket
        cofi_required = ticket_max * 1.0 if ticket_max else 0
        if cofi_required > p.cofi_max * 2:
            score -= 5
            debug["cofi"] = "insuffisant"
        elif cofi_required > p.cofi_max:
            score -= 2
        else:
            score += 1

    # 3. Effort vs gain (heuristique par nature)
    nature_principale = aide["natures"][0] if aide["natures"] else ""
    effort = {
        "Subvention": 4,
        "Avance remboursable": 5,
        "Appel à projet": 7,
        "Allègement fiscal": 2,
        "Exonération de charges sociales": 2,
        "Prêt": 3,
        "Prêt d'honneur": 3,
        "Garantie": 2,
        "Accompagnement": 1,
        "Participation en capital": 6,
    }.get(nature_principale, 4)
    # ratio : gain / effort
    if ticket_max and effort:
        ratio = (ticket_max / 1000) / effort  # k€ par jour
        score += min(ratio / 3, 8)
        debug["ratio_kE_par_jour"] = round(ratio, 1)

    # 4. Bonus secteur si match explicite
    if p.secteurs and any(s in aide["profils"] for s in p.secteurs):
        score += 2

    # 5. Bonus innovation
    if p.innovation and aide.get("id_domaine") == "4":
        score += 3

    # 6. Bonus si export et international
    if p.export and aide.get("id_domaine") == "2":
        score += 3

    # 7. Pénalité aide trop locale si pas dans la région
    if aide.get("couverture_geo") == "1":
        terrs = set(aide.get("territoires", []))
        if p.region.lower() in [t.lower() for t in terrs]:
            score += 2
        elif "FRANCE" not in terrs:
            score -= 3

    # 8. Boost pour les "grands dispositifs" reconnaissables
    nom_lower = aide["nom"].lower()
    if any(k in nom_lower for k in ["france 2030", "i-démo", "pionniers", "bourse french tech"]):
        score += 6
    if any(k in nom_lower for k in ["aide pour le développement", "aide à l'innovation",
                                     "avance innovation", "prêt innovation"]):
        score += 5
    if "diag " in nom_lower or "diag " in nom_lower:
        score += 3

    # 9. Pénalités fortes pour aides hors-cible startup
    blacklist_keywords = [
        "btp", "agricole", "agriculture", "pêche",
        "cotisation foncière", "cotisation sur la valeur",
        "cvae", "cfe -", "taxe foncière",
        "quartier prioritaire", "qpv -", "zfu -", "zrr -",
        "gnr", "gazole", "carburant",
        "viticult", "élevage", "céréalier",
        "bassin minier", "ruralité revitalisation",
    ]
    if any(b in nom_lower for b in blacklist_keywords):
        # mais on les garde si user a explicitement secteur correspondant
        if not (
            ("agric" in nom_lower and any("agro" in s.lower() for s in p.secteurs))
            or ("btp" in nom_lower and any("artisan" in s.lower() or "bâtiment" in s.lower() for s in p.secteurs))
        ):
            score -= 12
            debug["blacklist"] = True

    # 10. Pénalité aide trop génériquement fiscale (zonage, pas spécifique innovation)
    fiscal_zonage = ["zfu", "zrr", "qpv", "zone franche", "zone de revitalisation", "ruralité"]
    if any(z in nom_lower for z in fiscal_zonage) and not p.export:
        score -= 5

    return score, debug


def add_automatic_aides(p: Profile, top: list[dict]) -> list[dict]:
    """Ajoute les aides automatiques (CIR, JEI, etc.) si applicables."""
    out = list(top)
    seen_names = {a["nom"].lower() for a in out}

    # JEI
    if (
        p.rd_pure
        and (p.age_annees is None or p.age_annees < 8)
        and p.effectif in ("1", "2", "3", "4")
    ):
        if "jeune entreprise innovante" not in " ".join(seen_names):
            jei = AIDES_AUTOMATIQUES["JEI"]
            out.append({
                "nom": jei["nom"],
                "id": jei["id"],
                "natures": jei["natures"],
                "montant_min_eur": jei["ticket_min"],
                "montant_max_eur": jei["ticket_max"],
                "lien": jei["lien"],
                "objet": jei["criteres_eligibilite"],
                "timeline": jei["timeline"],
                "tip": jei["tip"],
                "automatique": True,
            })

    # CIR
    if p.rd_pure or p.innovation:
        if "crédit d'impôt recherche" not in " ".join(seen_names):
            cir = AIDES_AUTOMATIQUES["CIR"]
            out.append({
                "nom": cir["nom"],
                "id": cir["id"],
                "natures": cir["natures"],
                "montant_min_eur": cir["ticket_min"],
                "montant_max_eur": cir["ticket_max"],
                "lien": cir["lien"],
                "objet": cir["criteres_eligibilite"],
                "timeline": cir["timeline"],
                "tip": cir["tip"],
                "automatique": True,
            })

    # CII
    if p.innovation and not p.rd_pure and p.effectif in ("1", "2", "3", "4"):
        if "crédit d'impôt innovation" not in " ".join(seen_names):
            cii = AIDES_AUTOMATIQUES["CII"]
            out.append({
                "nom": cii["nom"],
                "id": cii["id"],
                "natures": cii["natures"],
                "montant_min_eur": cii["ticket_min"],
                "montant_max_eur": cii["ticket_max"],
                "lien": cii["lien"],
                "objet": cii["criteres_eligibilite"],
                "timeline": cii["timeline"],
                "tip": cii["tip"],
                "automatique": True,
            })

    # ACRE
    if p.stade in ("preseed",) and (p.age_annees is None or p.age_annees < 1):
        if "acre" not in " ".join(seen_names):
            acre = AIDES_AUTOMATIQUES["ACRE"]
            out.append({
                "nom": acre["nom"],
                "id": acre["id"],
                "natures": acre["natures"],
                "montant_min_eur": acre["ticket_min"],
                "montant_max_eur": acre["ticket_max"],
                "lien": acre["lien"],
                "objet": acre["criteres_eligibilite"],
                "timeline": acre["timeline"],
                "tip": acre["tip"],
                "automatique": True,
            })

    return out


def deduplicate_by_dispositif(aides: list[dict]) -> list[dict]:
    """Si plusieurs aides ont des noms très proches (déclinaisons régionales),
    n'en garder qu'une représentative."""
    seen = {}
    for a in aides:
        # signature : 4 premiers mots du nom normalisés
        sig = re.sub(r"[^a-z0-9 ]", "", a["nom"].lower())
        sig = " ".join(sig.split()[:4])
        if sig not in seen:
            seen[sig] = a
    return list(seen.values())


def build_top5(p: Profile, catalogue: list[dict] | None = None) -> tuple[list[dict], list[dict]]:
    """Renvoie (top5, deuxieme_cercle)."""
    if catalogue is None:
        catalogue = load_catalogue()
    candidates = [a for a in catalogue if aide_passes_filter(a, p) and aide_passes_region(a, p)]

    scored = []
    for a in candidates:
        s, dbg = score_aide(a, p)
        if s >= 0:
            scored.append((s, a, dbg))

    scored.sort(key=lambda x: -x[0])

    # Dédupliquer par signature de nom (déclinaisons régionales)
    seen_names = {}
    scored_dedup = []
    for s, a, dbg in scored[:60]:
        sig = re.sub(r"[^a-z0-9 ]", "", a["nom"].lower())
        sig = " ".join(sig.split()[:4])
        if sig not in seen_names:
            seen_names[sig] = True
            scored_dedup.append((s, a))

    # Appliquer les règles de cumul/exclusion (familles BPI mutuellement exclusives)
    # On garde au plus 1 aide par famille (sauf diags & crédits d'impôt: 2)
    deduped = filtrer_par_familles(scored_dedup)

    # Ajouter aides automatiques (CIR, JEI, CII, ACRE) si applicables
    top_aides = add_automatic_aides(p, deduped)

    # Re-passer le filtre familles après ajout des aides automatiques
    # (un CIR ajouté ne doit pas concurrencer un crédit d'impôt déjà sélectionné)
    top_aides_with_score = [(0, a) for a in top_aides]
    top_aides = filtrer_par_familles(top_aides_with_score)

    # Mix : aides automatiques en tête, puis catalogue
    auto = [a for a in top_aides if a.get("automatique")][:2]
    non_auto = [a for a in top_aides if not a.get("automatique")][:6]
    top5 = (auto + non_auto)[:5]

    # Deuxième cercle : autres aides du catalogue (pas dans le top 5)
    top5_noms = {a["nom"] for a in top5}
    deuxieme = [a for a in non_auto if a["nom"] not in top5_noms][:3]

    return top5, deuxieme


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile-json", required=True)
    ap.add_argument("--limit", type=int, default=5)
    args = ap.parse_args()

    with open(args.profile_json) as f:
        raw = json.load(f)
    p = Profile(
        projets=set(raw.get("projets", [])),
        domaine=raw.get("domaine", "1"),
        stade=raw.get("stade", "seed"),
        natures=set(raw.get("natures", [])),
        secteurs=set(raw.get("secteurs", [])),
        effectif=raw.get("effectif", "2"),
        region=raw.get("region", "France"),
        export=raw.get("export", False),
        innovation=raw.get("innovation", False),
        rd_pure=raw.get("rd_pure", False),
        cofi_max=raw.get("cofi_max", 100_000),
        nom_entreprise=raw.get("nom_entreprise", "Votre entreprise"),
        age_annees=raw.get("age_annees"),
    )
    top5, deux = build_top5(p)
    print(f"# Top {len(top5)} aides crédibles\n")
    for i, a in enumerate(top5, 1):
        print(f"{i}. {a['nom']}")
        print(f"   Ticket: {a.get('montant_min_eur') or '?'}-{a.get('montant_max_eur') or '?'} €")
        print(f"   Natures: {', '.join(a['natures'][:2])}")
        if a.get("automatique"):
            print(f"   [AUTO] {a.get('tip', '')[:100]}")
        print()
    print(f"\n## Deuxième cercle ({len(deux)})")
    for a in deux:
        print(f"  - {a['nom']}")


if __name__ == "__main__":
    main()
