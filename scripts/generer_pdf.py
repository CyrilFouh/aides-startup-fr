"""Génère un PDF du diagnostic avec la charte graphique Reki.

Charte Reki (déduite des rapports d'audit Reki) :
  - Jaune doré #E8C44E (header de couverture, accents)
  - Rouge corail #D64545 (badges BLOQUANT, alertes)
  - Orange #E89A3D (badges ATTENTION)
  - Vert #5BA85B (validations)
  - Noir #1A1A1A (textes)
  - Gris moyen #9A9A9A (labels meta)

Usage :
    python3 generer_pdf.py --profile-json profile.json --output rapport.pdf
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scoring_lead_magnet import Profile, build_top5  # noqa: E402
from generer_export import (  # noqa: E402
    STADE_LABEL,
    EFFECTIF_LABEL,
    NATURE_LABEL,
    fmt_eur,
    fmt_ticket,
    compute_pourquoi,
    dimension_montant,
    guess_timeline,
    guess_tip,
    compute_total,
    render_plan_action,
    render_pieges,
)


# ===== Charte graphique Reki =====
CSS = """
@page {
    size: A4;
    margin: 22mm 18mm 22mm 18mm;
    @top-left {
        content: "REKI";
        font-family: 'Helvetica', 'Arial', sans-serif;
        font-weight: 700;
        font-size: 11pt;
        color: #1A1A1A;
        letter-spacing: 0.06em;
    }
    @top-right {
        content: "Diagnostic aides publiques · " string(client);
        font-family: 'Helvetica', 'Arial', sans-serif;
        font-size: 8pt;
        color: #6A6A6A;
    }
    @bottom-left {
        content: "Reki — Conseil en financement non dilutif";
        font-family: 'Helvetica', 'Arial', sans-serif;
        font-size: 8pt;
        color: #6A6A6A;
    }
    @bottom-right {
        content: "Page " counter(page);
        font-family: 'Helvetica', 'Arial', sans-serif;
        font-size: 8pt;
        color: #6A6A6A;
    }
}

/* Page de couverture sans header/footer normal */
@page :first {
    margin: 0;
    @top-left { content: ""; }
    @top-right { content: ""; }
    @bottom-left { content: ""; }
    @bottom-right { content: ""; }
}

* { box-sizing: border-box; }

body {
    font-family: 'Helvetica', 'Arial', sans-serif;
    color: #1A1A1A;
    font-size: 10pt;
    line-height: 1.45;
    margin: 0;
    padding: 0;
}

/* Page de couverture */
.cover {
    page-break-after: always;
    height: 297mm;
    width: 210mm;
    position: relative;
    margin: 0;
    padding: 0;
}

.cover-band {
    background: #E8C44E;
    padding: 18mm 22mm 14mm 22mm;
    height: 48%;
    position: relative;
}

.cover-logo {
    font-size: 18pt;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: #1A1A1A;
}

.cover-meta {
    position: absolute;
    bottom: 18mm;
    left: 22mm;
    right: 22mm;
}

.cover-tag {
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 0.18em;
    color: #6A6A6A;
    text-transform: uppercase;
    margin-bottom: 6mm;
}

.cover-title {
    font-size: 14pt;
    font-weight: 700;
    color: #1A1A1A;
    margin-bottom: 4mm;
}

.cover-client {
    font-size: 24pt;
    font-weight: 800;
    color: #1A1A1A;
    line-height: 1.1;
    margin-bottom: 3mm;
}

.client-name-anchor {
    string-set: client content();
    height: 0;
    overflow: hidden;
    visibility: hidden;
}

.cover-date {
    font-size: 11pt;
    color: #6A6A6A;
}

.cover-content {
    padding: 10mm 22mm 18mm 22mm;
}

.summary-table {
    width: 100%;
    border-collapse: collapse;
    margin: 2mm 0 4mm 0;
}

.summary-table td {
    padding: 2.5mm 0;
    border-bottom: 1px solid #E0E0E0;
    vertical-align: top;
}

.summary-table td.label {
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #6A6A6A;
    text-transform: uppercase;
    width: 38%;
}

.summary-table td.value {
    font-size: 10.5pt;
    font-weight: 700;
    color: #1A1A1A;
}

