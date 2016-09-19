import numpy as np
from abc import ABCMeta, abstractmethod


class Environment(object):
    """
    Environment abstract class.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        """
        Constructor.

        """
        # Properties
        self.stateDim = None
        self.actionDim = None
        self.nStates = None
        self.nActions = None
        self.horizon = None
        # End episode
        self._atGoal = None
        self._absorbing = None
        # Discount factor
        self.gamma = None

    @abstractmethod
    def evaluate(self, fqi, expReplay=False, render=False):
        """
        This function evaluates the regressor in the provided object parameter.
        Params:
            fqi (object): an object containing the trained regressor
            expReplay (bool): flag indicating whether to do experience replay
            render (bool): flag indicating whether to render visualize behavior
                           of the agent
        Returns:
            J

        """
        pass

    def runEpisode(self, fqi, collect, render=False):
        """
        This function runs an episode using the regressor in the provided
        object parameter.
        Args:
            fqi (object): an object containing the trained regressor
            expReplay (bool): flag indicating whether to do experience replay
            render (bool): flag indicating whether to render visualize behavior
                           of the agent
        Returns:
            - J
            - number of steps
            - a flag indicating if the goal state has been reached
            - augmented training set (if using experience replay)
            - augmented target set (if using experience replay)

        """
        J = 0
        t = 0
        testSuccessful = 0

        if collect:
            stateList = list()
            actionList = list()
            rewardList = list()
            while(t < self.horizon and not self._isAbsorbing()):
                state = self._getState()
                stateList.append(state)
                if fqi is None:
                    action = np.random.choice(fqi._actions)
                    action_list.append(action)
                    r = self._step(int(action[0]), render=render)
                    rewardList.append(r)
                    t += 1
                else:
                    action, _ = fqi.predict(np.array(state))
                    action_list.append(action)
                    r = self._step(int(action[0]), render=render)
                    rewardList.append(r)
                    J += self.gamma ** t * r
                    t += 1

                    if self._isAtGoal():
                        testSuccessful = 1
                        print("Goal reached")
                    else:
                        print("Failure")

            state = self._getState()
            stateList.append(state)

            s = np.array(stateList)
            a = np.array(actionList)
            s1 = s[1:]
            s = s[:-1]
            t = np.array([[0] * (s.shape[0] - 1) + [1]]).T
            r = np.array(rewardList)
            sast = np.concatenate((s, a, s1, t), axis=1)

            return (J, t, testSuccessful, sast, r)
        else:
            while(t < self.horizon and not self._isAbsorbing()):
                state = self._getState()
                action, _ = fqi.predict(np.array(state))
                r = self._step(action, render=render)
                J += self.gamma ** t * r
                t += 1

                if self._isAtGoal():
                    print('Goal reached')
                    testSuccessful = 1

            return (J, t, testSuccessful)

    @abstractmethod
    def _step(self, u, render=False):
        """
        This function performs the step function of the environment.
        Args:
            u (int): the id of the action to be performed.
        Returns:
            the new state and the obtained reward

        """
        pass

    @abstractmethod
    def _reset(self, state=None):
        """
        This function set the current state to the initial state
        and reset flags.
        Args:
            state (np.array): the initial state

        """
        pass

    @abstractmethod
    def _getState(self):
        """
        Returns:
            a tuple containing the current state.

        """
        pass

    def _isAbsorbing(self):
        """
        Returns:
            True if the state is absorbing, False otherwise.

        """
        return self._absorbing

    def _isAtGoal(self):
        """
        Returns:
            True if the state is a goal state, False otherwise.

        """
        return self._atGoal