"""Génère l'export markdown du diagnostic à remettre au fondateur.

Usage :
    python3 generer_export.py --profile-json profile.json --output rapport.md
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scoring_lead_magnet import Profile, build_top5  # noqa: E402

STADE_LABEL = {
    "preseed": "Pré-amorçage",
    "seed": "Seed / Amorçage",
    "serieA": "Série A",
    "serieB": "Série B / Scale-up",
    "bootstrap": "Bootstrap / Autofinancé",
    "pme": "PME établie",
    "pme_grand": "PME 50-249",
    "eti": "ETI",
}

EFFECTIF_LABEL = {
    "1": "0 salarié",
    "2": "1-9 (TPE)",
    "3": "10-49",
    "4": "50-249 (PME)",
    "5": "250-4 999 (ETI)",
    "6": "5 000+ (GE)",
}

NATURE_LABEL = {
    "subvention": "Subvention",
    "pret_avance": "Prêt / avance",
    "fiscal_social": "Allègement fiscal/social",
    "fonds_propres": "Fonds propres",
    "garantie": "Garantie",
    "accompagnement": "Accompagnement",
}


def fmt_eur(v):
    if not v:
        return "?"
    if v >= 1_000_000:
        return f"{v / 1_000_000:.1f} M€"
    if v >= 1_000:
        return f"{int(v / 1000)} k€"
    return f"{int(v)} €"


def fmt_ticket(a):
    mn, mx = a.get("montant_min_eur"), a.get("montant_max_eur")
    if mn and mx and mn != mx:
        return f"{fmt_eur(mn)} – {fmt_eur(mx)}"
    if mx:
        return f"jusqu'à {fmt_eur(mx)}"
    return "(montant variable)"


def render_aide(a, idx, p):
    """Rend une aide en markdown — version condensée et opérationnelle."""
    auto = a.get("automatique", False)
    tag_auto = " 🟢 *automatique*" if auto else ""

    pourquoi = compute_pourquoi(a, p)
    montant = fmt_ticket(a)
    timeline = (a.get("timeline") or guess_timeline(a)).split("(")[0].strip()
    tip = a.get("tip") or guess_tip(a)
    lien = a.get("lien") or "—"

    # Tableau condensé en 2 lignes
    return f"""### {idx}. {a['nom']}{tag_auto}

> **{pourquoi}**

| Ticket attendu | Timeline | Tip Reki |
|---|---|---|
| {dimension_montant(a, p)} | {timeline} | {tip[:120]} |

[→ Fiche officielle]({lien})
"""


def compute_pourquoi(a, p):
    """Phrase justifiant la pertinence pour ce profil."""
    if a.get("automatique"):
        if "JEI" in a["nom"] or "Jeune Entreprise" in a["nom"]:
            return f"Avec votre profil R&D et votre ancienneté, vous activez ~{fmt_eur(a.get('montant_min_eur', 0))}+/an d'exonérations sans dossier lourd."
        if "CIR" in a["nom"]:
            return "Toute dépense R&D salariale ou sous-traitance agréée vous donne 30 % en cash. Levier le plus rapide pour une startup en R&D."
        if "CII" in a["nom"]:
            return "Sur design, prototypage, intégration : 20 % en crédit d'impôt remboursable, plafond 80 k€/an."
        if "ACRE" in a["nom"]:
            return "Exonération de charges sociales 1ʳᵉ année, à activer dans les 45 jours."
    nom = a["nom"].lower()
    if "france 2030" in nom and "ia" in nom:
        return "Votre projet IA s'inscrit dans la stratégie nationale ; phase 1 accessible en early stage."
    if "france 2030" in nom:
        return "Votre capacité de cofinancement permet d'aligner un projet de 1-2 M€ avec subvention 50 %."
    if "bourse french tech" in nom:
        return "Bourse calibrée pour startups < 1 an, ticket modéré mais signal fort auprès des investisseurs."
    if "avance innovation" in nom:
        return "Avance récupérable uniquement en cas de succès commercial — outil sous-utilisé par les startups."
    if "prêt innovation" in nom:
        return "Outil de bouclage par excellence du plan de financement, taux préférentiel."
    if "i-démo" in nom:
        return "Si vous avez un consortium R&D et une assiette > 1 M€, ticket effectif x4."
    if "diag" in nom:
        return "Cofinancement 50-75 % d'une mission de conseil ; signal positif sur dossiers ultérieurs."
    # Fallback intelligent : utiliser le début de l'objet de l'aide si présent
    objet = (a.get("objet") or "").strip()
    if objet:
        snippet = objet[:140].rsplit(" ", 1)[0] if len(objet) > 140 else objet
        return f"{snippet}…" if len(objet) > 140 else snippet
    return "Aide cohérente avec votre profil et votre stade."


def dimension_montant(a, p):
    """Dimensionne l'aide pour le profil utilisateur."""
    petit_min, petit_max, moyen_max, gros_max, plafond = p.stade_grille
    mx = a.get("montant_max_eur") or 0
    if not mx:
        return "à instruire"
    if mx > plafond:
        return f"plafond officiel {fmt_eur(mx)} mais réaliste pour votre stade : {fmt_eur(min(gros_max, mx))}"
    if mx < petit_min * 0.5:
        return f"~{fmt_eur(mx)} (petit ticket, à arbitrer selon effort)"
    # estimation : 60% du max si gros, 80% si moyen
    if mx > moyen_max:
        return f"~{fmt_eur(int(mx * 0.6))} attendu pour votre profil ({fmt_eur(mx)} max officiel)"
    return f"~{fmt_eur(int(mx * 0.7))} attendu ({fmt_eur(mx)} max officiel)"


