from math import *
from random import random
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
        # targetPos = Trigo.getPolarTarget(targetPos, targetHeading)
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
#                              Beginning
# =============================================================================#
# =============================================================================#

def actionWarBase():
    """
    - the food is located by a rounding of 5 distance between each food
    """
# I AM HERE
    broadcastMessageToAll('base', '')
    setDebugString(str(getNbElementsInBag()))

    dico['messages'] = getMessages()
    dico['messages_enemies'] = []

    # Recieving messages
    recievingMessages()
    # Sending messages
    sendingMessages()

    # TODO: State machine
    if getMaxHealth() - getHealth() >= 250 and getNbElementsInBag() > 0:
        return eat()

    if getHealth() < 5000:
        if getHealth() > 4000 and random() < 0.5:
            return createEngineer()
        else:
            return idle()
    elif random() > 0.7:
        setNextAgentToCreate(WarAgentType.WarKamikaze)
        return create()
    return idle()

dico = {}
dico['messages_ressources'] = []


def recievingMessages():
    for message in dico['messages']:
            # FOOD
            # found
        if message.getMessage() == 'foodFound':
            food = Trigo.roundCoordinates(
                Trigo.getCarthesianFromMessage(message))
            if food not in dico['messages_ressources']:
                dico['messages_ressources'].append(food)

            # not found
        elif message.getMessage() == 'nofood':
            food = Trigo.roundCoordinates(
                Trigo.getCarthesianFromMessage(message))
            if food in dico['messages_ressources']:
                dico['messages_ressources'].remove(food)

        # ENNEMIES
        elif message.getMessage() == 'enemyFound':
            enemy = Trigo.getCarthesianAgentFromMessage(message)
            stored = False

            for storedEnemy in dico['messages_enemies']:
                if enemy['id'] == storedEnemy['id']:
                    stored = True
                    break

            if not stored:
                dico['messages_enemies'].append(enemy)


def sendingMessages():
    # FOOD
    for food in dico['messages_ressources']:
        broadcastMessageToAgentType(WarAgentType.WarExplorer, 'food', [
            str(food['x']),
            str(food['y'])])

    # ENNEMIES
    for enemy in dico['messages_enemies']:
        broadcastMessageToAll('enemy', [
            str(enemy['x']),
            str(enemy['y']),
            str(enemy['heading']),
            str(enemy['type']),
            str(enemy['id'])])
