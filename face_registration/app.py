import cuda_config
from camera import Camera
from face_detector import FaceDetector
from face_embedding import FaceEmbedding
from database import Database
from registration import Registration
from gui import RegistrationGUI
from excel import ExcelManager



camera = Camera()

detector = FaceDetector()

embedding_model = FaceEmbedding()

database = Database()

excel = ExcelManager()

registration = Registration(
    camera,
    detector,
    embedding_model,
    database
)



gui = RegistrationGUI()



# Connect buttons

gui.capture_button.configure(
    command=lambda:
    registration.capture_face(gui)
)


gui.register_button.configure(
    command=lambda:
    registration.register_user(gui)
)



gui.run()