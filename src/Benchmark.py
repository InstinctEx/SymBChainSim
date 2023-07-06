import Chain.tools as tools
from Chain.Parameters import Parameters
from Chain.Network import Network

from datetime import datetime

from Chain.Manager import Manager

import random, numpy, os, yaml

import Chain.Consensus.BigFoot.BigFoot as BigFoot
import Chain.Consensus.PBFT.PBFT as PBFT

from Chain.Metrics import SimulationState, Metrics

import matplotlib.pyplot as plt
import statistics as st
import numpy as np

# ############### SEEDS ############
# seed = 5
# random.seed(seed)
# numpy.random.seed(seed)
# ############### SEEDS ############

def generate_config():
    with open("Configs/Benchmark/scenario.yaml", 'rb') as f:
        data = yaml.safe_load(f)

    data["behaviour"]["crash_probs"]["faulty_nodes"] = 0

    return data

def kill_node(Manager, num_intervals, percent):
    pass

def benachmark():
    print("Starting...")
    manager = Manager()
    data = generate_config()
    manager.set_up(data=data)
    manager.run()

    SimulationState.store_state(manager.sim)
    Metrics.measure_all(SimulationState.blockchain_state)

    print("Done!")

    # for n in manager.sim.nodes:
    #     print(n, '| Total_blocks:', n.blockchain_length(),
    #         '| pbft:',len([x for x in n.blockchain if x.consensus == PBFT]),
    #         '| bf:',len([x for x in n.blockchain if x.consensus == BigFoot]),
    #         )
    
    # SimulationState.store_state(manager.sim)

    # Metrics.measure_all(SimulationState.blockchain_state)
    # Metrics.print_metrics()

    # print(Parameters.simulation["events"])

    # print(st.mean([b.extra_data["num_remaining"] for b in manager.sim.nodes[0].blockchain]))

    return {
        "latency": st.mean([value["AVG"] for value in Metrics.latency.values()]),
        "throughput": st.mean([value for value in Metrics.throughput.values()]),
        "decetralisation": st.mean([value for value in Metrics.decentralisation.values()])
    }

def run_all():
    cummulative_results = []
    for _ in range(10):
        cummulative_results.append(benachmark())

      
    plot(cummulative_results)

def plot(results): 
    if isinstance(results, list):
        mets = {key:[] for key in results[0].keys()}
        for res in results:
            for key, value in res.items():
                mets[key].append(value)
        
        fig, ax = plt.subplots(1,3)
        ax[0].bar(np.arange(len(mets["latency"])), mets["latency"])
        ax[1].bar(np.arange(len(mets["throughput"])), mets["throughput"])
        ax[2].bar(np.arange(len(mets["decetralisation"])), mets["decetralisation"])
        plt.show()
    else:
        fig, ax = plt.subplots(1,3)
        ax[0].boxplot(results["latency"])
        ax[1].bar(0, st.mean(results["throughput"]))
        ax[2].bar(0, st.mean(results["decetralisation"]))
        plt.show()
    
run_all()
