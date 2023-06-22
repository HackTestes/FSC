# This should simulate the cache ceherance protocols
# write-once
# Firefly
# MSI
# MESI

from collections import namedtuple



# We assume, they are all referencing the same block (different blocks, different result tables)
# operations = [(CPU, action), ...] => (CPU 0, 'read')
Op = namedtuple('Op', 'cpu action')
operations_sequence = [Op(0, 'read'), Op(1, 'write'), Op(2, 'read')]
operations_sequence = [Op(0, 'read'), Op(0, 'write'), Op(0, 'write'), Op(1, 'read')]


# This class will hold cache information of each CPU and the bus
class Env:

    def __init__(self, number_of_CPUs):

        # CPU 0 -> cache[0]
        # This stores the states such as 'modified', 'shared' or 'invalid'
        self.cpu_caches = [None]*number_of_CPUs
        
        # An array helps to share the variable without copy
        # This should represent a bus with one line
        # The operations are strings
        self.bus = ['']

        # This represents the origin of the data: cache 1, processor 1 or memory
        self.data_source = ''

    def clear_bus_source(self):

        # This loop is just in case someone adds mode lines
        for bus_line in range(len(self.bus)):
            self.bus[ bus_line ] = ''

        self.data_source = ''

    def reset_env(self):

        for cache_idx in range(len(self.cpu_caches)):
            self.cpu_caches[ cache_idx ] = None

        self.clear_bus_source()

    def print_current_state(self, operation, cache_op):
        operation_str = f'CPU {operation.cpu} {operation.action} u'
        print(f'{operation_str:25s} {str(self.cpu_caches):40s} {str(self.bus):35s} {str(self.data_source):20s} {cache_op:20s}')

    def invalidate_caches(self, invalid_state):
        for cache_idx in range(len(self.cpu_caches)):

            if self.cpu_caches[ cache_idx ] != None:
                self.cpu_caches[ cache_idx ] = invalid_state




def write_once(env, current_CPU, current_operation):

    # Write miss
    if current_operation == 'write' and (env.cpu_caches[current_CPU] == None or env.cpu_caches[current_CPU] == 'Invalid'):

        if 'Dirty' in env.cpu_caches:
            
            # Get the cache with the dirty block
            dirty_idx = env.cpu_caches.index('Dirty')

            # Update the state
            env.cpu_caches[current_CPU] = 'Dirty'

            # Invalidade the cache
            env.cpu_caches[dirty_idx] = 'Invalid'

            # Bus operation
            env.bus[0] = f'Read-Inv(C{current_CPU})'

        # There is no dirty copy 
        else:
            # Invalidade the caches
            env.invalidate_caches('Invalid')

            # Update the state
            env.cpu_caches[current_CPU] = 'Dirty'

            # Bus operation
            env.bus[0] = f'Read-Inv(C{current_CPU})'

        # Data source
        env.data_source = f'Processor {current_CPU}'

        return 'write miss'

    # Read miss
    if current_operation == 'read' and (env.cpu_caches[current_CPU] == None or env.cpu_caches[current_CPU] == 'Invalid'):

        if 'Dirty' in env.cpu_caches:

            # Get the cache with the dirty block
            dirty_idx = env.cpu_caches.index('Dirty')

            # Update the state
            env.cpu_caches[current_CPU] = 'Valid'

            # Promote dirty to valid
            env.cpu_caches[dirty_idx] = 'Valid'

            # Bus operation
            env.bus[0] = f'Read-Blk(C{current_CPU})'

            # Data source
            env.data_source = f'Cache {dirty_idx}'

        # There is no Dirty copy  -> this is also true for valid copies in olther caches
        else:
            # Update the state
            env.cpu_caches[current_CPU] = 'Valid'

            # Bus operation
            env.bus[0] = f'Read-Blk(C{current_CPU})'

            # Data source
            env.data_source = f'Memory'

        return 'read miss'

    # Write hit
    if current_operation == 'write' and env.cpu_caches[current_CPU] != None and env.cpu_caches[current_CPU] != 'Invalid':

        if env.cpu_caches[current_CPU] == 'Dirty':

            # No need to update the state

            # Bus operation
            env.bus[0] = f'---'

        elif env.cpu_caches[current_CPU] == 'Reserved':

            # Invalidade the caches
            env.invalidate_caches('Invalid')

            # Update the state
            env.cpu_caches[current_CPU] = 'Dirty'

            # Bus operation
            env.bus[0] = f'---'

        elif env.cpu_caches[current_CPU] == 'Valid':

            # Invalidade the caches
            env.invalidate_caches('Invalid')

            # Update the state
            env.cpu_caches[current_CPU] = 'Reserved'

            # Bus operation
            env.bus[0] = f'Write-Inv(C{current_CPU})'

        # Data source
        env.data_source = f'Processor {current_CPU}'

        return 'write hit'


    # Read hit
    if current_operation == 'read' and env.cpu_caches[current_CPU] != None and env.cpu_caches[current_CPU] != 'Invalid':

        # No need to update the state

        # Bus operation
        env.bus[0] = f'---'

        # Data source
        env.data_source = f'Cache {current_CPU}'


        return 'read hit'



