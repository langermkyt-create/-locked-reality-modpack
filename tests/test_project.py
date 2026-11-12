import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "kubejs/data/locked_reality"


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
        self.assertIn("yungs-better-dungeons", data["projects"])

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
            advancement = DATA / "advancements" / f"{planet}.json"
            function = DATA / "functions" / f"chapter_{planet}.mcfunction"
            data = json.loads(advancement.read_text(encoding="utf-8"))
            self.assertIn("minecraft:changed_dimension", data["criteria"]["arrive"]["trigger"])
            self.assertTrue(function.is_file())

    def test_quest_chain_json_and_reward_functions(self):
        quest_ids = ("moon_relics", "mars_core", "venus_filter", "mercury_seal", "glacio_key", "final_wither")
        for quest_id in quest_ids:
            advancement = DATA / "advancements/quests" / f"{quest_id}.json"
            data = json.loads(advancement.read_text(encoding="utf-8"))
            self.assertTrue(data.get("criteria"))
            self.assertTrue(data.get("requirements"))
            reward_function = data["rewards"]["function"].split(":", 1)[1]
            self.assertTrue((DATA / "functions" / f"{reward_function}.mcfunction").is_file())

    def test_all_advancement_parents_exist(self):
        for advancement in (DATA / "advancements").rglob("*.json"):
            data = json.loads(advancement.read_text(encoding="utf-8"))
            parent = data.get("parent")
            if parent and parent.startswith("locked_reality:"):
                relative = parent.split(":", 1)[1]
                self.assertTrue((DATA / "advancements" / f"{relative}.json").is_file(), parent)


if __name__ == "__main__":
    unittest.main()
