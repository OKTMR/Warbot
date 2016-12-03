# =============================================================================#
#                                   Predict
# =============================================================================#


class Predict(object):

    @staticmethod
    def redefAngle(angleFromOrigin, polar):
        polar['angle'] = (polar['angle'] + (360 - angleFromOrigin)) % 360
        return polar

    @staticmethod
    def collision(targetPos, targetHeading, mySpeed):
        # pas encore sur si vraiment utile ....
        angleShift = (targetPos['angle'] + 270) % 360
        targetToBe = Trigo.getPolarTarget(targetPos, targetHeading)
        targetToBe = Predict.redefAngle(angleShift, targetToBe)
        targetVector = Trigo.toCarthesian(targetToBe)

        valueY = sqrt(pow(mySpeed, 2) - pow(targetVector['x'], 2))
        collisionTime = targetPos['distance'] / (valueY + targetVector['y'])

        relativeAngle = (degrees(atan2(valueY, targetVector['x'])) + 360) % 360
        relativeCollision = {'distance': mySpeed * collisionTime,
                             'angle': relativeAngle}

        return Predict.redefAngle(-angleShift, relativeCollision)
