from math import *

class Trigo(object):
    @staticmethod
    def getPolarFromMessage(message):
        polarA = {'distance': float(message.getDistance()),
                  'angle': float(message.getAngle())}
        carthesianA = Trigo.toCarthesian(polarA)

        polarO = {'distance': float(message.getContent()[0]),
                  'angle': float(message.getContent()[1])}
        carthesianO = Trigo.toCarthesian(polarO)

        carthesianTarget={'x':carthesianA['x'] + carthesianO['x'],
                         'y': carthesianA['y'] + carthesianO['y']}
        polarTarget = Trigo.toPolar(carthesianTarget)
        return polarTarget

    @staticmethod
    def toCarthesian(polar):
        return {'x': polar['distance'] * cos(radians(polar['angle'])),
                'y': polar['distance'] * sin(radians(polar['angle']))}

    @staticmethod
    def toPolar(carthesian):
        return {'distance':hypot(carthesian['x'],carthesian['y']),
                'angle':degrees(atan2(carthesian['y'],carthesian['x']))}

class HarvestState(object):
    @staticmethod
    def execute():
        setDebugString("On va chercher la bouffe")
        for percept in dico['ressources']:
            setHeading(percept.getAngle())
            if(percept.getDistance() < getMaxDistanceTakeFood()):
                if (getNbElementsInBag() >= getBagSize() - 1):
                    actionWarExplorer.nextState = GoHomeState
                else:
                    actionWarExplorer.nextState = SearchState
                    setDebugString("Je prends la bouffe")
                return take()
            else:
                actionWarExplorer.nextState = SearchState
                return move()

class GoHomeState(object):
    @staticmethod
    def execute():
        setDebugString("On depose la bouffe")
        if((dico['percepts_alliesBase'] is not None) and (len(dico['percepts_alliesBase']) != 0)):
            base = dico['percepts_alliesBase'][0]
            if(base.getDistance() < maxDistanceGive()):
                if getNbElementsInBag() <= 1:
                    actionWarExplorer.nextState = SearchState
                setIdNextAgentToGive(base.getID());
                return give()
            else:
                return move()
        else:
            for message in dico['messages'] :
                if(message.getSenderType() == WarAgentType.WarBase):
                    setHeading(message.getAngle())
            broadcastMessageToAgentType(WarAgentType.WarBase,"whereAreYouBase","")
            return move()

class SearchState(object):
    @staticmethod
    def execute():
        #if units
        setDebugString("On cherche")
        if(len(dico['ressources']) != 0):
            actionWarExplorer.currentState = HarvestState
            return HarvestState.execute()

        if((dico['messagesFood'] is not None) and (len(dico['messagesFood']) != 0)):
            for message in dico['messagesFood'] :
                if(message.getSenderType() == WarAgentType.WarExplorer):
                    tritri = Trigo.getPolarFromMessage(message)
                    angle = tritri['angle']
                    distance = tritri['distance']
                    setHeading(angle)
        return move()

def actionWarExplorer():
    dico['percepts'] = []
    dico['percepts_enemies'] = []
    dico['percepts_alliesBase'] = []
    dico['ressources'] = []
    dico['messages'] = []
    dico['messagesFood'] = []

    dico['percepts'] = getPercepts()
    dico['percepts_enemies'] = getPerceptsEnemies()
    dico['percepts_alliesBase'] = getPerceptsAlliesByType(WarAgentType.WarBase)
    #percept ressources
    for percept in dico['percepts']:
        if percept.getType().equals(WarAgentType.WarFood) :
            dico['ressources'].append(percept)

    if((dico['ressources'] is not None) and (len(dico['ressources']) != 0)):
        broadcastMessageToAgentType(WarAgentType.WarExplorer,"FoodHere",[str(dico['ressources'][0].getDistance()),str(dico['ressources'][0].getAngle())])

    dico['messages'] = getMessages()

    for message in dico['messages']:
        if(message.getSenderType() == WarAgentType.WarExplorer):
            dico['messagesFood'].append(message)

    if (isBlocked()) :
        RandomHeading()
        return move()
    # FSM - Changement d'état
    if(actionWarExplorer.nextState != None):
        actionWarExplorer.currentState = actionWarExplorer.nextState
        actionWarExplorer.nextState = None

    return actionWarExplorer.currentState.execute()

# Initialisation des variables
dico = {}
actionWarExplorer.nextState = SearchState
actionWarExplorer.currentState = None
