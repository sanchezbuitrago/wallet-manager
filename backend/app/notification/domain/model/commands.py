from app.commons import base_types


class SendWhatsAppMessageCommand(base_types.ValueObject):
    remote_jid: str
    message: str
