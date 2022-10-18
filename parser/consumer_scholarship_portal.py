import pika
import json
import parser_scholarship_portal
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()


channel.queue_declare(queue='new_data_scholarship_portal')

def callback(ch,method,properties,body):
    parser_scholarship_portal.parse_scholarship_portal(body)

channel.basic_consume(queue='new_data_scholarship_portal',auto_ack=True,on_message_callback=callback)
channel.start_consuming()