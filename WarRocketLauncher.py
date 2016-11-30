from pprint import pprint
import sys
if "./teams/" not in sys.path:
    sys.path.append('./teams/')

from oktamer.utils import Trigo, Predict, Stats  # noqa

# =============================================================================#
# =============================================================================#
#                              Beginning
# =============================================================================#
# =============================================================================#
pprint(sys.path)
pprint(globals())
pprint(Stats.agent("WarRocketLauncher").SPEED)
pprint(Stats.projectile("WarRocket").SPEED)


def actionWarRocketLauncher():

    percepts = getPerceptsEnemies()

    for percept in percepts:
        if (percept.getType().equals(WarAgentType.WarRocketLauncher) or
                percept.getType().equals(WarAgentType.WarLight) or
                percept.getType().equals(WarAgentType.WarHeavy)):
            if isEnemy(percept):
                setDebugString("Mode hunter")
                collision = Predict.collision(
                    {'distance': percept.getDistance(),
                     'angle': percept.getAngle()},
                    {'distance': 0,
                     'angle': percept.getHeading()},
                    p.WarRocket.SPEED)
                setHeading(collision['angle'])

                if (isReloaded()):
                    setTargetDistance(collision['distance'])
                    return fire()
                else:
                    return reloadWeapon()
            else:
                setDebugString("No cible")

        elif percept.getType().equals(WarAgentType.WarBase):
            if isEnemy(percept):
                setDebugString("Mode hunter")
                setHeading(percept.getAngle())

                if isReloaded():
                    setTargetDistance(percept.getDistance())
                    return fire()
                else:
                    return reloadWeapon()
            else:
                setDebugString("No cible")
        else:
            setDebugString("No cible")

    if (len(percepts) == 0):
        setDebugString("No cible")

    if(isBlocked()):
        RandomHeading()

    return move()
