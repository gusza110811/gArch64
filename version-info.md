# Versioning Info
This project uses a slightly custom versioning scheme.  
This document explains how to interpret each type of version.

## Releases

### Stable Release
The main versions you should normally use.  
Format: **`MAJOR.minor.patch`** (classic semantic-style).  

⚠️ Note: A stable release may be *revised in place* without bumping the patch number (rare).

---

### Unstable Release
Experimental but working builds.  
Format: **`snapshot[num] pre-v[version]`**  

- `[num]` is a global sequential counter (does not reset).  
- Example: `snapshot7 pre-v1.2` = the 7th snapshot overall, leading up to version `v1.2`.

---

### Cumulative Patch Release
Roll-up releases that gather multiple fixes before the next official patch.  
Format: **`v[version]-patch`**  

- Example: `v1.1-patch` = ongoing cumulative patch work for version `1.1`.  
- New fixes are not separate releases, but are tagged (see below).

---

## Tags (GitHub only)

### Stable Tag
Same as stable release format: **`vMAJOR.minor.patch`**

---

### Unstable Tag
Tracks the latest working commit for snapshots.  
Format: **`snapshot[num]`**

- Example: `snapshot7` = the 7th snapshot tag.

---

### Cumulative Patch Tag
Internal staging tags for cumulative patch releases.  
Format: **`v[version]-patch[patch number]`**

- Example: `v1.1-patch4` = the 4th staged patch for version `1.1`.  
- Once finalized, these roll into a proper patch release (e.g. `v1.1.1`).