def guess_timeline(a):
    n = a.get("natures", [])
    if "Allègement fiscal" in n or "Exonération de charges sociales" in n:
        return "Application immédiate / déclaration N+1"
    if "Appel à projet" in n:
        return "5-9 mois (instruction + audition)"
    if "Subvention" in n:
        return "3-6 mois"
    if "Avance remboursable" in n or "Prêt" in n:
        return "2-4 mois"
    return "à confirmer (variable)"


def guess_selectivite(a):
    n = a.get("natures", [])
    if "Allègement fiscal" in n or "Exonération de charges sociales" in n:
        return "Automatique (mais contrôle a posteriori)"
    if "Appel à projet" in n:
        return "10-25 % (concurrentiel)"
    if "Prix" in n:
        return "<10 % (très concurrentiel)"
    return "30-50 % en moyenne"


def guess_tip(a):
    nom = a["nom"].lower()
    if "diag" in nom:
        return "Démarrez par là : RAC limité, ouvre l'accès à d'autres aides, signal positif Bpifrance."
    if "bourse french tech" in nom:
        return "Pré-rendez-vous chargé d'affaires Bpifrance régional impératif avant le dépôt."
    if "prêt d'honneur" in nom:
        return "Hors cible si déjà capitalisé — destiné aux fondateurs en début de parcours."
    return "Vérifier la fiche officielle au moment du dépôt — barèmes 2026 en évolution."


def compute_total(top5, p):
    """Estime la fourchette de potentiel total sur 18 mois."""
    total_min = 0
    total_max = 0
    for a in top5:
        mn = a.get("montant_min_eur") or 0
        mx = a.get("montant_max_eur") or 0
        # Pondération par nature (probabilité d'obtention)
        n = a.get("natures", [])
        if "Allègement fiscal" in n or "Exonération de charges sociales" in n:
            total_min += mn * 0.7
            total_max += mx * 0.9
        elif "Appel à projet" in n:
            total_min += mn * 0.15
            total_max += mx * 0.35
        elif "Prêt" in n or "Avance remboursable" in n:
            total_min += mn * 0.4
            total_max += mx * 0.6
        else:
            total_min += mn * 0.3
            total_max += mx * 0.5
    return int(total_min), int(total_max)


def render_plan_action(top5, p):
    """Plan d'action 90 jours."""
    lines = []
    j = 0
    week = 1

    # Activer aides automatiques en priorité
    autos = [a for a in top5 if a.get("automatique")]
    for a in autos[:2]:
        lines.append(f"- **Semaine {week}** : activer {a['nom']} (déclaration / rescrit selon dispositif)")
        week += 1

    # Diags si présents
    diags = [a for a in top5 if "diag" in a["nom"].lower()]
    for a in diags[:1]:
        lines.append(f"- **Semaine {week}-{week+2}** : déposer une demande pour {a['nom']} (RAC limité, signal Bpifrance positif)")
        week += 3

    # Gros dispositifs
    gros = [a for a in top5 if not a.get("automatique") and a.get("montant_max_eur", 0) >= 100_000][:2]
    for a in gros:
        lines.append(f"- **Mois {(week//4)+1}-{(week//4)+3}** : préparer le dossier pour {a['nom']} (15-30 jours-hommes prévisionnels)")
        week += 8

    # Suivi
    lines.append(f"- **Tout au long** : tenir le registre des aides perçues et anticiper les plafonds de minimis (300 k€/3 ans)")

    return "\n".join(lines)


