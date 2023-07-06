import yaml, os, json

def read_yaml(path):
    with open(path, 'rb') as f:
        data = yaml.safe_load(f)
    return data

class Parameters:
    '''
        Contains all the parameters defining the simulator
    '''
    simulation = {}
    application = {}
    execution = {}
    data = {}
    consensus = {}
    network = {}

    BigFoot = {}
    PBFT = {}

    @staticmethod
    def all_params(serializable=False):
        params = {
            "simulation": Parameters.simulation,
            "application": Parameters.application,
            "execution": Parameters.execution,
            "data": Parameters.data,
            "consensus": Parameters.consensus,
            "network": Parameters.network,

            "BigFoot": Parameters.BigFoot,
            "PBFT": Parameters.PBFT
        }
        
        if serializable:
            ser_params = {}
            for p_key, data in params.items():
                temp = {}
                for key, value in data.items():
                    try:
                        json.dumps(value)
                        temp[key] = value
                    except TypeError:
                        pass

                ser_params[p_key] = temp

            return ser_params
        
        return params
                
    @staticmethod
    def load_params_from_config(config, **kwargs):
        if "data" in kwargs and kwargs["data"]:
            params = kwargs["data"]
        else:
            if config is None:
                config = f"Configs/{os.environ['config']}.yaml"
            else:
                config = f"Configs/{config}"

            params = read_yaml(config)

        Parameters.simulation = params["simulation"]
        Parameters.simulation["events"] = {} # cnt events of each type
        
        Parameters.behaiviour = params["behaviour"]

        Parameters.network = params["network"]

        Parameters.application = params["application"]
        Parameters.application["txIDS"] = 0 # incremental txion ids starting on...
        Parameters.calculate_fault_tolerance()

        Parameters.execution = params["execution"]

        Parameters.data = params["data"]

        Parameters.BigFoot = read_yaml(params['consensus']['BigFoot'])
        Parameters.PBFT = read_yaml(params['consensus']['PBFT'])


    @staticmethod
    def calculate_fault_tolerance():
        Parameters.application["f"] = int((Parameters.application["Nn"] - 1) / 3)
        Parameters.application["required_messages"] = (2 * Parameters.application["f"]) + 1
    