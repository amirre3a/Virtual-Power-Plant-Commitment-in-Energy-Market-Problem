import pandas as pd
import matplotlib.pyplot as plt
import os
from pyomo.environ import *

# Check the current working directory
print("Current Working Directory:", os.getcwd())

# List files in the current working directory
print("Files in the current working directory:", os.listdir(os.getcwd()))

# Load cost and demand data from Excel
cost = pd.read_excel('VPP_input.xlsx', sheet_name='costloadcontrol', index_col=0)
demand = pd.read_excel('VPP_input.xlsx', sheet_name='demandloadcontrol', index_col=0)

# Inspect the DataFrames
print("Cost DataFrame:")
print(cost.head())
print("Cost DataFrame Index:")
print(cost.index)

print("\nDemand DataFrame:")
print(demand.head())
print("Demand DataFrame Columns:")
print(demand.columns)

# Create a Pyomo model
model = ConcreteModel()

# Sets
model.i = Set(initialize=cost.index)
model.t = RangeSet(1, 24)

# Parameters
model.cost_a = Param(model.i, initialize=cost['a'].to_dict())
model.cost_b = Param(model.i, initialize=cost['b'].to_dict())
model.cost_pmax = Param(model.i, initialize=cost['pmax'].to_dict())
# Adjusting demand parameter initialization
model.demand = Param(model.t, initialize=demand.iloc[:, 0].to_dict())

# Variables
model.pdg = Var(model.t, model.i, domain=NonNegativeReals)
model.Z = Var(domain=NonNegativeReals)

# Upper bounds for pdg
for i in model.i:
    for t in model.t:
        model.pdg[t, i].setub(model.cost_pmax[i])

# Objective function
def objective_rule(model):
    return sum(model.cost_a[i] * model.pdg[t, i] ** 2 + model.cost_b[i] * model.pdg[t, i] for t in model.t for i in model.i)
model.of = Objective(rule=objective_rule, sense=minimize)

# Constraints
def co1_rule(model, t):
    return sum(model.pdg[t, i] for i in model.i) == model.demand[t]
model.co1 = Constraint(model.t, rule=co1_rule)

# Solve the model using IPOPT for nonlinear problems
solver = SolverFactory('ipopt')
solver.solve(model)

# Collect results
pdg_results = pd.DataFrame(index=model.t, columns=model.i)
for t in model.t:
    for i in model.i:
        pdg_results.at[t, i] = model.pdg[t, i].value

# Display results
print("Objective Value (Z):", model.Z.value)
print("PDG Results:")
print(pdg_results)

# Save results to Excel
pdg_results.to_excel('VPP_output_load_control.xlsx', sheet_name='pdg')

# Plot results
fig, ax = plt.subplots(figsize=(10, 6))

pdg_results.plot(kind='bar', stacked=True, ax=ax, color=['orange', 'yellow', 'green', 'brown', 'darkgoldenrod', 'blue', 'purple', 'pink'])

ax.set_xlabel('Time (t)')
ax.set_ylabel('PDG')
ax.set_title('WITH LOAD CONTROL')

plt.legend(title='Generators', loc='upper left', labels=model.i)
plt.tight_layout()
plt.show()
