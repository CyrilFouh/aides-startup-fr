# Aides Startup FR — by Reki

> **Diagnostic personnalisé en 5 minutes** des aides publiques françaises (subventions, prêts, crédits d'impôt, France 2030, BPI, JEI, CIR…) auxquelles votre entreprise est éligible. Skill Claude prêt à installer en drag-and-drop.

[![Version](https://img.shields.io/github/v/release/REPLACE_USERNAME/aides-startup-fr-by-reki?label=version)](https://github.com/REPLACE_USERNAME/aides-startup-fr-by-reki/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/REPLACE_USERNAME/aides-startup-fr-by-reki/total)](https://github.com/REPLACE_USERNAME/aides-startup-fr-by-reki/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Made by Reki](https://img.shields.io/badge/made%20by-Reki-ff5a5f)](https://www.reki.eu)

---

## 🎯 Ce que vous y gagnez

En 10 questions ciblées, ce skill vous donne :

- **Top 5 des aides** les plus crédibles pour **votre profil** (et pas une liste générique de 200 aides)
- **Montants attendus** dimensionnés à votre stade (pré-amorçage, Seed, Série A, PME, ETI…)
- **Critères officieux** que les comités regardent en pratique, pas juste les textes officiels
- **Plan d'action 90 jours** ordonné par priorité et effort
- **Rapport markdown exportable** à conserver et à partager
- **Pièges à éviter** (saturation de minimis, prêts d'honneur hors cible, etc.)

> Le skill s'appuie sur l'open data des **2 384 aides publiques françaises actives** (source : aides-entreprises.fr) enrichies avec des fiches 2025-2026 sur les principaux dispositifs France 2030, Bpifrance, JEI, CIR, CII, CICo, Diags.

---

## 📥 Installer en 30 secondes

1. **Télécharger le skill** : cliquez sur le bouton ci-dessous, le fichier `aides-startup-fr-by-reki.skill` se télécharge.

   👉 **[Télécharger la dernière version](https://github.com/REPLACE_USERNAME/aides-startup-fr-by-reki/releases/latest/download/aides-startup-fr-by-reki.skill)**

2. **Glisser-déposer** le fichier `.skill` dans la fenêtre de Claude (claude.ai ou app desktop Cowork). Claude affiche un bouton **"Installer ce skill"** : cliquez.

3. **Poser votre question** :

   > « Quelles aides publiques pour ma startup ? »
   > « Comment financer mon projet de R&D sans dilution ? »
   > « Suis-je éligible à France 2030 ? »

   Claude détecte automatiquement le besoin et lance le diagnostic en 10 questions.

---

## 🧭 À qui ça s'adresse

| Profil | Pertinence |
|---|---|
| Fondateur / dirigeant **startup pré-amorçage à Série B** | ⭐⭐⭐⭐⭐ |
| Dirigeant de **PME établie** (10-249 sal.) | ⭐⭐⭐⭐⭐ |
| **Artisan, commerçant, indépendant** créant son entreprise | ⭐⭐⭐⭐ |
| **ETI** sur projet d'innovation ou export | ⭐⭐⭐⭐ |
| **Particulier**, **collectivité**, **association non-ESS** | ❌ Hors périmètre |

---

## 🔍 Comment ça fonctionne

Le skill suit une logique d'entonnoir validée par analyse statistique de **gain d'information conditionnel** (sélection gloutonne) :

```
2 384 aides
   ↓ Q1 — Type de projet
   ↓ Q2 — Domaine principal
   ↓ Q3 — Stade de financement
   ↓ Q4 — Nature de l'aide souhaitée
   ↓ Q5 — Secteur d'activité
   ↓ Q6 — Effectif
   ↓ Q7 — Région du siège
   ↓ Q8 — Dimension export / international
   ↓ Q9 — Caractère R&D / innovation
   ↓ Q10 — Cash disponible pour cofinancement
~25 aides candidates
   ↓ Scoring de crédibilité (cohérence taille / ticket, effort vs gain, sélectivité, cumulabilité)
Top 5 + plan d'action + export markdown
```

---

## 📂 Structure du repo

```
aides-startup-fr-by-reki/
├── SKILL.md                    Description et triggers du skill
├── data/
│   └── catalogue_compact.json  ~1 700 aides crédibles, 3,2 Mo
├── scripts/
│   ├── load_data.py            Chargement du catalogue
│   ├── scoring_lead_magnet.py  Filtrage + scoring
│   └── generer_export.py       Génération de l'export markdown
├── references/
│   ├── 10_questions_lead_magnet.md
│   ├── coherence_taille_montant.md
│   ├── fiches_aides_france2030_bpi.md
│   └── fiches_aides_fiscales.md
└── assets/
    ├── cta_reki.md
    └── export_template.md
```

---

## 🤝 À propos de Reki

[Reki](https://www.reki.eu) accompagne startups et PME pour aller chercher **10 k€ à 10 M€ de financement non-dilutif** : montage de dossiers Bpifrance et France 2030, sécurisation JEI/CIR, optimisation des cumuls de minimis et RGEC.

> Ce skill est un *lead magnet* : on vous donne un diagnostic gratuit et fiable pour vous montrer ce qu'on sait faire. Si vous voulez ensuite déléguer le montage des dossiers, nous travaillons majoritairement en **success fee** — pas d'aide obtenue, pas (ou peu) de facture.

📅 **Réserver 15 min avec Cyril Fougères** : https://calendly.com/cyril-reki/15-minute-meeting
✉️ **Écrire** : cyril@reki.eu
🌐 **Site Reki** : https://www.reki.eu

---

## 🛠️ Pour les développeurs

### Modifier le skill localement

```bash
git clone https://github.com/REPLACE_USERNAME/aides-startup-fr-by-reki.git
cd aides-startup-fr-by-reki
# Éditer les fichiers (SKILL.md, scripts/, references/, etc.)
./make_skill.sh   # repackage en aides-startup-fr-by-reki.skill
```

### Exécuter le scoring sans passer par Claude

```bash
# Préparer un profil JSON (cf. exemples dans assets/)
python3 scripts/scoring_lead_magnet.py --profile-json mon_profil.json

# Générer l'export complet
python3 scripts/generer_export.py --profile-json mon_profil.json --output rapport.md
```

### Contribuer

Les *issues* et *pull requests* sont bienvenues. Suggestions particulièrement utiles :

- Mises à jour des fiches enrichies *(LFSS 2026, dispositifs régionaux)*
- Ajout de nouveaux dispositifs hors catalogue open data
- Corrections de critères ou de montants observés
- Personas de test supplémentaires

---

## 📜 Licence

MIT — voir [LICENSE](LICENSE). Vous pouvez librement utiliser, modifier, redistribuer ce skill, y compris à des fins commerciales. Mention de Reki appréciée mais non exigée.

---

## ⚠️ Avertissement

Ce skill est un **outil d'aide à la décision** basé sur des données publiques et des heuristiques métier. Les montants, taux d'obtention, critères et timelines indiqués sont des estimations qui peuvent évoluer. La **fiche officielle de chaque dispositif fait foi** au moment du dépôt. Pour une instruction réelle de votre dossier, consultez le financeur concerné (Bpifrance, ADEME, Région, URSSAF, DGFiP) ou faites-vous accompagner — par Reki par exemple 😉.

---

*Made with ❤️ in France by [Reki](https://www.reki.eu) — open-source pour l'écosystème startup français.*
