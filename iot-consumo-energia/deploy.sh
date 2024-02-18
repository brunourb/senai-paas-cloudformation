#!/bin/bash

echo "Compactando o projeto"
zip iot-energia.zip lambda.py requirements.txt

echo "Fazendo upload do arquivo"
aws s3 cp iot-energia.zip s3://inserir-um-nome-unico-globalmente/iot-energia.zip --profile=aws_academy

echo "Subindo a stack no cloudformation"
aws cloudformation create-stack --profile=aws_academy --region=us-east-1 \
    --stack-name 'iot-consumo-energia-stack' \
    --capabilities CAPABILITY_IAM \
    --template-body file://$(pwd)/stack.yaml