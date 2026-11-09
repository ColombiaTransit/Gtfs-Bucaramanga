#!/usr/bin/env python3
"""SITME-only GTFS foundation smoke tests; no OSM/network dependencies."""
import csv
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/'scripts'/'build_sitme_gtfs_base.py'
spec=importlib.util.spec_from_file_location('sitme_gtfs_base',SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class SITMEOnlyBaseTests(unittest.TestCase):
    def test_geofence_first_coordinate_matches_ui(self):
        location={'ID':'12','COORDINATES':[{'lat':7.1,'lng':-73.1},{'lat':7.15,'lng':-73.15}]}
        self.assertEqual((7.1,-73.1),mod.first_gps(location))
        self.assertNotEqual((7.125,-73.125),mod.first_gps(location))

    def test_user_confirmed_aliases_only(self):
        self.assertEqual(mod.ALIASES,{'150873':'150965','150877':'150969','163015':'163024'})
        self.assertIn({'150798','150973'},mod.DISTINCT)
        self.assertIn({'164171','164933'},mod.DISTINCT)

    def test_route_inventory_without_discontinued_services(self):
        self.assertEqual(len(mod.ROUTES),12)
        self.assertEqual('RD27/RD15',mod.ROUTES[3350])
        self.assertNotIn(3302,mod.ROUTES)
        self.assertNotIn(3317,mod.ROUTES)
        self.assertNotIn(3343,mod.ROUTES)

    def test_distance_nonnegative_and_utf8(self):
        self.assertAlmostEqual(0,mod.km((7,-73),(7,-73)))
        self.assertGreater(mod.km((7,-73),(7.01,-73)),1)
        self.assertEqual('00FF80',mod.rgb('#00ff80'))
        self.assertEqual('',mod.rgb('not-a-color'))

    def test_official_source_integration(self):
        snap=os.getenv('SITME_SNAPSHOT')
        root=os.getenv('SITME_WORKSPACE') or str(Path(__file__).resolve().parents[1])
        if not snap: self.skipTest('Set SITME_SNAPSHOT to the immutable source ZIP for full integration')
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            summary=mod.create(Path(snap),Path(root)/'data/sitme/stop_candidates_reconciled_2026-11-09.csv',
                               Path(root)/'data/sitme/route_stop_visits_reconciled_2026-11-09.csv',folder)
            self.assertEqual((summary['routes'],summary['stops'],summary['shape_points'],summary['stop_visits']),
                             (12,528,10699,950))
            self.assertFalse(summary['external_osm_used'])
            def read(path):
                with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
            stops=read(folder/'gtfs_base/stops.txt')
            shapes=read(folder/'gtfs_base/shapes.txt')
            visits=read(folder/'source_audit/route_stop_sequences.csv')
            mapping=read(folder/'source_audit/location_id_to_gtfs_stop_id.csv')
            ids={s['stop_id'] for s in stops}
            self.assertEqual(len(ids),528)
            self.assertEqual(len(mapping),531)
            self.assertTrue(all(v['stop_id'] in ids for v in visits))
            self.assertNotEqual(next(x['gtfs_stop_id'] for x in mapping if x['source_location_id']=='150798'),
                                next(x['gtfs_stop_id'] for x in mapping if x['source_location_id']=='150973'))
            self.assertNotEqual(next(x['gtfs_stop_id'] for x in mapping if x['source_location_id']=='164171'),
                                next(x['gtfs_stop_id'] for x in mapping if x['source_location_id']=='164933'))
            self.assertEqual(next(x['gtfs_stop_id'] for x in mapping if x['source_location_id']=='150873'),
                             next(x['gtfs_stop_id'] for x in mapping if x['source_location_id']=='150965'))
            self.assertEqual(len(shapes),10699)
            self.assertFalse((folder/'gtfs_base/stop_times.txt').exists())


if __name__=='__main__':unittest.main()