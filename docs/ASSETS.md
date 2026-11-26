# Visual assets and external references

## Interactive Earth globe

`frontend/public/assets/earth-land-dots.json` is a derived point grid from Natural Earth 1:110m land polygons distributed in the `world-atlas` package. It is used only to render a stylized interactive globe locally. It is **not satellite imagery, live geospatial data, a boundary product, or an analysis layer**. `world-atlas` is distributed under ISC terms; the underlying Natural Earth data is public domain.

The purple colour treatment and orbit lines are interface artwork. Their satellite-shaped markers do not represent named spacecraft or current orbital positions. Users who want real mission/position data can open the official external NASA Eyes 3D satellite tracker from the landing page. Vyora does not fetch or use that external data in its model runs.

## External Earth-observation references

- [NASA Eyes on the Earth](https://eyes.nasa.gov/apps/earth/#/satellites) — NASA's interactive satellite and Earth-science visualization.
- [GOES full-disk image animation](https://www.star.nesdis.noaa.gov/goes/fulldisk_band.php?sat=G19&band=GEOCOLOR&length=12) — an external NOAA animation of real GOES imagery; not embedded or streamed by Vyora.
- [NASA GOES spacecraft 3D model](https://science.nasa.gov/mission/goes-spacecraft-3d-model/) — reference for interactive spacecraft presentation.

These links leave the local Vyora app. They are references and must not be presented as Vyora outputs or live connections.
