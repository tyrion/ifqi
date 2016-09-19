import json
from sklearn.ensemble import ExtraTreesRegressor
from ifqi.models.mlp import MLP
from sklearn.linear_model import LinearRegression
from ifqi.models.ensemble import ExtraTreeEnsemble, MLPEnsemble, LinearEnsemble
from ifqi.models.actionRegressor import ActionRegressor
from ifqi.envs.carOnHill import CarOnHill
from ifqi.envs.invertedPendulum import InvPendulum
from ifqi.envs.acrobot import Acrobot
from ifqi.envs.bicycle import Bicycle
from ifqi.envs.swingPendulum import SwingPendulum
from ifqi.envs.cartPole import CartPole
from ifqi.envs.lqg1d import LQG1D


class Experiment(object):
    """
    This class has the purpose to load the configuration
    file of the experiment and return the required model
    and mdp.

    """
    def __init__(self, config_file):
        """
        Constructor.
        Args:
            config_file (str): the name of the configuration file.

        """
        with open(config_file) as f:
            self.config = json.load(f)

        self.mdp = self.getMDP()

    def loadModel(self):
        self.model = self._getModel()

    def _getModel(self):
        """
        This function loads the model required in the configuration file.
        Returns:
            the required model.

        """
        modelConfig = self.config['model']
        if modelConfig['modelName'] == 'ExtraTree':
            model = ExtraTreesRegressor
            params = {'nEstimators': modelConfig['nEstimators'],
                      'criterion': self.config['supervisedAlgorithm']
                                              ['criterion'],
                      'minSamplesSplit': modelConfig['minSamplesSplit'],
                      'minSamplesLeaf': modelConfig['minSamplesLeaf']}
        elif modelConfig['modelName'] == 'ExtraTreeEnsemble':
            model = ExtraTreeEnsemble
            params = {'nEstimators': modelConfig['nEstimators'],
                      'criterion': self.config['supervisedAlgorithm']
                                              ['criterion'],
                      'minSamplesSplit': modelConfig['minSamplesSplit'],
                      'minSamplesLeaf': modelConfig['minSamplesLeaf']}
        elif modelConfig['modelName'] == 'MLP':
            model = MLP
            params = {'nInput': self.mdp.stateDim,
                      'nOutput': 1,
                      'hiddenNeurons': modelConfig['nHiddenNeurons'],
                      'nLayers': modelConfig['nLayers'],
                      'optimizer': modelConfig['optimizer'],
                      'activation': modelConfig['activation']}
        elif modelConfig['modelName'] == 'MLPEnsemble':
            model = MLPEnsemble
            params = {'nInput': self.mdp.stateDim,
                      'nOutput': 1,
                      'hiddenNeurons': modelConfig['nHiddenNeurons'],
                      'nLayers': modelConfig['nLayers'],
                      'optimizer': modelConfig['optimizer'],
                      'activation': modelConfig['activation']}
        elif modelConfig['modelName'] == 'Linear':
            model = LinearRegression
            params = {}
        elif modelConfig['modelName'] == 'LinearEnsemble':
            model = LinearEnsemble
            params = {}
        else:
            raise ValueError('Unknown estimator type.')

        return ActionRegressor(model, self.mdp.nActions, **params)

    def getMDP(self):
        """
        This function loads the mdp required in the configuration file.
        Returns:
            the required mdp.

        """
        if self.config['mdp']['mdpName'] == 'CarOnHill':
            return CarOnHill()
        elif self.config['mdp']['mdpName'] == 'SwingUpPendulum':
            return InvPendulum()
        elif self.config['mdp']['mdpName'] == 'Acrobot':
            return Acrobot()
        elif self.config["mdp"]["mdpName"] == "BicycleBalancing":
            return Bicycle(navigate=False)
        elif self.config["mdp"]["mdpName"] == "BicycleNavigate":
            return Bicycle(navigate=True)
        elif self.config["mdp"]["mdpName"] == "SwingPendulum":
            return SwingPendulum()
        elif self.config["mdp"]["mdpName"] == "CartPole":
            return CartPole()
        elif self.config["mdp"]["mdpName"] == "LQG1D":
            return LQG1D()
        else:
            raise ValueError('Unknown mdp type.')
