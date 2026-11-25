# Voltrix deck presenter notes

The actual source PDF is not stored in this checkout. These notes should be checked against the final slide deck before presenting. Use the current scope/evidence in `docs/PPT_ALIGNMENT_AND_SELECTION_GUIDE.md` and do not present future work as complete.

1. **Title / team:** State PS code HK26-PS-19; verify official Team ID, names, and any placeholders against event registration.
2. **Problem:** Explain that SAR records microwave backscatter, not visible colour. If a slide uses an illustration, identify whether it is synthetic or real source imagery.
3. **Current demo:** The trained checkpoint shown today is grayscale B-side PNG → paired A-side image estimate. The channel audit does not verify sensor identity or prove VV/VH-to-optical mapping.
4. **Stack:** The accepted live interface is React/Vite + FastAPI. Streamlit exists as an optional alternate. If the submitted deck says Streamlit, correct the slide or deliberately rehearse that version.
5. **Model:** Compact ResU-Net, 2 model input channels to 3 output channels. For this checkpoint, the two inputs are duplicates of one grayscale PNG channel, not separate VV/VH.
6. **Evidence:** On 200 of 4,576 supplied test tiles (seed 42), B→A ResU-Net MAE was 0.09632 vs 0.35373 for the simple baseline; SSIM was 0.67069 vs 0.24769. Folder split geographic independence was not independently verified.
7. **Failure / limitations:** Average prediction RGB spread was 0.03778 vs target 0.13053; some outputs remain under-coloured. A green-looking example does not prove true colour, geography, or operational value.
8. **Consistency / features:** Flip-view agreement is not calibrated uncertainty. The current PNG model has no water, vegetation, building, or land-cover classifier.
9. **Future:** A genuine licensed VV/VH→optical training run, verified geographic holdout, source/licence review, and phone/offline rehearsal remain future milestones.

## Safe answer if asked whether Vyora restores real colour

“No. The current checkpoint predicts pixels resembling paired A-side PNG targets from grayscale B-side PNG inputs. It is an early prototype, and the source/sensor semantics and geographic independence are not verified. The output is not true-colour ground truth or a decision product.”
