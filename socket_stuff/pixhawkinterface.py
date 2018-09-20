
from dronekit import connect, Vehicle
import json

class Drone(Vehicle):

    def __init__(self, *args):

        super(Drone, self).__init__(*args)
        self.sendDict = {}

    def toJSON(self):


        return json.dumps(self.sendDict, default=lambda o: o.__dict__)

    def updateDict(self):

        self.sendDict = {"global_loc": self.location.global_frame}



if __name__=="__main__":

    uav = connect('/dev/ttyACM0', wait_ready=True, vehicle_class=Drone)
    uav.updateDict()

    a = uav.toJSON()

    print(a)












