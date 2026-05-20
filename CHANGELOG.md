# Changelog

Toutes les modifications notables de ce skill sont documentées ici.

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).
Versionnement [Semantic Versioning](https://semver.org/lang/fr/).

## [1.3.0] — 2026-05-20

### Corrigé — Bug critique (signalé via brief de test NovaSense AI)
- **Mapping Q2 ↔ id_domaine catalogue** : la numérotation présentée à
  l'utilisateur (Q2 "Innovation" = 2) ne correspondait pas aux codes du
  catalogue (id_domaine "4" = Innovation). Conséquence : un fondateur
  qui répondait "Innovation" filtrait en fait sur les aides Export.
  Ajout de `Q2_TO_CATALOG_DOMAIN` qui traduit les réponses Q2 vers les
  codes catalogue. Top 5 retrouve les vraies aides d'innovation
  (Avance Innovation, Prêt Innovation R&D, Pionniers IA, BFT…).

### Corrigé — Bug design
- **Aides à secteur exclusif filtrées** : pénalité -20 au score si
  l'aide cible un secteur (Métiers d'art, Agriculture, ESS, Tourisme,
  Culture, Agro) et que l'utilisateur n'a pas coché ce secteur dans
  Q5. Évite "Plan métiers d'art à l'export" ou "Aide installation
  viticulteur" dans le top 5 d'une startup tech.

### Modifié
- **Q5 refondue dans SKILL.md** : passe de "Secteur principal (11
  options)" à "Activité dans un secteur spécifique ? (oui/non avec
  6 secteurs niches)". Plus discriminante et alignée sur le scoring.
- **Tolérance domaine élargie** : le filtre dur accepte désormais aussi
  `id_domaine = "0"` (indéterminé) en plus de `"1"` (Économie générale)
  pour les projets innovation, récupérant 18 aides utiles auparavant
  écartées.
- **Profile.from_raw** : factory unique pour construire un profil depuis
  un dict, appelée dans les 3 mains (scoring, export, pdf). Centralise
  les mappings Q2 et Q5 — plus de divergence possible entre scripts.
- **CII cumulable avec CIR sur lots distincts** : retrait de la clause
  `not p.rd_pure` dans `add_automatic_aides`. La famille `credits_impot`
  accepte déjà 2 entrées, la dédup se charge du reste.
- **compute_pourquoi fallback intelligent** : utilise l'objet de l'aide
  tronqué à ~140 caractères au lieu du libellé générique "Aide cohérente
  avec votre profil et votre stade".
- **Trailing whitespace dans la synthèse** : `.strip()` ajouté après les
  `.split()` pour éviter les espaces parasites dans `top_priorities`.

## [1.2.0] — 2026-05-20

### Ajouté
- **Rappels périodiques Reki** : tous les ~10 messages, le skill glisse
  un rappel court positionnant Reki (Cyril Fougères, CEO, 10 ans
  d'expertise en financements publics) avec lien Calendly direct.
  3 formats alternatifs pour varier la formulation.
- **Redirect contact** : quand l'utilisateur demande "à qui s'adresser",
  "qui contacter", "qui peut m'aider à monter le dossier", etc., le
  skill route systématiquement vers Cyril Fougères / Reki avec
  formulation type incluant l'argument success fee.
- Fallback si l'utilisateur insiste sur acteurs gratuits (Bpifrance
  régional, CCI, Conseillers-Entreprises) tout en rappelant le modèle
  success fee de Reki.

## [1.1.0] — 2026-05-06

### Ajouté
- Génération de PDF avec charte graphique Reki (jaune doré, sections
  numérotées, badges Automatique vert pour CIR/JEI, bandeau ⚠️ Règle de
  cumul) via WeasyPrint
- Logique de cumul/exclusion entre aides Bpifrance (familles mutuellement
  exclusives : API / Avance Innovation / Prêt Innovation R&D ne sont plus
  proposées ensemble)
- Section "Aides alternatives" qui mentionne les autres aides de la même
  famille à considérer si la principale est rejetée

### Modifié
- Export markdown raccourci (~25 % plus court) avec format tableau condensé
  par aide pour une lecture plus opérationnelle
- Plan d'action 90 jours en tableau (Quand / Action / Dispositif / Effort)

### Corrigé
- Plus de double-comptage de potentiel total quand plusieurs aides
  Bpifrance non-cumulables apparaissaient dans le même top 5

## [1.0.0] — 2026-05-06

### Ajouté
- Skill initial avec parcours en 10 questions discriminantes
- Catalogue compact de 1 679 aides crédibles (extraction de l'open data
  aides-entreprises.fr — 2 384 aides au total)
- Fiches enrichies 2025-2026 sur 6 dispositifs France 2030 / Bpifrance
  (Projets d'Innovation, Pionniers IA, Bourse French Tech, ADI, Avance
  Innovation, Prêt Innovation R&D)
- Fiches enrichies sur 6 dispositifs fiscaux (JEI, JEC, JEII, CIR, CII, CICo)
  + 5 Diags Bpifrance (Décarbon'Action, IA, Cyber, Adaptation, Biodiversité)
- Grille de cohérence taille / montant / stade (référence
  `coherence_taille_montant.md`)
- Scoring de crédibilité multi-critère (cohérence ticket, ratio gain/effort,
  cumulabilité, sélectivité)
- Injection automatique des aides invisibles du catalogue (CIR, JEI, ACRE)
- Génération d'export markdown personnalisé avec plan d'action 90 jours
- CTA Reki standardisé en fin de rapport

### Source des données
- Open data aides-entreprises.fr / CCI France (extraction mai 2026)
- Recherches web 2025-2026 sur bpifrance.fr, urssaf.fr, bofip.impots.gouv.fr,
  legifrance.gouv.fr, entreprises.gouv.fr

### Limitations connues
- Les statistiques de sélectivité (taux d'obtention) sont des estimations
  cabinet, pas des chiffres officiels publiés.
- Les déclinaisons régionales d'un même dispositif sont parfois dédupliquées
  par signature de nom — la version dédupliquée peut masquer une variante
  pertinente.
- Le seuil R&D JEI à 25 % prévu au PLFSS 2026 n'est pas encore intégré
  (à mettre à jour si la loi est promulguée).
