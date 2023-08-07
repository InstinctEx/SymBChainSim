from Chain.Simulation import Simulation
from Chain.Parameters import Parameters
from Chain.Network import Network

from Chain.Consensus.PBFT.PBFT import PBFT
from Chain.Consensus.BigFoot.BigFoot import BigFoot

import Chain.tools as tools

from Chain.SimState import SimulationState
from Chain.Metrics import Metrics

CPs = {
    PBFT.NAME: PBFT,
    BigFoot.NAME: BigFoot
}

class Blockchain:
    def __init__(self):
        # create simulator
        self.sim = None
        self.next_interval = None

    def init_training_evnironment(self):
        # load params (cmd and env)
        tools.set_env_vars_from_config()
        Parameters.load_params_from_config()

        Parameters.application["CP"] = CPs[Parameters.simulation["init_CP"]]

        self.sim = Simulation()
        self.next_interval = Parameters.application["TI_dur"]

        # initialise network
        Network.init_network(self.sim.nodes) 
    
    def init_simulation(self):
        # initialise the simulation without generation transactions since they will come from outside the env
        self.sim.init_simulation(generate_txions=False)

    def add_interval_transactions(self, txions, use_priority):
        Parameters.simulation["txion_model"].add_interval_transactions(txions, use_priority)
    
    def simulate_interval(self):
        # simulate events until clock hits the end of current interval
        self.sim.sim_next_event()

        while self.sim.clock < self.next_interval:
            self.sim.sim_next_event()

        # calculate the end of the next interval        
        self.next_interval += Parameters.application["TI_dur"]
        
        # check if finished and extract the state of the blockchain
        finished = self.sim.clock >= Parameters.simulation["simTime"]
        SimulationState.store_state(self.sim)

        return SimulationState.blockchain_state, finished
    
def example_for_training():
    # dummy data modeling the QL agent
    episodes = range(1)
    
    def QL_generate_txions(start):
        Parameters.simulation["txion_model"].generate_interval_txions(start)
        return []

    def QL_training(state):
        pass

    '''
        Suppose this is the QLearning enviroment where you have imported the following:
            from SymBChainSim.src.Chain.TrainingAPI import Blockchain
    '''

    # create your blockchain training enviroemnt (this will create a blockchain enviroemnt based on the config file you have in the SBS.src.config.base.yaml)
    environment = Blockchain()
    
    # for each episode
    for ep in episodes:
        # initialise the enviroment
        environment.init_training_evnironment()
        
        # use the QL to generate the first set of transactions for the first interval
        txions = QL_generate_txions(environment.sim.clock)
        # add the first set of transaction for this episode to the pools of the nodes
        # environment.add_interval_transactions(txions, use_priority=True)
        # initialise the simulation
        environment.init_simulation()

        # until the current episode finishes
        while True:
            # simulate interval
            state, finished = environment.simulate_interval()

            if finished: # episode finished break and start the next episode
                break
            # episode not finished

            # use the state of the blockchain to calculate the reward of the previous action and train
            QL_training(state)
            # alternative store the sate action pair and train at the end of the episode (depends on how you want to train your agent)

            # generate and add the next set of generated transactions to the system
            txions = QL_generate_txions(environment.sim.clock)
            #environment.add_interval_transactions(txions, use_priority=True)
