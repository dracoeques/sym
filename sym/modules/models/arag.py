from dataclasses import dataclass

@dataclass
class AugmentedRagModel:
    """ Pull in relevant data given this task"""

    def collect(self, context, n=10):
        """ Given a context vector, find the N most relevant items"""
        pass

    def predict(self, context, target):
        """ Given a context and a target, predict relevancy"""
        pass