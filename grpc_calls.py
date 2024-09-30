import os.path
import threading
import grpc
import Lms_pb2,Lms_pb2_grpc
from imports import grpc_helper
from datetime import datetime

COURSE_ID = "8d313659-2360-44a2-9ab0-57dbd1ddc201"
ASSIGNMENT_ID = "2d8f2298-beac-4a27-b70a-c1da56600993"

def studentLogin(username,password):
    try:
        stub = grpc_helper.auth_stub
        response = stub.studentLogin(Lms_pb2.LoginRequest(username=username,
                                                          password=password))
        if response.code == "200":
            return response.token,None
        else:
            return None,response.error
    except grpc.RpcError as rpc_error:
        code = rpc_error.code()
        print(rpc_error.details())

        return None,rpc_error

    except Exception as error:
        return None,error

def facultyLogin(username,password):
    try:
        stub = grpc_helper.auth_stub
        response = stub.facultyLogin(Lms_pb2.LoginRequest(username=username,
                                                          password=password))
        if response.code == "200":
            return response.token,None
        else:
            return None,response.error
    except grpc.RpcError as rpc_error:
        code = rpc_error.code()
        print(rpc_error.details())
        if code == grpc.StatusCode.UNAUTHENTICATED:
            return None,rpc_error.details()
        else:
            return None,rpc_error.details()

def generate_file_chunks_for_assignment_upload(path,filename,assignment_name):
    block_size = 1024*1024
    with open(path,"rb") as f:
        while chunk := f.read(block_size):
            yield Lms_pb2.SubmitAssignmentRequest(course=COURSE_ID,assignment_name=ASSIGNMENT_ID,data=chunk,filename=filename)


def submitAssignment(assignment_file,assignment_name,filename):
    try:
        metadata = (
            ("authorization", grpc_helper.access_token),
        )

        stub = grpc_helper.assignment_stub
        response = stub.submitAssignment(generate_file_chunks_for_assignment_upload(assignment_file,filename,assignment_name),
                                         metadata=metadata)
        if response.code == "200":
            return None
        else:
            return response.error
    except grpc.RpcError as rpc_error:
        code = rpc_error.code()
        print(rpc_error.details())
        if code == grpc.StatusCode.UNAUTHENTICATED:
            return rpc_error.details()
        else:
            return rpc_error.details()


def getCourseContents(course,term):
    try:
        metadata = (
            ("authorization", grpc_helper.access_token),
        )

        stub = grpc_helper.materials_stub
        response = stub.getCourseContents(Lms_pb2.GetCourseContentsRequest(course=COURSE_ID,term=term),
                                         metadata=metadata)

        if not response.error:
            return response.data,None
        else:
            return None,response.error
    except grpc.RpcError as rpc_error:
        code = rpc_error.code()
        print(rpc_error.details())
        if code == grpc.StatusCode.UNAUTHENTICATED:
            return None,rpc_error.details()
        else:
            return None,rpc_error.details()


def getCourseMaterial(course,term,id):
    try:
        metadata = (
            ("authorization", grpc_helper.access_token),
        )

        stub = grpc_helper.materials_stub
        data = b""
        filename= None
        code = None
        error = None
        for response in stub.getCourseMaterial(Lms_pb2.GetCourseMaterialRequest(course=COURSE_ID,term=term,name=id),
                                         metadata=metadata):
            data += response.data
            filename = response.filename

            error = response.error
        if not error:
            return data,filename,None
        else:
            return None,None,error
    except grpc.RpcError as rpc_error:
        code = rpc_error.code()
        print(rpc_error.details())
        if code == grpc.StatusCode.UNAUTHENTICATED:
            return None,None,rpc_error.details()
        else:
            return None,None,rpc_error.details()

