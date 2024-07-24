from game import *
from learningAgents import ReinforcementAgent
from featureExtractors import *
import random, util, math
from collections import defaultdict

class QLearningAgent(ReinforcementAgent):

   def __init__(self, **args):
       ReinforcementAgent.__init__(self, **args)
       self.qvalues = defaultdict(float)  # Use a defaultdict for constant-time access

   def getQValue(self, state, action):

       return self.qvalues[(state, action)]

   def computeValueFromQValues(self, state):

       legal_actions = self.getLegalActions(state)
       if not legal_actions:
           return 0.0
       return max(self.getQValue(state, action) for action in legal_actions)

   def computeActionFromQValues(self, state):
       legal_actions = self.getLegalActions(state)
       if not legal_actions:
           return None

       max_q_value = self.computeValueFromQValues(state)
       best_actions = [action for action in legal_actions if self.getQValue(state, action) == max_q_value]
       if not best_actions:
           # If all Q-values are equal, choose a random legal action
           return random.choice(legal_actions)
       else:
           return random.choice(best_actions)

   def getAction(self, state):

       legal_actions = self.getLegalActions(state)
       if not legal_actions:
           return None

       if util.flipCoin(self.epsilon):
           return random.choice(legal_actions)
       else:
           return self.getPolicy(state)

   def update(self, state, action, nextState, reward):
       next_value = self.computeValueFromQValues(nextState)
       td_error = reward + self.discount * next_value - self.getQValue(state, action)
       self.qvalues[(state, action)] += self.alpha * td_error

   def getPolicy(self, state):
       return self.computeActionFromQValues(state)

   def getValue(self, state):
       return self.computeValueFromQValues(state)


class PacmanQAgent(QLearningAgent):
   def __init__(self, epsilon=0.05, gamma=0.8, alpha=0.02, numTraining=0, **args):
       args['epsilon'] = epsilon
       args['gamma'] = gamma
       args['alpha'] = alpha
       args['numTraining'] = numTraining
       self.index = 0  # This is always Pacman
       QLearningAgent.__init__(self, **args)

   def getAction(self, state):
       action = QLearningAgent.getAction(self, state)
       self.doAction(state, action)
       return action


class ApproximateQAgent(PacmanQAgent):

   def __init__(self, extractor='IdentityExtractor', **args):
       self.featExtractor = util.lookup(extractor, globals())()
       PacmanQAgent.__init__(self, **args)
       self.weights = {
           "bias": 0.0,
           "closest-capsule": 0.5,
           "closest-ghost": -2.0,
           '#-of-ghosts-1-step-away': -1.0,
           'eats-food': 0.1,
           'closest-food': 0.1,
           "score": 1.0,
           "distance-to-ghost0": -0.5,
           "distance-to-ghost1": -0.5,
           "distance-to-ghost2": -0.5,
           "distance-to-ghost3": -0.5
       }

   def getWeights(self):
       return self.weights

   def getWeight(self, feature):
       return self.weights[feature]

   def getQValue(self, state, action):

       features = self.featExtractor.getFeatures(state, action)
       return sum(features[feature] * self.getWeight(feature) for feature in features)

   def update(self, state, action, nextState, reward):
       features = self.featExtractor.getFeatures(state, action)
       next_value = self.getValue(nextState)
       td_error = reward + self.discount * next_value - self.getQValue(state, action)

       for feature in features:
           self.weights[feature] += self.alpha * td_error * features[feature]


   def final(self, state):
       PacmanQAgent.final(self, state)

       if self.episodesSoFar == self.numTraining:
           pass