import pika
import parser_scholars4dev
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()


channel.queue_declare(queue='new_data_scholars4dev')

def callback(ch,method,properties,body):
    parser_scholars4dev.parse_scholars4dev(body)

channel.basic_consume(queue='new_data_scholars4dev',on_message_callback=callback)
channel.start_consuming()