def render_pieges(p):
    """Pièges à éviter pour ce profil."""
    pieges = []
    if p.cofi_max < 100_000:
        pieges.append("- Ne pas viser des appels à projets France 2030 demandant > 200 k€ de cofinancement.")
    if p.stade == "seed":
        pieges.append("- Éviter les prêts d'honneur (calibrés pour des fondateurs avant levée).")
    if p.rd_pure or p.innovation:
        pieges.append("- Ne pas saturer l'enveloppe de minimis (300 k€/3 ans) avec de petites aides régionales si vous visez une grosse aide France 2030 RGEC.")
    pieges.append("- Vérifier les calendriers de dépôt 2026 (relèves divisées par 2 sur i-Démo).")
    pieges.append("- Documenter les time-sheets R&D dès le J1 pour sécuriser JEI/CIR en cas de contrôle URSSAF/DGFiP.")
    return "\n".join(pieges)


def render_export(p: Profile, top5: list[dict], deuxieme: list[dict]) -> str:
    today = datetime.date.today().strftime("%d/%m/%Y")

    total_min, total_max = compute_total(top5, p)
    equiv_levee = "demi-levée à dilution équivalente" if total_max < 1_500_000 else "levée complète à dilution équivalente"

    top_priorities = " · ".join([a["nom"].split("(")[0].split(" - ")[0].strip()[:40] for a in top5[:3]])

    risque_principal = (
        "Saturation de l'enveloppe de minimis si vous accumulez trop de petites aides"
        if p.cofi_max > 200_000
        else "Capacité de cofinancement limitée — privilégier les aides automatiques et les prêts plutôt que les AAP gros tickets"
    )

    aides_md = "\n".join(render_aide(a, i + 1, p) for i, a in enumerate(top5))

    plan = render_plan_action(top5, p)
    pieges = render_pieges(p)

    deux_md = "\n".join(f"- **{a['nom']}** — {fmt_ticket(a)}" for a in deuxieme[:5]) or "*(rien à signaler — top 5 couvre déjà votre profil)*"

    cta_path = Path(__file__).resolve().parent.parent / "assets" / "cta_reki.md"
    cta = cta_path.read_text(encoding="utf-8") if cta_path.exists() else ""

    nature_str = ", ".join(NATURE_LABEL.get(n, n) for n in p.natures) or "(non précisée)"
    secteurs_str = ", ".join(p.secteurs) or "PME tous secteurs"
    projets_str = ", ".join(p.projets) or "(non précisé)"

    return f"""# Diagnostic aides publiques — {p.nom_entreprise}

> **{STADE_LABEL.get(p.stade, p.stade)}** • {EFFECTIF_LABEL.get(p.effectif, p.effectif)} • {p.region} • {secteurs_str} — {today}

## 🎯 Synthèse

**Potentiel total réaliste sur 18 mois** : **{fmt_eur(total_min)} à {fmt_eur(total_max)}** d'aides cumulées *(équivalent {equiv_levee})*.

**Priorités** : {top_priorities}

**À surveiller** : {risque_principal}

---

## 📋 Top 5 des aides crédibles

{aides_md}

> ⚠️ **Cumul** : les aides Bpifrance pré-industrielles (Aide à l'Innovation, Avance Innovation, Prêt Innovation R&D) **ne se cumulent pas** sur les mêmes dépenses. Le top 5 retient la plus pertinente pour votre profil. Les autres existent et sont mentionnées en deuxième cercle.

---

## 🗓️ Plan d'action 90 jours

{plan}

---

## 🔄 Aides alternatives *(même famille — si la principale est rejetée)*

{deux_md}

---

## ⚠️ Pièges à éviter

{pieges}

---

{cta}
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile-json", required=True)
    ap.add_argument("--output", required=True, help="Chemin du fichier markdown à écrire")
    args = ap.parse_args()

    with open(args.profile_json) as f:
        raw = json.load(f)
    p = Profile.from_raw(raw)
    top5, deux = build_top5(p)
    md = render_export(p, top5, deux)
    Path(args.output).write_text(md, encoding="utf-8")
    print(f"Export généré : {args.output}")


if __name__ == "__main__":
    main()
