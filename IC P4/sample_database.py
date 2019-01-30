from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from camdatabase import *

engine = create_engine('sqlite:///camcatalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Delete Brand if exisitng.
session.query(Brand).delete()
# Delete ModelName if exisitng.
session.query(ModelName).delete()
# Delete Users if exisitng.
session.query(UserData).delete()

# Create sample users
User1 = UserData(name="Mallipudi Prasannaraj",
                 email="prasannarajmallipudi@gmail.com",
                 picture='https://lh5.googleusercontent.com/-6tCX9WOltBs'
                         '/AAAAAAAAAAI/AAAAAAAADJc/T4yOqe2XIjc/photo.jpg')
session.add(User1)
session.commit()
User2 = UserData(name="Prasannaraj", email="prasannaraj.m@apssdc.in",
                 picture='https://lh4.googleusercontent.com/-EW6n0vdHiOk'
                         '/AAAAAAAAAAI/AAAAAAAAAE4/kHbfWo9laMw/photo.jpg')
session.add(User2)
session.commit()

# Create sample Brands
Brand1 = Brand(name="Nikon", user_id=1)
session.add(Brand1)
session.commit()

Brand2 = Brand(name="Canon", user_id=1)
session.add(Brand2)
session.commit

Brand3 = Brand(name="Panasonic", user_id=1)
session.add(Brand3)
session.commit()

Brand4 = Brand(name="Sony", user_id=1)
session.add(Brand4)
session.commit()

Brand5 = Brand(name="LG", user_id=1)
session.add(Brand5)
session.commit()


# Populate a Brand with models for testing
# Using different users for models also
try:
    Model1 = ModelName(id=101,
                       brand_id=2,
                       user_id=1,
                       modelnumber="D7000",
                       colors="Red",
                       price="50000",
                       description="FULL HD | 64 GB ROM | Expandable Upto|"
                       " 25MPxl  4000 mAh Li Polymer Battery"
                       " Qualcomm Snapdragon 625 Processor")

    session.add(Model1)
    session.commit()
except Exception as ex:
    print(ex)

try:
    Model2 = ModelName(id=102,
                       brand_id=3,
                       user_id=1,
                       modelnumber="Canon 5D",
                       colors="Red",
                       price="300000",
                       description="FULL HD | 128 GB ROM | Expandable Upto|"
                       " 45MPxl  5000 mAh Li Polymer Battery "
                       "Qualcomm Snapdragon 625 Processor")

    session.add(Model2)
    session.commit()
except Exception as ex:
    print(ex)

try:
    Model3 = ModelName(id=103,
                       brand_id=4,
                       user_id=1,
                       modelnumber="Panasonic 514",
                       colors="Black",
                       price="60000",
                       description="FULL HD+ | 64 GB ROM | Expandable Upto|"
                       " 45MPxl  5000 mAh Li Polymer Battery "
                       "Qualcomm Snapdragon 625 Processor")

    session.add(Model3)
    session.commit()
except Exception as ex:
    print(ex)
print("Your database has been populated with sample data base")