def Firefly(env, current_CPU, current_operation):

    # Write miss
    if current_operation == 'write' and env.cpu_caches[current_CPU] == None:

        # There is a Dirty in some other cache
        if 'Dirty' in env.cpu_caches:
            env.cpu_caches[current_CPU] = 'Shared'
            dirty_idx = env.cpu_caches.index('Dirty') # This will not error, because we know it exists (the codition above)
            env.cpu_caches[dirty_idx] = 'Shared' # Update the other copy to shared

            # Show the source
            env.data_source = f'Processor {current_CPU}'

        # There is a Valid_exclusive in some other cache
        elif 'Valid_exclusive' in env.cpu_caches:
            env.cpu_caches[current_CPU] = 'Shared'
            VE_idx = env.cpu_caches.index('Valid_exclusive') # This will not error, because we know it exists (the codition above)
            env.cpu_caches[VE_idx] = 'Shared' # Update the other copy to shared

            # Show the source
            env.data_source = f'Processor {current_CPU}'

        # There is a Shared in some other cache
        elif 'Shared' in env.cpu_caches:
            env.cpu_caches[current_CPU] = 'Shared'

            # Show the source
            env.data_source = f'Processor {current_CPU}'

        # The block is not in any other cache
        else:
            # Update the state
            env.cpu_caches[current_CPU] = 'Dirty'

            #  Show the source
            env.data_source = f'Memory'

        # Put the bus operation
        env.bus[0] = f'Read-Blk(C{current_CPU}), value(P{current_CPU})'

        return 'write miss'

    # Read miss
    if current_operation == 'read' and env.cpu_caches[current_CPU] == None:

        # Update the current state
        # There is a Dirty in some other cache
        if 'Dirty' in env.cpu_caches:
            env.cpu_caches[current_CPU] = 'Shared'
            dirty_idx = env.cpu_caches.index('Dirty') # This will not error, because we know it exists (the codition above)
            env.cpu_caches[dirty_idx] = 'Shared' # Update the other copy to shared

            # Show the source
            env.data_source = f'Cache {dirty_idx}'

        # There is a Valid_exclusive in some other cache
        elif 'Valid_exclusive' in env.cpu_caches:
            env.cpu_caches[current_CPU] = 'Shared'
            VE_idx = env.cpu_caches.index('Valid_exclusive') # This will not error, because we know it exists (the codition above)
            env.cpu_caches[VE_idx] = 'Shared' # Update the other copy to shared

            # Show the source
            env.data_source = f'Cache {VE_idx}'

        # There is a Shared in some other cache
        elif 'Shared' in env.cpu_caches:

            shared_idx = [i for i, x in enumerate(env.cpu_caches) if x == "Shared"]
            env.cpu_caches[current_CPU] = 'Shared'

            #shared_idx = env.cpu_caches.index('Shared') # This will not error, because we know it exists (the codition above)

            # Show the source
            env.data_source = f'Cache {shared_idx}'

        # The block is not in any other cache
        else:
            # Update the state
            env.cpu_caches[current_CPU] = 'Valid_exclusive'

            #  Show the source
            env.data_source = f'Memory'

        # Put the bus operation
        env.bus[0] = f'Read-Blk(C{current_CPU})'

        return 'read miss'

    # Write hit
    if current_operation == 'write' and env.cpu_caches[current_CPU] != None:

        # These are done locally
        if env.cpu_caches[current_CPU] == 'Dirty':

            # No need to update the state

            # Put the bus operation
            env.bus[0] = f'---'


        elif env.cpu_caches[current_CPU] == 'Valid_exclusive':

            # Update the state locally
            env.cpu_caches[current_CPU] = 'Dirty'

            # Put the bus operation
            env.bus[0] = f'---'


        elif env.cpu_caches[current_CPU] == 'Shared':

            # It continues to be shared

            # Put the bus operation
            env.bus[0] = f'Read-Blk(C{current_CPU}), value(P{current_CPU})'

        # Show the source
        env.data_source = f'Processor {current_CPU}'

        return 'write hit'


    # Read hit
    if current_operation == 'read' and env.cpu_caches[current_CPU] != None:

        # Read hits are done locally 

        # Put the bus operation
        env.bus[0] = f'---'

        # Show the source
        env.data_source = f'Cache {current_CPU}'

        return 'read hit'

