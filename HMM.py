

import random
import argparse
import codecs
import os
import numpy
import sys

# Sequence - represents a sequence of hidden states and corresponding
# output variables.

class Sequence:
    def __init__(self, stateseq, outputseq):
        self.stateseq  = stateseq   # sequence of states
        self.outputseq = outputseq  # sequence of outputs
    def __str__(self):
        return ' '.join(self.stateseq)+'\n'+' '.join(self.outputseq)+'\n'
    def __repr__(self):
        return self.__str__()
    def __len__(self):
        return len(self.outputseq)

# HMM model
class HMM:
    def __init__(self, transitions={}, emissions={}):
        """creates a model from transition and emission probabilities
        e.g. {'happy': {'silent': '0.2', 'meow': '0.3', 'purr': '0.5'},
              'grumpy': {'silent': '0.5', 'meow': '0.4', 'purr': '0.1'},
              'hungry': {'silent': '0.2', 'meow': '0.6', 'purr': '0.2'}}"""

        self.transitions = transitions
        self.emissions = emissions

    def load(self, basename):
        """reads HMM structure from transition (basename.trans),
        and emission (basename.emit) files,
        as well as the probabilities."""
        loop = 0
        while loop < 2 :
            if loop == 0 :
                reading_file = open(basename + ".trans", 'r')
            else :
                reading_file = open(basename + ".emit", 'r')
            for line in reading_file:
                splitted = line.split(" ")
                if loop == 0:
                    if splitted[0] not in self.transitions:
                        self.transitions[splitted[0]] = {}
                    self.transitions[splitted[0]][splitted[1]] = splitted[2].strip()
                else:
                    if splitted[0] not in self.emissions:
                        self.emissions[splitted[0]] = {}
                    self.emissions[splitted[0]][splitted[1]] = splitted[2].strip()
            reading_file.close()
            loop += 1

    def generate(self, n):
        """return an n-length Sequence by randomly sampling from this HMM."""
        if n < 1:
            return Sequence([], [])

        i = 1
        stateseq = []
        outputseq = []
        while i <= n :
            if len(stateseq) == 0 :
                possible_next_states = self.transitions["#"]
            else :
                possible_next_states = self.transitions[stateseq[-1]]

            next_state = random.choices(list(possible_next_states.keys()), weights = [float(weight) for weight in possible_next_states.values()], k=1)
            stateseq.append(next_state[0])
            emission = random.choices(list(self.emissions[next_state[0]].keys()), weights = [float(weight) for weight in self.emissions[next_state[0]].values()], k=1)
            outputseq.append(emission[0])
            i += 1

        return Sequence(stateseq, outputseq)

    def forward(self, sequence):

        vertibi_matrix = [[]]
        vertibi_matrix[0].append(1.0)
        for possible_emission in self.emissions.keys():
            vertibi_matrix[0].append(float(0.0))

        for index in range(len(sequence)):
            vertibi_matrix.append([])
            vertibi_matrix[index + 1].append(float(0.0))
            for possible_emission in self.emissions.keys() :
                if index == 0 :
                    vertibi_matrix[index + 1].append(round(float(self.emissions[possible_emission][sequence[index]]) * float(self.transitions["#"][possible_emission]), 3))
                else :
                    inner_index = 1
                    p_list = []
                    for prev_emission in self.emissions.keys():
                        p_list.append(float(self.emissions[possible_emission][sequence[index]]) * float(self.transitions[prev_emission][possible_emission]) * vertibi_matrix[index][inner_index])
                        inner_index += 1
                    vertibi_matrix[index + 1].append(sum(p_list))


        return vertibi_matrix
    ## you do this: Implement the Viterbi algorithm. Given a Sequence with a list of emissions,
    ## determine the most likely sequence of states.






    def viterbi(self, sequence):
        pass
    ## You do this. Given a sequence with a list of emissions, fill in the most likely
    ## hidden states using the Viterbi algorithm.

if __name__ == "__main__" :

    base_name = 'cat'
    sequence_length = 20
    if len(sys.argv) < 1:
        print("Usage: HMM.py basename (such that basename.emit and basename.py)")
        sys.exit(-1)

    try:
        base_name = sys.argv[1]
    except:
        print("Usage: HMM.py basename (such that basename.emit and basename.py)")
        sys.exit(-1)
    h = HMM()
    h.load(base_name)

    if "--generate" in sys.argv :
        try:
            sequence_length = int(sys.argv[sys.argv.index("--generate") + 1])
            sequence = h.generate(sequence_length)
            print(" ".join(sequence.stateseq))
            print(" ".join(sequence.outputseq))
        except:
            print("Usage: HMM.py basename (such that basename.emit and basename.py)")
            print("Optional parameters include --generate [int] to specify the length of the sequence")
            sys.exit(-1)

    if "--forward" in sys.argv :
        print(h.forward(["purr", "silent", "silent", "meow", "meow"]))

    if "--vertibi" in sys.argv:
        print("WOW")
