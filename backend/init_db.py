"""
Database initialization script
Run this to create tables and seed initial data
"""

from app.core.database import engine, Base
from app.models.models import Sensor, Worker, Alert
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Seed initial data
    with Session(engine) as session:
        # Create sensors
        sensors = [
            Sensor(
                id=str(uuid.uuid4()),
                name="Gas Sensor - Floor 1",
                type="gas",
                location="Production Floor",
                warning_threshold=300,
                critical_threshold=500,
                status="active"
            ),
            Sensor(
                id=str(uuid.uuid4()),
                name="Temperature Sensor - Floor 1",
                type="temperature",
                location="Production Floor",
                warning_threshold=40,
                critical_threshold=60,
                status="active"
            ),
            Sensor(
                id=str(uuid.uuid4()),
                name="Vibration Sensor - Machine Bay",
                type="vibration",
                location="Machine Bay",
                warning_threshold=8,
                critical_threshold=15,
                status="active"
            ),
            Sensor(
                id=str(uuid.uuid4()),
                name="Ultrasonic - Entry Gate",
                type="ultrasonic",
                location="Entry Gate",
                warning_threshold=100,
                critical_threshold=50,
                status="active"
            ),
        ]
        
        # Create workers
        workers = [
            Worker(
                id=str(uuid.uuid4()),
                name="John Doe",
                role="Technician",
                department="Production",
                assigned_area="Floor 1",
                status="active",
                ppe_compliance=True,
                location_zone="Production Floor"
            ),
            Worker(
                id=str(uuid.uuid4()),
                name="Jane Smith",
                role="Supervisor",
                department="Safety",
                assigned_area="All Areas",
                status="active",
                ppe_compliance=True,
                location_zone="Office"
            ),
        ]
        
        try:
            session.add_all(sensors)
            session.add_all(workers)
            session.commit()
            print(f"✅ Seeded {len(sensors)} sensors and {len(workers)} workers")
        except Exception as e:
            print(f"❌ Error seeding data: {e}")
            session.rollback()

if __name__ == "__main__":
    print("🔧 Initializing database...")
    init_db()
    print("✨ Database initialization complete!")
