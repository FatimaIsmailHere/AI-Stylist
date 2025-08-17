from database import Base, engine  # Adjust import if needed
import models 
# This will create all tables defined by Base's subclasses (your models)
Base.metadata.create_all(bind=engine)
print("All tables created!")