from Chain.Parameters import Parameters

import random, sys, numpy as np

from bisect import insort

from collections import namedtuple

Transaction = namedtuple("Transaction", "id, timestamp, size")

PriorityTransaction = namedtuple("PriorityTransaction", "id, timestamp, size, priority")

class TransactionFactory:
    '''
        Handles the generation and execution of transactions
    '''
    def __init__(self, nodes) -> None:
        self.nodes = nodes

    def transaction_prop(self, tx):
        '''
            Models the propagations of transactions to nodes
                note: Propagation delays can be accounted for here
                Named tuples are IMMUTABLE! Create new tuples based on the TX with the new timestamps
        '''
        for node in self.nodes:
            node.pool.append(tx)

    def add_interval_transactions(self, txions, use_priority):
        '''
            Used to add transactions (FOR THE CURRENT INTERVAL)
            from an external source to the blockchain system

            txions should be a list of dictionary with the following keys
            {id:int, timestamp:double , size:double, (priority:int if use_priority == True)}
        '''

        for tx in txions:
            if use_priority:
                t = PriorityTransaction(tx["id"], tx["timestamp"], tx["size"], tx["priority"])
            else:
                t = Transaction(tx["id"], tx["timestamp"], tx["size"])

            self.transaction_prop(t)

    def generate_interval_txions(self, start):
        '''
            Generates transactions for a time interval
        '''
        for second in range(round(start), round(start + Parameters.application["TI_dur"])):
            for _ in range(Parameters.application["Tn"]):
                # generate incrementing txions ids
                id =  Parameters.application["txIDS"]
                Parameters.application["txIDS"] += 1
                            
                timestamp = second
                
                #size = random.expovariate(1/Parameters.application["Tsize"])
                size = Parameters.application["Tsize"]
                
                if Parameters.application["usePriorityTransactions"]:
                    # Generate priority transactions
                    tx = PriorityTransaction(id, timestamp, size, random.randint(1,3))
                else:
                    # Generate normla transactions
                    tx = Transaction(id, timestamp, size)
                    
                self.transaction_prop(tx)


    def execute_transactions(self, pool):
        '''
            Given a transaction pool, returns the transactions to be placed in the next block
        '''
        
        transactions = []
        size = 0

        if Parameters.application["usePriorityTransactions"]: # execute priority transactions
            # Find the smallest and highest priority txion in the pool
            prios = [x.priority for x in pool]
            min_prio, max_prio = min(prios), max(prios)
            
            # starting from the highest priority level to the lowest
            for p in reversed(range(min_prio, max_prio+1)):
                # get all txions in the current priority level
                prio_pool = [x for x in pool if x.priority == p]

                # process each transaction in the current level until the block is full or no transactions are left
                for tx in prio_pool:
                    if size + tx.size <= Parameters.data["Bsize"]:
                        transactions.append(tx)
                        size += tx.size
                    else:
                        break 
        else: # normal transaction case
            for tx in pool:
                if size + tx.size <= Parameters.data["Bsize"]:
                    transactions.append(tx)
                    size += tx.size
                else:
                    break

        return transactions, size
