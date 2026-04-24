# Addon Update Workflow

Use this checklist when preparing any addon update. It keeps code changes, versioning, startup update notes, changelog entries, verification, and commit history aligned.

## 1. Confirm Scope

- Identify the changes included in the update: UI, behavior, bug fixes, docs, translations, dependency changes, or release-only metadata.
- Decide whether the update is user-facing. User-facing changes should usually update version, release notes, and changelog.
- Decide the next version in `superfreetss_addon/version.py` when preparing a release-style update.
- Keep local state files such as `meta.json` unchanged unless the task explicitly requires it.

## 2. Implement the Change

Edit only the files needed for the requested update.

Common areas:

- UI components: `superfreetss_addon/component_*.py`
- Main menu and hooks: `superfreetss_addon/gui.py`, `__init__.py`
- Text resources: `superfreetss_addon/i18n.py`
- Addon update popup: `superfreetss_addon/release_notes.py`
- Version: `superfreetss_addon/version.py`
- Public changelog: `CHANGELOG.md`

Follow existing code patterns and keep unrelated refactors out of the update.

## 3. Update Version

Edit:

- `superfreetss_addon/version.py`

Set:

```python
ANKI_SUPER_FREE_TTS_VERSION='x.y.z'
```

Skip this step only when the change is internal and should not trigger an addon update announcement.

## 4. Update Addon Release Notes

Edit:

- `superfreetss_addon/release_notes.py`

Add a new `ReleaseNoteEntry` at the top of `RELEASE_NOTES`.

Required languages:

- `en`
- `vi`
- `ko`

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

When the update adds or changes UI text, edit:

- `superfreetss_addon/i18n.py`

Make sure all new keys exist for:

- `en`
- `vi`
- `ko`

For formatted strings, confirm placeholders match across languages, for example:

- `{count}`
- `{tag}`
- `{0}`

If the update does not touch UI text, this step can be skipped.

## 7. Verify

Run compile checks for changed Python files. Start with the files touched by the update:

```powershell
python -m py_compile .\superfreetss_addon\version.py .\superfreetss_addon\release_notes.py .\superfreetss_addon\i18n.py
```

Add any other changed Python files to the command.

For UI changes, manually check the affected Anki screen.

For language changes, manually check each affected UI language.

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
git add --sparse -- CHANGELOG.md superfreetss_addon/version.py superfreetss_addon/release_notes.py
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
