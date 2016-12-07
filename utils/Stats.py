import edu.warbot.agents.agents as a
import edu.warbot.agents.projectiles as p


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
