

class MessageNotif(object):
    # The class "constructor" - It's actually an initializer
    def __init__(self, status, message, type_notif, item):
        self.status = status
        self.message = message
        self.type_notif = type_notif
        self.item = item

def get_message_notif(status, item_name='', message_custom=None):

    message = 'Undefined message notification.'
    type_notif = 'warning'

    if status=='success_add':
        message = 'Success Add New Record  : '
        type_notif = 'success'
    if status=='failed_add':
        message = 'Failed Add New Record.'
        type_notif = 'danger'
    if status=='success_edit':
        message = 'Success Edit Record  : '
        type_notif = 'success'
    if status=='failed_edit':
        message = 'Failed Edit Record.'
        type_notif = 'danger'
    if status=='success_del':
        message = 'Success Delete Record  : '
        type_notif = ' success'
    if status=='failed_del':
        message = 'Failed Delete Record.'
        type_notif = 'danger'
    if message_custom:
        message = message_custom
        type_notif = 'info'


    return MessageNotif(status,message,type_notif,item_name)
