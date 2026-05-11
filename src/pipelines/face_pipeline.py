import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st

from src.database.db import get_all_students


@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(face_recognition_models.pose_predictor_model_location())
    facerec = dlib.face_recognition_model_v1(face_recognition_models.face_recognition_model_location())
    return detector, sp, facerec


def get_face_embeddings(image_np):
    detector, sp, facerec = load_dlib_models()
    faces = detector(image_np, 1)
    encodings = []
    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1)
        encodings.append(np.array(face_descriptor))
    return encodings


@st.cache_resource
def get_trained_model():
    X, y = [], []
    student_db = get_all_students()

    if not student_db:
        return None

    for student in student_db:
        embedding = student.get('face_embedding')
        if embedding:
            X.append(np.array(embedding))
            y.append(student.get('student_id'))

    if not X:
        return None

    clf = SVC(kernel='linear', probability=True, class_weight='balanced')
    try:
        clf.fit(X, y)
    except ValueError as e:
        st.warning(f'Model training failed: {e}')
        return None

    # Build a lookup map for O(1) embedding retrieval by student_id
    embedding_map = {sid: emb for sid, emb in zip(y, X)}
    return {'clf': clf, 'embedding_map': embedding_map, 'y': y}


def train_classifier():
    get_trained_model.clear()  # only clears model cache, preserves dlib cache
    model_data = get_trained_model()
    return bool(model_data)


def predict_attendance(class_image_np):
    encodings = get_face_embeddings(class_image_np)
    detected_student = {}

    model_data = get_trained_model()
    if not model_data:
        return detected_student, [], len(encodings)

    clf = model_data['clf']
    embedding_map = model_data['embedding_map']
    all_students = sorted(list(embedding_map.keys()))

    for encoding in encodings:
        if len(all_students) >= 2:
            predicted_id = int(clf.predict([encoding])[0])
        else:
            predicted_id = int(all_students[0])

        student_embedding = embedding_map.get(predicted_id)
        if student_embedding is None:
            continue

        distance = np.linalg.norm(student_embedding - encoding)
        if distance <= 0.6:
            detected_student[predicted_id] = True

    return detected_student, all_students, len(encodings)
