############################################################################
############################ PREPROCESS #####################################
############################################################################

lines = []
with open('Topology.txt') as f:
    lines = f.readlines()

#print(lines)

network=dict()
#lines=['10.1.2.10\n', '2\n', '10.1.3.10\t2\n', '10.1.5.10\t1\n', 'End']
length=len(lines)
c=0
while c<length:
    current_node=lines[c][:-1]
    network[current_node]=dict()
    c=c+1
    no_of_edges=(lines[c][:-1])
    no_of_edges=int(no_of_edges)
    c=c+1
    for i in range(no_of_edges):
        str=lines[c]
        lis=str.split("\t")
        destination_node=lis[0]
        weight=int(lis[1][:-1])
        network[current_node][destination_node]=weight
        c=c+1
    c=c+1    
#print(network)


############################################################################
############################ BellmanFord Algo ##############################
############################################################################

def findHop(pred, src, current):
    temp = current
    while(current != src):
        temp = current
        current = pred[current]
    return temp 

def myFunc(ip):
    pred = {}
    distances = {}
    for router in network:
        distances[router] = float('inf')
        pred[router] = None
    distances[ip] = 0
    pred[ip] = ip    
    
    for i in range(len(network)-1):
        for u in network:
            for v in network[u]:
                #print(f"u:{u}, dist_u:{distances[u]}    v:{v}, dist_v:{distances[v]},   u-v:{network[u][v]},    check:{distances[u] + network[u][v] < distances[v]}")
                if distances[u] + network[u][v] < distances[v]:
                    distances[v] = distances[u] + network[u][v]
                    pred[v] = u

    # print(distances)
    # print(pred)

    hop = {}
    data = {}
    for router in network:
        hop[router] = findHop(pred, ip, router)
        data[router] = {
            'distance': distances[router],
            'hop': hop[router]
        }

    # print(data)
    return data

############################################################################
################################ PART 1 ####################################
############################################################################

def distanceFinder(ip):
    data = myFunc(ip)
    #print(data)
    for router in data:
        print(ip, router, float(data[router]['distance']), data[router]['hop'])


############################################################################
################################ PART 2 ####################################
############################################################################

def updateRouterCost(ip_1, ip_2, new_cost, src_ip):
    old = myFunc(src_ip) 

    network[ip_1][ip_2] = new_cost
    network[ip_2][ip_1] = new_cost

    new = myFunc(src_ip)

    print('Case-1')
    for u,v in zip(old, new): # for u in old --- this also works as u=v
        if(old[u]['distance'] == new[v]['distance']): print(src_ip, u, float(old[u]['distance']), old[u]['hop'] )
    print('Case-2')
    for u,v in zip(old, new): # for u in old --- this also works as u=v
        if(old[u]['distance'] != new[v]['distance']): print(src_ip, u, float(new[v]['distance']), new[v]['hop'] )


############################################################################
################################ PART 3 ####################################
############################################################################

def addRouter(new_ip, neighbours, costs, src_ip):
    temp = {}
    for neighbour, cost in zip(neighbours, costs):
        temp[neighbour] = cost
    
    network[new_ip] = temp
    
    for neighbour, cost in zip(neighbours, costs):
        #print(neighbour, cost)
        network[neighbour][new_ip] = cost

    # print(network)
    distanceFinder(src_ip)


############################################################################
################################ USAGE #####################################
############################################################################

########### UNCOMMENT TO USE ###########

# PART 1
# distanceFinder('10.1.4.10') 

# PART 2
# updateRouterCost('10.1.3.10', '10.1.4.10', 10, '10.1.2.10')

# PART 3
# addRouter('10.1.6.10',{'10.1.5.10', '10.1.4.10'}, {3,4}, '10.1.2.10')
