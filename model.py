from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2, ECS, EKS, Lambda
from diagrams.aws.database import RDS, ElastiCache, Redshift
from diagrams.aws.integration import SQS
from diagrams.aws.network import VPC, ELB, Route53
from diagrams.aws.storage import S3
import random
import json
import openai

# from dotenv import load_dotenv
# import os

# load_dotenv()
# openai.api_key = os.getenv("OPENAPI_KEY")


class ER_GPT:
    def __init__(self):
        self.temperature = 0
        pass

    # Step 1, get the architecture components
    def step_1(self, user_input):
        it_prompt = "I want you to act as an IT Cloud Architect with an experience in reference diagrams that can help introduce new tools."
        assistant_prompt = "Include cloud services, SAP App Server, and Database as nodes. Include Private subnet, Virtual Private Cloud as a containers."
        # user_input = "Build an SAP architecture on AWS with multi-cloud deployment for redundancy and vendor flexibility."

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "system", "content": it_prompt},
                {"role": "user", "content": assistant_prompt},
                {"role": "user", "content": user_input},
            ],
            functions=[
                {
                    "name": "get_architecture_components",
                    "description": "Get the cloud architecture components split into containers (categorization) and nodes or application services",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "containers": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "Region or VPC or private subnet",
                                },
                                "description": "Top-layer category of nodes such as region / VPC / private subnet, but not the nodes themselves",
                            },
                            "nodes": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "Database or application.",
                                },
                                "description": "Application nodes or cloud service. If duplicated in multiple containers, include as that many nodes.",
                            },
                        },
                        "required": ["nodes"],
                    },
                }
            ],
            function_call={"name": "get_architecture_components"},
            temperature=self.temperature,
        )
        architecture_result = completion.choices[0].message.function_call.arguments
        print(architecture_result)
        return architecture_result

    # Step 2, get the step by step diagram
    def step_2(self, architecture_result):
        diagram_system_prompt = "Act as a teacher for creating an instruction for drawing an entity diagram based on the cloud software architectural decision. Use nodes for rectangles and clusters for containers."
        diagram_assistant_prompt = "Nodes stay inside of containers. Nodes connect to other nodes. Containers cannot connect to other containers."
        diagram_input = (
            architecture_result
            + "\nBased on the components of this cloud architecture, create an instruction for drawing an accurate entity diagram."
        )

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "system", "content": diagram_system_prompt},
                {"role": "assistant", "content": diagram_assistant_prompt},
                {"role": "user", "content": diagram_input},
            ],
            functions=[
                {
                    "name": "get_diagram_instruction",
                    "description": "Get the instruction for drawing an entity diagram based on the cloud software architectural decision",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "instructions": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "Current step for drawing an entity diagram",
                                },
                                "description": "Instruction for drawing an entity diagram",
                            }
                        },
                    },
                    "required": ["instructions"],
                }
            ],
            function_call={"name": "get_diagram_instruction"},
            temperature=self.temperature,
        )
        diagram_result = completion.choices[0].message.function_call.arguments
        print(diagram_result)
        return diagram_result

    # Step 3, get the code
    def step_3(self, diagram_result):
        code_imports = "Cluster, Diagram, Edge, EC2, ECS, EKS, Lambda, RDS, ElastiCache, Redshift, SQS, ELB, Route53, S3"
        example_code = 'with Diagram("diagram", show=False):\n with Cluster("ReplicaSet"): \n pods = [Pod("pod{}".format(i)) for i in range(1, 3)]\n rs = ReplicaSet("rs")\n rs - pods\n dp = Deployment("dp")\n dp << rs\n hpa = HPA("hpa")\n dp << hpa\n net >> rs << dp'
        code_import = """from diagrams.aws.compute import EC2, ECS, EKS, Lambda\n
        from diagrams.aws.database import RDS, ElastiCache, Redshift
        from diagrams.aws.integration import SQS
        from diagrams.aws.network import VPC, ELB, Route53
        from diagrams.aws.storage import S3"""
        # from diagrams import Cluster, Diagram, Edge
        code_system_prompt = f"Act as a developer coding diagrams in Python. Containers are instantiated with With statement. Example code {example_code}. Replace containers with Cluster class. For nodes, use the following import: {code_import}."
        code_prompt = (
            diagram_result
            + "\nFollow the instruction step by step and write a python code that generates a diagram using diagrams library. Save the image as diagram and show=True. Don't label connections. Don't inlcude } at the end. Don't import anything."
        )

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "system", "content": code_system_prompt},
                {"role": "user", "content": code_prompt},
            ],
            functions=[
                {
                    "name": "get_python_code_for_diagram",
                    "description": "Get the python code for drawing an entity diagram without from diagrams import X. Do not draw lines from cluster to another cluster. It does not have any import statement.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                            }
                        },
                    },
                    "required": ["code"],
                }
            ],
            function_call={"name": "get_python_code_for_diagram"},
            temperature=self.temperature,
        )
        code_result = completion.choices[0].message.function_call.arguments
        code_result = json.loads(code_result, strict=False)["code"]
        code_result = self.remove_import_statements(self.replace_Node(code_result))

        print(code_result)
        self.run_code(code_result)
        return code_result

    # step 4 edit the diagram
    def step_4(self, user_edit_input, code_result):
        # user_edit_input = "Include a non-SAP data outside of virtual private cloud."

        edit_system_prompt = (
            f"Act as a senior developer and comment with #. Draw containers with Cluster(). Here is the original code: "
            + code_result
        )
        edit_prompt = (
            user_edit_input
            + "\nNow edit the code to fix the diagram so that the user is sataisfied with the direction, cluster, node, or edges. If new application or service is mentioned, call the appropriate diagrams class. Make minimum changes and don't delete anything unless told to."
        )

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "system", "content": edit_system_prompt},
                {"role": "user", "content": edit_prompt},
            ],
            functions=[
                {
                    "name": "get_python_code_for_diagram",
                    "description": "Get the python code for drawing an entity diagram without from diagrams import X. Do not draw lines from container to another container.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                            }
                        },
                    },
                    "required": ["code"],
                }
            ],
            function_call={"name": "get_python_code_for_diagram"},
            temperature=self.temperature,
        )
        edit_result = completion.choices[0].message.function_call.arguments
        edit_result = json.loads(edit_result, strict=False)["code"]
        self.run_code(edit_result)
        return edit_result

    def run_code(self, code, done=False):
        while True:
            try:
                exec(code)
                break
            except OSError:
                with Diagram("diagram", show=True):
                    exec(code)
            except SyntaxError:
                if not done:
                    self.run_code(code[:-2], done=True)
                    break

    def remove_import_statements(self, import_string):
        lines = import_string.split("\n")
        filtered_lines = [line for line in lines if "from" and "import" not in line]
        return "\n".join(filtered_lines)

    def replace_Node(self, code):
        all_nodes = [
            "EC2",
            "ECS",
            "EKS",
            "Lambda",
            "RDS",
            "ElastiCache",
            "Redshift",
            "SQS",
            "ELB",
            "Route53",
            "S3",
        ]
        return code.replace("Node", random.choice(all_nodes))
