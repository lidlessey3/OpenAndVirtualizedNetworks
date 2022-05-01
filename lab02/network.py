from cmath import sqrt
import json
from node import Node
from line import Line
from signal import Signal_information
from connection import Connection
from pandas import DataFrame

class Network:
    
    def __init__(self, path : str) -> None:
        input_file = open(path)
        data = json.load(input_file)
        input_file.close()
        self.nodes = {}
        self.lines = {}
        
        for key,value in data.items():
            tmp_data = {
                "label" : key,
                "position" : (value["position"][0],value["position"][1]),
                "connected_nodes" : value["connected_nodes"]
            }
            self.nodes[key] = Node(tmp_data)
        for value in self.nodes.values():
            for end_l in value.connected_node:
                self.lines[value.label + end_l] = Line(value.label + end_l, sqrt((value.position[0] - self.nodes[end_l].position[0])**2 + (value.position[1] - self.nodes[end_l].position[1])**2))
                self.lines[value.label + end_l].connect(value, self.nodes[end_l])
                value.addLine(self.lines[value.label + end_l], end_l)
    
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

    def find_best_snr(self, begin : str, end : str) -> list:
        best = []
        best_snr = -1.0
        for path in self.find_paths(begin, end):
            sig = self.propagate(Signal_information(1e-3, path))
            if(sig.get_signal_noise_ration() < best_snr or best_snr == -1):
                best_snr = sig.get_signal_noise_ration()
                best = list(path)
        return best


    def find_best_latency(self, begin : str, end : str) -> list:
        best = []
        best_snr = -1.0
        for path in self.find_paths(begin, end):
            sig = self.propagate(Signal_information(1e-3, path))
            if(sig.latency < best_snr or best_snr == -1):
                best_snr = sig.latency
                best = list(path)
        return best

    def stream(self, cons : list, to_use = lambda net,begin,end: net.find_best_latency(begin, end)):
        for con in cons:
            sig = self.propagate(Signal_information(1e-3, to_use(self, con.input, con.output)))
            con.setLatency(sig.latency)
            con.setSNR(sig.get_signal_noise_ration())

if __name__=="__main__":
    net=Network("lab02/nodes.json")
    nodes=["A","B","C","D","E", "F"]
    paths_d = []
    noises_d = []
    latencies_d = []
    snr_d = []
    for node_s in nodes:
        for node_e in nodes:
            if(node_s != node_e):
                paths = net.find_paths(node_s, node_e)
                for path in paths:
                    print(str(path) + ":")
                    tmp_s = ""
                    for node in path:
                        tmp_s += node
                        if (node != path[-1]):
                            tmp_s += "->"
                    sig = net.propagate(Signal_information(1e-3, path))
                    print(sig)
                    paths_d.append(tmp_s)
                    noises_d.append(sig.noise_power)
                    latencies_d.append(sig.latency)
                    snr_d.append(sig.get_signal_noise_ration())
    dataframe = DataFrame([paths_d, noises_d, latencies_d, snr_d], None, ["label", "noise", "latency", "snr"], True)
                    

                    
            

