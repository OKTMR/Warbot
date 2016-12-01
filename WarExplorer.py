from math import *
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
    return init()


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

# =============================================================================#
# =============================================================================#
#                               INIT SCRIPT
# =============================================================================#
# =============================================================================#
# Initialisation des variables
dico = {}
actionWarExplorer.nextState = SearchState
actionWarExplorer.currentState = None
# erratic mouvements
dico['mouvement'] = True


def init():
    # init mouvement
    if 'mouvement' not in dico:
        dico['mouvement'] = True

    if 'heading' not in dico:
        dico['heading'] = getHeading()

    initPerception()
    initInformation()
    settingRessources()

    if isBlocked():
        RandomHeading()
        dico['heading'] = getHeading()
        return mouvement()
    # FSM - Changement d'état
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
                                    str(enemy.getId())])


def initInformation():
    dico['messages'] = getMessages()
    dico['messages_enemies'] = []
    dico['messages_ressources'] = []

    for message in dico['messages']:
        if message.getMessage().equals('food'):
            food = Trigo.getCarthesianFromMessage(message)
            dico['messages_ressources'].append(food)


def settingRessources():
    for foodC from dico['messages_ressources']:
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
