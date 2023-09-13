import pickle
import statistics as st
from Chain.Parameters import Parameters

import matplotlib.pyplot as plt
import numpy as np

class Metrics:
    latency = {}
    throughput = {}
    blocktime = {}

    decentralisation = {}

    
    @staticmethod
    def measure_all(state):
        Metrics.measure_latency(state)
        Metrics.measure_throughput(state)
        Metrics.measure_interblock_time(state)
        Metrics.measure_decentralisation_nodes(state)

    @staticmethod
    def print_metrics():
        averages = {n:{} for n in Metrics.latency.keys()}
        val = "{v:.3f}"

        #latency
        for key, value in Metrics.latency.items():
            averages[key]["Latency"] = val.format(v=value["AVG"])

        # throughput
        for key, value in Metrics.throughput.items():
            averages[key]["Throughput"] = val.format(v=value)

        # blockctime
        for key, value in Metrics.blocktime.items():
            averages[key]["Blocktime"] = val.format(v=value["AVG"])

        # decentralisation
        for key, value in Metrics.decentralisation.items():
            val = "{v:.6f}"
            averages[key]["Decentralisation"] = val.format(v=value)

        print("-"*30, "METRICS", "-"*30)

        for key, value in averages.items():
            print(f"Node: {key} -> {value}")

    @staticmethod
    def measure_latency(bc_state):
        for node_id, node_state in bc_state["blockchain"].items():

            Metrics.latency[node_id] = {"values": {}}
            for b in node_state["blockchain"]:
                Metrics.latency[node_id]["values"][b["id"]] = st.mean(
                    [b["time_added"] - t.timestamp for t in b["transactions"]]
                )
            
            Metrics.latency[node_id]["AVG"] = st.mean(
                [b_lat for _, b_lat in Metrics.latency[node_id]["values"].items()]
            )
    
    @staticmethod
    def measure_throughput(bc_state):
        """
            Measured as:  sum_processed_txions / timestamp of state snapshot
        """
        for node_id, node_state in bc_state["blockchain"].items():
            sum_tx = sum([len(x["transactions"]) for x in node_state["blockchain"]])
            Metrics.throughput[node_id] = sum_tx/bc_state["timestamp"]

    @staticmethod
    def measure_interblock_time(bc_state):
        for node_id, node_state in bc_state["blockchain"].items():
            # for each pair of blocks create the key valie pair "curr -> next": next.time_added - curre.time_added
            diffs = { f"{curr['id']} -> {next['id']}" : next["time_added"] - curr["time_added"] 
                     for curr, next in zip(node_state["blockchain"][:-1], node_state["blockchain"][1:]) }
            
            Metrics.blocktime[node_id] = {"values": diffs, "AVG": st.mean(diffs.values())}
    
    @staticmethod
    def gini_coeficient(cumulative_dist):
        lorenz_curve = [(x+1)/len(cumulative_dist) for x in range(len(cumulative_dist))]
        x_axis = [x for x in range(len(lorenz_curve))]
        '''
            TODO: Validate that this is indeed correct
            NOTE: seems kind of correct
        '''

        # calculate the area of the lorenze curve
        lor_area = np.trapz(lorenz_curve, x_axis) 
        # calculate the area of the actual cumulatice distribution
        act_area = np.trapz(cumulative_dist, x_axis) 
        # calculate what percentage is the area between the lorenze cruve and the actual curve
        return 1 - act_area / lor_area
        
    def gini_coeficient_rmad(values):
        '''
            An alternative approach is to define the Gini coefficient
            as half of the relative mean absolute difference, which is
            equivalent to the definition based on the Lorenz curve.
        '''
        enum = 0
        for x_i in values:
            for x_j in values:
                enum += abs(x_i - x_j)
        
        n = len(values)

        return enum / (2 * (n*n) * st.mean(values))

    @staticmethod
    def measure_decentralisation_nodes(bc_state, rmad=True):
        '''
            TODO: 
                Consider how nodes entering and exiting the consensus can be taken into account

            NOTE: 
                This method assumes all nodes are accounted for in the final system state 
                and no later added nodes produced blocks and left

                !IF NODES THAT HAVE PRODUCED BLOCKS ARE NOT IN THE GIVEN SYSTEM STATE THIS BREAKS!

                if an extra node joins later this skews the decentralisaion since
                the node did not have equal proposing chances as the other nodes 

                    -- dont know if this is considered when measuring decentralisation
                       but seems like it should not be since the node was not there so 
                       its not the algorithms faults that the system is "less decentralised"

                NOTE:
                    possible solution:
                        Note when nodes enter and left (might be (probably is) hard to know when a node leaves)
                        calculating decentralisaion seperatatly for each interval where nodes are "stable"
                        average the decentralisations out
        '''        
        nodes = [int(x) for x in bc_state["blockchain"].keys()]

        for node_id, node_state in bc_state["blockchain"].items():
            block_distribution = {x:0 for x in nodes}
            total_blocks = len(node_state["blockchain"])

            for b in node_state["blockchain"]:
                block_distribution[b["miner"]] += 1

            if rmad == True:
                gini = Metrics.gini_coeficient_rmad(block_distribution.values())
            else:
                dist = sorted([(key, value) for key, value in block_distribution.items()], key=lambda x:x[1])
                dist = [(x[0], x[1]/total_blocks) for x in dist]        
                cumulative_dist = [sum([x[1] for x in dist[:i+1]]) for i in range(len(dist))]
                    
                gini = Metrics.gini_coeficient(cumulative_dist)

            Metrics.decentralisation[node_id] = gini