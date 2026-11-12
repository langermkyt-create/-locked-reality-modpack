bossbar set locked_reality:architect visible false
tellraw @s {"text":"ФИНАЛ: Архитектор повержен","color":"light_purple","bold":true}
tellraw @s {"text":"Последняя печать разрушена. Искусственная реальность больше не удерживает тебя.","color":"gold"}
tellraw @s {"text":"Ты нашёл яйцо дракона — знак того, что путь домой открыт. История текущей версии завершена.","color":"gray"}
give @s minecraft:dragon_egg 1
