import sys
from pprint import pprint
if "./teams/" not in sys.path:
    sys.path.append('./teams/')

if "Trigo" not in sys.modules:
    from oktamer.utils import *  # noqa

# =============================================================================#
# =============================================================================#
#                              Beginning
# =============================================================================#
# =============================================================================#
pprint(sys.modules)


def actionWarBase():
    """
    - the food is located by a rounding of 5 distance between each food
    """
# I AM HERE
    broadcastMessageToAgentType(WarAgentType.WarExplorer, 'base', '')
    setDebugString(str(getNbElementsInBag()))

# Recieving messages
    dico['messages'] = getMessages()
    for message in dico['messages']:
        # FOOD
        # found
        if message.getMessage() == 'food':
            food = Trigo.roundCoordinates(
                Trigo.toCarthesian(Trigo.getPolarFromMessage(message)))
            if food not in dico['messages_ressources']:
                dico['messages_ressources'].append(food)

        # not found
        elif message.getMessage() == 'nofood':
            food = Trigo.roundCoordinates(
                Trigo.toCarthesian(Trigo.getPolarFromMessage(message)))
            if food in dico['messages_ressources']:
                dico['messages_ressources'].remove(food)

        # ENNEMIES


# Sending messages
    # FOOD
    for food in dico['messages_ressources']:
        polarFood = Trigo.toPolar(food)
        broadcastMessageToAgentType(WarAgentType.WarExplorer, 'food', [
            str(polarFood['distance']),
            str(polarFood['angle'])])

    # ENNEMIES
    return idle()


dico = {}
dico['messages_ressources'] = []
