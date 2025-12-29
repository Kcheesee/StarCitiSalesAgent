"""
Ship and related models
"""

from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    code = Column(String(50))
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship
    ships = relationship("Ship", back_populates="manufacturer")


class Ship(Base):
    __tablename__ = "ships"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    class_name = Column(String(255))

    # Manufacturer
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"))
    manufacturer_name = Column(String(255))

    # Classification
    focus = Column(String(255), index=True)
    type = Column(String(100), index=True)

    # Dimensions
    length = Column(DECIMAL(10, 2))
    beam = Column(DECIMAL(10, 2))
    height = Column(DECIMAL(10, 2))
    mass = Column(Integer)

    # Capacity
    cargo_capacity = Column(Integer, default=0, index=True)
    vehicle_inventory = Column(DECIMAL(10, 2))
    personal_inventory = Column(DECIMAL(10, 2))

    # Crew
    crew_min = Column(Integer, index=True)
    crew_max = Column(Integer)
    crew_weapon = Column(Integer)
    crew_operation = Column(Integer)

    # Health & Shields
    health = Column(Integer)
    shield_hp = Column(Integer)
    shield_face_type = Column(String(50))

    # Speed
    speed_scm = Column(Integer)
    speed_max = Column(Integer)
    speed_zero_to_scm = Column(DECIMAL(10, 2))
    speed_zero_to_max = Column(DECIMAL(10, 2))

    # Agility
    agility_pitch = Column(DECIMAL(10, 2))
    agility_yaw = Column(DECIMAL(10, 2))
    agility_roll = Column(DECIMAL(10, 2))

    # Acceleration
    accel_main = Column(DECIMAL(10, 2))
    accel_retro = Column(DECIMAL(10, 2))
    accel_vtol = Column(DECIMAL(10, 2))
    accel_maneuvering = Column(DECIMAL(10, 2))

    # Fuel
    fuel_capacity = Column(DECIMAL(10, 2))
    fuel_intake_rate = Column(DECIMAL(10, 2))
    fuel_usage_main = Column(DECIMAL(10, 2))
    fuel_usage_maneuvering = Column(DECIMAL(10, 2))

    # Quantum
    quantum_speed = Column(Integer)
    quantum_spool_time = Column(DECIMAL(10, 2))
    quantum_fuel_capacity = Column(DECIMAL(10, 2))
    quantum_range = Column(Integer)

    # Emissions
    emission_ir = Column(Integer)
    emission_em_idle = Column(Integer)
    emission_em_max = Column(Integer)

    # Descriptions
    description = Column(Text)
    description_de = Column(Text)
    description_cn = Column(Text)

    # External data
    marketing_description = Column(Text)
    price_usd = Column(DECIMAL(10, 2), index=True)
    price_auec = Column(Integer)
    store_url = Column(String(500))
    image_url = Column(String(500))
    image_local_path = Column(String(500))

    # Metadata
    raw_data = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    manufacturer = relationship("Manufacturer", back_populates="ships")
    hardpoints = relationship("ShipHardpoint", back_populates="ship", cascade="all, delete-orphan")
    components = relationship("ShipComponent", back_populates="ship", cascade="all, delete-orphan")
    vehicle_bays = relationship("ShipVehicleBay", back_populates="ship", cascade="all, delete-orphan")
    embedding = relationship("ShipEmbedding", back_populates="ship", uselist=False, cascade="all, delete-orphan")


class ShipHardpoint(Base):
    __tablename__ = "ship_hardpoints"

    id = Column(Integer, primary_key=True, index=True)
    ship_id = Column(Integer, ForeignKey("ships.id", ondelete="CASCADE"), index=True)

    hardpoint_name = Column(String(255))
    size = Column(Integer)
    type = Column(String(100))
    category = Column(String(100))
    quantity = Column(Integer, default=1)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationship
    ship = relationship("Ship", back_populates="hardpoints")


class ShipComponent(Base):
    __tablename__ = "ship_components"

    id = Column(Integer, primary_key=True, index=True)
    ship_id = Column(Integer, ForeignKey("ships.id", ondelete="CASCADE"), index=True)

    component_type = Column(String(100))
    component_name = Column(String(255))
    size = Column(Integer)
    manufacturer = Column(String(255))
    quantity = Column(Integer, default=1)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationship
    ship = relationship("Ship", back_populates="components")


class ShipVehicleBay(Base):
    __tablename__ = "ship_vehicle_bays"

    id = Column(Integer, primary_key=True, index=True)
    ship_id = Column(Integer, ForeignKey("ships.id", ondelete="CASCADE"), index=True)

    bay_type = Column(String(100))
    capacity = Column(Integer)
    max_size = Column(String(50))

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationship
    ship = relationship("Ship", back_populates="vehicle_bays")


class ShipEmbedding(Base):
    __tablename__ = "ship_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    ship_id = Column(Integer, ForeignKey("ships.id", ondelete="CASCADE"), unique=True, index=True)

    search_text = Column(Text, nullable=False)
    embedding = Column(JSON)  # JSONB array of floats (will be vector type with pgvector)

    embedding_model = Column(String(100), default="text-embedding-3-small")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship
    ship = relationship("Ship", back_populates="embedding")
