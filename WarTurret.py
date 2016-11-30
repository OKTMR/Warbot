class ObserveState(object):

    @staticmethod
    def execute():
        if len(dico['targets']) > 0 and isReloaded():
            setDebugString("Fire !!!")
            actionWarTurret.currentState = FireState

            for potential_target in dico['targets']:
                if potential_target.getDistance() < dico['targets'][0].getDistance():
                    dico['targets'][0] = potential_target
            return FireState.execute()

        else:
            setDebugString("Hold on to this position")
            setHeading((getHeading() + 90) % 360)
            setViewDirection((getHeading() + 90) % 360)
            return idle()

class ReloadState(object):

    @staticmethod
    def execute():
        setDebugString("Je recharge")
        actionWarTurret.nextState = ObserveState
        return reloadWeapon()


class FireState(object):

    @staticmethod
    def execute():
        setDebugString("Projectile lancé !!!")
        setHeading(dico['targets'][0].getAngle())
        setTargetDistance(dico['targets'][0].getDistance())
        actionWarTurret.nextState = ReloadState
        return fire()


def actionWarTurret():
    dico['targets'] = getPerceptsEnemies()
    print(dico['targets'])
    if actionWarTurret.nextState is not None:
        actionWarTurret.currentState = actionWarTurret.nextState
        actionWarTurret.nextState = None
    return actionWarTurret.currentState.execute()

# Initialisation des variables
dico = {}
actionWarTurret.nextState = ReloadState
actionWarTurret.currentState = None
