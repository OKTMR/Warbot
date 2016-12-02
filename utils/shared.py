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
    # TODO: IF can destroy targets :
    print('DEFINE ENEMIES DETECTION IF CAN FIRE')
    # settingEnemies()
    # settingTargets()

    if isBlocked():
        RandomHeading()
        dico['heading'] = getHeading()
        return mouvement()
    # FSM - Changement d'état
    # TODO: actionWar to define
    print('actionWar NOT CHANGED IN shared')
    if actionWar.nextState is not None:
        actionWar.currentState = actionWar.nextState
        actionWar.nextState = None

    return actionWar.currentState.execute()


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
                                    str(enemy.getID())])


def initInformation():
    dico['messages'] = getMessages()
    dico['messages_enemies'] = []
    dico['messages_ressources'] = []

    for message in dico['messages']:
        if message.getMessage().equals("food"):
            food = Trigo.getCarthesianFromMessage(message)
            dico['messages_ressources'].append(food)
        # TODO: If has an enemy management
        print('IF CAN FIRE shared')
        # if message.getMessage().equals("enemy"):
        #   enemy = Trigo.getCarthesianAgentFromMessage(message)
        #   dico['messages_enemies'].append(enemy)


def settingRessources():
    for foodC in dico['messages_ressources']:
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


def settingEnemies():
    dico['enemies'] = []

    for enemyMessage in dico['messages_enemies']:
        dico['enemies'].append(Trigo.toPolar(enemyMessage))

    for enemyPercept in dico['percepts_enemies']:
        canBeAdded = True
        for enemyMessage in dico['enemies']:
            if enemyPercept.getID() == enemyMessage['id']:
                canBeAdded = False
                break

        if canBeAdded:
            enemyPerceptC = {'distance': enemyPercept.getDistance(),
                             'angle': enemyPercept.getAngle(),
                             'heading': enemyPercept.getHeading(),
                             'type': enemyPercept.getType(),
                             'id': enemyPercept.getID()}
            dico['enemies'].append(enemyPerceptC)


def settingTargets():
    dico['targets'] = []
    for enemy in dico['enemies']:
        if(enemy['distance'] <= Stats.projectile('WarShell').RANGE * 2):
            enemySpeed = 0
            if hasattr(str(Stats.agent(enemy['type'])), 'SPEED'):
                enemySpeed = Stats.agent(enemy['type']).SPEED
            collision = Predict.collision(
                enemy,
                {'distance': Stats.agent(enemy['type']).SPEED,
                 'angle': enemy['heading']},
                Stats.projectile('WarShell').SPEED)

            if(collision['distance'] <=
               Stats.projectile('WarShell').RANGE):
                dico['targets'].append(collision)