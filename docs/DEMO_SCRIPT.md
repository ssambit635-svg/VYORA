# Vyora: judge demo script

A simple 2–3 minute walkthrough. **Read the runner status from the app before you speak:** if it says Development, describe a rule-based demo; say “checkpoint” only when the API reports checkpoint inference.

## Before the demo

1. Start FastAPI and the React/Vite app; open the local workspace.
2. Check the **Model Status** card. For checkpoint inference, explicitly select `backend/checkpoints/vyora_resunet_b_to_a.pt`; otherwise present the run as Development mode.
3. Use one of the four bundled scenes. They are synthetic interface examples—not satellite images. If using an upload, verify that its format matches the active runner's input contract.

## Talk track, point by point

1. **Show the landing dashboard.** Drag the Earth, use arrow keys, then scroll through the sticky overview. “This is a textured 3D Earth with NASA GOES and Landsat 8 spacecraft models. Their paths are illustrative and not-to-scale; no live satellite positions are connected.”
2. **Explain the workflow.** Point to Choose a scene → Compare views → Note and export. “The diagram shows the local review flow; it does not imply an external data feed.”
3. **Show the workspace.** Point out the four synthetic examples and the API-reported runner mode/version. “The status is live from the local API; this demo does not use production login.”
4. **Run one scene.** “I will show the output this runner returned. If the banner says Development, these are hand-authored rules—not trained AI inference.”
5. **Compare source and estimate.** Drag the before/after slider—or focus it and use the arrow keys. “This is an estimated image, not recovered true colour or ground truth.”
6. **Switch the result layers.** Show Original input, Estimated colour, Consistency and Feature summary. “Consistency is a stability cue, not confidence. Shares appear only when returned by the API and are not validated land-cover detections. The app marks feature masks and attention maps unavailable.”
7. **Inspect the input.** Open the channel lens and histogram. “Separate VV/VH is claimed only when the API verifies distinct bands; a grayscale preview is not a VV/VH pair.”
8. **Review a region.** Drag a crop in Region Zoom Compare; the same image-space region is shown across input, output and consistency. Add a short human note and export the review JSON. “These notes are user annotations in normalized image coordinates, not geographic labels.”
9. **Show the run report and exports.** Point out source dimensions, input type, observed processing time, CRS and palette/rule shares only when returned. Export the output PNG or result JSON; a CRS/extent-preserving GeoTIFF preview is conditional on compatible georeferenced input.
10. **Close with the limits and footer.** Point out the runner status and external NASA/NOAA references. “Those links open outside Vyora; they are not connected to a run. Vyora does not detect floods, cyclones or land-cover classes, and it is not an official warning system. The source data's sensor semantics and geographic independence still need verification.”

## Feature check: what is in the app

| Feature | Status | Judge-friendly description |
|---|---|---|
| Landing page and demo entry | Present | Explains the workflow and keeps demo access local; no production authentication is claimed. |
| Interactive 3D Earth and spacecraft | Present | NASA Earth day/night/cloud textures and NASA GOES/Landsat 8 GLB models; drag, keyboard and reset controls. Scroll moves the camera. Orbits are illustrative, not-to-scale, and not live tracking. |
| Workflow diagram | Present | Shows input → estimate → human review at a glance. |
| NASA Eyes / NOAA GOES references | External links | NASA Eyes is an external satellite tracker; NOAA is an external real imagery animation. Neither is embedded or connected to Vyora runs. |
| Shared public/workspace footer | Present | Includes workspace navigation, runner label, prototype scope and external references. |
| Overview and scene library | Present | Four bundled synthetic scenes plus API-reported runner status. |
| Image upload | Present, input-dependent | PNG/JPEG preview or two-band GeoTIFF in supported modes; file contract is shown in the UI. |
| Image estimate and before/after slider | Present | Compare the source with the output returned by the active runner. |
| Result layer switcher | Present | Original, estimated colour, consistency, and API-returned feature summary. |
| Feature-mask and attention layers | Not produced | Clearly labelled unavailable; no mask or saliency output is invented. |
| Input-channel lens and histogram | Present, data-dependent | Inspect channel previews and available API statistics; identical preview channels are called out. |
| Region zoom comparison | Present | Compare the same selected image-space crop across views. |
| Human review notes | Present | Add notes to a marked normalized image region and export JSON. |
| Intelligence summary | Present, API-data-dependent | Dimensions and runtime; CRS and palette/rule shares only when returned. |
| Exports | Present, input-dependent | PNG and result JSON; GeoTIFF preview only when the API can preserve georeferencing. |
| Method, limits and runner status | Present | Describes the active method and research-prototype limits. |
| Hazard detection or official alerts | Not present | Do not describe Vyora as a flood, cyclone or emergency-warning detector. |

## If judges ask about model results

The documented corrected B→A checkpoint was evaluated on a 200-tile subset and outperformed a simple palette baseline on paired-pixel metrics. Its average colour spread remains much lower than the target's, and geographic independence/source semantics were not independently verified. See [Evaluation](EVALUATION.md) for the exact metrics and caveats. These results do not establish true-colour recovery or real-world hazard performance.
