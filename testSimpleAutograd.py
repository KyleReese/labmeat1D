import autograd.numpy as np
import autograd.scipy.signal as sig
from autograd import grad
from autograd.builtins import tuple
import matplotlib.pyplot as plt

HowManyCells = 51
values = np.zeros((HowManyCells))
# values[HowManyCells//2] = 10
def doPDE(values, movablePts):
    #movablePts = list(movablePts)
    # Update the values based on diffusion of the proteins to nearby cells
    D = 0.1#get the diffusion parameter
    adjustmentPDE = D * nonLinearAdjustment(movablePts)
    #print(nonLinearAdjustment(movablePts))
    #simple diffusion is just a convolution
    convolveLinear = np.array([1*D,-2*D,1*D]) 
    # accumulate the changes due to diffusion 
    for rep in range(0, 50):
        #linear diffusion
        values =  values + sig.convolve(values, convolveLinear)[1:-1] #take off first and last
        # non-linear diffusion, add the adjustment
        values = values + np.multiply(values, adjustmentPDE)
        # add source at each iteration
        values = values + addSources(movablePts)
    # the total update returned is the difference between the original values and the values after diffusion
    return values
    
def addSources(moveablePts):
    sources = np.zeros((HowManyCells))
    for x in moveablePts:
        try:
            xIndex = int(x)
        except:
            xIndex = int(x._value)
        one = np.array([0]*xIndex + [1] + [0]*(HowManyCells - xIndex-1))
        sources = one + sources
    return sources
    
############################################################################
### Non Linear PDE 
def nonLinearAdjustment(movablePts):
    # adds an adjustment to the material transfer to take into account
    # the actural position of the cell point in space
    # adjustment is constant for each simulation, because the points do
    # not move so compute once
    allAdjustment = np.zeros(HowManyCells)
    # print("points")
    # print(movablePts)
    for x in list(movablePts): #only single numbers in x one D
        try:
            pointI = int(x)
        except:
            pointI = int(x._value)
        thisAdj= []
        totalAdj =0 # accumulate the changes around the center point
        for xI in range(0, HowManyCells):
            # find the array locations just before or just after the moveable point
            if ((pointI == xI - 1 and pointI > 0) or           
                (pointI == xI + 1 and pointI < HowManyCells)): 
                deltaConc = distToConc(abs(x - (xI+0.5))) #distance off from the center
                thisAdj.append(deltaConc) 
                totalAdj = totalAdj + deltaConc #accun
            # Otherwise no adjustment   
            else:
                thisAdj.append(0) 
        #print(thisAdj)
        #accumulate this movable point into the total adjustment 
        allAdjustment = allAdjustment + np.array(thisAdj)
    return allAdjustment
        
def distToConc(distance):
    # maps the distance between two points (in thise case one dimention)
    # positive closer, zero if 1, negative if further away
    return 1 - distance
    
def fitness(moveablePts):
    global values
    values = np.zeros((HowManyCells))
    values = doPDE(values, moveablePts)
    return(values[10])
    
    

# print(doPDE(values, (25.99, 3.4)))
# print(fitness((25.99, 3.4)))
if __name__ == "__main__":
    allLoss = []
    stepSize = 0.1

    fig = plt.figure(figsize=(16, 4), facecolor='white')
    ax_loss         = fig.add_subplot(151, frameon=True)
    ax_values       = fig.add_subplot(152, frameon=True)
    # ax_img          = fig.add_subplot(153, frameon=True)
    # ax_diffused_img = fig.add_subplot(154, frameon=True)
    # ax_loss_map     = fig.add_subplot(155, frameon=True)

    def callback(mvable_pts, iter, nowLoss):
        global values
        # ==================================== #
        # ==== LOSS as a function of TIME ==== #
        # ==================================== #
        ax_loss.cla()
        ax_loss.set_title('Train Fitness')
        ax_loss.set_xlabel('t')
        ax_loss.set_ylabel('fitness')
        allLoss.append(nowLoss)
        time = np.arange(0, len(allLoss), 1)
        ax_loss.plot(time, allLoss, '-', linestyle = 'solid', label='fitness') #, color = colors[i]
        ax_loss.set_xlim(time.min(), time.max())
        ax_loss.legend(loc = 'upper left')
        # print('moveable points:', mvable_pts)
        
        ax_values.cla()
        ax_values.set_title('Values')
        ax_loss.set_xlabel('position')
        ax_loss.set_ylabel('value')
        ax_values.plot(values)
        # print('values', values)

        plt.draw()
        plt.pause(0.001)
        return 3

    gradPDE = grad(fitness)
    # print(gradPDE((25.99, 3.4)))
    mvable_pts = [3.4, 17.99]

    for i in range(350):
        grad_pts = gradPDE(mvable_pts)
        print(grad_pts)
        mvable_pts = list(np.array(mvable_pts) + np.array(grad_pts)* stepSize)

        newfitness = fitness(mvable_pts)
        print('loss', newfitness)
        callback(mvable_pts, i, newfitness)
    #print(values)