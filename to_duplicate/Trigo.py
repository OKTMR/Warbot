# =============================================================================#
# =============================================================================#
#                                   Trigo
# =============================================================================#
# =============================================================================#
class Trigo(object):
    @staticmethod
    def getCarthesianTarget(carthesianSender,carthesianObjective):
        return {'x': carthesianSender['x'] + carthesianObjective['x'],
                'y': carthesianSender['y'] + carthesianObjective['y']}

    @staticmethod
    def getPolarTarget(polarSender,polarObjective):
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
        return Trigo.getPolarTarget(polarA,polarO)

    @staticmethod
    def toCarthesian(polar):
        return {'x': polar['distance'] * cos(radians(polar['angle'])),
                'y': polar['distance'] * sin(radians(polar['angle']))}

    @staticmethod
    def toPolar(carthesian):
        return {'distance': hypot(carthesian['x'],carthesian['y']),
                'angle': (degrees(atan2(carthesian['y'],carthesian['x'])) + 360) % 360}

    @staticmethod
    def roundCoordinates(carthesian):
        carthesian['x'] = Trigo.myfloor(carthesian['x'])
        carthesian['y'] = Trigo.myfloor(carthesian['y'])
        return carthesian

    @staticmethod
    def myfloor(x):
        return int(5 * round(float(x)/5))

    @staticmethod
    def inView(viewAngle, angleOfView, targetAngle):
        return abs((viewAngle - targetAngle + 180 + 360) % 360 - 180) < (angleOfView/2)
