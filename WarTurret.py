class RotateState(object):

    @staticmethod
    def execute():
        if len(dico['targets']) > 0 and isReloaded():
            setDebugString("KILL")
            actionWarTurret.currentState = FireState

            for potential_target in dico['targets']:
                if potential_target.getDistance() < target.getDistance():
                    target = potential_target
            return FireState.execute()

        else:
            setDebugString("Je change d'angle")
            setHeading((getHeading() + 180) % 360)
            return idle()


class ReloadState(object):

    @staticmethod
    def execute():
        actionWarTurret.nextState = RotateState
        return reloadWeapon()


class FireState(object):

    @staticmethod
    def execute():
        setHeading(target.getAngle())
        setTargetDistance(target.getDistance())
        actionWarTurret.nextState = ReloadState
        return fire()


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
actionWarTurret.nextState = RotateState
actionWarTurret.currentState = None
