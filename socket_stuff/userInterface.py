import _thread
import multiprocessing




class UI:

    def __init__(self, input_pipe, output_pipe):

        self.userInput = ''
        self.inPipe = input_pipe
        self.outPipe = output_pipe


    def start(self):
        self.listener = _thread.start_new_thread(self.userInputLoop, ())
        self.commandLoop()

    def userInputLoop(self):

        while True:
            self.userInput = input()

    def commandLoop(self):
        pipeData = ''
        self.outPipe.send(0)
        while True:
            if self.inPipe.poll():
                pipeData = self.inPipe.recv()
            try:
                input = self.userInput.split(".")

                if input[0] != '':
                    print (len(input))
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
                            #name   #parameter  #newvalue
                    inst = [input[1],input[2],input[3]]
                    self.outPipe.send(inst)


            except:
                pass


            else:
                pass

            self.userInput = ''