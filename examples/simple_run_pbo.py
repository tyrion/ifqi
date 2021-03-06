import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import ExtraTreesRegressor

from ifqi import envs
from ifqi.algorithms.fqi import FQI
from ifqi.evaluation import evaluation
from ifqi.evaluation.utils import check_dataset
import ifqi.algorithms
from ifqi.models.actionregressor import ActionRegressor
from ifqi.models.regressor import Regressor
from ifqi.models.mlp import MLP
from ifqi.models.ensemble import Ensemble
from ifqi.algorithms.pbo.PBO import PBO

mdp = envs.LQG1D()
state_dim, action_dim, reward_dim = envs.get_space_info(mdp)
reward_idx = state_dim + action_dim
discrete_actions = np.array([-8, -7, -6, -5, -4, -3, -2.5, -2, -1.5, -1, -.75,
                             -.5, -.25, 0, .25, .5, .75, 1, 1.5, 2, 2.5, 3, 4,
                             5, 6, 7, 8])
dataset = evaluation.collect_episodes(mdp, n_episodes=1000)
check_dataset(dataset, state_dim, action_dim, reward_dim)
sast = np.append(dataset[:, :reward_idx],
                 dataset[:, reward_idx + reward_dim:-1],
                 axis=1)
r = dataset[:, reward_idx]


class LQG_Q():
    def __init__(self, theta):
        self.theta = theta

    def predict(self, sa, **opt_pars):
        if 'f_rho' in opt_pars:
            k, b = opt_pars['f_rho']
        else:
            k, b = self.theta
        return b * sa[:, 1] ** 2 - (sa[:, 1] - k * sa[:, 0]) ** 2

theta = np.array([1., 0.])
regressor_params = {'theta': theta}
regressor = Regressor(LQG_Q, **regressor_params)

pbo = PBO(estimator=regressor,
          state_dim=state_dim,
          action_dim=action_dim,
          discrete_actions=discrete_actions,
          gamma=mdp.gamma,
          horizon=mdp.horizon,
          features=None,
          verbose=True)

epsilon = 1e-5
delta = np.inf

theta, _ = pbo.fit(sast, r)
while delta > epsilon:
    theta, delta = pbo.fit()

    print('Delta theta:', delta)

print(theta)

initial_states = np.ones((10., 1)) * 10
values = evaluation.evaluate_policy(mdp, pbo, initial_states=initial_states)
print(values)
