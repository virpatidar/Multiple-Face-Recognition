import numpy as np
from mtcnn import MTCNN
from keras_facenet import FaceNet
from sklearn.metrics.pairwise import cosine_similarity
from config import FACE_MATCH_THRESHOLD

detector = MTCNN()
embedder = FaceNet()

def extract_faces(image):
    results = detector.detect_faces(image)
    faces = []
    for r in results:
        x,y,w,h = r['box']
        faces.append(image[y:y+h, x:x+w])
    return faces

def get_embedding(face):
    face = face.astype('float32')
    emb = embedder.embeddings([face])[0]
    return emb

def match_face(embedding, stored_embeddings):
    best_score = 0
    best_user = None

    for user_id, emb in stored_embeddings:
        score = cosine_similarity([embedding],[emb])[0][0]
        if score > best_score and score > FACE_MATCH_THRESHOLD:
            best_score = score
            best_user = user_id

    return best_user
