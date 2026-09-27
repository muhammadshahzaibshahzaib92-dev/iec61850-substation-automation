"""
fault_to_goose.py

Fault-to-GOOSE Protection Logic — detects fault current using pandapower,
checks it against a threshold, and if exceeded, automatically publishes a
GOOSE trip message via libiec61850 (Python bindings).

Requires: root/sudo (raw socket access for GOOSE), pyiec61850 (built from
source — see the main IEC 61850 Substation Automation repo for build steps).
"""

import warnings
warnings.filterwarnings("ignore")

import time
import pandapower as pp
import pandapower.shortcircuit as sc
import pyiec61850 as iec61850


def build_network():
    """Builds the 132kV/11kV substation model (buses, transformer, load, ext_grid)."""
    net = pp.create_empty_network(name="Sample Substation")
    bus1 = pp.create_bus(net, vn_kv=132, name="Bus 1 - Grid Side (132kV)")
    bus2 = pp.create_bus(net, vn_kv=11, name="Bus 2 - Plant Side (11kV)")
    pp.create_ext_grid(net, bus=bus1, vm_pu=1.0, name="Grid Supply")
    pp.create_transformer_from_parameters(
        net, hv_bus=bus1, lv_bus=bus2, sn_mva=25,
        vn_hv_kv=132, vn_lv_kv=11, vk_percent=8.5, vkr_percent=0.5,
        pfe_kw=0, i0_percent=0, name="Transformer T1"
    )
    pp.create_load(net, bus=bus2, p_mw=15, q_mvar=5, name="Plant Load")
    net.ext_grid["s_sc_max_mva"] = 1000
    net.ext_grid["rx_max"] = 0.1
    return net


def check_fault(net, threshold_ka=10.0):
    """Calculates 3-phase fault current and compares it against the threshold."""
    sc.calc_sc(net, fault="3ph", case="max")
    fault_ka = net.res_bus_sc.ikss_ka.max()
    print(f"Fault current: {fault_ka:.2f} kA")
    return fault_ka > threshold_ka


def publish_trip():
    """Multicasts a GOOSE trip message (loopback interface, for local testing)."""
    interface = "lo"
    dataSetValues = iec61850.LinkedList_create()
    iec61850.LinkedList_add(dataSetValues, iec61850.MmsValue_newIntegerFromInt32(1234))
    iec61850.LinkedList_add(dataSetValues, iec61850.MmsValue_newBinaryTime(False))
    iec61850.LinkedList_add(dataSetValues, iec61850.MmsValue_newBoolean(True))

    publisher = iec61850.GoosePublisher_create(None, interface)

    if publisher:
        iec61850.GoosePublisher_setGoCbRef(publisher, "IED1LD0/LLN0$GO$gcbTrip")
        iec61850.GoosePublisher_setConfRev(publisher, 1)
        iec61850.GoosePublisher_setDataSetRef(publisher, "IED1LD0/LLN0$TripDataSet")
        iec61850.GoosePublisher_setTimeAllowedToLive(publisher, 500)

        result = iec61850.GoosePublisher_publish(publisher, dataSetValues)
        if result == -1:
            print("Error sending GOOSE message!")
        else:
            print("GOOSE trip triggered automatically!")

        iec61850.GoosePublisher_destroy(publisher)
    else:
        print("Failed to create GOOSE publisher.")


# Main entry point: build the network, check for a fault, and trip if needed
if __name__ == "__main__":
    t0 = time.time()
    net = build_network()

    t1 = time.time()
    tripped = check_fault(net, threshold_ka=10.0)
    t2 = time.time()
    print(f"[TIMING] Fault detect time: {(t2 - t1) * 1000:.2f} ms")

    if tripped:
        publish_trip()
        t3 = time.time()
        print(f"[TIMING] GOOSE publish time: {(t3 - t2) * 1000:.2f} ms")
        print(f"[TIMING] Total (detect + publish): {(t3 - t1) * 1000:.2f} ms")
    else:
        print("Normal — no trip needed.")
