

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

            next_state = random.choices(list(possible_next_states.keys()),
                                        weights=[float(weight) for weight in possible_next_states.values()], k=1)
            stateseq.append(next_state[0])
            emission = random.choices(list(self.emissions[next_state[0]].keys()),
                                      weights=[float(weight) for weight in self.emissions[next_state[0]].values()], k=1)
            outputseq.append(emission[0])
            i += 1

        return Sequence(stateseq, outputseq)

    def forward(self, sequence):

        sequence_to_return = self.viterbi(sequence)

        if len(sequence_to_return.stateseq) > 0 :
            if sequence_to_return.stateseq[0] == "1,1":
                print(sequence_to_return.stateseq[-1], "is the likely current location")
                if sequence_to_return.stateseq[-1] in ["2,5", "3,4", "4,3", "4,4", "5,5"]:
                    print("SAFE To Land")
                else:
                    print("NOT SAFE To Land")

        return sequence_to_return

    def viterbi(self, sequence) :

        outputseq = sequence.outputseq
        viterbi_matrix = [[]]
        viterbi_matrix[0].append(1.0)
        for possible_emission in self.emissions.keys():
            viterbi_matrix[0].append(float(0.0))

        for index in range(len(outputseq)):
            viterbi_matrix.append([])
            viterbi_matrix[index + 1].append(float(0.0))
            for possible_emission in self.emissions.keys():
                if outputseq[index] not in self.emissions[possible_emission]:
                    float1 = 0.0
                else:
                    float1 = float(self.emissions[possible_emission][outputseq[index]])
                if index == 0:
                    if possible_emission not in self.transitions["#"]:
                        float2 = 0.0
                    else:
                        float2 = float(self.transitions["#"][possible_emission])
                    viterbi_matrix[index + 1].append(float1 * float2)
                else:
                    inner_index = 1
                    p_list = []
                    for prev_emission in self.emissions.keys():
                        if possible_emission not in self.transitions[prev_emission]:
                            float2 = 0.0
                        else:
                            float2 = float(self.transitions[prev_emission][possible_emission])
                        p_list.append(float1 * float2 * viterbi_matrix[index][inner_index])
                        inner_index += 1
                    viterbi_matrix[index + 1].append(sum(p_list))

        likely_sequence = []
        for day in range(len(viterbi_matrix)):
            likely_sequence.append(list(self.emissions.keys())[viterbi_matrix[day].index(max(viterbi_matrix[day])) - 1])

        sequence.stateseq = likely_sequence[1:]
        return sequence

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
    sequence = Sequence([], [])

    if "--generate" in sys.argv :
        try:
            sequence_length = int(sys.argv[sys.argv.index("--generate") + 1])
            sequence = h.generate(sequence_length)
            print("Creating Sequence")
            print("Default Length:", sequence_length)
            print(" ".join(sequence.stateseq))
            print(" ".join(sequence.outputseq))
        except:
            print("Creating Sequence")
            print("Default Length: 10")
            sequence = h.generate(10)
            print(" ".join(sequence.stateseq))
            print(" ".join(sequence.outputseq))

    if "--forward" in sys.argv :

        # Try to access the .obs file
        try:
            file = sys.argv[sys.argv.index("--forward") + 1]
            if file.endswith(".obs"):
                obs_file = open(file)
                sequences = []
                for line in obs_file:
                    if len(line.strip()) != 0:
                        sequences.append(h.forward(Sequence([], line.strip().split(" "))))
                print("FORWARD RESULTS:\n")
                for sequence in sequences:
                    print(sequence.stateseq[-1], "- is the most likely final state")
                    print("of")
                    print(" ".join(sequence.outputseq))
                    print()
                print("----------------------------")
            else:
                print("INVALID FILE:", file)
        except:
            # Happens when the .obs can't be opened. It just does a normal test
            # Checks to see if --generate made a sequence with len(outputseq) > 1. If not, make one of length 10
            # Passes in a sequence of input[] and output[something] and sees if the output sequence is close to the
            # sequence made from .generate()
            print("Problem opening file\n")
            if len(sequence.outputseq) < 1:
                print("Creating Sequence")
                print("Default Length: 10")
                sequence = h.generate(10)
            sequence_copy = Sequence([], [sequence.outputseq])
            sequence_copy = h.forward(sequence_copy)
            print("Here's the original sequence states:")
            print(sequence.stateseq)
            print("Here's the original sequence emissions:")
            print(sequence.outputseq)
            print(
                "Given ONLY the emission sequence, here is what the forward algorithm THINKS the LAST state is: ")
            print(sequence_copy.stateseq[-1])
            print("How accurate is it?")

    if "--viterbi" in sys.argv:

        # Try to access the .obs file
        try:
            file = sys.argv[sys.argv.index("--viterbi") + 1]
            if file.endswith(".obs"):
                obs_file = open(file)
                sequences = []
                for line in obs_file:
                    if len(line.strip()) != 0:
                        sequences.append(h.viterbi(Sequence([], line.strip().split(" "))))
                print("VERTIBI RESULTS:\n")
                for sequence in sequences:
                    print("State Sequence")
                    print (" ".join(sequence.stateseq))
                    print ("from")
                    print("Output Sequence")
                    print (" ".join(sequence.outputseq))
                    print()
                print("----------------------------")
            else:
                print("INVALID FILE:", file)
        except:
            # Happens when the .obs can't be opened. It just does a normal test
            # Checks to see if --generate made a sequence with len(outputseq) > 1. If not, make one of length 10
            # Passes in a sequence of input[] and output[something] and sees if the output sequence is close to the
            # sequence made from .generate()
            print("Problem opening file")
            if len(sequence.outputseq) < 1:
                print("Creating Sequence")
                print("Default Length: 10")
                sequence = h.generate(10)
            sequence_copy = Sequence([], [sequence.outputseq])
            sequence_copy = h.viterbi(sequence_copy)
            print("Here's the original sequence states:")
            print(sequence.stateseq)
            print("Here's the original sequence emissions:")
            print(sequence.outputseq)
            print(
                "Given ONLY the emission sequence, here is what the forward algorithm THINKS the most likely inputs are: ")
            print(sequence_copy.stateseq)
            print("How accurate is it?")

    # print(
    #     "The results have finished printing. Viterbi outputs something that I am satisfied with.\n"
    #     "However, there is always a possibility that it will be working with SMALL numbers. If I use Math.round,\n"
    #     "then I can get the results shown in the pptx example. However, with it, smaller numbers would be treated as 0,\n"
    #     "and results will be weird. I apologize but I need to not round to get a good answer that is not\n"
    #     "ADJ ADJ ADJ ADJ for the sentence flies went to sleep or something\n"
    #     "- Colin Pham")