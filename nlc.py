import pandas as pd
import matplotlib.pyplot as plt
from pyomo.environ import *

# Load cost and demand data from Excel
cost = pd.read_excel('VPP_input.xlsx', sheet_name='costnoloadcontrol', index_col=0)
demand = pd.read_excel('VPP_input.xlsx', sheet_name='demandnoloadcontrol', index_col=0)

# Create a Pyomo model
model = ConcreteModel()

# Sets
model.i = RangeSet(1, 5)
model.t = RangeSet(1, 24)

# Parameters
model.cost_a = Param(model.i, initialize=cost['a'].to_dict())
model.cost_b = Param(model.i, initialize=cost['b'].to_dict())
model.cost_pmax = Param(model.i, initialize=cost['pmax'].to_dict())
model.demand = Param(model.t, initialize=demand.iloc[:, 0].to_dict())

# Variables
model.pdg = Var(model.t, model.i, domain=NonNegativeReals)
model.Z = Var(domain=NonNegativeReals)

# Lower and upper bounds for pdg
for i in model.i:
    for t in model.t:
        model.pdg[t, i].setlb(0)
        model.pdg[t, i].setub(model.cost_pmax[i])

# Objective function
def objective_rule(model):
    return sum(model.cost_a[i] * model.pdg[t, i] ** 2 + model.cost_b[i] * model.pdg[t, i] for t in model.t for i in model.i)
model.of = Objective(rule=objective_rule, sense=minimize)

# Constraints
def co1_rule(model, t):
    return sum(model.pdg[t, i] for i in model.i) == model.demand[t]
model.co1 = Constraint(model.t, rule=co1_rule)

# Solve the model using IPOPT
solver = SolverFactory('ipopt')
solver.solve(model)

# Collect results
pdg_results = pd.DataFrame(index=model.t, columns=model.i)
for t in model.t:
    for i in model.i:
        pdg_results.at[t, i] = model.pdg[t, i].value

# Plot results
fig, ax = plt.subplots(figsize=(10, 6))

pdg_results.plot(kind='bar', stacked=True, ax=ax, color=['orange', 'yellow', 'green', 'brown', 'darkgoldenrod'])

ax.set_xlabel('Time (t)')
ax.set_ylabel('PDG')
ax.set_title('NO LOAD CONTROL')

plt.legend(title='Generators', loc='upper left', labels=['1', '2', '3', '4', '5'])
plt.tight_layout()
plt.show()

# Save results to Excel
pdg_results.to_excel('VPP_output_noload_control.xlsx', sheet_name='pdg')
