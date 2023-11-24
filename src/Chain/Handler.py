import bisect

from Chain.Parameters import Parameters
from Chain.Network import Network

import Chain.tools as tools

from Chain.Event import Event, MessageEvent

'''
    Handling and running Events
'''


def handle_event(event, backlog=False):
    '''
        Handless events by calling their respctive handlers and backlogs

        Possible outcomes from handlers:
            handled     - Event was handled sucessfully (no state change e.g vote counted but not enough votes yet, old message ETC..)
            new_state   - Event was handled and node changed state -> check backlog to see if messages can be handled under this new state
            invalid     - Invalid message
            unhadled    - Could not handle (error message)
            backlog     - future message, add to backlog
    '''

    # if node is dead - event will not be handled
    if not event.actor.state.alive:
        return 'dead_node'

    '''
        TODO: Leave this check to the protocol
    '''
    # if this event is CP specific and the CP of the event does not mactch the current CP - old message
    if "CP" in event.payload and event.payload['CP'] != event.actor.cp.NAME:
        return 'invalid'

    # if we are not handling backlog events and this is a network event
    # handle actions related with the receiving of the message
    if not backlog and isinstance(event, MessageEvent):
        Network.receive(event.actor, event)

    # handlle event using it's respective handler
    ret = event.handler(event)

    if ret == 'backlog' and not backlog:
        # add future event to backlog (not backlog prevents us infinetely adding events to backlog while checking the backlog)
        bisect.insort(event.actor.backlog, event)
    elif ret == 'new_state' and not backlog:
        # if the event caused the node to go to a new satate, check the backlog (some future events might be ready to be handled)
        handle_backlog(event.actor)
    elif ret == 'unhadled':
        print(event)
        raise ValueError("Event was not handled by its own handler!")

    return ret


def handle_backlog(node):
    '''
        Tries to handle every event in the backlog - removes handled events
    '''
    remove_list = []

    for event in node.backlog:
        tools.debug_logs(
            msg=f"{node.__str__(full=True)}", input=f"HANDLING BACKLOOOG: {event} ", in_col="43", clear=False)

        ret = handle_event(event, backlog=True)

        tools.debug_logs(msg=f"event returned {ret}")

        if ret == 'handled' or ret == 'new_state' or ret == 'invalid':
            remove_list.append(event)

    # if event causes node to enter new round - backlog is cleared and thus this will error out
    if node.backlog:
        node.backlog = [e for e in node.backlog if e not in remove_list]
