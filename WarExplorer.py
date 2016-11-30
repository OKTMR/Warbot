import sys
if "./teams/" not in sys.path:
    sys.path.append('./teams/')

from oktamer.utils import Trigo, Stats, Predict  # noqa

# =============================================================================#
# =============================================================================#
#                             Planned mouvements
# =============================================================================#
# =============================================================================#


def mouvement():
    if dico['mouvement']:
        setHeading(dico['heading'] + 20)
        dico['mouvement'] = False
    else:
        setHeading(dico['heading'] - 20)
        dico['mouvement'] = True
    return move()

# =============================================================================#
# =============================================================================#
#                                  Beginning
# =============================================================================#
# =============================================================================#


def actionWarExplorer():
    dico['percepts'] = []
    dico['percepts_enemies'] = []
    dico['percepts_alliesBase'] = []
    dico['percepts_ressources'] = []

    if 'mouvement' not in dico:
        dico['mouvement'] = True

    if 'heading' not in dico:
        dico['heading'] = getHeading()

    dico['messages'] = []
    dico['messages_ressources'] = []

    dico['percepts'] = getPercepts()
    dico['percepts_enemies'] = getPerceptsEnemies()
    dico['percepts_alliesBase'] = getPerceptsAlliesByType(WarAgentType.WarBase)
    # percept ressources
    for percept in dico['percepts']:
        if percept.getType().equals(WarAgentType.WarFood):
            dico['percepts_ressources'].append(percept)

    for ressource in dico['percepts_ressources']:
        broadcastMessageToAgentType(WarAgentType.WarBase, 'food', [
                                    str(ressource.getDistance()),
                                    str(ressource.getAngle())])

    # messages
    dico['messages'] = getMessages()

    # message ressources
    for message in dico['messages']:
        if (message.getSenderType() == WarAgentType.WarBase and
                message.getMessage() == 'food'):
            food = Trigo.getPolarFromMessage(message)
            confirmFoodExistance = True

            if (food['distance'] < distanceOfView() and
                    Trigo.inView(getHeading(), angleOfView(),
                                 food['angle'])):
                inPerception = False

                for ressource in dico['percepts_ressources']:
                    if (Trigo.roundCoordinates(Trigo.toCarthesian(food)) ==
                        Trigo.roundCoordinates(Trigo.toCarthesian(
                            {'distance': ressource.getDistance(),
                             'angle': ressource.getAngle()}))):
                        inPerception = True
                        break

                if not inPerception:
                    confirmFoodExistance = False
                    broadcastMessageToAgentType(WarAgentType.WarBase, 'nofood',
                                                [str(food['distance']),
                                                 str(food['angle'])])

            if confirmFoodExistance:
                dico['messages_ressources'].append(food)

    if isBlocked():
        RandomHeading()
        dico['heading'] = getHeading()
        return move()
    # FSM - Changement d'état
    if actionWarExplorer.nextState is not None:
        actionWarExplorer.currentState = actionWarExplorer.nextState
        actionWarExplorer.nextState = None

    return actionWarExplorer.currentState.execute()


# =============================================================================#
# =============================================================================#
#                                States
# =============================================================================#
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
        if len(dico['percepts_alliesBase']) != 0:
            base = dico['percepts_alliesBase'][0]
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

        if len(dico['messages_ressources']) != 0:
            minDistance = dico['messages_ressources'][0]['distance']
            minAngle = dico['messages_ressources'][0]['angle']
            for food in dico['messages_ressources']:
                if food['distance'] < minDistance:
                    minAngle = food['angle']
            dico['heading'] = minAngle

        return mouvement()


# Initialisation des variables
dico = {}
actionWarExplorer.nextState = SearchState
actionWarExplorer.currentState = None
