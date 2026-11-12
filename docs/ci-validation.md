# Проверка кампании перед сборкой

Этот файл фиксирует контрольный список для CI:
- все story advancement JSON должны разбираться;
- родительские advancement IDs должны существовать;
- у каждого задания должна существовать reward function;
- планетарные задачи должны быть привязаны к нужному измерению;
- Forge dedicated server должен загрузить KubeJS, Ad Astra, Cataclysm, YUNG's Better Dungeons и custom Mage Citadel dimension;
- финальная награда должна срабатывать только после смерти босса с тегом locked_reality_final_boss.

Полное ручное прохождение клиента всё равно требуется отдельно; успешный smoke test сервера не заменяет его.