.cover-footer {
    position: absolute;
    bottom: 12mm;
    left: 22mm;
    right: 22mm;
    border-top: 1px solid #E0E0E0;
    padding-top: 4mm;
    font-size: 8pt;
    color: #6A6A6A;
}

/* Sections */
.section-title {
    font-size: 14pt;
    font-weight: 700;
    color: #1A1A1A;
    margin-top: 8mm;
    margin-bottom: 4mm;
    padding-left: 0;
    display: flex;
    align-items: center;
}

.section-num {
    background: #1A1A1A;
    color: white;
    font-size: 9pt;
    font-weight: 700;
    padding: 2mm 3mm;
    margin-right: 4mm;
    display: inline-block;
}

/* Synthèse */
.kpi-block {
    background: #FAF6E8;
    border-left: 4px solid #E8C44E;
    padding: 5mm 6mm;
    margin: 4mm 0 6mm 0;
}

.kpi-label {
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #6A6A6A;
    text-transform: uppercase;
    margin-bottom: 1mm;
}

.kpi-value {
    font-size: 16pt;
    font-weight: 800;
    color: #1A1A1A;
    line-height: 1.2;
}

.kpi-sub {
    font-size: 9pt;
    color: #6A6A6A;
    margin-top: 1mm;
}

/* Aide block */
.aide {
    margin: 5mm 0;
    padding: 5mm 6mm;
    background: white;
    border: 1px solid #E0E0E0;
    border-left: 4px solid #E8C44E;
    page-break-inside: avoid;
}

.aide.auto {
    border-left-color: #5BA85B;
    background: #F4FAF4;
}

.aide-head {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 2mm;
}

.aide-title {
    font-size: 11pt;
    font-weight: 700;
    color: #1A1A1A;
    flex: 1;
}

.aide-num {
    font-size: 8pt;
    color: #9A9A9A;
    font-weight: 700;
    margin-right: 3mm;
}

.aide-badge {
    background: #5BA85B;
    color: white;
    font-size: 7.5pt;
    font-weight: 700;
    padding: 1mm 2.5mm;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-left: 2mm;
}

.aide-pourquoi {
    font-size: 9.5pt;
    color: #1A1A1A;
    font-style: italic;
    margin: 2mm 0 3mm 0;
    border-left: 2px solid #E8C44E;
    padding-left: 3mm;
}

.aide.auto .aide-pourquoi {
    border-left-color: #5BA85B;
}

.aide-grid {
    display: table;
    width: 100%;
    margin-top: 3mm;
}

.aide-cell {
    display: table-cell;
    width: 33%;
    padding-right: 3mm;
    vertical-align: top;
    font-size: 8.5pt;
}

.aide-cell-label {
    font-size: 7pt;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #6A6A6A;
    text-transform: uppercase;
    margin-bottom: 0.5mm;
}

.aide-cell-value {
    color: #1A1A1A;
    line-height: 1.3;
}

.aide-link {
    display: block;
    margin-top: 3mm;
    font-size: 8pt;
    color: #6A6A6A;
}

.aide-link a {
    color: #6A6A6A;
    text-decoration: none;
}

/* Plan d'action */
.plan-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 3mm;
    font-size: 9pt;
}

