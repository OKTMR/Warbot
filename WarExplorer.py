

class HarvestState(object):
    @staticmethod
    def execute():
        setDebugString("On va chercher la bouffe")
        for percept in dico['ressources']:
            setHeading(percept.getAngle())
            if(percept.getDistance() <= getMaxDistanceTakeFood()):
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
                actionWarExplorer.nextState = SearchState
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
        for message in dico['messages'] :
            if(message.getSenderType() == WarAgentType.WarExplorer):
                setHeading(trigo(message.getDistance(),message.getAngle(),message.getContent()[0],message.getContent()[1])["angle"]);

        return move()

def trigo(distanceA,angleA,distanceO,angleO):
    aX = distanceA*cos(angleA)
    aY = distanceA*sin(angleA)
    oX = distanceO*cos(angleO)
    oY = distanceO*sin(angleO)
    dX = aX + oX
    dY = aY + oY
    distanceD = hypot(dX,dY)
    angleD = atan (dX / dY)
    return {"distance" : distanceD, "angle" : angleD}

def actionWarExplorer():

    dico['percepts'] = []
    dico['percepts_enemies'] = []
    dico['percepts_alliesBase'] = []
    dico['ressources'] = []
    dico['messages'] = []
    
    dico['percepts'] = getPercepts()
    dico['percepts_enemies'] = getPerceptsEnemies()
    dico['percepts_alliesBase'] = getPerceptsAlliesByType(WarAgentType.WarBase)
    dico['messages'] = getMessages()
    #percept ressources
    for percept in dico['percepts']:
        if percept.getType().equals(WarAgentType.WarFood) :
            dico['ressources'].append(percept)
    if((dico['ressources'] is not None) and (len(dico['ressources']) != 0)):
        broadcastMessageToAgentType(WarAgentType.WarExplorer,"FoodHere",str(dico['ressources'][0].getDistance()),str(dico['ressources'][0].getAngle()))


    dico['messages'] = getMessages()

    if (isBlocked()) :
        RandomHeading()
        return move()
    # FSM - Changement d'état
    if(actionWarExplorer.nextState != None):
        actionWarExplorer.currentState = actionWarExplorer.nextState
        actionWarExplorer.nextState = None

    if actionWarExplorer.currentState:
        return actionWarExplorer.currentState.execute()
    else:
        result = SearchState.execute()
        actionWarExplorer.nextState = SearchState
        return result

# Initialisation des variables
dico = {}
actionWarExplorer.nextState = SearchState
actionWarExplorer.currentState = None