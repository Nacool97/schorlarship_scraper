import pika
import parser_scholars4dev
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()


channel.queue_declare(queue='new_data_scholarship_portal')

def callback(ch,method,properties,body):
    print(list(body)[0], type(body))

channel.basic_consume(queue='new_data_scholarship_portal',auto_ack=True,on_message_callback=callback)
channel.start_consuming()