import math

# This should simulate the behaviour of an MMU unit

# page_table
# page_table[page_num] = frame_num

page_table = [None]*10

# Easier to see which pages are associated to each frame
page_table[0] = 2
page_table[1] = 1
page_table[2] = 0
page_table[3] = 5

# Page size in BYTES
page_size = 1024

# This calculation is not accurate to the hardware, but helps with calculations
# done by-hand
def get_physical_add(page_table, page_size, virtual_add):
    page_num = math.floor(virtual_add/page_size)
    frame = page_table[page_num]

    if frame == None:
        return 'Page Fault'

    # Page offset == deslocamento
    page_offset = virtual_add % page_size

    physical_add = page_offset + frame*1024

    return {'virtual_add': virtual_add, 'physical_add': physical_add, 'page_offset': page_offset, 'page': page_num, 'frame': frame}

# Slides
print(get_physical_add(page_table, page_size, 3900))
print(get_physical_add(page_table, page_size, 12))

print(get_physical_add(page_table, page_size, 1024))
print(get_physical_add(page_table, page_size, 2789))
print(get_physical_add(page_table, page_size, 3984))


