import streamlit as st
from diagrams import Diagram, Cluster
from diagrams.k8s.clusterconfig import HPA
from diagrams.k8s.compute import Deployment, Pod, ReplicaSet
from diagrams.k8s.network import Ingress, Service
from PIL import Image


def main():
    with Diagram("diagram", show=False):
        net = Ingress("domain.com") >> Service("svc")
        with Cluster("ReplicaSet"):
            pods = [Pod("pod{}".format(i)) for i in range(1, 3)]
            rs = ReplicaSet("rs")
            _ = rs - pods
        dp = Deployment("dp")
        _ = dp << rs
        hpa = HPA("hpa")
        _ = dp << hpa
        _ = net >> rs << dp

        print()

    st.image(Image.open("diagram.png"))


if __name__ == "__main__":
    main()
