from sym.modules.discovery.crawlers.scrape_utils import tag_article

title = "DC POLICE'S SURPRISING SOLUTION TO CAR ROBBERIES"
body = """The DC police are combatting the rise in car robberies by offering free Apple AirTags to residents in certain areas, following a similar initiative by New York mayor Eric Adams.
The AirTag, a coin-sized device that can be traced via Apple devices, won't prevent vehicle theft but could aid in recovery and potentially deter future thefts."""

for t in tag_article(title=title, body_text=body):
    print(t)