def MSI(env, current_CPU, current_operation):

    # Data source: we don't care about it here
    env.data_source = f'-'

    # Write miss
    if current_operation == 'write' and (env.cpu_caches[current_CPU] == None or env.cpu_caches[current_CPU] == 'Invalid'):

        if 'Modified' in env.cpu_caches:
            mod_idx = env.cpu_caches.index('Modified')

            # Invalidade the caches
            env.invalidate_caches('Invalid')

            # Update the state
            env.cpu_caches[current_CPU] = 'Modified'

            # Bus operation
            env.bus[0] = f'BusRdX(C{current_CPU}), Flush(C{mod_idx})'

        elif 'Shared' in env.cpu_caches:

            # Get all the caches that have a shared block
            shared_idx = [i for i, x in enumerate(env.cpu_caches) if x == "Shared"]

            # Invalidade the caches
            env.invalidate_caches('Invalid')

            # Update the state
            env.cpu_caches[current_CPU] = 'Modified'

            # Bus operation
            env.bus[0] = f'BusRd(C{current_CPU}), Flush(C {shared_idx})'
    
        # There is no Shared or Modified
        else:
            # Update the state
            env.cpu_caches[current_CPU] = 'Modified'

            # Bus operation
            env.bus[0] = f'BusRdX(C{current_CPU})'

        return 'write miss'

    # Read miss
    if current_operation == 'read' and (env.cpu_caches[current_CPU] == None or env.cpu_caches[current_CPU] == 'Invalid'):

        if 'Modified' in env.cpu_caches:

            mod_idx = env.cpu_caches.index('Modified')

            # Update the state
            env.cpu_caches[current_CPU] = 'Shared'
            env.cpu_caches[mod_idx] = 'Shared'

            # Bus operation
            env.bus[0] = f'BusRd(C{current_CPU}), Flush(C{mod_idx})'

        elif 'Shared' in env.cpu_caches:

            # Get all the caches that have a shared block
            shared_idx = [i for i, x in enumerate(env.cpu_caches) if x == "Shared"]

            # Update the state
            env.cpu_caches[current_CPU] = 'Shared'

            # Bus operation
            env.bus[0] = f'BusRd(C{current_CPU}), Flush(C {shared_idx})'

        # There is no Shared or Modified
        else:
            # Update the state
            env.cpu_caches[current_CPU] = 'Shared'

            # Bus operation
            env.bus[0] = f'BusRd(C{current_CPU})'

        return 'read miss'

    # Write hit
    if current_operation == 'write' and env.cpu_caches[current_CPU] != None and env.cpu_caches[current_CPU] != 'Invalid':

        if env.cpu_caches[current_CPU] == 'Modified':
            # No need to update the state

            # Bus operation
            env.bus[0] = f'---'

        elif env.cpu_caches[current_CPU] == 'Shared':

            # Invalidade the caches
            env.invalidate_caches('Invalid')

            # Update the state
            env.cpu_caches[current_CPU] = 'Modified'

            # Bus operation
            env.bus[0] = f'BusRdX(C{current_CPU})'

        return 'write hit'


    # Read hit
    if current_operation == 'read' and env.cpu_caches[current_CPU] != None and env.cpu_caches[current_CPU] != 'Invalid':

        # No need to update the state

        # Bus operation
        env.bus[0] = f'---'

        return 'read hit'

