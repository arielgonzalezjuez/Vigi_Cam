from django.shortcuts import render, redirect, get_object_or_404
from .models import Persona, RegistroAcceso, Camara
from .forms import PersonaForm, CamaraForm, ClienteRegistrarForm, ClienteActualizarForm
from threading import Thread
import cv2
# import dlib
import datetime
# from onvif import ONVIFCamera
from django.http import StreamingHttpResponse
# import face_recognition
import numpy as np
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def cctv(request):
    return render(request, 'cctv.html')

def company(request):
    return render(request, 'company.html')

def testimonial(request):
    return render(request, 'testimonial.html')

def cameras(request):
    return render(request, 'cameras.html')

def inicio_sesion(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form':AuthenticationForm})
    else:
        cliente = authenticate(request,username=request.POST['username'], password=request.POST['password'])
        if cliente is None:
            return render(request, 'login.html', {'form':AuthenticationForm, 'error':'Usuario o contraseña incorrectos'})
        else:
            login(request,cliente)
            return redirect('index')
        
@login_required
def cerrarSession(request):
    logout(request) 
    return redirect('index')

# Vista para manejar la lista de personas y el registro de cámaras
@login_required
def lista_personas(request):
    personas = Persona.objects.all()
    return render(request, 'lista_persona.html', {'personas': personas})

@login_required
def registrar_persona(request):
    title = 'Registrar Persona'
    if request.method == 'POST':
        form = PersonaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_personas')
    else:
        form = PersonaForm()
    return render(request, 'registrar_persona.html', {'form': form, 'title': title})

@login_required
def editar_persona(request, id_persona):
    title = 'Editar Persona'
    persona = get_object_or_404(Persona, pk=id_persona)
    if request.method == 'POST':
        form = PersonaForm(request.POST, request.FILES, instance=persona)
        if form.is_valid():
            form.save()
            return redirect('lista_personas')
    else:
        form = PersonaForm(instance=persona)
    return render(request, 'registrar_persona.html', {'form': form, 'persona': persona, 'title': title})

@login_required
def eliminar_persona(request, id_persona):
    persona = get_object_or_404(Persona, pk=id_persona)
    if request.method == "POST":
        persona.delete()
        return redirect('lista_personas')

# Modelo de Persona y RegistroAcceso está incluido para almacenar la información
# de la persona y los registros de accesos

# Función para iniciar la captura y el reconocimiento facial desde una cámara ONVIF
@login_required
def registrar_camara(request):
    if request.method == 'POST':
        formC = CamaraForm(request.POST)
        if formC.is_valid():
            formC.save()
            return redirect('reconocimiento_facial')
    else:
        formC = CamaraForm()
    return render(request, 'registrar_camara.html', {'formC': formC})

@login_required
def reconocimiento_facial(request):
     cameras = Camara.objects.all()
     return render(request, 'reconocimiento.html', {'camaras': cameras})

@login_required
def capturaVideo(request):
     return StreamingHttpResponse(gen_frames(),content_type='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    video = cv2.VideoCapture(0)
    
    while True:
        succes, frame = video.read()
        if not succes:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# def video_feed():
#     cap = cv2.VideoCapture(0)

#     known_face_encodings = []
#     known_face_names = []

#     # Carga imágenes de ejemplo y genera encodings
#     # known_face_encodings.append(face_recognition.face_encodings(face_recognition.load_image_file("tu_imagen.jpg"))[0])
#     # known_face_names.append("Nombre")

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
        
#         rgb_frame = frame[:, :, ::-1]
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             name = "Desconocido"

#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#                 # Guardar la imagen capturada
#                 imagen_capturada = cv2.imencode('.jpg', frame)[1].tobytes()
#                 image_file = ContentFile(imagen_capturada, name=f"captura_{datetime.datetime.now().timestamp()}.jpg")

#                 # Busca la persona en la base de datos
#                 persona = Persona.objects.filter(nombre=name).first()
#                 if persona:
#                     RegistroAcceso.objects.create(persona=persona, imagen_capturada=image_file)

#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
#             cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', frame)[1].tobytes() + b'\r\n')

#     cap.release()
