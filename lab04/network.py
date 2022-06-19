from cmath import sqrt
import json
from math import floor
import random
import numpy as np
import scipy.special as sp
from lightpath import Lightpath
from node import Node
from line import Line
from segnale import Signal_information
from connection import Connection
from pandas import DataFrame
import matplotlib.pyplot as plt
import constants as my_cs

class Network:
    
    def __init__(self, path : str, channels : int) -> None:
        input_file = open(path)
        data = json.load(input_file)
        input_file.close()
        self.nodes = {}
        self.lines = {}
        self.channels = channels
        
        for key,value in data.items():
            tmp_data = {
                "label" : key,
                "position" : (value["position"][0],value["position"][1]),
                "connected_nodes" : value["connected_nodes"]
            }
            if("transceiver" not in value):
                tmp_data['transceiver'] = "fixed-rate"
            else:
                tmp_data['transceiver'] = value['transceiver']
            self.nodes[key] = Node(tmp_data)
        for value in self.nodes.values():
            for end_l in value.connected_node:
                self.lines[value.label + end_l] = Line(value.label + end_l, sqrt((value.position[0] - self.nodes[end_l].position[0])**2 + (value.position[1] - self.nodes[end_l].position[1])**2), channels)
                self.lines[value.label + end_l].connect(value, self.nodes[end_l])
                value.addLine(self.lines[value.label + end_l], end_l)
        
        self.create_weighted_paths_and_route_space()

    def recursive_path(self, start : str, end : str, forbidden : list, all_path : list) -> list:
        if(start == end):
            all_path.append(list(forbidden))
            return
        for next_node in self.nodes[start].connected_node:
            if(next_node not in forbidden):
                forbidden.append(next_node)
                self.recursive_path(next_node, end, forbidden, all_path)
                forbidden.pop()

    def find_paths(self, start : str, end : str)->list:
        result=[]
        self.recursive_path(start, end, [start], result)
        return result

    def propagate(self, signal: Signal_information) -> Signal_information:
        node = signal.update_path()
        self.nodes[node].propagate(signal)
        return signal

    def recursive_check_path(self, path : list, pos : int, channel : int = 0) -> bool: # recursively checks if the path is free or not
        if(pos==len(path) - 1):
            return True
        if(self.lines[path[pos]+ path[pos+1]].occupy(channel)):
            if(self.recursive_check_path(path, pos + 1, channel)):
                self.last_channel = channel
                return True
            self.lines[path[pos] + path[pos+1]].free(channel)
        if(pos == 0 and channel != self.channels - 1):
            return self.recursive_check_path(path, 0, channel + 1)
        else:
            return False

    def find_best_snr(self, begin : str, end : str) -> list:
        best = []
        best_snr = -1.0
        best_channel = -1
        for path in self.find_paths(begin, end):
            sig = self.propagate(Signal_information(1e-3, path))
            if((sig.get_signal_noise_ration() < best_snr or best_snr == -1) and self.recursive_check_path(path, 0)):
                best_snr = sig.get_signal_noise_ration()
                if(len(best) != 0):
                    for i in range(0, len(best)-1):
                        self.lines[best[i]+best[i+1]].free(best_channel)
                best = list(path)
                best_channel = self.last_channel
        self.last_channel = best_channel
        return best

    def find_best_latency(self, begin : str, end : str) -> list:
        best = []
        best_snr = -1.0
        best_channel = -1
        for path in self.find_paths(begin, end):
            sig = self.propagate(Signal_information(1e-3, path))
            if((float(sig.latency.real) < best_snr or best_snr == -1) and self.recursive_check_path(path, 0)):
                best_snr = sig.latency.real
                if(len(best) != 0):
                    for i in range(0, len(best)-1):
                        self.lines[best[i]+best[i+1]].free(best_channel)
                best_channel = self.last_channel
                best = list(path)
        self.last_channel = best_channel
        return best

    def stream(self, cons : list, to_use = lambda net,begin,end: net.find_best_latency(begin, end)): # testes all the possible connections
        for con in cons:
            if(to_use): # depending on the best path selected I use the appropriate function
                path = self.find_best_latency(con.input, con.output)
                con.setChannel(self.last_channel)       # set the channel of the connection to the last one check for inside the function
            else:
                path = self.find_best_snr(con.input, con.output)
                con.setChannel(self.last_channel)       # set the channel of the connection to the last one check for inside the function
            
            if(len(path)!=0):   # if a path was found
                con.setBitRate(self.calculate_bit_rate(path, self.nodes[con.input].transceiver))    # calculate the bitrate using the first node technology
                if(con.bitRate > 0):    # if the GSNR requirements are met
                    sig = self.propagate(Signal_information(con.signal_power, path))
                    con.setLatency(sig.latency.real)
                    con.setSNR(sig.get_signal_noise_ration().real)
                else:       # if the bitrate is 0 (GSNR requirements not met)
                    for i in range(0, len(path)-1):     # free the line
                        self.lines[path[i]+path[i+1]].free(con.channel)
                    con.setLatency(None)    # and reject the connection
                    con.setSNR(0.0)
            else:   # if no path is found reject the connection
                con.setLatency(None)
                con.setSNR(0.0)
    
    def path_to_string(self, path) -> str: # given a list of nodes it turns it into a string
        tmp_s = ""
        for node in path:
            tmp_s += node
            if (node != path[-1]):
                tmp_s += "->"
        return tmp_s

    def create_weighted_paths_and_route_space(self) -> None: # creates the weighted path and the route space
        nodes=["A","B","C","D","E", "F"]
        labels_d = []
        data = []
        for node_s in nodes:
            for node_e in nodes:
                if(node_s != node_e):
                    paths = self.find_paths(node_s, node_e)
                    for path in paths:
                        sig = self.propagate(Signal_information(1e-3, path))
                        labels_d.append(self.path_to_string(path))
                        data.append([self.path_to_string(path), sig.noise_power.real, sig.latency.real, sig.get_signal_noise_ration().real])
        self.weighted_paths = DataFrame(data, columns=['label', 'noise', 'latency', 'snr'], index=labels_d)
        data = []
        for label in labels_d:
            tmp=[]
            for i in range(self.channels):
                tmp.append(True)
            data.append(tmp)
        self.route_space = DataFrame(data, index=labels_d, columns=list(range(0, self.channels)))

    def calculate_bit_rate(self, lightPath : Lightpath, strategy):
        snr = 10**(self.weighted_paths.loc[self.path_to_string(lightPath.path), 'snr']/10.0)
        return self.calculate_bit_rate_actual(snr, strategy, lightPath.Rs)

    def calculate_bit_rate_actual(self, snr, strategy, rs = my_cs.RS): # depending on the stratefy calculates the speed depending on the snr
        if(strategy == 'fixed-rate'):
            if(snr >= 2*sp.erfcinv(2 * my_cs.BERT)**2 *  rs/ my_cs.BN):
                return 100e9
            else:
                return 0
        elif(strategy == 'flex-rate'):
            if(snr <= 2*sp.erfcinv(2 * my_cs.BERT)**2 *  rs/ my_cs.BN):
                return 0
            elif(snr <= 14.0/3.0*sp.erfcinv(3.0/2.0 * my_cs.BERT)**2 *  rs/ my_cs.BN):
                return 100e9
            elif(snr <= 10.0*sp.erfcinv(8.0/3.0 * my_cs.BERT)**2 *  rs/ my_cs.BN):
                return 200e9
            else:
                return 400e9
        elif(strategy == 'shannon'):
            return 2* rs*np.log2(1.0+snr* rs/ my_cs.BN)
        else:
            return 0

