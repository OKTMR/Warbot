from oktamer.Trigo import Trigo
from oktamer.Stats import Stats
from oktamer.Predict import Predict

# =============================================================================#
# =============================================================================#
#                              Beginning
# =============================================================================#
# =============================================================================#


class SearchState(object):

    @staticmethod
    def execute():
        if len(dico['enemyBase']) > 0:
            actionWarRocketLauncher.nextState = EnemyBaseState
            return EnemyBaseState.execute()
        if isReloaded() and len(dico['targets']) > 0:
            return FireState.execute()

        if not isReloaded():
            setDebugString('Je recharge')
            return reloadWeapon()
        else:

            return mouvement()


class EnemyBaseState(object):

    @staticmethod
    def execute():
        if not isReloaded():
            setDebugString('Je recharge')
            return reloadWeapon()
        for base in dico['enemyBase']:
            if(base['distance'] < Stats.projectile(dico['projectile']).RANGE):
                setDebugString('Fire !!!')
                setHeading(base['angle'])
                setTargetDistance(base['distance'])
                return fire()
            else:
                dico['heading'] = base['angle']
                return mouvement()


class FireState(object):

    @staticmethod
    def execute():
        dico['target'] = dico['targets'][0]

        for potentTarget in dico['targets']:
            if (potentTarget['distance'] < dico['target']['distance']):
                dico['target'] = potentTarget
        setDebugString('Fire !!!')
        setHeading(dico['target']['angle'])
        setTargetDistance(dico['target']['distance'])
        actionWarRocketLauncher.nextState = SearchState
        return fire()


def actionWarRocketLauncher():
    return init()


# Initialisation des variables
dico = {}
actionWarRocketLauncher.nextState = SearchState
actionWarRocketLauncher.currentState = None
# erratic mouvements
dico['mouvement'] = True
# if can fire
dico['projectile'] = 'WarRocket'
# =============================================================================#
# =============================================================================#
#                               INIT SCRIPT
# =============================================================================#
# =============================================================================#


def init():
    # init mouvement
    if 'mouvement' not in dico:
        dico['mouvement'] = True

    if 'heading' not in dico:
        dico['heading'] = getHeading()

    initPerception()
    initInformation()
    settingRessources()
    settingEnemies()
    settingTargets()

    if isBlocked():
        RandomHeading()
        dico['heading'] = getHeading()
        return mouvement()
    # FSM - Changement d'état
    if actionWarRocketLauncher.nextState is not None:
        actionWarRocketLauncher.currentState = actionWarRocketLauncher.nextState
        actionWarRocketLauncher.nextState = None

    return actionWarRocketLauncher.currentState.execute()


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
    dico['messages_enemies_bases'] = []

    for message in dico['messages']:
        if message.getMessage() == 'food':
            food = Trigo.getCarthesianFromMessage(message)
            dico['messages_ressources'].append(food)
        elif message.getMessage() == 'enemy':
            enemy = Trigo.getCarthesianAgentFromMessage(message)
            dico['messages_enemies'].append(enemy)
        elif message.getMessage() == 'enemyBase':
            enemy = Trigo.getCarthesianAgentFromMessage(message)
            dico['messages_enemies_bases'].append(enemy)


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


def settingEnemies():
    dico['enemies'] = []
    dico['enemyBase'] = []

    for enemyPercept in dico['percepts_enemies']:
        dico['enemies'].append({'distance': enemyPercept.getDistance(),
                                'angle': enemyPercept.getAngle(),
                                'heading': enemyPercept.getHeading(),
                                'type': enemyPercept.getType(),
                                'id': enemyPercept.getID()})

    for enemyMessage in dico['messages_enemies']:
        canBeAdded = True
        for enemyPercept in dico['enemies']:
            if enemyPercept['id'] == enemyMessage['id']:
                canBeAdded = False
                break

        if canBeAdded:
            enemyPolar = Trigo.toPolar(enemyMessage)
            enemyPolar['heading'] = enemyMessage['heading']
            enemyPolar['type'] = enemyMessage['type']
            enemyPolar['id'] = enemyMessage['id']
            dico['enemies'].append(enemyPolar)

    for enemyBase in dico['messages_enemies_bases']:
        enemyPolar = Trigo.toPolar(enemyBase)
        enemyPolar['heading'] = enemyBase['heading']
        enemyPolar['type'] = enemyBase['type']
        enemyPolar['id'] = enemyBase['id']
        dico['enemyBase'].append(enemyPolar)


def settingTargets():
    dico['targets'] = []

    for enemy in dico['enemies']:
        if(enemy['distance'] <=
           Stats.projectile(dico['projectile']).RANGE * 2):
            enemySpeed = 0
            if enemy['type'] in [WarAgentType.WarEngineer,
                                 WarAgentType.WarExplorer,
                                 WarAgentType.WarHeavy,
                                 WarAgentType.WarKamikaze,
                                 WarAgentType.WarLight,
                                 WarAgentType.WarRocketLauncher]:
                enemySpeed = Stats.agent(enemy['type']).SPEED
            collision = Predict.collision(
                enemy,
                {'distance': enemySpeed,
                 'angle': enemy['heading']},
                Stats.projectile(dico['projectile']).SPEED)

            if(collision['distance'] <=
               Stats.projectile(dico['projectile']).RANGE):
                dico['targets'].append(collision)

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