def MESI(env, current_CPU, current_operation):

    # Data source: we don't care about it here
    env.data_source = f'-'

    # Write miss
    if current_operation == 'write' and (env.cpu_caches[current_CPU] == None or env.cpu_caches[current_CPU] == 'Invalid'):

        if 'Modified' in env.cpu_caches:
            mod_idx = env.cpu_caches.index('Modified')

            # Invalidade the caches
            env.invalidate_caches('Invalid')

            # Update the state
            env.cpu_caches[current_CPU] = 'Modified'

            # Bus operation
            env.bus[0] = f'BusRdX(C{current_CPU}), Flush(C{mod_idx})'

        elif 'Exclusive' in env.cpu_caches:

            exc_idx = env.cpu_caches.index('Exclusive')

            # Update the state
            env.cpu_caches[current_CPU] = 'Modified'
            env.cpu_caches[exc_idx] = 'Invalid'

            # Bus operation
            env.bus[0] = f'BusRdX(C{current_CPU}), Flush(C{exc_idx})'

        elif 'Shared' in env.cpu_caches:

            # Get all the caches that have a shared block
            shared_idx = [i for i, x in enumerate(env.cpu_caches) if x == "Shared"]

            # Invalidade the caches
            env.invalidate_caches('Invalid')

            # Update the state
            env.cpu_caches[current_CPU] = 'Modified'

            # Bus operation
            env.bus[0] = f'BusRd(C{current_CPU}), Flush(C {shared_idx})'
    
        # There is no Shared or Modified
        else:
            # Update the state
            env.cpu_caches[current_CPU] = 'Modified'

            # Bus operation
            env.bus[0] = f'BusRdX(C{current_CPU})'

        return 'write miss'

    # Read miss
    if current_operation == 'read' and (env.cpu_caches[current_CPU] == None or env.cpu_caches[current_CPU] == 'Invalid'):

        if 'Modified' in env.cpu_caches:

            mod_idx = env.cpu_caches.index('Modified')

            # Update the state
            env.cpu_caches[current_CPU] = 'Shared'
            env.cpu_caches[mod_idx] = 'Shared'

            # Bus operation
            env.bus[0] = f'BusRd(S)(C{current_CPU}), Flush(C{mod_idx})'

        elif 'Exclusive' in env.cpu_caches:

            exc_idx = env.cpu_caches.index('Exclusive')

            # Update the state
            env.cpu_caches[current_CPU] = 'Shared'
            env.cpu_caches[exc_idx] = 'Shared'

            # Bus operation
            env.bus[0] = f'BusRd(S)(C{current_CPU}), Flush(C{exc_idx})'

        elif 'Shared' in env.cpu_caches:

            # Get all the caches that have a shared block
            shared_idx = [i for i, x in enumerate(env.cpu_caches) if x == "Shared"]

            # Update the state
            env.cpu_caches[current_CPU] = 'Shared'

            # Bus operation
            env.bus[0] = f'BusRd(S)(C{current_CPU}), Flush(C {shared_idx})'

        # There is no Shared or Modified
        else:
            # Update the state
            env.cpu_caches[current_CPU] = 'Exclusive'

            # Bus operation
            env.bus[0] = f'BusRd(~S)(C{current_CPU})'

        return 'read miss'

    # Write hit
    if current_operation == 'write' and env.cpu_caches[current_CPU] != None and env.cpu_caches[current_CPU] != 'Invalid':

        if env.cpu_caches[current_CPU] == 'Modified':
            # No need to update the state

            # Bus operation
            env.bus[0] = f'---'

        elif env.cpu_caches[current_CPU] == 'Exclusive':
            # Update the state
            env.cpu_caches[current_CPU] = 'Modified'

            # Bus operation
            env.bus[0] = f'---'

        elif env.cpu_caches[current_CPU] == 'Shared':

            # Invalidade the caches
            env.invalidate_caches('Invalid')

            # Update the state
            env.cpu_caches[current_CPU] = 'Modified'

            # Bus operation
            env.bus[0] = f'BusRdX(C{current_CPU})'

        return 'write hit'


    # Read hit
    if current_operation == 'read' and env.cpu_caches[current_CPU] != None and env.cpu_caches[current_CPU] != 'Invalid':

        # No need to update the state

        # Bus operation
        env.bus[0] = f'---'

        return 'read hit'
    
def execute_algorithm(number_of_CPUs, operations_sequence, cache_coherence_algorithm):

    # Initialize an empty env
    env = Env(number_of_CPUs)

    print(f'{"Action":25s} {"CPUs caches":40s} {"Bus":35s} {"Data source":20s} {"Cache"} \n{"-"*140}\n')

    # Run each operation
    for operation in operations_sequence:

        # All cache algorithms must have the same args
        cache_op = cache_coherence_algorithm(env, operation.cpu, operation.action)

        env.print_current_state(operation, cache_op)

        # Restart the bus and the source
        env.clear_bus_source()

    print(f'\n{"-"*140}\n')

execute_algorithm(3, operations_sequence, write_once)
execute_algorithm(3, operations_sequence, Firefly)
execute_algorithm(3, operations_sequence, MSI)
execute_algorithm(3, operations_sequence, MESI)

