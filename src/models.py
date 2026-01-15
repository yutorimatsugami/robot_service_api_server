from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, BigInteger
from database import Base

class RobotMst(Base):
    __tablename__ = "robot_mst"
    robot_id = Column(String(10), primary_key=True, index=True)
    status = Column(Integer, default=0)
    loc_x = Column(Float)
    loc_y = Column(Float)
    battery_level = Column(Integer, default=100)

class MapNode(Base):
    __tablename__ = "map_node"
    node_id = Column(Integer, primary_key=True, index=True)
    node_name = Column(String(50), nullable=False)
    coord_x = Column(Float, nullable=False)
    coord_y = Column(Float, nullable=False)
    attribute = Column(Integer, nullable=False)
    adj_nodes = Column(String(255))

class AdContent(Base):
    __tablename__ = "ad_content"
    ad_id = Column(Integer, primary_key=True, index=True)
    shop_name = Column(String(100), nullable=False)
    category = Column(String(50))
    file_path = Column(String(255))
    description = Column(Text)
    business_hours = Column(String(100))
    map_node_id = Column(Integer, ForeignKey("map_node.node_id"))

class FaqResponse(Base):
    __tablename__ = "faq_responses"
    response_id = Column(Integer, primary_key=True, index=True)
    intent_key = Column(String(50), unique=True, nullable=False)
    trigger_keywords = Column(Text)
    response_text = Column(Text, nullable=False)
    category = Column(String(50))
