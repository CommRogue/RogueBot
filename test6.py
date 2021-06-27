from scapy.all import sniff
from scapy.layers import http
from datetime import datetime


def print_query(query):
    httpLayer = query.getlayer(http.HTTPRequest) #get the http layer object

    #convert the timestamp (sequence of encoded characters that can be decoded into time) found in the http layer object to a datetime object
    timeSent = datetime.fromtimestamp(httpLayer.time)

    #print the information by converting the time to string, and the Host and Method by decoding the bytes to string
    print(f"{str(timeSent)}   Packet Sniffed: {httpLayer.name}, with method {(httpLayer.Method).decode('utf-8')}, sent to {(httpLayer.Host).decode('utf-8')}")

def filter_http(packet): #check if packet is HTTP and if so, check if it's a GET request
    return packet.haslayer(http.HTTPRequest) and str(packet).find("GET")

print("----- Started Sniffing (Packets Will Show Up Below) -----")
packets = sniff(count=2500, lfilter=filter_http, prn=print_query)