def getAssignments(course,name):
    try:
        metadata = (
            ("authorization", grpc_helper.access_token),
        )

        stub = grpc_helper.assignment_stub
        data = b""
        code = None
        error = None
        for response in stub.getSubmittedAssignment(Lms_pb2.GetSubmittedAssignmentsRequest(course=COURSE_ID, assignment_name=ASSIGNMENT_ID),
                                          metadata=metadata):
            data += response.data
            code = response.code
            error = response.error
        if not data:
            print(error)
            return None,"No Assignments"
        if code != "200":
            return None,"No Assignments"
        else:
            return data,None

    except grpc.RpcError as rpc_error:
        code = rpc_error.code()
        print(rpc_error.details())
        if code == grpc.StatusCode.UNAUTHENTICATED:
            return None,rpc_error.details()
        else:
            return None,rpc_error.details()

def generate_file_chunks_for_material_upload(path,filename,material_name):
    block_size = 1024*1024
    with open(path,"rb") as f:
        while chunk := f.read(block_size):
            yield Lms_pb2.UploadCourseMaterialRequest(course=COURSE_ID,term="20241",filename=filename,data=chunk,created=str(datetime.now()),name=material_name)



def uploadMaterial(path,name):
    filename = os.path.split(path)[1]
    try:
        metadata = (
            ("authorization", grpc_helper.access_token),
        )
        stub = grpc_helper.materials_stub
        response = stub.courseMaterialUpload(generate_file_chunks_for_material_upload(path,filename,name),
                                          metadata=metadata)
        if not response.error:
            return None
        else:
            return response.error
    except grpc.RpcError as rpc_error:
        code = rpc_error.code()
        print(rpc_error.details())
        if code == grpc.StatusCode.UNAUTHENTICATED:
            return rpc_error.details()
        else:
            return rpc_error.details()

def create_query(course, query):
    request = Lms_pb2.CreateQueryRequest(course=COURSE_ID, query=query)
    try:
        metadata = (
            ("authorization", grpc_helper.access_token),
        )
        stub = grpc_helper.queries_stub
        response = stub.createQuery(request,metadata=metadata)
        return response.error
    except grpc.RpcError as e:
        print(f"gRPC failed with {e.code()}: {e.details()}")
        return e.details()

def get_queries(course, term):
    request = Lms_pb2.GetQueriesRequest(course=COURSE_ID, term=term)
    try:
        metadata = (
            ("authorization", grpc_helper.access_token),
        )
        stub = grpc_helper.queries_stub
        response = stub.getQueries(request,metadata=metadata)
        return response.queries,None
    except grpc.RpcError as e:
        print(f"gRPC failed with {e.code()}: {e.details()}")
        return None,e.details()
def answer_query( query_id, answer):
    request = Lms_pb2.AnswerQueryRequest(qid=query_id, answer=answer)
    try:
        metadata = (
            ("authorization", grpc_helper.access_token),
        )
        stub = grpc_helper.queries_stub
        response = stub.answerQuery(request,metadata=metadata)
        return response.error
    except grpc.RpcError as e:
        print(f"gRPC failed with {e.code()}: {e.details()}")
        return e.details()
def generate_requests():
    session = True
    print("You can ask any queries related to Science and Technology")
    print("Enter 'quit' to stop the chat")
    while session:
        query = input()
        if not query:
           print("Please enter a query")
           continue
        if query == "quit":
            session = False
        else:
            yield Lms_pb2.AskLlmRequest(query=query)
            print(f"You: {query}")
def listen_for_messages(response_iterator):
    for response in response_iterator:
        if response.error:
            print(response.error)
        else:
            print(f"LLM: {response.message}")
def chat_with_phi():
    try:
        metadata = (
            ("authorization", grpc_helper.access_token),
        )
        stub = grpc_helper.llm_stub
        for response in stub.askLlm(generate_requests(), metadata=metadata):
            if response.error:
                print(response.error)
            else:
                print(f"LLM: {response.reply}")

        return None
    except Exception as error:
        return error