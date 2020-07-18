
def _index(user_list, id):
    """ 
    Given a list of tuples the first element of which is user id,
    return the index of the user whose id matches id.
    """
    
    print("_index:user_list")
    print (user_list)
    for i in range(len(user_list)):
        if user_list[i][0] == id: return i 
        
    return None

def _next_vwork_index(vworks, vwork_val):
    """
    Return the index where a vwork with value vwork_val should be 
    placed.
    """

    i = 0
    length = len(vworks)
    for i in range(length):
        if vwork_val < vworks[i][1]: return i
    return length


def _next_user_get(vworks, last_by=None):
    """
    Gets id of next user that needs to complete a chore. Expects a 
    list of sorted vworks.

    If empty list provided, returns None, otherwise, returns id 
    of next user scheduled to work. 

    If last_by provided equal to first user on the list, returns 
    next_user.
    """


    # if no user provided, then nobody is scheduled
    if(not(vworks)): return None

    # Return first user if only one user in list
    if(len(vworks) == 1): return vworks[0][0]

    # Otherwise return last user not in list
    for user in vworks:   
        if user[0] != last_by:
            return user[0]
    
    return None



def _order_project(vworks, vdeltas, interval, initial_offset, last_by=None, period=90):
    """
    Given 
        a set of vworks, 
        a set of vdeltas, 
        a chore interval in days, 
        an initial offset in days for the next chore,
        a time period in days, 
    return a list of tuples of user id and scheduled offsets from 
    the present day.
    """
    # TODO: Write an implementation of this function with red-black 
    # tree

    # Replace vworks with a copy of vworks
    vworks = vworks[:]

    # If neither the lists nor interval is provided , return nothing
    
    if(not(vworks and vdeltas and interval)): return None
    
    order_projection = []
    elapsed_time = initial_offset

    while(elapsed_time <= period):
        # Get id of next person in queue
        last_by = _next_user_get(vworks, last_by)

        # Update the order projection based with retrieved id
        order_projection.append((last_by, elapsed_time))
        
        # Update value of user's vwork
        print("_order_project:last_by : ")
        print(last_by)
        print("order_project:index of last_by")
        print(_index(vworks, last_by))
        vwork = vworks.pop(_index(vworks, last_by)) 
        vwork = (vwork[0], vwork[1] + vdeltas[_index(vdeltas, last_by)][1])
        
        # Insert vwork into appropriate position in the list
        vworks.insert(_next_vwork_index(vworks, vwork[1]), vwork)

        # Update elapsed time 
        elapsed_time += interval 
    
    return order_projection




 """   
Run with: 

from common.util.simplecfsscheduler import _test
_test()

"""
def _test():
    TEST_last_by = 1
    print(TEST_last_by)
    #TEST_vworks = [(1, 25), (2, 45), (3,30), (4,60), (5, 10)]
    #TEST_vworks = [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]
    TEST_vworks = [(1,0)]
    
    #TEST_vdeltas = [(1, 3.0), (2, 0.5), (3, 1), (4, 2.0), (5, 1)]
    TEST_vdeltas = [(1, 2.0), (2, 1.0), (3, 1.0), (4, 1.0), (5, 0.25)]

    print(TEST_vworks)
    print("Next user when no last by:")
    print(_next_user_get(vworks = sorted(TEST_vworks, key = lambda user: user[1])) )
    print("Next user when last by exists:")
    print(_next_user_get(vworks = sorted(TEST_vworks, key = lambda user:user[1]), last_by = TEST_last_by))

    print("Order of users and offsets with initial offset of 2")
    print(_order_project(sorted(TEST_vworks), TEST_vdeltas, 5, 2, TEST_last_by))

    