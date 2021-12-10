# Copyright (c) 2021, Ciena Corporation, All Rights Reserved
# SPDX-License-Identifier: LGPL-2.1-only

from scripts import show_queueing
import pytest


def test_show_drop_summary():

    data = {
        # Interface with dropped packets
        "dp0p1s1": {
            "shaper": {
                "subports": [
                    {
                        "tc": [
                            {"packets": 10, "dropped": 10, "random_drop": 0},
                            {"packets": 10, "dropped": 10, "random_drop": 0},
                            {"packets": 100, "dropped": 10, "random_drop": 0},
                            {"packets": 1000, "dropped": 10, "random_drop": 50},
                        ],
                    }
                ],
            }
        },
        "dp0p1s2": {
            "shaper": {
                "subports": [
                    {
                        "tc": [
                            {"packets": 100, "dropped": 100, "random_drop": 0},
                            {"packets": 100, "dropped": 100, "random_drop": 0},
                            {"packets": 1000, "dropped": 0, "random_drop": 0},
                            {"packets": 1000, "dropped": 0, "random_drop": 50},
                        ],
                    }
                ],
            }
        },
        # Interface with 0 packets
        "dp0s8": {
            "shaper": {
                "subports": [
                    {
                        "tc": [
                            {"packets": 0, "dropped": 0, "random_drop": 0},
                            {"packets": 0, "dropped": 0, "random_drop": 0},
                            {"packets": 0, "dropped": 0, "random_drop": 0},
                            {"packets": 0, "dropped": 0, "random_drop": 0},
                        ],
                    }
                ],
            }
        },
        # Interface without qos data
        "dp0s9": {
            "shaper": {
                "vlans": [],
                "subports": [],
            }
        },

        # Interface with vlans
        "dp0p1s3": {
            "shaper": {
                "vlans": [
                    {
                        "tag": 200,
                        "subport": 1
                    },
                    {
                        "tag": 400,
                        "subport": 2
                    }
                ],
                "subports": [
                    {
                        "tc": [
                            {"packets": 1, "dropped": 0, "random_drop": 0},
                        ],
                    },
                    {
                        "tc": [
                            {"packets": 2, "dropped": 0, "random_drop": 0},
                        ],
                    },
                    {
                        "tc": [
                            {"packets": 3, "dropped": 0, "random_drop": 0},
                        ],
                    }
                ],
            }
        },
        # Interface with vlans that don't have QoS
        "dp0p1s4": {
            "shaper": {
                "vlans": [
                    {
                        "tag": 200,
                    },
                    {
                        "tag": 400,
                    }
                ],
                "subports": [
                    {
                        "tc": [
                            {"packets": 1, "dropped": 0, "random_drop": 0},
                        ],
                    },
                ],
            }
        },
    }

    table_data = show_queueing.extract_drop_summary_data(data)
    # Run `pytest-3 -s tests/scripts/test_show_queueing.py` and manually inspect printed table format
    print("\n")
    show_queueing.print_table(table_data)

    row0 = iter(table_data[0])
    assert next(row0) == "Total"                            # Interface Name
    # Queued Packets = 2200 + 1120 + 6 + 1 
    assert next(row0) == 3327
    # Dropped Packets = 250 + 90
    assert next(row0) == 340
    # Dropped Percentage = (Dropped Packets / Queued Packets) * 100
    assert next(row0) == pytest.approx(19.399, 0.0001)

    row3 = iter(table_data[3])
    assert next(row3) == "dp0s8"
    assert next(row3) == 0
    assert next(row3) == 0
    assert next(row3) == 0

    row5 = iter(table_data[5])
    assert next(row5) == "dp0p1s3.200"

    row7 = iter(table_data[8])
    assert next(row7) == "dp0s9"
    # No Qos data on counters.
    # The tabulate library converts None to "-" when printing to the terminal
    assert next(row7) is None
    assert next(row7) is None
    assert next(row7) is None


