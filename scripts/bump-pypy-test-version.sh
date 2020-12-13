set -e
version_file=mloq/version.py
current_version=$(grep __version__ $version_file | cut -d\" -f2)
ts=$(date +%s)
new_version="$current_version$ts"
bumpversion --current-version $current_version --new-version $new_version patch $version_file