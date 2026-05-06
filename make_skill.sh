#!/usr/bin/env bash
# Repackage le skill en archive .skill (zip) prête à distribuer.
# Usage : ./make_skill.sh [nom_de_sortie]
# Par défaut : aides-startup-fr-by-reki.skill

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

OUTPUT_NAME="${1:-aides-startup-fr-by-reki.skill}"
SKILL_DIR_NAME="aides-startup-fr-by-reki"

# Crée un dossier temporaire avec le contenu du skill
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

mkdir -p "$TMPDIR/$SKILL_DIR_NAME"

# Copie tous les fichiers nécessaires (en excluant les artefacts dev)
rsync -a \
  --exclude='.git/' \
  --exclude='.github/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='*.skill' \
  --exclude='.DS_Store' \
  --exclude='make_skill.sh' \
  --exclude='CHANGELOG.md' \
  --exclude='LICENSE' \
  --exclude='README.md' \
  --exclude='.gitignore' \
  ./ "$TMPDIR/$SKILL_DIR_NAME/"

# Zippe en .skill
rm -f "$OUTPUT_NAME"
(cd "$TMPDIR" && zip -r "$SCRIPT_DIR/$OUTPUT_NAME" "$SKILL_DIR_NAME" >/dev/null)

SIZE=$(du -h "$OUTPUT_NAME" | cut -f1)
echo "✅ Skill packagé : $OUTPUT_NAME ($SIZE)"
echo "📋 Drag-droppez ce fichier dans Claude.ai ou Cowork pour l'installer."
