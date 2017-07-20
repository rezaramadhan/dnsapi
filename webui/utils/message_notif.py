

class MessageNotif(object):
    # The class "constructor" - It's actually an initializer
    def __init__(self, status, message, type_notif, message_item):
        self.status = status
        self.message = message
        self.type_notif = type_notif
        self.message_item = message_item

def get_message_notif(status, message_item=None, message_custom=None):
    message_notif = {}
    message = 'Undefined message notification. See Log.'
    type_notif = 'warning'


    if status=='success_add':
        message = 'Success Add New Record  : '
        type_notif = 'success'
    if status=='failed_add':
        message = 'Failed Add New Record : '
        type_notif = 'danger'
    if status=='success_edit':
        message = 'Success Edit Record  : '
        type_notif = 'success'
    if status=='failed_edit':
        message = 'Failed Edit Record : '
        type_notif = 'danger'
    if status=='success_delete':
        message = 'Success Delete Record  : '
        type_notif = 'success'
    if status=='failed_delete':
        message = 'Failed Delete Record : '
        type_notif = 'error'
    if status=='success_addzone':
        message = 'Success Add New Zone  : '
        type_notif = 'success'
    if status=='failed_addzone':
        message = 'Failed Add New Record : '
        type_notif = 'danger'

    if status=='error':
        message = 'Error to process action : '
        type_notif = 'danger'

    # Log Link
    if type_notif!='success':
        message_item = message_item+'. See Log.'

    # Custom Message (Info)
    if message_custom:
        message = message_custom
        type_notif = 'info'

    message_notif['status'] = status
    message_notif['message'] = message
    message_notif['type_notif'] = type_notif
    message_notif['message_item'] = message_item

    return message_notif
