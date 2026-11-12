tellraw @s {"text":"ИСПЫТАНИЕ ПРОЙДЕНО: Страж Края","color":"gold","bold":true}
tellraw @s {"text":"Страж пал. Его ядро открывает путь в искусственный мир мага — Цитадель.","color":"dark_purple"}
give @s minecraft:amethyst_shard 2
execute in locked_reality:mage_citadel run tp @s 0 63 -12 0 0
execute in locked_reality:mage_citadel run function locked_reality:build_citadel
tellraw @s {"text":"Ты вошёл в Цитадель. В центре арены пробуждается Архитектор.","color":"light_purple","bold":true}
execute in locked_reality:mage_citadel run summon minecraft:wither 0 66 0 {Tags:["locked_reality_final_boss"],CustomName:'{"text":"Маг — Архитектор","color":"dark_purple","bold":true}',CustomNameVisible:1b,Health:600.0f,Attributes:[{Name:"generic.max_health",Base:600.0d},{Name:"generic.attack_damage",Base:18.0d}]}
