import threading
import multiprocessing


class UI:
    # TODO: fill with comments
    def __init__(self, input_pipe, output_pipe, killer):

        self.userInput = ''
        self.inPipe = input_pipe
        self.outPipe = output_pipe
        self.kill = killer

    def start(self):

        self.listener = threading.Thread(target=self.userInputLoop)
        self.listener.daemon = True
        self.listener.start()
        self.commandLoop()

    def userInputLoop(self):

        while not self.kill.kill:
              
            self.userInput = input()  
                  
                

    def commandLoop(self):
        pipeData = ''
        self.outPipe.send([0])

        while not self.kill.kill:            

            if self.inPipe.poll():
                pipeData = self.inPipe.recv()
            try:
                input = self.userInput.split(".")

                if input[0] == 'quit':
                    self.outPipe.send('quit')
                    self.kill.kill = True

                if input[0] == 'agents':
                    for i in pipeData:
                        print("{} : {}".format(i, pipeData[i].ip))
                if input[0] in pipeData:
                    if input[1] == 'ip':
                        print(pipeData[input[0]].ip)
                    if input[1] == 'type':
                        print(pipeData[input[0]].vehicleType)
                    if input[1] == 'mode':
                        print(pipeData[input[0]].mode)
                    if input[1] == 'rate':
                        print(pipeData[input[0]].upateRate)

                if input[0] == 'set' and len(input) == 4:
                    # name   #parameter  #newvalue
                    inst = [input[1], input[2], input[3]]
                    self.outPipe.send(inst)

                

            except:
                pass

            else:
                pass

            self.userInput = ''
        self.outPipe.send('quit')

    def dummyfunction(self):
        whatisthisnotworking = 1
