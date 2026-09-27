"""Migration acceptance tests: prevent losses, invented precision, and growth caps."""

from __future__ import annotations

import copy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from content_model import BASELINE, MIGRATION, ROOT, Document, digest, json_text, read_json
from migrate_content import capture_baseline, extract
from validate_content import validate_catalogs, validate_migration


class ContentMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="90s-land-content-")
        self.root = Path(self.temporary.name)
        for directory in (Path("data"), MIGRATION, BASELINE, Path("docs/design/references")):
            shutil.copytree(ROOT / directory, self.root / directory)
        (self.root / "assets").symlink_to(ROOT / "assets", target_is_directory=True)

    def tearDown(self):
        self.temporary.cleanup()

    def edit(self, relative, change):
        path = self.root / relative
        data = read_json(path)
        change(data)
        path.write_text(json_text(data), encoding="utf-8")

    def test_current_catalogs_and_frozen_import_are_valid(self):
        self.assertEqual(validate_catalogs(ROOT), [])
        self.assertEqual(validate_migration(ROOT), [])

    def test_unicode_entities_and_nested_markup_keep_exact_source_ranges(self):
        source = '<main id="main">é<p>A &amp; B <em>★</em></p><img src="x" /></main>'
        doc = Document(source)
        paragraph = doc.one(lambda node: node.tag == "p")
        self.assertEqual(doc.raw(paragraph), '<p>A &amp; B <em>★</em></p>')
        self.assertEqual(doc.text(paragraph), 'A & B ★')
        self.assertEqual(doc.raw(doc.one(lambda node: node.tag == "main")), source)

    def test_extraction_is_deterministic_and_does_not_use_live_page_copy(self):
        (self.root / "index.html").write_text("This later redesign is not import source.")
        for relative, expected in extract(self.root).items():
            self.assertEqual((ROOT / relative).read_text(encoding="utf-8"), expected)

    def test_baseline_cannot_be_recaptured(self):
        before = (self.root / BASELINE / "manifest.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "refusing to replace"):
            capture_baseline(self.root, "0" * 40, [])
        self.assertEqual((self.root / BASELINE / "manifest.json").read_bytes(), before)

    def test_new_artifacts_resources_and_featured_entries_are_allowed(self):
        def add_artifact(records):
            added = copy.deepcopy(records[0])
            added.update(id="new-preserved-growth-test", slug="new-preserved-growth-test")
            records.append(added)
        def add_resource(records):
            added = copy.deepcopy(records[0])
            added.update(id="new-resource-growth-test", url="https://example.org/new", featured=True)
            records.append(added)
        self.edit(Path("data/artifacts.json"), add_artifact)
        self.edit(Path("data/resources.json"), add_resource)
        self.assertEqual(validate_catalogs(self.root), [])

    def test_replacing_record_at_same_count_cannot_hide_loss(self):
        self.edit(Path("data/resources.json"), lambda records: records[0].update(id="replacement-id"))
        self.assertTrue(any("baseline IDs removed" in error for error in validate_catalogs(self.root)))

    def test_duplicate_ids_and_dangling_artifact_relationships_fail(self):
        self.edit(Path("data/artifacts.json"), lambda records: records.append(copy.deepcopy(records[0])))
        self.assertTrue(any("duplicate id" in error for error in validate_catalogs(self.root)))
        shutil.copy2(ROOT / "data/artifacts.json", self.root / "data/artifacts.json")
        self.edit(Path("data/artifacts.json"), lambda records: records[0].update(relatedArtifacts=["missing-object"]))
        self.assertTrue(any("unknown related artifact" in error for error in validate_catalogs(self.root)))

    def test_main_content_gaps_are_rejected_even_with_updated_hash(self):
        def corrupt(data):
            location = data["records"][0]["blocks"][0]["provenance"]
            location["start"] += 1
            source = (self.root / location["snapshot"]).read_text()
            location["sha256"] = digest(source[location["start"]:location["end"]])
        self.edit(MIGRATION / "pages.json", corrupt)
        self.assertTrue(any("gap or overlap" in error for error in validate_migration(self.root)))

    def test_missing_month_and_missing_inventory_disposition_fail(self):
        self.edit(MIGRATION / "months.json", lambda data: data["records"].pop())
        self.edit(MIGRATION / "inventory.json", lambda data: data["records"].pop())
        errors = validate_migration(self.root)
        self.assertTrue(any("month coverage differs" in error for error in errors))
        self.assertTrue(any("exactly one disposition" in error for error in errors))

    def test_month_context_cannot_be_promoted_to_exact_date_or_verified(self):
        self.edit(MIGRATION / "months.json", lambda data: data["records"][0].update(date="1990-01-01", datePrecision="day", verificationStatus="verified", publicationStatus="published"))
        errors = validate_migration(self.root)
        self.assertTrue(any("invent an exact event date" in error for error in errors))
        self.assertTrue(any("must remain unreviewed" in error for error in errors))
        self.assertTrue(any("must remain a draft" in error for error in errors))

    def test_annual_rank_scope_and_entity_relationships_are_checked(self):
        def corrupt(data):
            chart = data["records"][0]
            chart["scope"] = "weekly"
            chart["entries"][1].update(rank=1, entityId="missing-song")
        self.edit(MIGRATION / "charts.json", corrupt)
        errors = validate_migration(self.root)
        self.assertTrue(any("annual scope" in error for error in errors))
        self.assertTrue(any("ordered and unique" in error for error in errors))
        self.assertTrue(any("unknown song entity" in error for error in errors))

    def test_missing_anchor_and_unknown_source_are_rejected(self):
        self.edit(MIGRATION / "legacy-links.json", lambda data: data["records"].pop())
        self.edit(MIGRATION / "months.json", lambda data: data["records"][0].update(sourceIds=["missing-source"]))
        errors = validate_migration(self.root)
        self.assertTrue(any("baseline anchors" in error for error in errors))
        self.assertTrue(any("unknown source" in error for error in errors))

    def test_snapshot_corruption_is_detected(self):
        path = self.root / BASELINE / "pages/home.html.txt"
        path.write_text(path.read_text().replace("playable museum", "different museum", 1))
        self.assertTrue(any("Snapshot changed" in error for error in validate_migration(self.root)))

    def test_unsupported_import_schema_is_reported(self):
        self.edit(MIGRATION / "years.json", lambda data: data.update(schemaVersion=2))
        self.assertTrue(any("unsupported schemaVersion" in error for error in validate_migration(self.root)))


if __name__ == "__main__":
    unittest.main()
