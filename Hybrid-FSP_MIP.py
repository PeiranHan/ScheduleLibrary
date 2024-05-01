# -*- coding: utf-8 -*-
"""
@Time ： 2024/5/1 21:16
@Auth ： PeiranHan
@File ：Hybrid-FSP_MIP.py
@IDE ：PyCharm
"""
from docplex.mp.model import Model


"""
Section 3.7.1 MIP Model
"""


# Processing times for each job at each stage
processing_times = [
    [2, 3],
    [3, 4],
]

# Number of stages
num_stages = len(processing_times[0])

# Number of jobs
num_jobs = len(processing_times)

# Number of machines at each stage
machines_per_stage = {0: 2, 1: 1}

# Create a model instance
mdl = Model('Mixed Flow Shop Scheduling')

# Define the decision variables
C = {(j, i): mdl.continuous_var(name='C_{}_{}'.format(j, i)) for j in range(num_jobs) for i in range(num_stages)}
w = {(j, i, k): mdl.binary_var(name='w_{}_{}_{}'.format(j, i, k)) for j in range(num_jobs) for i in range(num_stages) for k in range(machines_per_stage[i])}
x = {(j, j_prime, i): mdl.binary_var(name='x_{}_{}_{}'.format(j, j_prime, i)) for j in range(num_jobs) for j_prime in range(num_jobs) for i in range(num_stages)}

# Define the objective function
mdl.minimize(mdl.max(C[j, num_stages - 1] for j in range(num_jobs)))

# Add the constraints to the model
for j in range(num_jobs):
    mdl.add_constraint(C[j, 0] >= processing_times[j][0])
    for i in range(1, num_stages):
        mdl.add_constraint(C[j, i] >= C[j, i - 1] + processing_times[j][i])
        mdl.add_constraint(C[j, i] >= 0)
        mdl.add_constraint(mdl.sum(w[j, i, k] for k in range(machines_per_stage[i])) == 1)

M = 1000  # Big M
for i in range(num_stages):
    for j in range(num_jobs):
        for j_prime in range(num_jobs):
            if j != j_prime:
                for k in range(machines_per_stage[i]):
                    mdl.add_constraint(C[j, i] >= C[j_prime, i] + processing_times[j][i] - M * (3 - x[j, j_prime, i] - w[j, i, k] - w[j_prime, i, k]))
                    mdl.add_constraint(C[j_prime, i] >= C[j, i] + processing_times[j_prime][i] - M * (2 + x[j, j_prime, i] - w[j, i, k] - w[j_prime, i, k]))

# Solve the model
mdl.solve()

# Print the optimal schedule
for j in range(num_jobs):
    for i in range(num_stages):
        print("Job {}, Stage {}: Completion Time = {}".format(j, i, C[j, i].solution_value))
