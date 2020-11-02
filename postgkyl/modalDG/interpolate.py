import numpy as np
#from postgkyl.data.data import Data

from postgkyl.modalDG.kernels import expand_1d, expand_2d, expand_3d, expand_4d, expand_5d, expand_6d

def interpolate(data, polyOrder=None, nodes=None, externalGrid=None):
    if polyOrder is None and data.polyOrder is not None:
        polyOrder = data.polyOrder
    else:
        # Something bad happened :D
        pass
    #end

    # Read grid information from input file.
    numDims = data.getNumDims()
    lower, upper = data.getBounds()
    numCells = data.getNumCells()
    
    # If user specifies an interpolation grid, use it. Otherwise calculate. 
    if externalGrid:
        intGrid = externalGrid
    else:
        intGrid = [np.linspace(lower[d],
                               upper[d],
                               numCells[d]*(polyOrder+1)+1)
                   for d in range(numDims)]
    #end

    # Calculate interpolation nodes for each element.
    if not nodes:
        dx = 2/(polyOrder+1)
        nodes = np.linspace(-1+dx/2, 1-dx/2, polyOrder+1)
    #end    
    
    # Set up array for interp node values
    values = data.getValues()
    intValues = np.zeros(np.int32(numCells*len(nodes)))
    intValues = intValues[..., np.newaxis]


    # Iterating through the node list, calculate value at each node for each element 
    # simultaneously, one dimension at a time.
    # TODO: Rework for numDims > 3, currently very slow.
    if numDims == 1:
        for i, x in enumerate(nodes):
            intValues[i::len(nodes), 0] = expand_1d[int(polyOrder-1)](values, x)
        #end
        
    elif numDims == 2:
        for i, x in enumerate(nodes):
            for j, y in enumerate(nodes):
                intValues[i::len(nodes), j::len(nodes), 0] = expand_2d[int(polyOrder-1)](values, x, y)
            #end
        #end
    #end
    
    elif numDims == 3:
        for i, x in enumerate(nodes):
            for j, y in enumerate(nodes):
                for k, z in enumerate(nodes):
                    intValues[i::len(nodes), j::len(nodes), k::len(nodes), 0] = expand_3d[int(polyOrder-1)](values, x, y, z)
                #end
            #end
        #end
    #end
    
    elif numDims == 4:
        for i, x in enumerate(nodes):
            for j, y in enumerate(nodes):
                for k, z in enumerate(nodes):
                    for l, r in enumerate(nodes):
                        intValues[i::len(nodes), j::len(nodes), k::len(nodes), l::len(nodes), 0] = expand_4d[int(polyOrder-1)](values, x, y, z, r)
                    #end
                #end
            #end
        #end
    #end
    
    elif numDims == 5:
        for i, x in enumerate(nodes):
            for j, y in enumerate(nodes):
                for k, z in enumerate(nodes):
                    for l, r in enumerate(nodes):
                        for m, s in enumerate(nodes):
                            intValues[i::len(nodes), j::len(nodes), k::len(nodes), l::len(nodes), m::len(nodes), 0] = expand_5d[int(polyOrder-1)](values, x, y, z, r, s)
                         #end       
                    #end
                #end
            #end
        #end
    #end
        
    elif numDims == 6:
        for i, x in enumerate(nodes):
            for j, y in enumerate(nodes):
                for k, z in enumerate(nodes):
                    for l, r in enumerate(nodes):
                        for m, s in enumerate(nodes):
                            for n, t in enumerate(nodes):
                                intValues[i::len(nodes), j::len(nodes), k::len(nodes), l::len(nodes), m::len(nodes), n::len(nodes), 0] = expand_6d[int(polyOrder-1)](values, x, y, z, r, s, t)
                         #end       
                    #end
                #end
            #end
        #end
    #end
    
    # Hardcoded stack 
    data.pushGrid(intGrid)
    data.pushValues(intValues)
#end