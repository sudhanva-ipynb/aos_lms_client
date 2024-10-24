from menu import *
from functions import *
from imports import *
from grpc_calls import *
import grpc
import time

LEADER_RETRY_DELAY = 2  # seconds to wait before retrying to fetch the leader
BOOTSTRAP_NODES = [
    {
        "id": "ee1f954b-99ab-48e2-95fd-730e4aec2489",
        "host": "localhost",
        "port": "50052"
    },
    {
        "id": "de3b3357-8c1f-4911-910e-977d2ff02611",
        "host": "localhost",
        "port": "50053"
    },
    {
        "id": "becedead-63a4-48a8-a017-e284cd02d21e",
        "host": "localhost",
        "port": "50054"
    }
]


# Function to get the leader id from the bootstrap nodes
def get_leader_id():
    for node in BOOTSTRAP_NODES:
        try:
            server_address = f"{node['host']}:{node['port']}"
            print(f"Trying to connect to bootstrap server: {server_address}")

            with grpc.insecure_channel(server_address) as channel:
                raft_stub = Lms_pb2_grpc.RaftStub(channel)
                response = raft_stub.getLeader(Lms_pb2.GetLeaderRequest(ack=1))  # Call GetLeader RPC

                if response.node_id:
                    print(f"Leader ID found: {response.node_id} (via {server_address})")
                    return response.node_id
                else:
                    print(f"No leader found from {server_address}, trying next...")
        except grpc.RpcError as error:
            print(f"Failed to fetch leader from {server_address}: {error}")

    return None  # If no leader is found or all servers fail


# Function to get leader host and port from the node list based on leader id
def get_leader_host_port(leader_id):
    for node in BOOTSTRAP_NODES:
        if node["id"] == leader_id:
            return node["host"], node["port"]
    return None, None  # If leader ID is not found in the list


# Function to connect to the leader using the host and port, and return the channel
def connect_to_leader(leader_host, leader_port):
    try:
        server_address = f"{leader_host}:{leader_port}"
        channel = grpc.insecure_channel(server_address)

        auth_stub = Lms_pb2_grpc.AuthStub(channel)
        assignment_stub = Lms_pb2_grpc.AssignmentsStub(channel)
        materials_stub = Lms_pb2_grpc.MaterialsStub(channel)
        queries_stub = Lms_pb2_grpc.QueriesStub(channel)
        llm_stub = Lms_pb2_grpc.LlmStub(channel)

        grpc_helper.set_auth_stub(auth_stub)
        grpc_helper.set_assignment_stub(assignment_stub)
        grpc_helper.set_materials_stub(materials_stub)
        grpc_helper.set_queries_stub(queries_stub)
        grpc_helper.set_llm_stub(llm_stub)

        print("Successfully connected to leader:", server_address)
        return channel  # Return the channel for later use
    except grpc.RpcError as error:
        print(f"Failed to connect to leader: {error}")
        return None


if __name__ == '__main__':
    while True:
        # Step 1: Get the leader ID from the bootstrap servers
        leader_id = get_leader_id()

        # Step 2: If leader ID is found, map it to the correct host and port
        if leader_id:
            leader_host, leader_port = get_leader_host_port(leader_id)

            if leader_host and leader_port:
                # Step 3: Attempt to connect to the leader using the host and port
                channel = connect_to_leader(leader_host, leader_port)
                if channel:
                    # Step 4: Handle the main menu if connection to leader is successful
                    handle_menu(main_menu_options, main_menu_action, "Main Menu")
                    break  # Exit the loop once connected and menu is handled
            else:
                print("Leader ID not found in node information, retrying...")
        else:
            print("Retrying to get the leader...")

        # Step 5: Wait before retrying to get leader info
        time.sleep(LEADER_RETRY_DELAY)
