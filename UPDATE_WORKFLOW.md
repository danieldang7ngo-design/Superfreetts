# Addon Update Workflow

Use this checklist when preparing any addon update. It keeps code changes, versioning, startup update notes, changelog entries, verification, and commit history aligned.

## 1. Confirm Scope

- Identify the changes included in the update: UI, behavior, bug fixes, docs, translations, dependency changes, or release-only metadata.
- Decide whether the update is user-facing. User-facing changes should usually update version, release notes, and changelog.
- Decide the next version in `superfreetts_addon/version.py` when preparing a release-style update.
- Keep local state files such as `meta.json` unchanged unless the task explicitly requires it.

## 2. Implement the Change

Edit only the files needed for the requested update.

Common areas:

- UI components: `superfreetts_addon/component_*.py`
- Main menu and hooks: `superfreetts_addon/gui.py`, `__init__.py`
- Text resources: `superfreetts_addon/i18n.py` + `superfreetts_addon/locales/*.json`
- Addon update popup: `superfreetts_addon/release_notes.py`
- Version: `manifest.json` and `superfreetts_addon/version.py`
- Public changelog: `CHANGELOG.md`

Follow existing code patterns and keep unrelated refactors out of the update.

## 3. Update Version

Edit both version fields so they match:

- `manifest.json` → `"version": "x.y.z"`
- `superfreetts_addon/version.py` → `ANKI_SUPER_FREE_TTS_VERSION='x.y.z'`

Skip this step only when the change is internal and should not trigger an addon update announcement. Never move a tag that has already been pushed; create a new version instead.

## 4. Update Addon Release Notes

Edit:

- `superfreetts_addon/release_notes.py`

Add a new `ReleaseNoteEntry` at the top of `RELEASE_NOTES`.

Required languages (all seven visible locales; English is the fallback):

- `en`
- `vi`
- `ko`
- `ja`
- `zh-CN`
- `zh-TW`
- `sv`

The release notes popup uses these entries after addon updates, so each entry should include:

- a short localized title
- concise bullets describing the user-visible changes
- matching message meaning across all supported UI languages

Skip this step only for non-release maintenance changes that should not appear in the startup update popup.

## 5. Update Changelog

Edit:

- `CHANGELOG.md`

Add a new section at the top:

```markdown
## x.y.z - YYYY-MM-DD
```

Include localized sections for at least:

- `English`
- `Tiếng Việt`

Add Korean too when the update affects Korean UI behavior or Korean users:

- `한국어`

## 6. Check i18n Coverage When Text Changes

When the update adds or changes UI text, edit the matching
`superfreetts_addon/locales/*.json` files. Add the English key first; add
reviewed translations for the other six locales when available. Missing keys
are allowed and fall back to English, but do not machine-generate unreviewed
translations just to inflate coverage.

For formatted strings, confirm placeholders match across languages, for example:

- `{count}`
- `{tag}`
- `{0}`

If the update does not touch UI text, this step can be skipped.

## 7. Verify

Run the same gates as CI:

```powershell
python -m pytest tests/ -q --tb=short
ruff check superfreetts_addon tests build_share.py scripts
bandit -r superfreetts_addon -ll
python -m pytest tests/ -q --cov=superfreetts_addon --cov-report=json:coverage.json --cov-fail-under=33
python scripts/check_critical_coverage.py coverage.json
python scripts/vendor_deps.py --check
```

Then build and inspect the package:

```powershell
python build_share.py
python scripts/verify_package.py SuperFreeTTS.ankiaddon
```

For UI changes, manually check the affected Anki screen on a real Anki
installation. For language changes, manually check each affected UI language;
machine-only translation is not a substitute for a native review. Real
macOS/Windows RAM and crash behavior must be verified on those platforms
(the Linux CI smoke tests cannot prove it).

Search for stale version references:

```powershell
rg -n "x\.y\.(z-1)|x\.y\.z" .
```

Ignore matches from third-party files under `external`.

## 8. Stage and Commit

Check the working tree:

```powershell
git status --short
```

Stage the intended files. If sparse checkout blocks `CHANGELOG.md`, use `--sparse`:

```powershell
git add --sparse -- CHANGELOG.md superfreetts_addon/version.py superfreetts_addon/release_notes.py
```

Include any related source files changed for the update.

Commit with a release-oriented message:

```powershell
git commit -m "chore(release): bump to x.y.z"
```

Use a more specific commit message when the update is not a release bump, for example:

```powershell
git commit -m "fix(preferences): restore saved language selection"
```

## 9. Final Sanity Check

Run:

```powershell
git status --short
```

Expected result: no output.

If the update includes UI language changes, manually verify in Anki:

- Preferences language selector restores the saved language.
- Settings and About render correctly.
- The startup update popup uses the current UI language.

If the update includes non-language UI or behavior changes, manually verify the changed workflow from the user's entry point.
