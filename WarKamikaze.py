
def actionWarKamikaze():
    if isBlocked():
        RandomHeading()
        return move()

    for enemy in getPerceptsEnemies():
        if not (enemy.getType().equals(WarAgentType.WarFood)):
            return fire()

    return move()