def test_get_difference_normal():
    prev = show_queueing.DropSummaryTableRow("interface1")
    prev.packet_data = {"queued_packets": 5,
                        "dropped_packets": 5,
                        "dropped_percentage": 100}

    current = show_queueing.DropSummaryTableRow("interface1")
    current.packet_data = {"queued_packets": 10,
                           "dropped_packets": 10,
                           "dropped_percentage": 100}

    actual_diff = show_queueing.get_difference([prev], [current])[0]
    assert actual_diff.packet_data == {"queued_packets": 5,
                                       "dropped_packets": 5,
                                       "dropped_percentage": 100}


def test_get_difference_zero():
    prev = show_queueing.DropSummaryTableRow("interface1")
    prev.packet_data = {"queued_packets": 0,
                        "dropped_packets": 0,
                        "dropped_percentage": 0}

    current = show_queueing.DropSummaryTableRow("interface1")
    current.packet_data = {"queued_packets": 0,
                           "dropped_packets": 0,
                           "dropped_percentage": 0}

    actual_diff = show_queueing.get_difference([prev], [current])[0]
    assert actual_diff.packet_data == {"queued_packets": 0,
                                       "dropped_packets": 0,
                                       "dropped_percentage": 0}


def test_get_difference_none():
    prev = show_queueing.DropSummaryTableRow("interface1")
    prev.packet_data = None

    current = show_queueing.DropSummaryTableRow("interface1")
    current.packet_data = None

    actual_diff = show_queueing.get_difference([prev], [current])[0]
    assert actual_diff.packet_data is None


def test_get_difference_interfaces_changed():
    prev1 = show_queueing.DropSummaryTableRow("interface1")
    prev2 = show_queueing.DropSummaryTableRow("interface2")
    prev2.packet_data = {"queued_packets": 0,
                         "dropped_packets": 0,
                         "dropped_percentage": 0}
    prev3 = show_queueing.DropSummaryTableRow("interface3")

    # Interfaces 1 & 3 are removed. Interface 4 is added
    curr2 = show_queueing.DropSummaryTableRow("interface2")
    curr2.packet_data = {"queued_packets": 10,
                         "dropped_packets": 10,
                         "dropped_percentage": 100}
    curr4 = show_queueing.DropSummaryTableRow("interface4")
    curr4.packet_data = {"queued_packets": 0,
                         "dropped_packets": 0,
                         "dropped_percentage": 0}

    diff_table = show_queueing.get_difference(
        [prev1, prev2, prev3], [curr4, curr2])

    # Check interface2 comes before interface4 as it has more drops
    assert diff_table[0].interface_name == "interface2"
    assert diff_table[0].packet_data == {"queued_packets": 10,
                                         "dropped_packets": 10,
                                         "dropped_percentage": 100}

    assert diff_table[1].interface_name == "interface4"
    assert diff_table[1].packet_data is None

    # Check removed interfaces are not in the table
    assert len(diff_table) == 2


"""
def test_monitor_drop_summary():
    # Ignore mypy issues when setting function attributes (https://github.com/python/mypy/issues/2087)

    def get_stubbed_data():

        try:
            get_stubbed_data.packets *= 3  # type: ignore
            get_stubbed_data.dropped *= 2  # type: ignore
        except AttributeError:
            get_stubbed_data.packets = 1  # type: ignore
            get_stubbed_data.dropped = 1  # type: ignore

        interfaces = {}
        for i in range(10):
            interfaces.update({
                f"dp0ps{i}": {
                    "shaper": {
                        "subports": [
                            {
                                "tc": [
                                    {"packets": get_stubbed_data.packets,  # type: ignore
                                     "dropped": get_stubbed_data.dropped,  # type: ignore
                                     "random_drop": 0},
                                ],
                            }
                        ],
                    }
                }
            })
        return interfaces

    # monkey patch module to retrieve data using stubbed function rather than querying vplaned
    show_queueing.get_qos_data = get_stubbed_data

    # Run `pytest-3 -s tests/scripts/test_show_queueing.py` and manually inspect printed table format
    print("\n")
    show_queueing.monitor_drop_summary()
"""
