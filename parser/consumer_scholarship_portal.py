import pika
import parser_scholars4dev
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()


channel.queue_declare(queue='new_data_scholarship_portal')

def callback(ch,method,properties,body):
    print(body, type(body))

channel.basic_consume(queue='new_data_scholarship_portal',on_message_callback=callback,auto_ack=True)
channel.start_consuming()
