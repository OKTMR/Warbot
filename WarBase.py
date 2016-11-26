from math import *

# =============================================================================#
# =============================================================================#
#                                    Trigo
# =============================================================================#
# =============================================================================#
class Trigo(object):
    @staticmethod
    def getPolarFromMessage(message):
        polarA = {'distance': float(message.getDistance()),
                  'angle': float(message.getAngle())}

        polarO = {'distance': float(message.getContent()[0]),
                  'angle': float(message.getContent()[1])}
        return Trigo.getPolarTarget(polarA,polarO)

    @staticmethod
    def getCarthesianTarget(carthesianSender,carthesianObjective):
        return {'x': carthesianSender['x'] + carthesianObjective['x'],
                'y': carthesianSender['y'] + carthesianObjective['y']}

    @staticmethod
    def getPolarTarget(polarSender,polarObjective):
        carthesianTarget = Trigo.getCarthesianTarget(
                Trigo.toCarthesian(polarSender),
                Trigo.toCarthesian(polarObjective))

        return Trigo.toPolar(carthesianTarget)

    @staticmethod
    def toCarthesian(polar):
        return {'x': polar['distance'] * cos(radians(polar['angle'])),
                'y': polar['distance'] * sin(radians(polar['angle']))}

    @staticmethod
    def toPolar(carthesian):
        return {'distance': hypot(carthesian['x'],carthesian['y']),
                'angle': (degrees(atan2(carthesian['y'],carthesian['x'])) + 360) % 360}

    @staticmethod
    def roundCoordinates(carthesian):
        carthesian['x'] = Trigo.myfloor(carthesian['x'])
        carthesian['y'] = Trigo.myfloor(carthesian['y'])
        return carthesian

    @staticmethod
    def myfloor(x):
        return int(5 * round(float(x)/5))

    @staticmethod
    def inView(viewAngle, angleOfView, targetAngle):
        return abs((viewAngle - targetAngle + 180 + 360) % 360 - 180) < (angleOfView/2)



# =============================================================================#
# =============================================================================#
#                              Beginning
# =============================================================================#
# =============================================================================#

"""
- the food is located by a rounding of 5 distance between each food
"""
def actionWarBase():
# I AM HERE
    broadcastMessageToAgentType(WarAgentType.WarExplorer,'base','')
    setDebugString(str(getNbElementsInBag()))

# Recieving messages
    dico['messages'] = getMessages()
    for message in dico['messages']:
        # FOOD
        # found
        if(message.getMessage() == 'food'):
            food = Trigo.roundCoordinates(Trigo.toCarthesian(Trigo.getPolarFromMessage(message)))
            if food not in dico['messages_ressources']:
                dico['messages_ressources'].append(food)

        # not found
        elif (message.getMessage() == 'nofood'):
            food =  Trigo.roundCoordinates(Trigo.toCarthesian(Trigo.getPolarFromMessage(message)))
            if food in dico['messages_ressources']:
                dico['messages_ressources'].remove(food)

        # ENNEMIES

# Sending messages
    # FOOD
    for food in dico['messages_ressources']:
        polarFood = Trigo.toPolar(food)
        broadcastMessageToAgentType(WarAgentType.WarExplorer,'food',[
            str(polarFood['distance']),
            str(polarFood['angle']) ])

    # ENNEMIES
    return idle()


dico = {}
dico['messages_ressources'] = []
