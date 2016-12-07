from math import *
from oktamer.Trigo import Trigo
from oktamer.Stats import Stats
from oktamer.Predict import Predict

# =============================================================================#
#                                   States
# =============================================================================#


class ObserveState(object):

    @staticmethod
    def execute():
        if isReloaded() and len(dico['targets']) > 0:
            return FireState.execute()
        else:
            setDebugString('Hold on to this position')
            setHeading((getHeading() + 179) % 360)

        if not isReloaded():
            setDebugString('Je recharge')
            return reloadWeapon()
        else:
            return idle()


class FireState(object):

    @staticmethod
    def execute():
        dico['target'] = dico['targets'][0]

        for potentTarget in dico['targets']:
            if (potentTarget['distance'] < dico['target']['distance']):
                dico['target'] = potentTarget
        setDebugString('Fire !!!')
        setHeading(dico['target']['angle'])
        actionWarTurret.nextState = ObserveState
        return fire()


def actionWarTurret():
    broadcastMessageToAgentType(WarAgentType.WarEngineer, 'turret', '')
    return init()


# Initialisation des variables
dico = {}
actionWarTurret.nextState = ObserveState
actionWarTurret.currentState = None
# if can fire
dico['projectile'] = Stats.projectile('WarShell')

# =============================================================================#
#                               INIT SCRIPT
# =============================================================================#


def init():
    initPerception()
    initInformation()
    settingEnemies()
    settingTargets()

    # FSM - Changement d'état
    if actionWarTurret.nextState is not None:
        actionWarTurret.currentState = actionWarTurret.nextState
        actionWarTurret.nextState = None

    return actionWarTurret.currentState.execute()


def initPerception():
    dico['percepts'] = getPercepts()
    dico['percepts_enemies'] = []
    dico['percepts_ressources'] = []

    # percept ressources
    for percept in dico['percepts']:
        if percept.getType().equals(WarAgentType.WarFood):
            dico['percepts_ressources'].append(percept)
        elif isEnemy(percept):
            dico['percepts_enemies'].append(percept)

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
        if message.getMessage() == 'enemy':
            enemy = Trigo.getCarthesianAgentFromMessage(message)
            dico['messages_enemies'].append(enemy)


def settingEnemies():
    dico['enemies'] = []

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
            enemyPolar['type'] = str(enemyMessage['type'])
            enemyPolar['id'] = int(enemyMessage['id'])
            dico['enemies'].append(enemyPolar)


def settingTargets():
    dico['targets'] = []
    for enemy in dico['enemies']:
        if(enemy['distance'] <= dico['projectile'].RANGE + 10):
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
                dico['projectile'].SPEED)

            if(collision['distance'] <= dico['projectile'].RANGE):
                dico['targets'].append(collision)
