from math import *
import edu.warbot.agents.agents as a
import edu.warbot.agents.projectiles as p


# =============================================================================#
# =============================================================================#
#                                   Stats
# =============================================================================#
# =============================================================================#


class Stats(object):

    @staticmethod
    def agent(agent):
        return getattr(a, str(agent))

    @staticmethod
    def projectile(projectile):
        return getattr(p, str(projectile))

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
    def getPolarAgentFromMessage(message):
        agent = Trigo.getPolarFromMessage(message)
        agent['heading'] = (float(message.getContent()[2]) + 360) % 360
        agent['type'] = str(message.getContent()[3])
        return agent

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
        targetPos = Trigo.getPolarTarget(targetPos, targetHeading)
        targetHeading = Predict.redefAngle(
            (targetPos['angle'] + 270) % 360, targetHeading)
        targetVector = Trigo.toCarthesian(targetHeading)

        valueY = sqrt(pow(mySpeed, 2) - pow(targetVector['x'], 2))
        collisionTime = targetPos['distance'] / \
            (valueY + targetVector['y'])

        relativeAngle = (degrees(atan2(valueY, targetVector['x'])) + 360) % 360
        relativeCollision = {'distance': mySpeed * collisionTime,
                             'angle': relativeAngle}

        return Predict.redefAngle(-(targetPos['angle'] + 270) % 360,
                                  relativeCollision)

# =============================================================================#
# =============================================================================#
#                                   States
# =============================================================================#
# =============================================================================#


class ObserveState(object):

    @staticmethod
    def execute():

        if isReloaded():
            if len(dico['targets']) > 0:
                setDebugString('Fire !!!')
                dico['target'] = dico['targets'][0]

                for potentTarget in dico['targets']:
                    if (potentTarget['distance'] < dico['target']['distance']):
                        dico['target'] = potentTarget

                return FireState.execute()
            elif len(dico['messages_enemies']) > 0:
                nearestCollision = None
                setDebugString('Fire !!!')

                for potentTarget in dico['messages_enemies']:
                    collision = Predict.collision(
                        potentTarget,
                        {'distance': Stats.agent(potentTarget['type']).SPEED,
                         'angle': potentTarget['heading']},
                        Stats.projectile('WarShell').SPEED)

                    if(nearestCollision is None or
                       nearestCollision > collision['distance']):
                        nearestCollision = collision['distance']
                        dico['target'] = potentTarget

                if(nearestCollision <
                   Stats.projectile('WarShell').RANGE):
                    return FireState.execute()

        setDebugString('Hold on to this position')
        setHeading((getHeading() + 90) % 360)

        if not isReloaded():
            return ReloadState.execute()
        else:
            return idle()


class ReloadState(object):

    @staticmethod
    def execute():
        setDebugString('Je recharge')
        if isReloaded():
            actionWarTurret.nextState = ObserveState

        return reloadWeapon()


class FireState(object):

    @staticmethod
    def execute():
        setDebugString('Projectile lancé !!!')
        collision = Predict.collision(
            dico['target'],
            {'distance': Stats.agent(dico['target']['type']).SPEED,
             'angle': dico['target']['heading']},
            Stats.projectile('WarShell').SPEED)

        setHeading(collision['angle'])
        actionWarTurret.nextState = ReloadState
        return fire()


def actionWarTurret():
    dico['percepts'] = []
    dico['percepts_enemies'] = []
    dico['percepts_alliesBase'] = []
    dico['percepts_ressources'] = []

    dico['targets'] = []

    dico['percepts'] = getPercepts()
    dico['percepts_enemies'] = getPerceptsEnemies()
    dico['percepts_alliesBase'] = getPerceptsAlliesByType(WarAgentType.WarBase)

    dico['messages_enemies'] = []
    # percept ressources
    for percept in dico['percepts']:
        if percept.getType().equals(WarAgentType.WarFood):
            dico['percepts_ressources'].append(percept)

    for ressource in dico['percepts_ressources']:
        broadcastMessageToAgentType(WarAgentType.WarBase, 'food', [
                                    str(ressource.getDistance()),
                                    str(ressource.getAngle())])

    # percept enemies
    for enemy in dico['percepts_enemies']:
        broadcastMessageToAgentType(WarAgentType.WarBase, 'enemyFound', [
                                    str(enemy.getDistance()),
                                    str(enemy.getAngle()),
                                    str(enemy.getHeading()),
                                    str(enemy.getType())])

    dico['messages'] = getMessages()

    for percept_target in dico['percepts_enemies']:
        dico['targets'].append(
            {'distance': percept_target.getDistance(),
             'angle': percept_target.getAngle(),
             'heading': percept_target.getHeading(),
             'type': percept_target.getType()}
        )

    for message in dico['messages']:
        if (message.getSenderType() == WarAgentType.WarBase and
                message.getMessage() == 'enemy'):
            enemy = Trigo.getPolarAgentFromMessage(message)

            if(enemy['distance'] <= Stats.projectile('WarShell').RANGE * 2):
                dico['messages_enemies'].append(enemy)

    if actionWarTurret.nextState is not None:
        actionWarTurret.currentState = actionWarTurret.nextState
        actionWarTurret.nextState = None
    return actionWarTurret.currentState.execute()

# Initialisation des variables
dico = {}
actionWarTurret.nextState = ObserveState
actionWarTurret.currentState = None
