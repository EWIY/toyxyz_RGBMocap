# Maintaining and publishing this fork

Use a dedicated source checkout. Preserve installed model folders, runtimes,
projects and character work in their original location. This fork's `custom`
branch is based on the original upstream history; `main` is kept as an upstream
reference. The public source contains all connected GUI/worker modules, not only
a patch or a subset of the local files.

Never stage `character_library/`, including downloaded character FBXs, textures
or material sidecars. Its dropdown code and documentation are source; the only
bundled character exception remains the pinned Epic Manny under `assets/`.

## Before publishing

1. Inspect `git status --short` and the staged diff. Add only source, documentation,
   tests, locked installation metadata and the upstream-approved resources.
2. Run `python tools/check_source.py`. It checks source composition, syntax,
   required dependency files, resource exceptions and the runtime registry hash.
3. Stage intended source files, then run `python tools/check_fork.py --write-manifest`.
   Stage the refreshed `SOURCE_MANIFEST.json`, then run `python tools/check_fork.py`.
   It also checks private/generated paths, model payloads, local developer paths,
   possible secrets, missing application imports, README links and official VGGT
   identity. It audits the Git index, not just `.gitignore` rules.
4. After installation, run `runtime\python.exe -X utf8 -B tools\run_fork_tests.py`.
   These regression tests use synthetic data and temporary folders. They do not
   require private clips, licensed bodies or checkpoints.
5. Commit the reviewed source. Clone that exact commit into a new writable folder,
   rerun both source checks there, and confirm the manifest matches. A source-only
   clone initially has no models, runtime, cache or character-work folder.
6. Exercise `install.cmd`, the launcher and relevant changed features in an isolated
   checkout. Record exactly what ran in [FORK_VALIDATION.md](FORK_VALIDATION.md).
   A source check does not prove GPU inference or an untested engine import.

The repository keeps fixed HTTPS dependencies and exact hashes. Some small
pure-Python dependencies are retained as unpacked source and rebuilt by the
installer; removing `installer/runtime_sources/` breaks installation. Likewise,
retain `prebuilt/motion-correction/`, its corresponding source/build files,
`installer/source-resources.json` and the approved importer shader assets.
Models and auxiliary body arrays are acquired separately, not committed.
Keep the official-target source together: `mocap/official_targets.py`,
`tools/setup_official_target.py`, GUI/worker integration and the anatomical finger
adapter, plus `mocap/bundled_targets.py`. The one approved FBX exception is
`assets/export_skeletons/ue5_manny/SKM_Manny_Simple.fbx`, with its Epic notice,
provenance and exact hash in `installer/source-resources.json`. All other character
FBXs, imported `.blend`/NPZ data, textures and the
local `config/official-export-targets.json` registry must stay out of Git. The small
Unity material-binding JSON contains only filenames, checksums and binding settings;
it is not a character asset. See [official setup](OFFICIAL_EXPORT_TARGETS.md).

## Configure the GitHub fork

The maintained fork is [EWIY/toyxyz_RGBMocap](https://github.com/EWIY/toyxyz_RGBMocap),
derived from [toyxyz/toyxyz_RGBMocap](https://github.com/toyxyz/toyxyz_RGBMocap).
`custom` is the distribution branch; `main` remains the upstream reference.
In a maintainer checkout with no `origin`, configure:

```cmd
git remote add origin https://github.com/EWIY/toyxyz_RGBMocap.git
git push -u origin custom
```

If `origin` already exists, review `git remote -v` and change that remote's URL
deliberately instead of adding a duplicate. Do not change `upstream` to your own
fork. Set `custom` as the GitHub default branch, or retain the README's explicit
`--branch custom` clone command. Normal clones then track `origin/custom`.

Do not push an installed folder through a web file uploader or a general-purpose
folder ZIP. Push the reviewed Git commit, or use `git archive` of that commit for
a source-only artifact. The manifest excludes itself to avoid a circular hash.
The root MIT file and all upstream component licenses must stay in the tree.

## Updating your fork

For normal users, `update.cmd` requires a clean tracked worktree and a named
branch with a tracking remote. A custom branch tracking `upstream/main` is
rejected to avoid updating a fork from the wrong branch. It uses fast-forward
pulls and preserves the upstream install-repair/pending-marker behavior.

For maintainers, merge upstream changes separately:

```cmd
git fetch upstream
git switch custom
git merge upstream/main
```

Review overlapping changes by behavior. Fusion worker dispatch and model-download
callbacks can coexist in one file; a shared filename alone is not a conflict.
Preserve both sides' validation entries and acknowledgments. Refresh the retained
upstream README from the exact upstream commit without changing its bytes.
Then review model/provider identities, dependency-lock/registry hashes, source
manifest, tests and clone/install behavior before pushing.

Do not publish a mirror-model hash as if it identified the official checkpoint.
Do not weaken validation to make a local substitution pass. Local model choices
and private work data stay outside the published Git tree.
