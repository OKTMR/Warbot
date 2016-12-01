# =============================================================================#
# =============================================================================#
#                                   Predict
# =============================================================================#
# =============================================================================#


class Predict(object):

    @staticmethod
    def redefAngle(angleFromOrigin, polar):
        polar['angle'] = (polar['angle'] + (360 - angleFromOrigin)) % 360
        return polar

    @staticmethod
    def collision(targetPos, targetHeading, mySpeed):
        # pas encore sur si vraiment utile ....
        # targetPos = Trigo.getPolarTarget(targetPos, targetHeading)
        targetHeading = Predict.redefAngle(
            (targetPos['angle'] + 270) % 360, targetHeading)
        targetVector = Trigo.toCarthesian(targetHeading)

        valueY = sqrt(pow(mySpeed, 2) - pow(targetVector['x'], 2))
        collisionTime = targetPos['distance'] / \
            (valueY + targetVector['y'])

        relativeAngle = (degrees(atan2(valueY, targetVector['x'])) + 360) % 360
        relativeCollision = {'distance': mySpeed *
                             collisionTime, 'angle': relativeAngle}

        return Predict.redefAngle(-(targetPos['angle'] + 270) % 360,
                                  relativeCollision)
