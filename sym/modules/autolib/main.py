from sqlalchemy.orm.attributes import flag_modified

def create_model_record(session, new_model, new_payload):
    """ Given a new_model and a new_payload object, update any values and save to db"""
    updated_model = update_model(new_model, new_payload)
    session.add(updated_model)
    session.commit()
    return updated_model

def update_model_record(session, existing_model, new_payload):
    """ Given an existing_model and a new_payload, update any values and save to db"""
    updated_model = update_model(existing_model, new_payload)
    session.commit()
    return updated_model

def update_model(existing_model, new_payload):
    for col in existing_model.__table__.columns.keys():
        if col not in new_payload:
            continue
        
        new_value = new_payload[col]
        if new_value:
            setattr(existing_model, col, new_value)
            flag_modified(existing_model, col)
    return existing_model

def convert_model2dict(existing_model, ignore_keys=None):
    d = {}
    for col in existing_model.__table__.columns.keys():
        v = getattr(existing_model, col)
        d[col] = v
    return d