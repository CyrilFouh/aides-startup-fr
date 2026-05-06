# Changelog

Toutes les modifications notables de ce skill sont documentées ici.

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).
Versionnement [Semantic Versioning](https://semver.org/lang/fr/).

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
