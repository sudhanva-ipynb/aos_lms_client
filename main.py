from menu import *
from functions import *
from imports import *
from grpc_calls import *



if __name__ == '__main__':
    with grpc.insecure_channel("localhost:50051") as channel:
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
        handle_menu(main_menu_options,main_menu_action,"Main  Menu")