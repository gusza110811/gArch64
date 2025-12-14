# Versioning Info
This document explains how to interpret each type of version.

## Releases

### Stable Release
The main versions you should use unless you know you want snapshots.  
As of December 2025, this doesn't mean they are fully stable, but generally are the *most* stable  
Format: **`MAJOR.minor.patch`**.

* Note 1: A stable release may be *revised in place* without bumping the patch number, but only for small changes without observable behavioral changes. these changes will not affect the ABI

* Note 2: `1.x` versions are not yet *solid*. ABI, instructions, and opcodes may change between minor releases. We\* do not guarantee compatibility between each minor release in this major release
<sub>*The amount of people working on this project is singular as of December 2025, but you never know who might contribute</sub>

---

### Unstable Release (Snapshots)
Experimental but working builds.  
Each snapshot even if leading up to the same stable version, are not guaranteed to be compatible with each other  
Format: **`snapshot[num] pre-v[version]`**  

- `[num]` is a global sequential counter (does not reset).
- `[version]` is the stable version the snapshot leads up to.
- Example: `snapshot6 pre-v1.2` = the 6th snapshot overall, leading up to version `v1.2`.

---

## Tags (Source control only)

### Stable Tag
Same as stable release format: **`vMAJOR.minor.patch`**

---

### Unstable Tag
Tracks the latest working commit for snapshots.  
Format: **`snapshot[num]`**

- Example: `snapshot6` = the 6th snapshot tag.

---

## Branching Model Note
Patch works are on a separate branch from main and will be merged back when the patches are necessary or when the patch work is done.

---