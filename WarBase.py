from math import *
from random import random
import edu.warbot.agents.agents as a
import edu.warbot.agents.projectiles as p


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
    elif random() > 0.5:
        setNextAgentToCreate(WarAgentType.WarExplorer)
        return create()
    return idle()

dico = {}
dico['messages_ressources'] = []
dico['fs'] = {}  # food zone


def recievingMessages():
    for message in dico['messages']:
            # FOOD
            # found
        if message.getMessage() == 'foodFound':
            foodC = Trigo.getCarthesianFromMessage(message)

            foodZone(foodC)

            food = Trigo.roundCoordinates(foodC)
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
        broadcastMessageToAll('food', [
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


def foodZone(foodC):
    if "near" not in dico['fs']:
        foodCdist = hypot(foodC['x'], foodC['y'])
        dico['fs']['near'] = foodC
        dico['fs']['far'] = foodC
        dico['fs']['baseNear'] = foodCdist
        dico['fs']['baseFar'] = foodCdist
        dico['fs']['between'] = 0

    betweenNear = hypot(foodC["x"] - dico['fs']['near']['x'],
                        foodC['y'] - dico['fs']['near']['y'])
    betweenFar = hypot(foodC["x"] - dico['fs']['far']['x'],
                       foodC['y'] - dico['fs']['far']['y'])

    if (betweenNear > dico['fs']['between'] or
            betweenFar > dico['fs']['between']):
        foodCdist = hypot(foodC['x'], foodC['y'])

        if betweenNear > betweenFar:
            dico['fs']['far'] = foodC
            dico['fs']['baseFar'] = foodCdist
            dico['fs']['between'] = betweenNear
        else:
            if dico['fs']['baseFar'] >= foodCdist:
                dico['fs']['near'] = foodC
                dico['fs']['baseNear'] = foodCdist
            else:
                dico['fs']['near'] = dico['fs']['far']
                dico['fs']['baseNear'] = dico['fs']['baseFar']
                dico['fs']['far'] = foodC
                dico['fs']['basefar'] = foodCdist

            dico['fs']['between'] = betweenFar
        broadcastMessageToAll('foodFar', [
            str(dico['fs']['far']['x']),
            str(dico['fs']['far']['y'])])
        broadcastMessageToAll('foodNear', [
            str(dico['fs']['near']['x']),
            str(dico['fs']['near']['y'])])

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
    def getCarthesianFromMessage(message):
        carthesianA = Trigo.toCarthesian(
            {'distance': float(message.getDistance()),
             'angle': float(message.getAngle())})

        carthesianO = {'x': float(message.getContent()[0]),
                       'y': float(message.getContent()[1])}
        return Trigo.getCarthesianTarget(carthesianA, carthesianO)

    @staticmethod
    def getCarthesianAgentFromMessage(message):
        agent = Trigo.getCarthesianFromMessage(message)
        agent['heading'] = (float(message.getContent()[2]) + 360) % 360
        agent['type'] = str(message.getContent()[3])
        agent['id'] = int(message.getContent()[4])
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
