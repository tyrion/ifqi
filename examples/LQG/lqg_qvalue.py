from __future__ import print_function

import os
import sys

sys.path.insert(0, os.path.abspath('../'))
from context import *

import numpy as np

import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

from ifqi.envs.lqg1d import LQG1D

mdp = LQG1D()
K = mdp.computeOptimalK()
print('Optimal K: {}'.format(K))
S = 1  # covariance of the controller
print('Covariance S: {}'.format(S))


class tmp_policy():
    def __init__(self, M, S):
        self.K = M
        if isinstance(S, (int, float)):
            self.S = np.array([S]).reshape(1, 1)

    def predict(self, state):
        return np.dot(self.K, state) + np.random.multivariate_normal(
            np.zeros(self.S.shape[0]), self.S, 1), 0


def estimate_qvalue(mdp, x, u, policy, ep_length=100, n_rep=100):
    returns = np.zeros(n_rep)
    for j in range(n_rep):
        mdp.state = x
        returns[j] = mdp._step(u)
        df = mdp.gamma
        for i in range(ep_length):
            s_t = mdp._getState()
            u_t = policy.predict(s_t)[0]
            returns[j] += df * mdp._step(u_t)
            df *= mdp.gamma
    return returns.mean(), 2 * returns.std() / np.sqrt(n_rep)


##############################################################
# Compute the discounted reward
n_rep = 1000
J = mdp.computeJ(K, S, n_random_x0=n_rep)
pol = tmp_policy(K, S)
Jsample = 0
for i in range(n_rep):
    Jsample += mdp.runEpisode(pol, False, True)[0]
Jsample /= n_rep
print(J, Jsample)

##############################################################
# Compute the q-function
x = np.array([2])
u = np.array([0])
q_val, q_std = estimate_qvalue(mdp, x, u, policy=pol, ep_length=400, n_rep=n_rep)
v = mdp.computeQFunction(x, u, K, S, n_rep)

print(q_val, q_std, v)

##############################################################
# Plot the q-function
xs = np.linspace(-mdp.max_pos, mdp.max_pos, 60)
us = np.linspace(-mdp.max_action, mdp.max_action, 50)

l = []
for x in xs:
    for u in us:
        v = mdp.computeQFunction(x, u, K, S, 100)
        l.append([x, u, v])
tabular_Q = np.array(l)
np.savetxt('lqg_qtable.txt', tabular_Q)
print('printed Q-table')

# print(tabular_Q.shape)
# print(tabular_Q)
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.scatter(tabular_Q[:, 0], tabular_Q[:, 1], tabular_Q[:, 2])
plt.show()