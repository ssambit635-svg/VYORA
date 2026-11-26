# Disaster Detection: Proposed Architecture (Not Yet Implemented)

## Scope boundary

The current Vyora paired-PNG model estimates image pixels. It is not a flood detector, cyclone detector, impact classifier, or forecast model. The three Result Workspace additions (SAR Channel Lens, Region Zoom Compare, and Human Review Notes) are inspection and annotation tools only; they do not add hazard inference.

“Pre-disaster cyclone/flash-flood detection” contains two different problems:

- **Cyclone forecasting** is a meteorological forecasting problem. SAR imagery can help observe a storm or its impacts, but this app's image-colorization model cannot predict a cyclone's formation, track, or landfall. A credible forecast product would need official forecast/best-track data and numerical weather prediction inputs/models, plus operational validation.
- **Flash-flood early warning** is a rainfall-runoff and hydrology problem. Pre-event SAR imagery alone cannot predict a flash flood. Forecast precipitation, catchment/topography, drainage, soil/land-cover, and observed water levels are needed. SAR is especially useful for mapping inundation during or after an event, including under cloud cover.

## Candidate system architecture

1. **Ingest and provenance**
   - Keep scenes georeferenced and record platform, acquisition time, orbit, product level, polarization, calibration status, CRS, processing history, event ID, and source/licence.
   - Build event-based pre-event baselines and post-event acquisitions. Use calibrated/co-registered Sentinel-1 VV/VH GRD time series; optionally add Sentinel-2 with cloud masks, DEM/slope, rainfall forecasts, gauges, land cover, and authoritative event boundaries.
   - Do not treat an arbitrary two-band image or grayscale preview as verified VV/VH. Keep previews separate from analysis-grade source data.

2. **Analysis-ready preprocessing**
   - Verify input metadata and polarization; apply orbit metadata, border/noise handling, radiometric calibration, terrain correction, geocoding, and consistent co-registration using an established SAR pipeline (for example, a validated SNAP/ESA workflow).
   - Harmonize grids, resolution, incidence geometry and no-data masks. Derive log-backscatter and temporal-change features only after QA. Preserve masks and transforms with every output.

3. **Separate task-specific models**
   - **Inundation mapping:** a temporal Siamese U-Net/change-detection segmentation model takes pre-event and event VV/VH stacks (and optional DEM/context) and predicts per-pixel flood probability. Add a permanent-water baseline and exclusion masks so normal water, shadow, layover, and vegetation effects are not casually called flooding.
   - **Cyclone analysis:** keep cyclone track/intensity forecasting outside this SAR image model; consume authoritative meteorological forecasts. A distinct, event-labelled impact model may map observed coastal inundation or damage from pre/post imagery. Do not conflate impact mapping after landfall with forecasting before landfall.
   - **Flash-flood warning:** pair precipitation nowcasts/forecasts with catchment hydrology and river/gauge observations for lead-time risk. Use SAR-derived inundation as an observation/verification input, not a substitute for the forecast drivers.

4. **Labels, splits, and evaluation**
   - Assemble independently reviewed event footprints and impact labels with timestamps and uncertainty. Split train/validation/test by entire event and geography—not random adjacent image tiles—and include diverse seasons, terrain, incidence angles, land cover, and sensors.
   - Report flood precision/recall, IoU/F1, omission/commission and false-alarm area, plus lead-time performance for a warning system. Report calibration/reliability and per-region/event failure cases. Compare against simple baselines and hold out unseen disasters.
   - Human review notes are useful annotations, but they are not ground truth until adjudicated, sourced, and versioned in a label workflow.

5. **Decision-support interface and operations**
   - Return hazard probability, event/time window, valid-data mask, source/provenance, model/version, thresholds, uncertainty/calibration status, and limitations. Show analyst review and correction workflow, audit trail, and safe abstention for poor-quality or out-of-distribution inputs.
   - Pilot retrospectively and with shadow-mode alerts before any operational use. Set thresholds with local disaster-management partners and track missed events, false alarms, data outages, and model drift. Never present an unvalidated prototype as an official warning.

## Near-term recommendation

Treat the current application as a transparent image-inspection demonstrator. The next ML milestone should be a small, documented **event-level flood-extent benchmark** using analysis-ready paired SAR and independent flood labels. Only after spatial/event-held-out validation should it be described as a flood-mapping prototype. Cyclone forecasting requires its own meteorological data/model scope and should not be promised as a feature of the current checkpoint.
