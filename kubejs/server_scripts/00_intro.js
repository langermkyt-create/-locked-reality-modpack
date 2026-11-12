// Locked Reality: first playable story hook.
// KubeJS 6 server event; deliberately uses vanilla commands/text only.
PlayerEvents.loggedIn(event => {
  event.player.tell("§5§lЗАПЕРТАЯ РЕАЛЬНОСТЬ");
  event.player.tell("§7Ты очнулся в мире, которого не должно существовать.");
  event.player.tell("§7Найди следы мага и выясни, как открыть путь между мирами.");
  event.player.tell("§8Сюжетные главы и новые планеты будут открываться по мере прохождения.");
});
