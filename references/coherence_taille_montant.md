# Cohérence taille de l'entreprise / montant d'aide

> Principe : un dispositif n'est crédible que si son ticket type est en
> phase avec la taille de la boîte. En proposer trop ou trop peu détruit
> la confiance du fondateur. Cette grille sert à filtrer et ranker.

## La grille de référence

| Profil entreprise | Ticket "petit" crédible | Ticket "moyen" crédible | Ticket "gros" crédible | À éviter (trop gros) | À éviter (trop petit) |
|---|---:|---:|---:|---:|---:|
| **Pre-seed** (0-3 pers., < 200 k€ levé, idée/POC) | 5-30 k€ | 30-100 k€ | 100-300 k€ | > 500 k€ | < 5 k€ |
| **Seed** (3-10 pers., 200 k€-1,5 M€ levé, MVP) | 25-75 k€ | 75-300 k€ | 300 k€-1 M€ | > 2 M€ | < 10 k€ |
| **Série A** (10-30 pers., 2-8 M€ levé, traction client) | 50-150 k€ | 150 k€-700 k€ | 700 k€-3 M€ | > 5 M€ (sauf consortium) | < 25 k€ |
| **Série B / Growth** (30-100 pers., 8-30 M€ levé, scaling) | 100-300 k€ | 300 k€-1,5 M€ | 1,5-5 M€ | < 50 k€ | < 50 k€ |
| **PME établie** (10-49 pers., > 3 ans, > 1 M€ CA) | 30-100 k€ | 100 k€-500 k€ | 500 k€-2 M€ | > 3 M€ (sauf collab) | < 25 k€ |
| **PME 50-249** (> 5 M€ CA) | 50-200 k€ | 200 k€-1 M€ | 1-3 M€ | / | < 30 k€ |
| **ETI** (250+) | 200-500 k€ | 500 k€-2 M€ | 2-10 M€ | / | < 100 k€ |

## Règles de cohérence

### Principe 1 — Effort vs gain
Le coût en jours-hommes pour préparer un dossier d'aide est sensiblement
constant : 5-15 j pour une bourse, 15-30 j pour une avance/prêt, 30-90 j
pour un AAP France 2030. Le **ratio gain attendu / effort** doit dépasser
~3 000 € / jour-homme pour qu'une aide soit crédible. En dessous, le
fondateur perd plus de valeur en attention qu'il n'en gagne en cash.

### Principe 2 — Capacité de cofinancement
La plupart des aides exigent 30-70 % de cofinancement par l'entreprise.
Le ticket d'aide doit donc respecter `aide_max ≤ cash_disponible × ratio_aide / (1 - ratio_aide)`.
Exemple : 1 M€ levé × 50 % / 50 % = 1 M€ d'aide max théorique sans
besoin de re-financement.

### Principe 3 — Maturité du dossier exigé
Plus le ticket est gros, plus le dossier est lourd : LOI clients, term-sheet
investisseur, business plan détaillé, etc. Un fondateur pre-seed sans MVP
n'a pas la matière pour un dossier France 2030. Le ranker doit le savoir.

### Principe 4 — Fenêtre temporelle de l'aide
Les bourses ont des "fenêtres" (entreprise < 1 an pour BFT, < 8 ans pour
JEI). Hors fenêtre = aide à exclure du top 5, même si techniquement
détectée par le filtre.

## Heuristiques d'élimination automatique

Une aide est **éliminée du top 5** (mais conservée en mention) si :

- Son ticket maximum < 30 % du ticket "petit" attendu pour le profil
- Son ticket minimum > 150 % du ticket "gros" attendu pour le profil
- Le dispositif a une fenêtre d'éligibilité que la boîte a dépassée
- Le dispositif est régional et la boîte n'est pas dans la région
- Le dispositif est sur enveloppe `de minimis` < 50 k€ ET la boîte a
  déjà ≥ 250 k€ de minimis sur 3 ans

## Heuristiques de promotion

Une aide est **promue dans le top 5** si :

- Son ticket médian observé tombe dans la fourchette "moyen" du profil
- L'aide est **automatique** (CIR, JEI) — elle ne consomme pas du temps
  d'instruction même si le gain est moyen
- L'aide est **cumulable** avec d'autres déjà identifiées (lots de
  dépenses distincts, RGEC vs de minimis)
- L'aide est **en flux tendu** (relève imminente, fenêtre fermante) —
  on signale alors l'urgence

## Exemples d'application

### Cas A — Startup IA Seed 5 personnes, 1 M€ levé
- ✅ France 2030 — Projets d'Innovation : ticket 75-500 k€ → cible
- ✅ BPI Avance Innovation : ticket 400 k€-1,5 M€ → cible haute mais ok
- ✅ JEI : automatique, 80-150 k€/an → cible
- ✅ CIR : automatique, 50-150 k€/an → cible
- ❌ Bourse French Tech (50 k€) : trop petit après 1 M€ levé
- ❌ Aide aux loyers Le Mans (5 k€) : ratio effort/gain mauvais
- ❌ France 2030 i-Démo (1 M€+ assiette) : trop gros sans consortium

### Cas B — Artisan-bâtiment 1 personne en création
- ✅ Prêt d'honneur Initiative France/Réseau Entreprendre : 30-45 k€
- ✅ ARCE Pôle Emploi : capital chômage
- ✅ ACRE : exonération 1ʳᵉ année
- ✅ Aide régionale Création : 10-30 k€
- ❌ France 2030 : hors cible totalement
- ❌ JEI : pas R&D
- ❌ CIR : pas de R&D, pas applicable

### Cas C — PME industrielle 80 personnes, 8 M€ CA
- ✅ Diag Décarbon'Action / IA / Cyber Bpifrance : 4-7 k€ (boost stratégique)
- ✅ Aide PME saut technologique régionale : 30-100 k€
- ✅ BPI Aide pour le Développement de l'Innovation : 200-700 k€
- ✅ CIR/CII : automatique
- ✅ France 2030 i-Démo en consortium : 500 k€-3 M€
- ❌ BFT/BFTE : hors fenêtre (> 1 an)
- ❌ Prêt d'honneur : non pertinent
