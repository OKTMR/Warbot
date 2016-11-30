class SearchState(object):

    @staticmethod
    def execute():
        if isReloading():
            setDebugString("Je recharge")
            actionWarTurret.currentState = ReloadingState
            return ReloadingState.execute()
        if !isReloaded():
            setDebugString("Je dois rechager")
            actionWarTurret.currentState = ReloadState
            return ReloadState.execute()
        elif len(dico['targets']) != 0:
            setDebugString("KILL")
            actionWarTurret.currentState = FireState
            if len(dico['targets']) > 1:
                for potential_target in dico['targets']:
                    if potential_target.getDistance() < target.getDistance():
                        target = potential_target
                return FireState.execute()
            else:
                return FireState.execute()
        else:
            setDebugString("Je change d'angle")
            actionWarTurret.currentState = RotateState
            return RotateState.execute()


class ReloadingState(object):

    @staticmethod
    def execute():
        if isReloading():
            return ReloadingState.execute()
        else:
            actionWarTurret.currentState = SearchState
            return SearchState.execute()


class ReloadState(object):

    @staticmethod
    def execute():
        actionWarTurret.nextState = SearchState
        return reloadWeapon()


class FireState(object):

    @staticmethod
    def execute():
        setHeading(target.getAngle())
        setTargetDistance(target.getDistance())
        return fire()


class RotateState(object):

    @staticmethod
    def execute():
        currentAngle = getHeading()
        currentAngle += 90
        if currentAngle >= 360:
            currentAngle = currentAngle - 360
        setHeading(currentAngle)
        actionWarTurret.currentState = SearchState
        return SearchState.execute()


def actionWarTurret():
    dico['targets'] = getPerceptsEnemies()
    if len(dico['targets']) != 0:
        target = dico['targets'][0]
    if actionWarTurret.nextState is not None:
        actionWarTurret.currentState = actionWarTurret.nextState
        actionWarTurret.nextState = None
    return actionWarTurret.currentState.execute()

# Initialisation des variables
dico = {}
target = None
actionWarTurret.nextState = SearchState
actionWarTurret.currentState = None
