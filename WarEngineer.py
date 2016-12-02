


def actionWarEngineer():

    if not dico['turret_made']:
        dico['messages'] = getMessages()
        dico['messages_turrets'] = []
        minDistanceTurret = None

        for message in dico['messages']:
            if message.getMessage() == 'turret':
                dico['messages_turrets'].append(message)
                if (minDistanceTurret is None or
                    minDistanceTurret > message.getDistance()):
                    minDistanceTurret = message.getDistance()

        if minDistanceTurret is not None and minDistanceTurret > 50 :
            dico['turret_made'] = True
            setNextBuildingToBuild(WarAgentType.WarTurret)
            return build()

        if isBlocked():
            RandomHeading()

        return move()
    else:
        perceptsBase = getPerceptsAlliesByType(WarAgentType.WarBase)
        baseDistance = None
        if getHealth() < 10:
            return "die"

        if isBlocked():
            RandomHeading()
            return move()

        if len(perceptsBase) > 0:
            baseAngle = perceptsBase[0].getAngle()
            baseId = perceptsBase[0].getID()
            baseDistance = perceptsBase[0].getDistance()
        if baseDistance is None:
            for message in getMessages():
                if (message.getSenderType() == WarAgentType.WarBase and
                        message.getMessage() == 'base'):
                    baseAngle = message.getAngle()
                    baseId = message.getSenderID()
                    baseDistance = message.getDistance()

        if baseDistance is not None:
            if baseDistance > maxDistanceGive():
                setHeading(baseAngle)
                return move()
            else:
                setIdNextBuildingToRepair(baseId)
                return WA.repair()
        else:
            return idle()


dico = {}
dico['turret_made'] = False
