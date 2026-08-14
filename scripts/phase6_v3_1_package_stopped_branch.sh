#!/bin/zsh
set -euo pipefail

repo_root="${0:A:h:h}"
cd "$repo_root"

bundle_tmp="$(mktemp -d /tmp/schwo_v31_bundle.XXXXXX)"
bundle_root="$bundle_tmp/SchWO_Phase6_V3_1_all_versions_20260814"
source_list="$bundle_tmp/source_paths.txt"
archive="$repo_root/SchWO_Phase6_V3_1_all_versions_computation_bundle_20260814.zip"
inventory_rel="docs/reports/phase6_v3_1_computation_bundle_inventory_20260814.tsv"

if [[ -e "$archive" || -e "$archive.sha256" ]]; then
  print -u2 "archive or checksum already exists; refusing to overwrite"
  exit 2
fi

mkdir -p "$bundle_root"

{
  print -l project.md status.md pyproject.toml
  print -l docs/review_gate_liveness_protocol.md docs/templates/t7_gate_verdict_template.md
  print -l docs/prompts/phase6_v3_master_prompt.md
  print -l references/notes/phase6_v3_absorption_scattering_conventions.md
  find configs -maxdepth 1 -type f \( -name 'phase6_v3_0*' -o -name 'phase6_v3_1*' \) -print
  find docs -maxdepth 1 -type f \( -name 'phase6_v3_0*' -o -name 'phase6_v3_1*' \) -print
  find docs/prompts -maxdepth 1 -type f -name '*v3_1*' -print
  find docs/handoffs/archive -maxdepth 1 -type f -name '*v3_1*' -print
  find docs/reports -maxdepth 1 -type f \( \
    -name 'phase6_v3_1_all_versions_failure_defect_report_20260814.md' -o \
    -name 'phase6_v3_1_computation_bundle_README_20260814.md' \
  \) -print
  find scripts -maxdepth 1 -type f -name 'phase6_v3_1*' -print
  find src/schwgw/validation -maxdepth 1 -type f \( -name 'phase6_v3*' -o -name 'phase6_mpmath_radial.py' \) -print
  find src/schwgw/numerics -type f ! -path '*/__pycache__/*' -print
  find src/schwgw/backgrounds -type f ! -path '*/__pycache__/*' -print
  find src/schwgw/perturbations -type f ! -path '*/__pycache__/*' -print
  find tests -type f \( -name 'test_phase6_v3*' -o -name '*v3_1*' \) ! -path '*/__pycache__/*' -print
  find generated/phase6_v3_1_z -maxdepth 1 -type f -print
  find generated/phase6_v3_1_z/conformance_vectors -type f -print
} | LC_ALL=C sort -u > "$source_list"

rsync -aR --files-from="$source_list" ./ "$bundle_root/"

inventory="$bundle_root/$inventory_rel"
mkdir -p "${inventory:h}"
{
  printf 'relative_path\tbytes\tsha256\n'
  find "$bundle_root" -type f ! -path "$inventory" -print0 |
    LC_ALL=C sort -z |
    while IFS= read -r -d '' file_path; do
      relative_path="${file_path#$bundle_root/}"
      bytes="$(stat -f '%z' "$file_path")"
      sha256="$(shasum -a 256 "$file_path" | awk '{print $1}')"
      printf '%s\t%s\t%s\n' "$relative_path" "$bytes" "$sha256"
    done
} > "$inventory"

cp "$inventory" "$repo_root/$inventory_rel"

(
  cd "$bundle_tmp"
  COPYFILE_DISABLE=1 /usr/bin/zip -X -9 -q -r "$archive" "${bundle_root:t}"
)

archive_sha256="$(shasum -a 256 "$archive" | awk '{print $1}')"
printf '%s  %s\n' "$archive_sha256" "${archive:t}" > "$archive.sha256"

file_count="$(find "$bundle_root" -type f | wc -l | tr -d ' ')"
bundle_bytes="$(du -sk "$bundle_root" | awk '{print $1 * 1024}')"
archive_bytes="$(stat -f '%z' "$archive")"

printf 'STAGING_DIRECTORY=%s\n' "$bundle_tmp"
printf 'FILE_COUNT=%s\n' "$file_count"
printf 'BUNDLE_BYTES=%s\n' "$bundle_bytes"
printf 'ARCHIVE_BYTES=%s\n' "$archive_bytes"
printf 'ARCHIVE_SHA256=%s\n' "$archive_sha256"
