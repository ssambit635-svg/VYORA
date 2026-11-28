# Visual assets and external references

## Landing-page 3D Earth and spacecraft

- `earth-day.webp`, `earth-night.webp`, and `earth-clouds.webp` are compressed/resized landing-page textures derived from the Solar System Scope Earth day/night/cloud maps, distributed as part of [`forest0xia/openglobes-space`](https://github.com/forest0xia/openglobes-space). That repository credits the Earth maps to Solar System Scope via Wikimedia Commons under CC BY 4.0. Vyora keeps the textures local; the scene makes no texture-service requests.
- `nasa-goes.glb` and `nasa-landsat8.glb` are optimized NASA spacecraft models distributed by [`forest0xia/openglobes-space`](https://github.com/forest0xia/openglobes-space), whose repository is Apache-2.0. The source models are credited to NASA 3D Resources and are described there as public-domain NASA models.
- Three.js and its bundled Meshopt decoder render the local models. The GLB geometry was converted to `EXT_meshopt_compression` for faster local delivery; source licenses remain with their respective upstream assets and packages.

The spacecraft models move along **illustrative, not-to-scale paths**. Vyora does not claim their rendered positions match current orbits, nor does the landing scene fetch live satellite tracking data. For real mission/position data, users can open the separate NASA Eyes tracker; it is not connected to Vyora runs.

## External Earth-observation references

- [NASA Eyes on the Earth](https://eyes.nasa.gov/apps/earth/#/satellites) — NASA's interactive satellite and Earth-science visualization.
- [GOES full-disk image animation](https://www.star.nesdis.noaa.gov/goes/fulldisk_band.php?sat=G19&band=GEOCOLOR&length=12) — an external NOAA animation of real GOES imagery; not embedded or streamed by Vyora.
- [NASA GOES spacecraft 3D model](https://science.nasa.gov/mission/goes-spacecraft-3d-model/) — reference for interactive spacecraft presentation.

These links leave the local Vyora app. They are references and must not be presented as Vyora outputs or live connections.
