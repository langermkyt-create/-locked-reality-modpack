execute in locked_reality:mage_citadel positioned 0 64 0 if entity @e[type=minecraft:wither,tag=locked_reality_final_boss,limit=1] run bossbar set locked_reality:architect players @a[distance=..128]
execute in locked_reality:mage_citadel as @e[type=minecraft:wither,tag=locked_reality_final_boss,limit=1] store result bossbar locked_reality:architect value run data get entity @s Health 1
