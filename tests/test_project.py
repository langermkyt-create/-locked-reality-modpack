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
        self.assertIn("l_enders-cataclysm", data["projects"])

    def test_story_has_five_chapters(self):
        data = json.loads((ROOT / "quests/story.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["chapters"]), 5)
        self.assertGreaterEqual(data["target_hours"][0], 20)
        self.assertLessEqual(data["target_hours"][1], 30)

    def test_intro_script_exists(self):
        self.assertTrue((ROOT / "kubejs/server_scripts/00_intro.js").is_file())

    def test_story_has_one_visible_advancement_root(self):
        root = json.loads((DATA / "advancements/story.json").read_text(encoding="utf-8"))
        self.assertEqual(root["criteria"]["awakened"]["trigger"], "minecraft:tick")
        moon = json.loads((DATA / "advancements/moon.json").read_text(encoding="utf-8"))
        self.assertEqual(moon["parent"], "locked_reality:story")

    def test_planet_chapter_advancements(self):
        planets = ("moon", "mars", "venus", "mercury", "glacio")
        for planet in planets:
            advancement = DATA / "advancements" / f"{planet}.json"
            function = DATA / "functions" / f"chapter_{planet}.mcfunction"
            data = json.loads(advancement.read_text(encoding="utf-8"))
            self.assertIn("minecraft:changed_dimension", data["criteria"]["arrive"]["trigger"])
            self.assertTrue(function.is_file())

    def test_quest_chain_json_and_reward_functions(self):
        quest_ids = ("moon_relics", "mars_core", "harbinger", "venus_filter", "mercury_seal", "ignis", "glacio_key", "ender_guardian", "final_wither", "planet_globes/moon_globe", "planet_globes/mars_globe", "planet_globes/venus_globe", "planet_globes/mercury_globe", "planet_globes/glacio_globe")
        for quest_id in quest_ids:
            advancement = DATA / "advancements/quests" / f"{quest_id}.json"
            data = json.loads(advancement.read_text(encoding="utf-8"))
            self.assertTrue(data.get("criteria"))
            self.assertTrue(data.get("requirements"))
            reward_function = data["rewards"]["function"].split(":", 1)[1]
            self.assertTrue((DATA / "functions" / f"{reward_function}.mcfunction").is_file())

    def test_bosses_gate_later_planetary_chapters(self):
        expected = {
            "venus_filter": ("locked_reality:quests/harbinger", 5),
            "mercury_seal": ("locked_reality:quests/venus_filter", 7),
            "glacio_key": ("locked_reality:quests/ignis", 11),
            "final_wither": ("locked_reality:quests/ender_guardian", None),
        }
        for quest_id, (parent, fragment_count) in expected.items():
            data = json.loads((DATA / "advancements/quests" / f"{quest_id}.json").read_text(encoding="utf-8"))
            self.assertEqual(data["parent"], parent)
            if fragment_count is not None:
                self.assertEqual(data["criteria"]["relic"]["conditions"]["items"][0]["count"]["min"], fragment_count)

    def test_objectives_are_dimension_specific(self):
        dimensions = {
            "moon_relics": "ad_astra:moon",
            "mars_core": "ad_astra:mars",
            "venus_filter": "ad_astra:venus",
            "mercury_seal": "ad_astra:mercury",
            "glacio_key": "ad_astra:glacio",
            "harbinger": "minecraft:overworld",
            "ignis": "minecraft:the_nether",
            "ender_guardian": "minecraft:the_end",
            "planet_globes/moon_globe": "ad_astra:moon",
            "planet_globes/mars_globe": "ad_astra:mars",
            "planet_globes/venus_globe": "ad_astra:venus",
            "planet_globes/mercury_globe": "ad_astra:mercury",
            "planet_globes/glacio_globe": "ad_astra:glacio",
        }
        for quest_id, dimension in dimensions.items():
            data = json.loads((DATA / "advancements/quests" / f"{quest_id}.json").read_text(encoding="utf-8"))
            for criterion in data["criteria"].values():
                self.assertEqual(criterion["conditions"]["player"]["location"]["dimension"], dimension)

    def test_mage_citadel_dimension_and_final_boss(self):
        dimension = json.loads((DATA / "dimension/mage_citadel.json").read_text(encoding="utf-8"))
        self.assertEqual(dimension["type"], "minecraft:the_end")
        self.assertEqual(dimension["generator"]["type"], "minecraft:flat")
        arena = (DATA / "functions/build_citadel.mcfunction").read_text(encoding="utf-8")
        self.assertIn("minecraft:polished_blackstone_bricks", arena)
        boss_spawn = (DATA / "functions/quest_ender_guardian.mcfunction").read_text(encoding="utf-8")
        self.assertIn("locked_reality:mage_citadel", boss_spawn)
        self.assertIn("locked_reality_final_boss", boss_spawn)
        finale = json.loads((DATA / "advancements/quests/final_wither.json").read_text(encoding="utf-8"))
        self.assertIn("locked_reality_final_boss", finale["criteria"]["defeat_architect"]["conditions"]["entity"]["nbt"])

    def test_smoke_test_checks_advancement_load_errors(self):
        smoke = (ROOT / "tests/smoke_server.py").read_text(encoding="utf-8")
        self.assertIn("Parsing error loading custom advancement locked_reality:", smoke)
        self.assertIn("Couldn't load advancement locked_reality:", smoke)

    def test_all_advancement_parents_exist(self):
        for advancement in (DATA / "advancements").rglob("*.json"):
            data = json.loads(advancement.read_text(encoding="utf-8"))
            parent = data.get("parent")
            if parent and parent.startswith("locked_reality:"):
                relative = parent.split(":", 1)[1]
                self.assertTrue((DATA / "advancements" / f"{relative}.json").is_file(), parent)


if __name__ == "__main__":
    unittest.main()
