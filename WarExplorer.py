from math import *
from oktamer.Trigo import Trigo

# =============================================================================#
#                                States
# =============================================================================#


class HarvestState(object):

    @staticmethod
    def execute():
        setDebugString('harvest')

        if len(dico['percepts_ressources']) != 0:
            minDistance = dico['percepts_ressources'][0].getDistance()
            minRessource = dico['percepts_ressources'][0]

            for ressource in dico['percepts_ressources']:
                if minRessource.getDistance() > ressource.getDistance():
                    minRessource = ressource

            dico["heading"] = minRessource.getAngle()
            if pickableFood(minRessource):
                if (getNbElementsInBag() >= getBagSize() - 1):
                    actionWarExplorer.nextState = GoHomeState
                else:
                    actionWarExplorer.nextState = SearchState
                    setDebugString('Je prends la bouffe')
                return take()
            else:
                actionWarExplorer.nextState = SearchState
                return mouvement()


class GoHomeState(object):

    @staticmethod
    def execute():
        setDebugString('gohome')
        if len(dico['percepts_allies_base']) != 0:
            base = dico['percepts_allies_base'][0]
            if isPossibleToGiveFood(base):
                if getNbElementsInBag() <= 1:
                    actionWarExplorer.nextState = SearchState
                return giveToTarget(base)
            else:
                return mouvement()
        else:
            for message in dico['messages']:
                if (message.getSenderType() == WarAgentType.WarBase and
                        message.getMessage() == 'base'):
                    dico['heading'] = message.getAngle()
            return mouvement()


class SearchState(object):

    @staticmethod
    def execute():
        # if units
        setDebugString('search')
        if len(dico['percepts_ressources']) != 0:
            actionWarExplorer.currentState = HarvestState
            return HarvestState.execute()

        if len(dico['ressources']) != 0:
            minDistance = dico['ressources'][0]['distance']
            minAngle = dico['ressources'][0]['angle']
            for food in dico['ressources']:
                if food['distance'] < minDistance:
                    minAngle = food['angle']
            dico['heading'] = minAngle

        return mouvement()


# =============================================================================#
#                                  Beginning
# =============================================================================#


def actionWarExplorer():
    return init()

# Initialisation des variables
dico = {}
actionWarExplorer.nextState = SearchState
actionWarExplorer.currentState = None
# erratic mouvements
dico['mouvement'] = True

# =============================================================================#
#                               INIT SCRIPT
# =============================================================================#


def init():
    # TODO: IF CAN MOVE
    # init mouvement
    if 'heading' not in dico:
        dico['heading'] = getHeading()

    initPerception()
    initInformation()
    settingRessources()

    if isBlocked():
        RandomHeading()
        dico['heading'] = getHeading()
        return mouvement()
    if actionWarExplorer.nextState is not None:
        actionWarExplorer.currentState = actionWarExplorer.nextState
        actionWarExplorer.nextState = None

    return actionWarExplorer.currentState.execute()


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
                                    str(ressourceCarthesian['y'])])

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


def settingRessources():
    dico['ressources'] = []
    for foodC in dico['messages_ressources']:
        food = Trigo.toPolar(foodC)
        foodExist = True
        if (food['distance'] < distanceOfView() and
                Trigo.inView(getHeading(), angleOfView(), food['angle'])):
            inPerception = False

            for foodPercept in dico['percepts_ressources']:
                if(foodC == Trigo.roundCoordinates(Trigo.toCarthesian({
                    'distance': foodPercept.getDistance(),
                        'angle': foodPercept.getAngle()}))):
                    inPerception = True
                    break

            if not inPerception:
                foodExist = False
                broadcastMessageToAgentType(WarAgentType.WarBase, 'nofood',
                                            [str(foodC['x']),
                                             str(foodC['y'])])

        if foodExist:
            dico['ressources'].append(food)

# =============================================================================#
#                             Planned mouvements
# =============================================================================#


def mouvement():
    if dico['mouvement']:
        setHeading(dico['heading'] + 20)
        dico['mouvement'] = False
    else:
        setHeading(dico['heading'] - 20)
        dico['mouvement'] = True
    return move()
