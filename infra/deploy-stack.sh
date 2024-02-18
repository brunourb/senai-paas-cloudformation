#!/bin/bash

SnsName=sns-iot-consumo-energia
SqsQueueDqlName=sqs-iot-consumo-energia-dlq
SqsQueueName=sqs-iot-consumo-energia
LambdaName=iot-consumo-energia-lambda
S3Key=iot-consumo-energia

echo "Alterando o nome da SnsName"
sed -i "s/@@SnsName@@/$SnsName/g" cloudformation-stack.yaml

echo "Alterando o nome da SqsQueueDqlName"
sed -i "s/@@SqsQueueDqlName@@/$SqsQueueDqlName/g" cloudformation-stack.yaml

echo "Alterando o nome da SqsQueueName"
sed -i "s/@@SqsQueueName@@/$SqsQueueName/g" cloudformation-stack.yaml

echo "Alterando o nome da LambdaName"
sed -i "s/@@LambdaName@@/$LambdaName/g" cloudformation-stack.yaml

echo "Alterando o nome S3Key"
sed -i "s/@@S3Key@@/$S3Key/g" cloudformation-stack.yaml