#!/usr/bin/env python3
"""Standard-library unit tests for conservative matching and immutable stop identity."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1]/'scripts'/'audit_sitme_osm_stop_positions.py'
spec=importlib.util.spec_from_file_location('sitme_stop_audit',SCRIPT)
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class MatchingAndRouteTests(unittest.TestCase):
    def test_direction_is_different(self):
        self.assertEqual('S-N',audit.direction('San Carlos S-n'))
        self.assertEqual('N-S',audit.direction('San Carlos N-s'))
        self.assertNotEqual(audit.direction('San Carlos S-n'),audit.direction('San Carlos N-s'))
        self.assertFalse(audit.direction('Portal del Valle'))

    def test_user_confirmed_stop_identity(self):
        self.assertEqual({'150873':'150965','150877':'150969','163015':'163024'},audit.ALIAS)
        self.assertIn(frozenset(('150798','150973')),audit.NEVER_MERGE)
        self.assertIn(frozenset(('164171','164933')),audit.NEVER_MERGE)

    def test_geodesic_distance(self):
        self.assertAlmostEqual(111, audit.meters((7.0,-73.0),(7.001,-73.0)),delta=2)

    def test_projected_relative_side(self):
        # Northward travel: east is right; west is left.
        _, _, cross_east=audit.project_segment((7.0005,-72.9999),(7.0,-73.0),(7.001,-73.0))
        _, _, cross_west=audit.project_segment((7.0005,-73.0001),(7.0,-73.0),(7.001,-73.0))
        self.assertLess(cross_east,0)
        self.assertGreater(cross_west,0)

    def test_osm_platform_vs_stop_position(self):
        data={'elements':[{'type':'node','id':5,'lat':7,'lon':-73,
                           'tags':{'public_transport':'stop_position','name':'A'}},
                          {'type':'node','id':6,'lat':7.001,'lon':-73,
                           'tags':{'highway':'bus_stop','name':'B'}}]}
        parsed=audit.parse_stops(data)
        self.assertEqual(['stop_position','platform'],[x['kind'] for x in parsed])

    def test_exact_matching_not_automatic_gtfs_approval(self):
        osm={'kind':'platform'}
        cat,reason,boarding=audit.determine_category({},osm,4,0.97,'',['right_of_travel'])
        self.assertEqual('A_strong_candidate',cat)
        cat2,_,_=audit.determine_category({},osm,4,0.97,'direction_label_conflict',[])
        self.assertTrue(cat2.startswith('C_'))

    def test_nearby_distinct_stops_remain_two_ids(self):
        for ids in audit.NEVER_MERGE:
            self.assertTrue(all(audit.ALIAS.get(x,x)==x for x in ids))


if __name__=='__main__':unittest.main()