.plan-table th {
    background: #1A1A1A;
    color: white;
    padding: 2.5mm 3mm;
    text-align: left;
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.plan-table td {
    padding: 2.5mm 3mm;
    border-bottom: 1px solid #E0E0E0;
    vertical-align: top;
}

.plan-table tr:nth-child(odd) td {
    background: #FAFAFA;
}

/* Cumul warning */
.cumul-warning {
    background: #FFF8E0;
    border-left: 4px solid #E89A3D;
    padding: 4mm 5mm;
    font-size: 8.5pt;
    color: #1A1A1A;
    margin: 5mm 0;
}

.cumul-warning strong {
    color: #B5762A;
}

/* Pièges */
.piege-list {
    list-style: none;
    padding-left: 0;
    margin: 3mm 0;
}

.piege-list li {
    padding: 2.5mm 4mm;
    margin-bottom: 2mm;
    background: #FFF4F4;
    border-left: 3px solid #D64545;
    font-size: 9pt;
}

/* CTA Reki */
.cta {
    page-break-before: always;
    background: #1A1A1A;
    color: white;
    padding: 18mm 14mm;
    margin: 8mm -18mm 0 -18mm;
    min-height: 240mm;
}

.cta h2 {
    color: #E8C44E;
    font-size: 22pt;
    font-weight: 800;
    margin: 0 0 6mm 0;
    line-height: 1.1;
}

.cta-lead {
    font-size: 11pt;
    line-height: 1.5;
    color: #E0E0E0;
    margin-bottom: 8mm;
}

.cta-block {
    background: rgba(255,255,255,0.05);
    border-left: 3px solid #E8C44E;
    padding: 5mm 6mm;
    margin-bottom: 6mm;
}

.cta-block h3 {
    color: white;
    font-size: 11pt;
    margin: 0 0 2mm 0;
}

.cta-block p {
    color: #C0C0C0;
    font-size: 9.5pt;
    margin: 0;
}

.cta-actions {
    margin-top: 10mm;
    padding-top: 6mm;
    border-top: 1px solid rgba(255,255,255,0.2);
}

.cta-action {
    margin-bottom: 4mm;
    font-size: 11pt;
    color: white;
}

.cta-action .icon {
    display: inline-block;
    width: 8mm;
    color: #E8C44E;
}

.cta-action a {
    color: white;
    text-decoration: none;
    border-bottom: 1px solid #E8C44E;
}

.cta-tip {
    margin-top: 10mm;
    padding: 4mm 5mm;
    background: rgba(232, 196, 78, 0.1);
    border-left: 3px solid #E8C44E;
    font-size: 9pt;
    color: #E0E0E0;
    font-style: italic;
}
"""


def render_aide_html(a, idx, p):
    auto = a.get("automatique", False)
    css_class = "aide auto" if auto else "aide"
    badge = '<span class="aide-badge">Automatique</span>' if auto else ""

    pourquoi = compute_pourquoi(a, p)
    montant = dimension_montant(a, p)
    timeline = (a.get("timeline") or guess_timeline(a)).split("(")[0].strip()
    tip = a.get("tip") or guess_tip(a)
    lien = a.get("lien") or "—"
    lien_html = f'<a href="{lien}">{lien}</a>' if lien != "—" else "—"

    return f"""
    <div class="{css_class}">
      <div class="aide-head">
        <div class="aide-title"><span class="aide-num">N°{idx}</span>{a['nom']}{badge}</div>
      </div>
      <div class="aide-pourquoi">{pourquoi}</div>
      <div class="aide-grid">
        <div class="aide-cell">
          <div class="aide-cell-label">Ticket attendu</div>
          <div class="aide-cell-value">{montant}</div>
        </div>
        <div class="aide-cell">
          <div class="aide-cell-label">Timeline</div>
          <div class="aide-cell-value">{timeline}</div>
        </div>
        <div class="aide-cell">
          <div class="aide-cell-label">Tip Reki</div>
          <div class="aide-cell-value">{tip[:200]}</div>
        </div>
      </div>
      <div class="aide-link">{lien_html}</div>
    </div>
    """


def render_plan_table(top5, p):
    rows = []
    autos = [a for a in top5 if a.get("automatique")]
    diags = [a for a in top5 if "diag" in a["nom"].lower()]
    gros = [a for a in top5 if not a.get("automatique") and a.get("montant_max_eur", 0) >= 100_000]

    for a in autos[:2]:
        rows.append(("S1", "Activer", a["nom"], "déclaration / rescrit"))
    for a in diags[:1]:
        rows.append(("S2-S4", "Déposer", a["nom"], "RAC limité, signal Bpifrance"))
    for i, a in enumerate(gros[:2]):
        rows.append((f"M{2+i*2}", "Préparer dossier", a["nom"], "15-30 j-h prévisionnels"))
    rows.append(("Continu", "Surveiller", "Plafond de minimis (300 k€/3 ans)", "registre des aides perçues"))

    rows_html = "\n".join(
        f'<tr><td><strong>{q}</strong></td><td>{action}</td><td>{nom}</td><td>{detail}</td></tr>'
        for q, action, nom, detail in rows
    )

    return f"""
    <table class="plan-table">
      <thead>
        <tr>
          <th>Quand</th>
          <th>Action</th>
          <th>Dispositif</th>
          <th>Effort</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
    """


def render_pieges_html(p):
    pieges = []
    if p.cofi_max < 100_000:
        pieges.append("Ne pas viser des AAP France 2030 demandant > 200 k€ de cofinancement.")
    if p.stade == "seed":
        pieges.append("Éviter les prêts d'honneur (calibrés pour des fondateurs avant levée).")
    if p.rd_pure or p.innovation:
        pieges.append("Ne pas saturer l'enveloppe de minimis (300 k€/3 ans) avec de petites aides régionales si vous visez une grosse aide France 2030 RGEC.")
    pieges.append("Vérifier les calendriers de dépôt 2026 (relèves divisées par 2 sur i-Démo).")
    pieges.append("Documenter les time-sheets R&D dès le J1 pour sécuriser JEI/CIR en cas de contrôle URSSAF/DGFiP.")

    items = "\n".join(f"<li>{p}</li>" for p in pieges)
    return f'<ul class="piege-list">{items}</ul>'


def render_pdf_html(p: Profile, top5: list[dict], deuxieme: list[dict]) -> str:
    today = datetime.date.today().strftime("%d/%m/%Y")
    total_min, total_max = compute_total(top5, p)

    secteurs_str = ", ".join(p.secteurs) or "PME tous secteurs"
    nature_str = ", ".join(NATURE_LABEL.get(n, n) for n in p.natures) or "—"
    projets_str = ", ".join(p.projets) or "—"

    aides_html = "\n".join(render_aide_html(a, i + 1, p) for i, a in enumerate(top5))
    plan_html = render_plan_table(top5, p)
    pieges_html = render_pieges_html(p)

    deux_html = ""
    if deuxieme:
        items = "\n".join(
            f'<li><strong>{a["nom"]}</strong> — {fmt_ticket(a)}</li>'
            for a in deuxieme[:3]
        )
        deux_html = f"""
        <h2 class="section-title"><span class="section-num">5</span>Aides alternatives</h2>
        <p style="font-size: 9pt; color: #6A6A6A;">Aides de la même famille que celles déjà retenues — non cumulables sur les mêmes dépenses, mais à considérer en remplacement si la principale est rejetée.</p>
        <ul class="piege-list" style="background:transparent;">{items}</ul>
        """

    rd_label = (
        "R&D pure (Frascati)" if p.rd_pure
        else ("Innovation (design, intégration)" if p.innovation else "Non")
    )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Diagnostic aides publiques — {p.nom_entreprise}</title>
<style>{CSS}</style>
</head>
<body>
<div class="client-name-anchor">{p.nom_entreprise}</div>

<!-- Page de couverture -->
<div class="cover">
  <div class="cover-band">
    <div class="cover-logo">REKI</div>
    <div class="cover-meta">
      <div class="cover-tag">Diagnostic Aides Publiques</div>
      <div class="cover-title">Aides publiques pour startups & PME</div>
      <div class="cover-client">{p.nom_entreprise}</div>
      <div class="cover-date">{today}</div>
    </div>
  </div>
  <div class="cover-content">
    <table class="summary-table">
      <tr>
        <td class="label">Stade</td>
        <td class="value">{STADE_LABEL.get(p.stade, p.stade)}</td>
      </tr>
      <tr>
        <td class="label">Effectif</td>
        <td class="value">{EFFECTIF_LABEL.get(p.effectif, p.effectif)}</td>
      </tr>
      <tr>
        <td class="label">Région</td>
        <td class="value">{p.region}</td>
      </tr>
      <tr>
        <td class="label">Secteur</td>
        <td class="value">{secteurs_str}</td>
      </tr>
      <tr>
        <td class="label">Caractère R&amp;D</td>
        <td class="value">{rd_label}</td>
      </tr>
      <tr>
        <td class="label">Cash dispo cofinancement</td>
        <td class="value">{fmt_eur(p.cofi_max)}</td>
      </tr>
      <tr>
        <td class="label">Potentiel total 18 mois</td>
        <td class="value" style="color:#B5762A;">{fmt_eur(total_min)} – {fmt_eur(total_max)}</td>
      </tr>
    </table>
  </div>
  <div class="cover-footer">
    Reki — Conseil en financement non dilutif · cyril@reki.eu · www.reki.eu
  </div>
</div>

<!-- Section 1 — Synthèse -->
<h2 class="section-title"><span class="section-num">1</span>Synthèse</h2>

<div class="kpi-block">
  <div class="kpi-label">Potentiel total réaliste sur 18 mois</div>
  <div class="kpi-value">{fmt_eur(total_min)} – {fmt_eur(total_max)}</div>
  <div class="kpi-sub">Aides cumulées éligibles avec votre profil — équivalent levée non-dilutive partielle.</div>
</div>

<p>Sur la base des 10 questions, votre entreprise <strong>{p.nom_entreprise}</strong> est positionnée pour activer un mix d'aides automatiques (crédits d'impôt, statut JEI) et de dispositifs sur dossier (France 2030, BPI). Le plan d'action qui suit ordonne les actions par priorité et effort.</p>

<!-- Section 2 — Top 5 -->
<h2 class="section-title"><span class="section-num">2</span>Top 5 des aides crédibles</h2>
{aides_html}

<div class="cumul-warning">
  <strong>⚠️ Règle de cumul</strong> — Plusieurs aides Bpifrance pré-industrielles
  (Aide à l'Innovation, Avance Innovation, Prêt Innovation R&amp;D) financent la même
  phase de R&amp;D et ne se cumulent <strong>pas</strong> sur les mêmes dépenses. Le
  top 5 retient la plus pertinente pour votre profil. Les autres figurent en
  alternatives, à considérer si la principale est rejetée.
</div>

<!-- Section 3 — Plan -->
<h2 class="section-title"><span class="section-num">3</span>Plan d'action 90 jours</h2>
{plan_html}

<!-- Section 4 — Pièges -->
<h2 class="section-title"><span class="section-num">4</span>Pièges à éviter</h2>
{pieges_html}

<!-- Section 5 — Alternatives -->
{deux_html}

<!-- CTA Reki -->
<div class="cta">
  <h2>Aller plus loin avec Reki</h2>
  <p class="cta-lead">
    Vous venez de recevoir un diagnostic automatique basé sur l'open data de
    2 384 aides publiques françaises, croisé avec des fiches enrichies
    2025-2026 sur les principaux dispositifs France 2030, BPI, JEI, CIR.
  </p>

  <div class="cta-block">
    <h3>Ce que ce diagnostic ne fait pas</h3>
    <p>Valider l'éligibilité fine au cas par cas. Monter les dossiers (un AAP France 2030 = 30 à 90 j-h). Coordonner les calendriers de dépôt et la stratégie de cumul. Préparer les auditions et défendre le projet devant les jurys.</p>
  </div>

  <div class="cta-block">
    <h3>Ce que Reki fait, depuis 5 ans</h3>
    <p>Accompagnement startups et PME pour aller chercher 100 k€ à 5 M€ de financement non-dilutif : dossiers Bpifrance, France 2030, sécurisation JEI/CIR, optimisation des cumuls. Approche success fee — pas d'aide obtenue, pas (ou peu) de facture.</p>
  </div>

  <div class="cta-actions">
    <div class="cta-action"><span class="icon">→</span> Réserver 15 min : <a href="https://calendly.com/cyril-reki/15-minute-meeting">calendly.com/cyril-reki</a></div>
    <div class="cta-action"><span class="icon">→</span> Écrire : <a href="mailto:cyril@reki.eu">cyril@reki.eu</a></div>
    <div class="cta-action"><span class="icon">→</span> En savoir plus : <a href="https://www.reki.eu">www.reki.eu</a></div>
  </div>

  <div class="cta-tip">
    💡 Joignez ce diagnostic à votre demande de RDV — ça nous fait gagner 30 minutes
    sur le premier appel et nous permet d'arriver avec un avis qualifié plutôt que
    des questions.
  </div>
</div>

</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile-json", required=True)
    ap.add_argument("--output", required=True, help="Chemin du PDF à générer")
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
    html = render_pdf_html(p, top5, deux)

    # Génération via WeasyPrint
    from weasyprint import HTML
    HTML(string=html).write_pdf(args.output)
    print(f"PDF généré : {args.output}")


if __name__ == "__main__":
    main()
