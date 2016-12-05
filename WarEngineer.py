from math import *
import edu.warbot.agents.agents as a
import edu.warbot.agents.projectiles as p

# =============================================================================#
#                                  States
# =============================================================================#


class MoveToFoodZoneState(object):

    @staticmethod
    def execute():
        if len(dico['ressources']) > 0:
            minDistance = None
            ressourceToGo = None
            for ressource in dico['ressources']:
                if (minDistance is None or
                        minDistance > ressource['distance']):
                    minDistance = ressource['distance']
                    ressourceToGo = ressource
            if ressourceToGo is not None and minDistance < 10:
                return CreateTurretState.execute()
            else:
                dico['heading'] = ressourceToGo['angle']
                return mouvement()

        elif dico['tick'] == 15 and dico['turrets_min_dist'] > 60:
            return CreateTurretState.execute()

        return mouvement()


class CreateTurretState(object):

    @staticmethod
    def execute():
        setNextBuildingToBuild(WarAgentType.WarTurret)
        actionWarEngineer.nextState = GoHomeState
        return build()


class GoHomeState(object):

    @staticmethod
    def execute():
        return "die"
        setDebugString('gohome')
        if len(dico['percepts_allies_base']) != 0:
            base = dico['percepts_allies_base'][0]
            if isPossibleToGiveFood(base):
                setIdNextBuildingToRepair(base.getID())
                return WA.repair()
            else:
                return mouvement()
        else:
            for message in dico['messages']:
                if (message.getSenderType() == WarAgentType.WarBase and
                        message.getMessage() == 'base'):
                    dico['heading'] = message.getAngle()
            return mouvement()
# =============================================================================#
#                                  Beginning
# =============================================================================#


def actionWarEngineer():
    if getHealth() <= 20:
        return "die"
    dico['tick'] = dico['tick'] + 1

    if dico['tick'] == 16:
        dico['tick'] = 0
        dico['turrets_min_dist'] = 100

    for message in getMessages():
        if (message.getMessage() == 'turret' and
                message.getDistance() < dico['turrets_min_dist']):
            dico['turrets_min_dist'] = message.getDistance()
    return init()

# Initialisation des variables
dico = {}
actionWarEngineer.nextState = MoveToFoodZoneState
actionWarEngineer.currentState = None
# erratic mouvements
dico['mouvement'] = True
dico['tick'] = 0
dico['turrets_min_dist'] = 100
dico['allowTurret'] = False
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
    if actionWarEngineer.nextState is not None:
        actionWarEngineer.currentState = actionWarEngineer.nextState
        actionWarEngineer.nextState = None

    return actionWarEngineer.currentState.execute()


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
        foodExist = True
        food = Trigo.toPolar(foodC)
        if (food['distance'] < distanceOfView() and
                Trigo.inView(getHeading(), angleOfView(), food['angle'])):
            inPerception = True

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
#                                   Stats
# =============================================================================#


class Stats(object):

    @staticmethod
    def agent(agent):
        return getattr(a, str(agent))

    @staticmethod
    def projectile(projectile):
        return getattr(p, str(projectile))
