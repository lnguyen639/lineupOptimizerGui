from pydfs_lineup_optimizer import get_optimizer, Site, Sport


optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
optimizer.load_players_from_CSV("/DK.csv")
player_to_lock = optimizer.get_player_by_name('LeBron James')
player_to_lock.max_exposure=0.3
optimizer.add_player_to_lineup(player_to_lock)
for lineup in optimizer.optimize(n=3):
    print(lineup)

