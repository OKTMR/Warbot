from math import *

# =============================================================================#
# =============================================================================#
#                                   Trigo
# =============================================================================#
# =============================================================================#


class Trigo(object):

    @staticmethod
    def getCarthesianTarget(carthesianSender, carthesianObjective):
        return {'x': carthesianSender['x'] + carthesianObjective['x'],
                'y': carthesianSender['y'] + carthesianObjective['y']}

    @staticmethod
    def getPolarTarget(polarSender, polarObjective):
        carthesianTarget = Trigo.getCarthesianTarget(
            Trigo.toCarthesian(polarSender),
            Trigo.toCarthesian(polarObjective))

        return Trigo.toPolar(carthesianTarget)

    @staticmethod
    def getPolarFromMessage(message):
        polarA = {'distance': float(message.getDistance()),
                  'angle': float(message.getAngle())}

        polarO = {'distance': float(message.getContent()[0]),
                  'angle': float(message.getContent()[1])}
        return Trigo.getPolarTarget(polarA, polarO)

    @staticmethod
    def toCarthesian(polar):
        return {'x': polar['distance'] * cos(radians(polar['angle'])),
                'y': polar['distance'] * sin(radians(polar['angle']))}

    @staticmethod
    def toPolar(carthesian):
        return {'distance': hypot(carthesian['x'], carthesian['y']),
                'angle': (degrees(atan2(carthesian['y'], carthesian['x'])) +
                          360) % 360}

    @staticmethod
    def roundCoordinates(carthesian):
        carthesian['x'] = Trigo.myfloor(carthesian['x'])
        carthesian['y'] = Trigo.myfloor(carthesian['y'])
        return carthesian

    @staticmethod
    def myfloor(x):
        return int(5 * round(float(x) / 5))

    @staticmethod
    def diffAngle(firstAngle, secondAngle):
        return abs((firstAngle - secondAngle + 180 + 360) % 360 - 180)

    @staticmethod
    def inView(viewAngle, angleOfView, targetAngle):
        return Trigo.diffAngle(viewAngle, targetAngle) < (angleOfView / 2)

# =============================================================================#
# =============================================================================#
#                                   Predict
# =============================================================================#
# =============================================================================#


class Predict(object):

    @staticmethod
    def redefAngle(angleFromOrigin, polar):
        polar['angle'] = (polar['angle'] + (360 - angleFromOrigin)) % 360
        return polar

    @staticmethod
    def collision(targetPos, targetHeading, mySpeed):
        targetHeading = Predict.redefAngle(
            (targetPos['angle'] + 270) % 360, targetHeading)
        targetVector = Trigo.toCarthesian(targetHeading)

        valueY = sqrt(pow(mySpeed, 2) - pow(targetVector['x'], 2))
        collisionTime = targetPos['distance'] / (valueY + targetVector['y'])

        relativeAngle = (degrees(atan2(valueY, targetVector['x'])) + 360) % 360
        relativeCollision = {'distance': mySpeed *
                             collisionTime, 'angle': relativeAngle}

        return Predict.redefAngle(-(targetPos['angle'] + 270) % 360,
                                  relativeCollision)


# =============================================================================#
# =============================================================================#
#                              Beginning
# =============================================================================#
# =============================================================================#


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
