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
