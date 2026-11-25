# Data card — paired SAR-to-optical reconstruction

## Intended use
Train Vyora's compact image-to-image baseline to map two Sentinel-1 radar channels (VV and VH) to an RGB rendering derived from paired Sentinel-2 optical imagery. This is a visual reconstruction/translation task, not land-cover classification, an official map product, or a disaster-warning system. SEN12MS classification labels under `labels/` are not required or consumed by this task.

## Dataset candidate
The team selected the official [SEN12MS dataset page](https://mediatum.ub.tum.de/1474000) and its [Toolbox repository](https://github.com/schmitt-muc/SEN12MS.git). SEN12MS provides paired Sentinel-1/Sentinel-2 imagery and suggested train/test lists; the Toolbox also provides labels and classification utilities for its classification use case. The data is not downloaded or included in this repository. Follow the source's access and licence terms; record the exact release, acquisition dates, and licence/attribution before redistribution or demo use.

## Format and pairing
The loader accepts separate VV/VH files or a native stacked-S1 GeoTIFF through `sar_path` plus explicit 1-based `vv_band` and `vh_band`. Sentinel-2 targets can be multiband GeoTIFFs; set `optical_bands` explicitly in visible red, green, blue order. For an order B01, B02, B03, B04, … this would be `[4, 3, 2]`, but verify order and metadata against the exact downloaded release rather than assuming. Pair S1/S2 files by the matching ROI/season/tile identifier, and verify CRS, transform, dimensions, acquisition relationship, and visual overlay. The loader's grid equality checks only guard against obvious alignment errors.

A manifest row needs `tile_id`, `scene_group`, `split`, `sar_path`, `vv_band`, `vh_band`, `optical_path`, `optical_bands`, `optical_scale`, `source`, and `licence`. Keep file paths relative to the dataset root. First run `scripts/inspect_sen12ms_pair.py --s1 <file> --s2 <matching-file>` to print band descriptions, tags, sample value percentiles, CRS and transforms. The `scripts/prepare_sen12ms_manifest.py` utility consumes Toolbox train/test lists and pairs corresponding S1/S2 names. It reserves whole ROI groups from the provided training list for validation and preserves the provided test list as the held-out test split. It intentionally fails if official train/test ROI groups overlap. The command-line helper requires VV/VH indexes, RGB indexes, and optical scale explicitly; pass values only after inspecting source metadata. It validates file paths, selected indexes, and exact grid equality.

## Preprocessed A/B PNG prototype path
The downloaded folder layout shown by the user has `train_A/train_B`, `val_A/val_B`, and `test_A/test_B` subfolders with 256×256 PNG tiles. `scripts/prepare_png_split_manifest.py` pairs exact relative filenames. The prototype loader converts A to grayscale and duplicates it into two input channels, while B is read as RGB. This is useful for a quick image-translation prototype but does not preserve separate VV and VH channels, source CRS/transform, or prove geographic independence of the supplied splits. Use the original GeoTIFF route for a true VV/VH geospatial workflow.

## Preprocessing and quality
- Confirm S1 polarization band mapping and whether values are linear power, amplitude, or dB. Apply the appropriate calibration/normalization; the current loader's percentile normalization is not Sentinel-1 radiometric calibration.
- Confirm S2 band order, scale, and reflectance product. A scale divisor of 10,000 is only a starting assumption, not verified release metadata.
- Cloud-screen optical targets and inspect sample pairs; cloudy targets teach the model to reconstruct clouds.
- Retain geographic ROI separation between train, validation, and test. Do not randomly split adjacent patches.
- Keep the official test list untouched for final evaluation. The validation ROI subset is generated reproducibly (default seed 42) from official training ROIs; document the exact split manifest and seed.

## Known limitations and prohibited claims
No real SEN12MS files have yet been inspected, trained on, or evaluated in this repository. The synthetic GeoTIFF fixtures only test code mechanics and do not establish band ordering, radiometry, alignment, image quality, model performance, or utility. Do not present outputs as true-colour ground truth, an official map, or an operational alert. Report held-out metrics only after an actual training run and evaluation on the reserved test scenes; document metrics, target scaling, split, and qualitative failure cases.
