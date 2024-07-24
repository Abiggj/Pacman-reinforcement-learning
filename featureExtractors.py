from game import Directions, Actions
import util


class FeatureExtractor:
    def getFeatures(self, state, action):
        util.raiseNotDefined()


class IdentityExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[(state, action)] = 1.0
        return feats


class CoordinateExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[state] = 1.0
        feats['x=%d' % state[0]] = 1.0
        feats['y=%d' % state[0]] = 1.0
        feats['action=%s' % action] = 1.0
        return feats


def closestFood(pos, food, walls):
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        if food[pos_x][pos_y]:
            return dist
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist + 1))
    return None


class SimpleExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()

        features = util.Counter()

        features["bias"] = 1.0

        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        features["#-of-ghosts-1-step-away"] = sum(
            (next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)

        if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:

            features["closest-food"] = float(dist) / (walls.width * walls.height)
        features.divideAll(10.0)
        return features


import util


def manhattanDistance(xy1, xy2):
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])


class BetterFeatureExtractor(SimpleExtractor):
    def __init__(self):
        self.max_feature_values = {
            "bias": 1.0,
            '#-of-ghosts-1-step-away': -1.0,
            'eats-food': 1.0,
            "closest-capsule": 0.005,
            "closest-ghost": -0.008,
            "distance-to-ghost0": -0.004,
            "distance-to-ghost1": -0.004,
            "distance-to-ghost2": -0.004,
            "distance-to-ghost3": -0.004,
            "closest-food": 0.07,
            "score": 0.03,
        }

    def getFeatures(self, state, action):
        features = SimpleExtractor.getFeatures(self, state, action)

        capsules = state.getCapsules()

        capsule_distances = [manhattanDistance(pos, state.getPacmanPosition()) for pos in capsules]
        if capsule_distances:
            features["closest-capsule"] = min(capsule_distances)
        else:
            features["closest-capsule"] = 0.0

        features["score"] = state.getScore()+0.01
        self.max_feature_values["score"] = state.getScore()  # Update the maximum score seen

        pacman_state = state.getPacmanState()
        pacman_position = pacman_state.getPosition()

        ghost_positions = state.getGhostPositions()
        ghost_distances = [manhattanDistance(pos, pacman_position) for pos in ghost_positions]
        if ghost_distances:
            features["closest-ghost"] = min(ghost_distances)
        else:
            features["closest-ghost"] = 0.0

        ghost_states = state.getGhostStates()
        for i, ghost_state in enumerate(ghost_states):
            ghost_position = ghost_state.getPosition()
            distance_to_ghost = manhattanDistance(pacman_position, ghost_position)
            features["distance-to-ghost{}".format(i)] = distance_to_ghost

        food = state.getFood()
        food_positions = [(x, y) for x in range(food.width) for y in range(food.height) if food[x][y]]
        food_distances = [manhattanDistance(pos, pacman_position) for pos in food_positions]
        if food_distances:
            features["closest-food"] = min(food_distances)
        else:
            features["closest-food"] = 0.0

        # Normalize features
        for feature in features:
            if self.max_feature_values[feature] is not None and (feature != 'score'):
                features[feature] /= self.max_feature_values[feature]

        return features
