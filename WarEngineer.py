from pprint import pprint


def actionWarEngineer():
    dico = getPerceptsAlliesByType(WarAgentType.WarBase)
    baseDistance = None
    if getHealth() < 20:
        return "die"

    if isBlocked():
        RandomHeading()
        return move()

    if len(dico) > 0:
        baseAngle = dico[0].getAngle()
        baseId = dico[0].getID()
        baseDistance = dico[0].getDistance()
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
