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
    def getCarthesianFromMessage(message):
        carthesianA = Trigo.toCarthesian(
            {'distance': float(message.getDistance()),
             'angle': float(message.getAngle())})

        carthesianO = {'x': float(message.getContent()[0]),
                       'y': float(message.getContent()[1])}
        return Trigo.getCarthesianTarget(carthesianA, carthesianO)

    @staticmethod
    def getPolarAgentFromMessage(message):
        agent = Trigo.getPolarFromMessage(message)
        agent['heading'] = (float(message.getContent()[2]) + 360) % 360
        agent['type'] = str(message.getContent()[3])
        agent['id'] = str(message.getContent()[4])
        return agent

    @staticmethod
    def getCarthesianAgentFromMessage(message):
        agent = Trigo.getCarthesianFromMessage(message)
        agent['heading'] = (float(message.getContent()[2]) + 360) % 360
        agent['type'] = str(message.getContent()[3])
        agent['id'] = str(message.getContent()[4])
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
        # pas encore sur si vraiment utile ....
        targetPos = Trigo.getPolarTarget(targetPos, targetHeading)
        targetHeading = Predict.redefAngle(
            (targetPos['angle'] + 270) % 360, targetHeading)
        targetVector = Trigo.toCarthesian(targetHeading)

        valueY = sqrt(pow(mySpeed, 2) - pow(targetVector['x'], 2))
        collisionTime = targetPos['distance'] / \
            (valueY + targetVector['y'])

        relativeAngle = (degrees(atan2(valueY, targetVector['x'])) + 360) % 360
        relativeCollision = {'distance': mySpeed *
                             collisionTime, 'angle': relativeAngle}

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
        setDebugString('Hold on to this position')
        setHeading((getHeading() + 179) % 360)

        if not isReloaded():
            setDebugString('Je recharge')
            return reloadWeapon()
        else:
            return idle()


class FireState(object):

    @staticmethod
    def execute():
        setDebugString('Projectile lancé !!!')
        enemySpeed = 0
        enemy = dico['target']
        if enemy['type'] != 'WarBase' and enemy['type'] != 'WarTurret':
            enemySpeed = Stats.agent(enemy['type']).SPEED
        collision = Predict.collision(
            enemy,
            {'distance': enemySpeed,
             'angle': enemy['heading']},
            Stats.projectile(dico['projectile']).SPEED)

        setHeading(collision['angle'])
        actionWarTurret.nextState = ReloadState
        return fire()


def actionWarTurret():
    return init()

# =============================================================================#
# =============================================================================#
#                               INIT SCRIPT
# =============================================================================#
# =============================================================================#


def init():
    initPerception()
    initInformation()
    settingRessources()
    # TODO: IF can destroy targets :
    settingEnemies()
    settingTargets()

    # FSM - Changement d'état
    if actionWarTurret.nextState is not None:
        actionWarTurret.currentState = actionWarTurret.nextState
        actionWarTurret.nextState = None

    return actionWarTurret.currentState.execute()


def initPerception():
    dico['percepts'] = getPercepts()
    dico['percepts_enemies'] = []
    dico['percepts_allies_base'] = []
    dico['percepts_ressources'] = []

    # percept ressources
    for percept in dico['percepts']:
        if percept.getType().equals(WarAgentType.WarFood):
            dico['percepts_ressources'].append(percept)
        elif isEnemy(percept):
            dico['percepts_enemies'].append(percept)
        elif percept.getType().equals(WarAgentType.WarBase):
            dico['percepts_allies_base'].append(percept)

    for ressource in dico['percepts_ressources']:
        ressourceCarthesian = Trigo.toCarthesian({
            "distance": ressource.getDistance(),
            'angle': ressource.getAngle()
        })
        broadcastMessageToAgentType(WarAgentType.WarBase, 'foodFound', [
                                    str(ressourceCarthesian['x']),
                                    str(ressource['y'])])

    # percept enemies
    for enemy in dico['percepts_enemies']:
        enemyCarthesian = Trigo.toCarthesian({
            'distance': enemy.getDistance(),
            'angle': enemy.getAngle()
        })
        broadcastMessageToAgentType(WarAgentType.WarBase, 'enemyFound', [
                                    str(enemyCarthesian['x']),
                                    str(enemyCarthesian['y']),
                                    str(enemy.getHeading()),
                                    str(enemy.getType()),
                                    str(enemy.getID())])


def initInformation():
    dico['messages'] = getMessages()
    dico['messages_enemies'] = []
    dico['messages_ressources'] = []

    for message in dico['messages']:
        if message.getMessage() == 'food':
            food = Trigo.getCarthesianFromMessage(message)
            dico['messages_ressources'].append(food)
        # TODO: If has an enemy management
        if message.getMessage() == 'enemy':
            enemy = Trigo.getCarthesianAgentFromMessage(message)
            dico['messages_enemies'].append(enemy)


def settingRessources():
    for foodC in dico['messages_ressources']:
        food = Trigo.toPolar(foodC)
        if (food['distance'] < distanceOfView() and
                Trigo.inView(getHeading(), angleOfView(), food['angle'])):
            inPerception = True

            for foodPercept in dico['percepts_ressources']:
                if(foodC == Trigo.roundCoordinates(Trigo.toCarthesian({
                    'distance': ressource.getDistance(),
                        'angle': ressource.getAngle()}))):
                    inPerception = True
                    break

            if not inPerception:
                foodExist = False
                broadcastMessageToAgentType(WarAgentType.WarBase, 'nofood',
                                            [str(foodC['x']),
                                             str(foodC['y'])])

        if foodExist:
            dico['ressources'].append(food)


def settingEnemies():
    dico['enemies'] = []

    for enemyMessage in dico['messages_enemies']:
        enemyPolar = Trigo.toPolar(enemyMessage)
        enemyPolar['heading'] = enemyMessage['heading']
        enemyPolar['type'] = enemyMessage['type']
        enemyPolar['id'] = enemyMessage['id']
        dico['enemies'].append(enemyPolar)

    for enemyPercept in dico['percepts_enemies']:
        canBeAdded = True
        for enemyMessage in dico['enemies']:
            if enemyPercept.getID() == enemyMessage['id']:
                canBeAdded = False
                break

        if canBeAdded:
            enemyPerceptC = {'distance': enemyPercept.getDistance(),
                             'angle': enemyPercept.getAngle(),
                             'heading': enemyPercept.getHeading(),
                             'type': enemyPercept.getType(),
                             'id': enemyPercept.getID()}
            dico['enemies'].append(enemyPerceptC)

from pprint import pprint


def settingTargets():
    dico['targets'] = []
    pprint(dico['enemies'])
    for enemy in dico['enemies']:
        if(enemy['distance'] <= Stats.projectile('WarShell').RANGE * 2):
            enemySpeed = 0
            if enemy['type'] != 'WarBase' and enemy['type'] != 'WarTurret':
                enemySpeed = Stats.agent(enemy['type']).SPEED
            collision = Predict.collision(
                enemy,
                {'distance': enemySpeed,
                 'angle': enemy['heading']},
                Stats.projectile(dico['projectile']).SPEED)

            if(collision['distance'] <=
               Stats.projectile('WarShell').RANGE):
                dico['targets'].append(collision)


# Initialisation des variables
# Initialisation des variables
dico = {}
actionWarTurret.nextState = ObserveState
actionWarTurret.currentState = None
# if can fire
dico['projectile'] = 'WarShell'
