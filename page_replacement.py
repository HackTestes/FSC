import math

# Parameters
qtd_page_frames = 3
page_references_sequence = [0, 1, 7, 2, 3, 2, 7, 1, 0, 3]

# Note: this code might not be efficient, but helps to understand the algorithm
# (other data structures might be used to improve it)
def FIFO(qtd_page_frames, page_references_sequence):
    page_fault_counter = 0

    # Each index represents a frame
    queue = []

    # Simulating the page requests
    for page in page_references_sequence:

        page_fault = False

        # Verify if the frames have the page
        if not (page in queue):

            page_fault = True
            page_fault_counter += 1
        
            # If not, add it to the queue
            if (len(queue) < qtd_page_frames):
                queue.append(page)

            # If full, remove the fist element and add the new page to the end
            else:
                queue.pop(0)
                queue.append(page)

        # The frames have the page
        # does nothing
        print(f' Queue: {queue}\n Page fault: {page_fault}\n Page: {page}\n\n')

    print(f'Number of page faults: {page_fault_counter}')


def LRU(qtd_page_frames, page_references_sequence):
    page_fault_counter = 0

    # Each index represents a frame
    queue = [] # Not exactly a queue here, since we can remove an element from the middle (let's say it is an almost queue)

    # Simulating the page requests
    for page in page_references_sequence:

        page_fault = False

        # Verify if the frames have the page
        if not (page in queue):

            page_fault = True
            page_fault_counter += 1
        
            # If not, add it to the queue
            if (len(queue) < qtd_page_frames):
                queue.append(page)

            # If full, remove the fist element and add the new page to the end
            # This time, the first element is the least used, since this list is organized by references
            else:
                queue.pop(0)
                queue.append(page) # Last referenced page

        # The frames have the page - update the references
        else:
            # Get page index in the list
            idx = queue.index(page)

            # Remove the page and put it on the top (treat it like a new page)
            queue.pop(idx)
            queue.append(page)
        
        print(f' Frames: {queue}\n Page fault: {page_fault}\n Page: {page}\n\n')

    print(f'Number of page faults: {page_fault_counter}')


def Optimal(qtd_page_frames, page_references_sequence):
    page_fault_counter = 0

    # Each index represents a frame
    page_list = []

    # Simulating the page requests
    for current_page_idx, page in enumerate(page_references_sequence):

        page_fault = False

        # Verify if the frames have the page
        if not (page in page_list):

            page_fault = True
            page_fault_counter += 1
        
            # If not, add it to the page_list
            if (len(page_list) < qtd_page_frames):
                page_list.append(page)

            # If full, remove the page that will take longer to be referenced
            else:
                # Get the next reference index for each page and for the one that should be replaced
                # We store this list to help with visualization
                page_nextRef = []
                page_replace = dict(page=-1, next_ref=-1, index=-1)

                for page_list_idx, page_in_list in enumerate(page_list):
    
                    # Current page next_ref
                    next_ref = -1 # -1 is an invalid position, this is just for the initialization
                    try:
                        # Start the search at the current position
                        next_ref = page_references_sequence.index(page_in_list, current_page_idx)
                    
                    # If we can't find the value, it should be +infinity (will no be referenced anymore)
                    except ValueError:
                        next_ref = math.inf

                    page_nextRef.append( (page_in_list, next_ref) )

                    # If it has a highest next_ref, update it
                    # It they are equal, the first will be used
                    # > : the first element will stay
                    # >= : store the last element
                    if next_ref > page_replace['next_ref']:
                        page_replace = dict(page=page_in_list, next_ref=next_ref, index=page_list_idx)

                print(f' Pages and the next reference: {page_nextRef}\n Page to be replaced: {page_replace}', end='\n')

                # Select the page that will take the longest to be referenced
                # (The one with the highest ref index basically)
                # and change the page
                page_list[ page_replace['index'] ] = page


        # The frames have the page
        # Do nothing
        
        print(f' Page list: {page_list}\n Page fault: {page_fault}\n Page: {page}\n\n')

    print(f'Number of page faults: {page_fault_counter}')


print('\n----------------------------FIFO----------------------------\n')
FIFO(qtd_page_frames, page_references_sequence)

print('\n----------------------------LRU----------------------------\n')
LRU(qtd_page_frames, page_references_sequence)

print('\n----------------------------OPTIMAL----------------------------\n')
Optimal(qtd_page_frames, page_references_sequence)