if __name__=="__main__":
    net=Network("lab02/nodes.json", 10)
    nodes=["A","B","C","D","E", "F"]
    cons = []
    for i in range(0,100):
        s = floor(random.uniform(0, len(nodes)))
        e = floor(random.uniform(0, len(nodes)))
        while e == s:
            e = floor(random.uniform(0, len(nodes)))
        cons.append(Connection(nodes[s], nodes[e], 1e-3))
    net.stream(cons)
    fig, [plot_latency, plot_snr] = plt.subplots(2)
    plot_latency.plot(list(map(lambda x:x.latency, cons)))
    plot_snr.plot(range(0,100), list(map(lambda x:x.snr, cons)))

    plt.show()

    db_a = []
    speed_fixed_a = []
    speed_flex_a = []
    speed_shannon_a = []
    for k in range(0,20):
        db_a.append(k)
        snr = 10**(k/10.0)
        speed_fixed_a.append(net.calculate_bit_rate_actual(snr, "fixed-rate")/1e9)
        speed_flex_a.append(net.calculate_bit_rate_actual(snr, "flex-rate")/1e9)
        speed_shannon_a.append(net.calculate_bit_rate_actual(snr, "shannon")/1e9)
    fig, plot_speed = plt.subplots()
    plot_speed.plot(db_a)
    plot_speed.plot(speed_fixed_a)
    plot_speed.plot(speed_flex_a)
    plot_speed.plot(speed_shannon_a)

    plt.show()


