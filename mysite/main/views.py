from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from . models import ToDoList, Item
from . forms import CreateNewList
from django.contrib.auth.models import User

import pyaudio
import numpy as np
import threading
# Create your views here.

def index(response, id):
    ls = ToDoList.objects.get(id=id)

    if response.method == "POST":
        print(response.POST)
        if response.POST.get("save"):
            for item in ls.item_set.all():
                if response.POST.get("c" + str(item.id)) == "clicked":
                    item.complete = True
                else:
                    item.complete = False

                item.save()

        elif response.POST.get("newItem"):
            txt = response.POST.get("new")

            if len(txt) > 2:
                ls.item_set.create(text=txt, complete=False)
            else:
                print("invalid")


    return render(response, "main/list.html", {"ls": ls})

def home(response, user=None):
    users = User.objects.all()
    usernames = [user.username for user in users]
    return render(response, "main/home.html", {'usernames': usernames})

def create(response):
    if response.method == "POST":
        form = CreateNewList(response.POST)

        if form.is_valid():
            n = form.cleaned_data["name"]
            t = ToDoList(name=n)
            t.save()

        return HttpResponseRedirect("/%i" %t.id)

    else:
         form = CreateNewList()
    return render(response, "main/create.html", {"form": form})


def call(response):

    CHUNK = 1024
    CHANNELS = 2
    RATE = 44100

    p = pyaudio.PyAudio()

    recording_buffer = np.zeros(CHUNK, dtype=np.int16)

    def record_audio():
        nonlocal recording_buffer
        stream = p.open(format=pyaudio.paInt16,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        while True:
            data = stream.read(CHUNK)
            recording_buffer = np.frombuffer(data, dtype=np.int16)

    def play_audio():
        nonlocal recording_buffer
        stream = p.open(format=pyaudio.paInt16,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK)
        while True:
            stream.write(recording_buffer.tobytes())

    record_thread = threading.Thread(target=record_audio)
    record_thread.start()

    play_thread = threading.Thread(target=play_audio)
    play_thread.start()

    record_thread.join()
    play_thread.join()

    p.terminate()

    return render(response, "main/call.html", {"call": call()})








