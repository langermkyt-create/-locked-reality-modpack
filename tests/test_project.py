import json, pathlib, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]

class ProjectTests(unittest.TestCase):
    def test_pack_manifest(self):
        data = json.loads((ROOT / "pack/pack.json").read_text(encoding="utf-8"))
        self.assertEqual(data["minecraft"], "1.20.1")
        self.assertEqual(data["loader"], "forge")
        self.assertEqual(data["java"], 17)

    def test_mod_selection(self):
        data = json.loads((ROOT / "pack/mods.json").read_text(encoding="utf-8"))
        self.assertIn("ad-astra", data["projects"])
        self.assertIn("kubejs", data["projects"])

    def test_story_has_five_chapters(self):
        data = json.loads((ROOT / "quests/story.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["chapters"]), 5)
        self.assertGreaterEqual(data["target_hours"][0], 20)
        self.assertLessEqual(data["target_hours"][1], 30)

    def test_intro_script_exists(self):
        self.assertTrue((ROOT / "kubejs/server_scripts/00_intro.js").is_file())

    def test_planet_chapter_advancements(self):
        planets = ("moon", "mars", "venus", "mercury", "glacio")
        for planet in planets:
            advancement = ROOT / "kubejs/data/locked_reality/advancements" / f"{planet}.json"
            function = ROOT / "kubejs/data/locked_reality/functions" / f"chapter_{planet}.mcfunction"
            data = json.loads(advancement.read_text(encoding="utf-8"))
            self.assertIn("minecraft:changed_dimension", data["criteria"]["arrive"]["trigger"])
            self.assertTrue(function.is_file())

if __name__ == "__main__":
    unittest.main()
