# SITME / Metrolínea operating-service source register

Research date: 2026-11-07. Distinguish **publication date** from **currently verified operation**. Do not silently extrapolate peak periods or use historical notices as current GTFS facts.

| Route | Service day | First departure | Last departure | Headway | Primary source date | Verification |
|---|---|---|---|---|---|---|
| P19 | Weekday | 04:48 | 19:30 | peak 10–12 min; off-peak 15 min | 2026-08-31 | Published, precise peak windows missing |
| P19 | Saturday | 05:00 | 18:30 | peak 10–12 min; off-peak 15 min | 2026-08-31 | Published, precise peak windows missing |
| P19 | Sunday/holiday | 06:00 | 17:30 | 10, 12 or 15 min depending on time band | 2026-08-31 | Published, time bands missing |
| P16N | Mon–Sun | 04:20 | 19:30 | 12 min | 2025-07-30 | Historical announcement, current status unverified |
| P16S | Mon–Sun | 04:20 | 19:30 | 12 min | 2025-07-30 | Historical announcement, current status unverified |
| PTB | Weekday | 05:00 | 22:00 | 10 min | 2026-04-07 | Historical; subsequent suspension reported, DO NOT publish as active |
| PTB | Saturday | 05:00 | 21:00 | 15 min | 2026-04-07 | Historical; DO NOT publish as active |
| PTB | Sunday/holiday | 05:30 | 20:00 | 25 min | 2026-04-07 | Historical; DO NOT publish as active |

## Last departures at major stations, NOT route-specific
Official announcement dated 2026-08-03, effective 2026-08-04, weekdays:
- Portal del Norte 21:30
- Parque Estación UIS 21:50
- Provenza Occidental 22:10
- Portal de Piedecuesta 22:40

## Source links
- P19 route geometry in both directions, payment operator Transcolombia, service windows and headways: https://www.bucaramanga.gov.co/noticias/ruta-complementaria-p19-incorpora-nuevos-medios-de-pago-y-fortalece/
- P16N/P16S detailed routing, 12 vehicles each, 12-min frequency: https://www.metrolinea.gov.co/v3.0/node/2232
- PTB original announcement and detailed path (historical only): https://www.bucaramanga.gov.co/noticias/sitme-pone-en-operacion-la-nueva-ruta-ptb-eje-estrategico-de-la-movilidad-en-bucaramanga/
- Official last-departure station announcement: https://dev.metrolinea.gov.co/v3.0/sitme-normaliza-sus-horarios-de-operacion-desde-este-martes-4-de-agosto-2296
- Official route/hour news index (contains older announcements): https://www.metrolinea.gov.co/v3.0/horario-rutas
- Official 2025 management report: https://www.metrolinea.gov.co/v3.0/sites/default/files/informe_gestion_anual_consolidado_2025_compressed.pdf
- 2024 service redesign (historical only): https://www.metrolinea.gov.co/v3.0/node/2168

## GTFS cautions
- P19 peak/off-peak windows are not specified: preserve headway ranges in research data, **do not fabricate frequencies.txt exact_secs or time bands**.
- P16N/S 2025 publication is not evidence that these routes operate unchanged in November 2026.
- PTB is historical; independently verify later termination/route replacement before deciding active status.
- Station departure times are not necessarily a route's first/last terminal dispatch.
- Route geometry and stop order require spatial/field validation.
