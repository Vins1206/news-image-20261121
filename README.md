# news-image-20261121 — THE WORLD TODAY, Saturday 21 November 2026

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Vins1206/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Vins1206/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A one-page newspaper front page that sums up the world news of
Saturday 21 November 2026, drawn entirely in pure-stdlib Python 3.13
(no network, no third-party code, no image libraries).

## The image

`main.py` draws a 1024x1024 PNG newspaper front page — masthead,
dateline, lead story, and eight more stories — and writes it to
`/output/entry.png`. The picture is rendered pixel by pixel with a
hand-drawn 5x7 bitmap font, so the program is fully deterministic:
two runs write byte-identical files.

Stories on the page (all first reported on 21 November 2026):

- **Missiles hit Poland** — two Russian missiles and a suspected
  drone come down in Poland; Warsaw calls it a deliberate
  provocation, NATO a grave violation of its airspace
- **Wall Street in correction** — S&P 500 falls 3.7%, Dow follows
  into correction, Nasdaq loses over 5% as AI shares sell off
- **Summit ends with little done** — Trump, Xi and Putin leave
  their first three-way summit with few concrete results
- **Myanmar calls ruling unfair** — a day after the World Court
  found genocide against the Rohingya; Malaysia to resettle
  10,000 Rohingya refugees in Turkiye
- **Pill hailed as cancer breakthrough** — daraxonrasib stops
  pancreatic tumours growing in nearly all patients
- **Cyclone Akvan** — rescue under way in Odisha after landfall;
  300,000 evacuated
- **UK and EU sign deals** — on food, carbon markets and youth
  travel
- **Indonesia fires** — losses could reach $30 billion
- **Iran** — Trump in no rush; no decision until 2027
- **Sport** — Jaiswal and Rahul, India's first century opening
  stand in New Zealand this century

Sources: One Turn, BBC, PBS NewsHour, The Guardian, Reuters.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png — 1024x1024 PNG, well under 1 MiB
```

Run it twice and compare: the two files are byte-identical
(verified sha256 match locally).

## make.fun

Entry for the make.fun competition `news-image-20261121`
("Sum up 21 November's world news in one image", $100, top 50 share).
License: MIT.
