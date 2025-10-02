# zCLI Release Checklist

Use this checklist when preparing a new release of zCLI.

## Pre-Release Checklist

### 1. Code Quality
- [ ] All tests pass: `zolo-zcli --shell` → `test all`
- [ ] No linter errors
- [ ] Code reviewed
- [ ] Documentation updated

### 2. Version Management
- [ ] Update version in `zCLI/version.py`
  ```python
  __version__ = "X.Y.Z"
  __version_info__ = (X, Y, Z)
  ```
- [ ] Update version references in documentation if needed
- [ ] Update `CHANGELOG.md` with new features/fixes (create if needed)

### 3. Dependencies
- [ ] All dependencies listed in `pyproject.toml`
- [ ] Dependencies have minimum version requirements
- [ ] No unused dependencies

### 4. Documentation
- [ ] README.md is up to date
- [ ] INSTALL.md has correct installation instructions
- [ ] All guides in `Documentation/` are current
- [ ] Code comments are clear

### 5. Security
- [ ] No hardcoded credentials or API keys
- [ ] `.gitignore` excludes sensitive files
- [ ] Test data is isolated (not production data)

---

## Release Process

### Step 1: Clean Build Environment

```bash
cd /Users/galnachshon/Projects/zolo-zcli
rm -rf dist/ build/ *.egg-info zolo_zcli.egg-info
```

### Step 2: Run Full Test Suite

```bash
zolo-zcli --shell
# In shell:
test all
exit
```

### Step 3: Build Distribution

```bash
python3 -m build
```

Verify output:
- `dist/zolo_zcli-X.Y.Z-py3-none-any.whl`
- `dist/zolo_zcli-X.Y.Z.tar.gz`

### Step 4: Test Installation Locally

```bash
# Create test environment
python3 -m venv /tmp/test_zcli_install
source /tmp/test_zcli_install/bin/activate

# Test wheel installation
pip install dist/zolo_zcli-X.Y.Z-py3-none-any.whl

# Verify
zolo-zcli --shell
# Test basic commands
exit

# Cleanup
deactivate
rm -rf /tmp/test_zcli_install
```

### Step 5: Commit Changes

```bash
git add .
git commit -m "Release v X.Y.Z"
git push origin main
```

### Step 6: Create Git Tag

```bash
# Create annotated tag
git tag -a vX.Y.Z -m "Release version X.Y.Z

Features:
- Feature 1
- Feature 2

Fixes:
- Fix 1
- Fix 2
"

# Push tag to GitHub
git push origin vX.Y.Z
```

### Step 7: Create GitHub Release (Optional)

1. Go to https://github.com/ZoloAi/zolo-zcli/releases
2. Click "Draft a new release"
3. Choose the tag you just created
4. Add release notes
5. Attach build artifacts (optional):
   - `zolo_zcli-X.Y.Z-py3-none-any.whl`
   - `zolo_zcli-X.Y.Z.tar.gz`
6. Publish release

### Step 8: Notify Users

Send installation instructions to authorized users:

```
New zCLI release: vX.Y.Z

To install or upgrade:
pip install --upgrade git+ssh://git@github.com/ZoloAi/zolo-zcli.git@vX.Y.Z

What's new:
- [Brief summary of changes]

Full release notes: https://github.com/ZoloAi/zolo-zcli/releases/tag/vX.Y.Z
```

---

## Post-Release Checklist

- [ ] Verify installation from Git works: `pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git@vX.Y.Z`
- [ ] Test on clean Python environment
- [ ] Update internal documentation/wikis
- [ ] Announce in team channels

---

## Hotfix Process

For urgent fixes:

1. Create hotfix branch from tag:
   ```bash
   git checkout -b hotfix/vX.Y.Z+1 vX.Y.Z
   ```

2. Make minimal changes to fix issue

3. Test thoroughly

4. Increment patch version (X.Y.Z → X.Y.Z+1)

5. Commit, tag, and release:
   ```bash
   git commit -m "Hotfix: [description]"
   git tag -a vX.Y.Z+1 -m "Hotfix release X.Y.Z+1"
   git push origin hotfix/vX.Y.Z+1
   git push origin vX.Y.Z+1
   ```

6. Merge back to main:
   ```bash
   git checkout main
   git merge hotfix/vX.Y.Z+1
   git push origin main
   ```

---

## Version Numbering

Follow Semantic Versioning (semver.org):

- **Major (X.0.0)**: Breaking changes, incompatible API changes
- **Minor (X.Y.0)**: New features, backward compatible
- **Patch (X.Y.Z)**: Bug fixes, backward compatible

Examples:
- `1.0.0` → First stable release
- `1.1.0` → Added new features (backward compatible)
- `1.1.1` → Bug fixes
- `2.0.0` → Breaking changes (API redesign)

---

## Rollback Procedure

If a release has critical issues:

1. **Quick rollback** - Point users to previous version:
   ```bash
   pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git@v1.0.0
   ```

2. **Fix and re-release** - Increment patch version

3. **Mark bad release** - Add warning to GitHub release notes

---

## Testing Matrix

Before each release, verify on:

- [ ] macOS (Darwin)
- [ ] Linux (Ubuntu/Debian)
- [ ] Windows 10/11 (if applicable)
- [ ] Python 3.8
- [ ] Python 3.9
- [ ] Python 3.10
- [ ] Python 3.11
- [ ] Python 3.12

---

**Maintainer**: Gal Nachshon (gal@zolo.dev)  
**Last Updated**: October 2025

