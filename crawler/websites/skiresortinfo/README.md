Fetch the list with all resorts

# How to run

All resorts:

```text
python3 websites/skiresortinfo/ski-resorts-list.py --pages 0
```

Specific region:

```text
python3 websites/skiresortinfo/ski-resorts-list.py https://www.skiresort.com/en/ski-resorts/alberta/ --pages 0
```

Whole country (all configured regions, see `COUNTRY_REGIONS`):

```text
python3 websites/skiresortinfo/ski-resorts-list.py canada --pages 0
```

Subset of a country's regions:

```text
python3 websites/skiresortinfo/ski-resorts-list.py canada --regions quebec ontario --pages 0
```

The scraper writes grouped files to:

```text
websites/skiresortinfo/[country]/[region]/ski-resorts-list.json
```

Each record includes `skiresortUrl` and `url` with the source resort page.

Create missing Convex registries and mountain SkiResort generators:

```text
python3 websites/skiresortinfo/create-mountain-crawlers.py websites/skiresortinfo/canada/alberta/ski-resorts-list.json
```