# THE WORLD TODAY — Saturday 21 November 2026

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Vins1206/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Vins1206/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>

A one-page newspaper front page summing up the world's news of
**Saturday 21 November 2026**, drawn entirely by `main.py` — pure Python
standard library, no Pillow, no network, no image files. The program
rasterises the page with its own tiny drawing engine (rectangles, lines,
discs, polygons, starbursts) and its own hand-plotted 5×7 bitmap
letterforms, then encodes the PNG by hand.

## The day's stories on the page

- **Lead — Russian missiles land in Poland.** Two Russian missiles and a
  suspected drone came down inside Poland during an overnight attack on
  Ukraine. Warsaw called it a deliberate provocation; NATO called it a
  grave violation of allied airspace. Kyiv said Russia fired more than
  400 drones and 110 missiles, killing eight people.
- **UK and EU sign a landmark post-Brexit reset.** Food checks scrapped,
  carbon markets linked, 100,000 youth visas each way, Britain back in
  Erasmus.
- **A 6.8 earthquake shakes Peru.** The quake struck Junín in the central
  Andes; tremors were felt 320 km away in Lima. No casualties reported.
- **World Court: Myanmar committed genocide.** The International Court of
  Justice ruled Myanmar's forces committed state-sponsored genocide
  against the Rohingya; Myanmar called the ruling unfair.
- **Markets strip.** US stocks fell 3.7% as AI shares sold off and the
  S&P 500 entered correction territory; COP31 climate talks in Antalya
  entered their final stage.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png`: 1024×1024, well under the 1 MiB limit.
Two runs write byte-identical output (fixed text, fixed geometry, fixed
zlib level — no clock, no randomness, no network).

## Competition

[Sum up 21 November's world news in one image](https://make.fun/bounty/news-image-20261121)
— $100 shared by the top 50 entries. Deadline: 23 November 2026, 00:00 UTC.
