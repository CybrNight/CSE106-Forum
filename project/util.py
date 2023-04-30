from . import db
import uuid


def generate_uuid(model, size=32):
    temp_uuid = uuid.uuid4().hex[:size]
    exists = True

    while exists:
        exists = db.session.query(model.uuid).filter_by(
            uuid=temp_uuid).first() is not None
        temp_uuid = uuid.uuid4().hex[:size]

    return temp_uuid
