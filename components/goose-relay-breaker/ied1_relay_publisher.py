"""
ied1_relay_publisher.py
Day 11: Pehla GOOSE Publisher (Relay) Script
IEC 61850 GOOSE trip messages publish karta hai, pyiec61850 (Python bindings) use karke.
"""

import pyiec61850 as iec61850
import time

def main():
    interface = "lo"

    # Dataset values banao jo GOOSE message mein publish hongi
    dataSetValues = iec61850.LinkedList_create()
    iec61850.LinkedList_add(dataSetValues, iec61850.MmsValue_newIntegerFromInt32(1234))
    iec61850.LinkedList_add(dataSetValues, iec61850.MmsValue_newBinaryTime(False))
    iec61850.LinkedList_add(dataSetValues, iec61850.MmsValue_newBoolean(False))  # trip status: False = normal

    # GOOSE publisher banao. parameters=None matlab library default
    # standard IEC 61850 GOOSE multicast address use karegi.
    publisher = iec61850.GoosePublisher_create(None, interface)

    if publisher:
        iec61850.GoosePublisher_setGoCbRef(publisher, "IED1LD0/LLN0$GO$gcbTrip")
        iec61850.GoosePublisher_setConfRev(publisher, 1)
        iec61850.GoosePublisher_setDataSetRef(publisher, "IED1LD0/LLN0$TripDataSet")
        iec61850.GoosePublisher_setTimeAllowedToLive(publisher, 500)

        for i in range(4):
            time.sleep(1)
            result = iec61850.GoosePublisher_publish(publisher, dataSetValues)
            if result == -1:
                print("Error sending message!")
            else:
                print(f"[IED-1] GOOSE published (message {i+1}/4)")

        iec61850.GoosePublisher_destroy(publisher)
    else:
        print("Failed to create GOOSE publisher. Reason: interface na milna ya root permission chahiye.")

if __name__ == "__main__":
    main()
