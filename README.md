**FinVista Capital: Financial Intelligence Assistant**
**Overview**
The Financial Intelligence Assistant is an AI-powered solution designed to streamline the analysis of complex financial documents. By leveraging a Retrieval-Augmented Generation (RAG) architecture, the application enables users to query annual reports and extract critical insights efficiently.

**Technical Architecture**
This project is built using a modern cloud-native stack:

Core Logic: Python-based RAG engine for intelligent document parsing and retrieval.

Data Storage: Vector database implementation using ChromaDB for efficient information retrieval.

Containerization: Application logic is containerized using Docker to ensure consistency across environments.

Deployment: Orchestrated on Amazon EKS (Kubernetes), utilizing a LoadBalancer service to provide public-facing access to the AI assistant.

**Key Features**
Automated Document Processing: Automatically ingests and indexes annual reports (PDFs).

Intelligent Querying: Uses advanced NLP to answer specific financial questions based on provided data.

Scalable Infrastructure: Kubernetes-ready design allows for scaling based on request volume.

Getting Started
Clone the repository: git clone <your-repository-url>

Environment Setup: Ensure your Python environment is configured with the dependencies listed in requirements.txt.

Deployment: The application is designed to be deployed to a Kubernetes cluster using the provided deployment.yaml and service.yaml files.

winget install eksctl

eksctl version

eksctl create cluster `
  --name financial-assistant-cluster `
  --region us-east-1 `
  --nodegroup-name standard-workers `
  --node-type t3.medium `
  --nodes 2 `
  --managed

kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

kubectl get nodes

kubectl get pods

kubectl get services
