import json
class SimulationState:
    '''
        Stores the state of the simulation.
    '''
    blockchain_state = {"blockchain": {}}
    events = {"consensus":{}, "other": {}}

    @staticmethod
    def store_state(sim):
        '''
            store_state can be called given a simulator object.
            store_state serializes and stores the simulator state
        ''' 
        SimulationState.blockchain_state["timestamp"] = sim.clock
        for n in sim.nodes:
            SimulationState.blockchain_state["blockchain"][n.id] = n.to_serializable()
    
    @staticmethod
    def write_state_to_disk():
        # Serializing json
        json_object = json.dumps(SimulationState.blockchain_state, indent=4)
        
        # Writing to sample.json
        with open("state.json", "w") as outfile:
            outfile.write(json_object)

    @staticmethod
    def load_state(sim):
        pass

    @staticmethod
    def store_event(event):
        if 'block' in event.payload.keys():
            block_id = event.payload['block'].id
            if block_id in SimulationState.events["consensus"].keys():
                SimulationState.events["consensus"][block_id].append(event.to_serializable())
            else:
                SimulationState.events["consensus"][block_id] = [event.to_serializable()] 
        else:
            type = event.payload['type']
            if type in SimulationState.events["other"].keys():
                SimulationState.events[type].append(event.to_serializable())
            else:
                SimulationState.events[type] = [event.to_serializable()]
            