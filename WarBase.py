from math import *
from random import random
from oktamer.Trigo import Trigo


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
    setDebugString("No rage de nos ravages")

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
        if getHealth() > 4000 and random() < 0.05:
            return createEngineer()
        else:
            return idle()
    else:
        setNextAgentToCreate(WarAgentType.WarRocketLauncher)
        return create()
    return idle()

dico = {}
dico['messages_ressources'] = []
dico['messages_enemies_bases'] = []


def recievingMessages():
    for message in dico['messages']:
            # FOOD
            # found
        if message.getMessage() == 'foodFound':
            foodC = Trigo.getCarthesianFromMessage(message)

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
                if enemy['type'] == 'WarBase':
                    dico['messages_enemies_bases'].append(enemy)


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

    for enemy in dico['messages_enemies_bases']:
        broadcastMessageToAll('enemyBase', [
            str(enemy['x']),
            str(enemy['y']),
            str(enemy['heading']),
            str(enemy['type']),
            str(enemy['id'])])
