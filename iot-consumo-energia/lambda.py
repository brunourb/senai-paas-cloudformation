from datetime import datetime
import json
import logging
import boto3
#Estamos criando uma instância da classe Logger para 'melhorar' a forma de apresentar 'dados'
#para o usuário fazer a 'auditoria' das informações que são processadas no lambda.
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#Tudo numa função LAMBDA começa pelo HANDLER.
# O HANDLER é responsável para 'iniciar' o processamento de uma função lambda.
# Geralmente em código python, podemos 'substituir' pelo método main(event, context)
#O evento que contém a informação relacionada ao 'recurso' que está enviando a mensagem
#Exemplo: uma SQS (fila), envia um JSON 'gigante' que está dentro da propriedade body
"""
Exemplo de um payload em SQS
{
  "Records": [
    {
      "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
      "receiptHandle": "MessageReceiptHandle",
      "body": "{\"grupo\":\"xxxx\",\"idDispositivo\":123123123,\"consumo\":40}",
      "attributes": {
        "ApproximateReceiveCount": "1",
        "SentTimestamp": "1523232000000",
        "SenderId": "123456789012",
        "ApproximateFirstReceiveTimestamp": "1523232000001"
      },
      "messageAttributes": {},
      "md5OfBody": "7b270e59b47ff90a553787216d55d91d",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:eu-west-1:156445482446:TestQueue",
      "awsRegion": "eu-west-1"
    }
  ]
}
"""
def handler(event, context):

    #event
    #As informações que serão 'tratadas/recebidas' estão dentro da variável event

    #context
    #É o contexto/instância/domínio de serviços que o serviço
    #  utilizador (lambda) pode acessar/identificar

    #Nome da função com ARN (item identificador)
    logger.info(f"Lambda function ARN: {context.invoked_function_arn}")
    
    #Nome do grupo de log que é exibid no cloudwatch
    logger.info(f"CloudWatch log stream name: {context.log_stream_name}") 
    logger.info(f"CloudWatch log group name: {context.log_group_name}")
    
    #ID da requisição do lambda
    logger.info(f"Lambda Request ID: {context.aws_request_id}")

    #Acessando o campo 'body' do primeiro registro em 'Records'
    mensagemSQS = event['Records'][0]['body']

    logger.info(f"Extratindo conteúdo de uma mensagem recebida de uma SQS: {mensagemSQS}")

    try:
        #Converter o texto(json) em dicionário
        #{\"grupo:\":\"xxxx\",\"idDispositivo\":123123123,\"consumo\":40}
        data = json.loads(mensagemSQS)

        logger.info(f"Mensagem do dicionário data: {data}")

        logger.info(f"Início processamento de dados do grupo nº {data['grupo']}")
        logger.info(f"Início processamento de dados do dispositivo nº {data['idDispositivo']}")
        logger.info(f"Início processamento de dados do consumo nº {data['consumo']}")

        
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao fazer parse do JSON: {str(e)}")
        #Tratamento de erro
        return {"statusCode": 400, "body": "Erro ao decodificar JSON no corpo da mensagem"}
    
    
    resultado = processar_dados(data, context)
    
    #logger.info(f"Fim processamento de dados do dispositivo nº {event['idDispositivo']}")    
    #logger.debug(resultado)
    
    return None

def processar_dados(data, context):
    response = ""
    
    # Inserir dependências no projeto do dynamodb seja o resource e cliente.
    # Um manipula os dados dentro do dynamo e o cilente, faz as consultas.
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('iot-consumo-energia')
    
    #Gerar o timestamp (registro do evento) para persistência
    dataEvento = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    
    #Capturando dados que foram enviados por um recurso: lambda, SQS (fila), SNS(tópico)
    #As informações 'chegam' na função através de EVENTOS
    grupo = data['grupo']
    idDispositivo = data['idDispositivo']
    consumo = data['consumo']

    
    #Preparar os dados para inserção no DYNAMODB
    #Chamar a instância do cliente para 'manipular' as informações no banco de dados
    try:
        
        #Preparando dados para persistência
        item={
                'dataEvento': dataEvento,
                'idDispositivo': idDispositivo,
                'grupo': grupo,
                'consumo': int(consumo)
            }
        logger.info("Criado objeto para persistência")
        
        #Persistência dos dados
        #response = dynamodb.put_item(TableName='temperatura',Item=item)
        response = table.put_item(Item=item)
        
        #Retorno dos dados
        return {
            'statusCode': 200,
            'message': json.dumps('Registro inserido com sucesso!'),
            'data': [item],
        }
        
    except:
        logger.debug(f"Valores recebidos: {item}")
        logger.debug(f"Retorno dynamoDB: {response}")
        #https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
        return {
            'statusCode': 400,
            'message': json.dumps('Erro ao registrar temperatura.'),
            'data': [item],
        }