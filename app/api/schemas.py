from marshmallow import Schema, fields, validate

class HospitalResultSchema(Schema):
    row = fields.Int(required=True)
    hospital_id = fields.Int(allow_none=True)
    name = fields.Str(required=True)
    status = fields.Str(required=True)
    error_detail = fields.Str(allow_none=True)

class BulkProcessResponseSchema(Schema):
    batch_id = fields.Str(required=True)
    total_hospitals = fields.Int(required=True)
    processed_hospitals = fields.Int(required=True)
    failed_hospitals = fields.Int(required=True)
    processing_time_seconds = fields.Float(required=True)
    batch_activated = fields.Bool(required=True)
    hospitals = fields.List(fields.Nested(HospitalResultSchema), required=True)
