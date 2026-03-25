from datetime import datetime
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


class DB:
    def __init__(self, app=None):
        self.client = None
        self.db = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.client = MongoClient(app.config["MONGO_URI"])
        self.db = self.client.get_database()
        app.db = self.db  # Make db available in app context

db = DB()


class User:
    @classmethod
    def get_collection(cls):
        from flask import current_app
        return current_app.db.users

    def __init__(self, name, email, driver_id=None, language="en", alert_volume=70, theme="dark"):
        self.name = name
        self.email = email
        self.driver_id = driver_id or f"DRV-{uuid.uuid4().hex[:8].upper()}"
        self.language = language
        self.alert_volume = alert_volume
        self.theme = theme
        self.created_at = datetime.utcnow()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        data = {
            "name": self.name,
            "email": self.email,
            "driver_id": self.driver_id,
            "language": self.language,
            "alert_volume": self.alert_volume,
            "theme": self.theme,
            "created_at": self.created_at,
            "password_hash": self.password_hash
        }
        if hasattr(self, '_id'):
            data["_id"] = self._id
        return data

    @classmethod
    def find_by_email(cls, email):
        return cls.get_collection().find_one({"email": email})

    @classmethod
    def find_by_id(cls, user_id):
        return cls.get_collection().find_one({"_id": user_id})

    def save(self):
        result = self.get_collection().insert_one(self.to_dict())
        self._id = result.inserted_id
        return self


class DetectionEvent:
    @classmethod
    def get_collection(cls):
        from flask import current_app
        return current_app.db.detection_events

    def __init__(self, user_id, event_type, confidence=0.0, meta=None):
        self.user_id = user_id
        self.event_type = event_type
        self.confidence = confidence
        self.meta = meta or {}
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "event_type": self.event_type,
            "confidence": self.confidence,
            "meta": self.meta,
            "created_at": self.created_at
        }

    def save(self):
        self.get_collection().insert_one(self.to_dict())
        return self
