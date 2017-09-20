from django.shortcuts import render,redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
import datetime

from reservierung import models
from reservierung import forms
from . import forms as s_forms
# Create your views here.

class SchilderReservierungDetail(DetailView):
    """
    Zeigt die Details zu einer Bestimmten Reservierung an.
    """
    model = models.Reservierung
    context_object_name = 'reservierung'
    template_name = 'schilder/reservierung_detail.html'


class SchilderList(ListView):
    """
    Liefert eine Liste aller Räume zurück, auch Räume an denen bisher kein
    digitales Türschild hängt. Dies ist für eine einfache Einrichtung der
    Türschilder hier
    """
    model = models.Raum
    context_object_name = 'schilder'
    template_name = 'schilder/schilder_list.html'


def schilder_detail(request,pk):
    """
    Startseite der Türschilder, liefert die Reservierungen
    für die aktuelle Woche zurück
    """
    # Aktuelle Woche und Jahr
    current_week = datetime.date.today().isocalendar()[1]
    current_year = datetime.date.today().isocalendar()[0]
    is_week = None
    if request.method == 'POST':
        jahr = int(request.POST['jahr'])
        woche = int(request.POST['woche'])

        if request.POST.__contains__('next_week'):
            if woche == datetime.date(jahr, 12, 28).isocalendar()[1]:
                woche = 1
                jahr = jahr + 1
            else:
                woche = woche + 1
        if request.POST.__contains__('last_week'):
            if woche == 1:
                jahr = jahr -1
                woche = datetime.date(jahr,12,28).isocalendar()[1]
            else:
                woche = woche - 1

    else:
        jahr = datetime.date.today().isocalendar()[0]
        woche = datetime.date.today().isocalendar()[1]

    if woche == current_week:
        is_week = True
    if woche != current_week:
        is_week = False
    reservierungen = []
    raum_frei = True
    raum = models.Raum.objects.get(id=pk)
    alle_reservierungen = models.Reservierung.objects.filter(reservierterRaum=raum.id)
    for reservierung in alle_reservierungen:
        if ((reservierung.anfangsDatum.isocalendar()[1] == woche and reservierung.anfangsDatum.isocalendar()[0] == jahr)
         or (reservierung.endDatum.isocalendar()[1] == woche and reservierung.endDatum.isocalendar()[0] == jahr)):
            reservierungen.append(reservierung)
        if reservierung.anfangsDatum <= datetime.date.today() and reservierung.endDatum >= datetime.date.today():
            if reservierung.anfangsZeit <= datetime.datetime.now().time() and reservierung.endZeit >= datetime.datetime.now().time():
                raum_frei = False
    context_dict = {'raum':raum,'reservierungen':reservierungen,
    'raum_frei':raum_frei,'woche':woche,'jahr':jahr,'current_week':current_week,
    'current_year':current_year,'is_week':is_week}
    return render(request,'schilder/generic_room.html',context_dict)

def schilder_login(request,room):
    """
    Spezieller Login für die Türschilder, leitet zurück zur Startseite
    des Türschildes von welchem aus die Loginseite aufgerufen wurde
    """
    current_room = models.Raum.objects.get(id=int(room))
    if request.method == 'POST':
        form = s_forms.SchilderLoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get("username"),
            password=form.cleaned_data.get("password"))
            if user is not None:
                login(request, user)
                return redirect('schilder:schilder-detail', pk=int(room))
    else:
        form = s_forms.SchilderLoginForm()
    return render(request, 'schilder/login.html',{'form':form,'current_room':current_room})

def schilder_logout(request,room):
    """
    Logout welcher zurück zum entsprechenden Schild leitet
    """
    print("logout")
    logout(request)
    return redirect('schilder:schilder-detail', pk=int(room))

def reservierung_form(request,pk):
    """
    Angepasste Reservierungs Funktion aus der App reservierung
    leitet nach erfolgreicher reservierung zurück zur Startseite des
    Türschildes von dem die Seite aufgerufen wurde
    """
    if request.user.is_authenticated:
        nutzer = request.user
        free_rooms = None
        reserv = None
        moeglich = False
        current_room = models.Raum.objects.get(id=int(pk))
        if request.method == 'POST':
            form = forms.ReservierungForm(data=request.POST)
            if form.is_valid():
                free_rooms = []
                reservierungen = models.Reservierung.objects.filter(reservierterRaum=form.cleaned_data.get("reservierterRaum"))
                if reservierungen.exists():
                    for reservierung in reservierungen:
                        print(reservierung)
                        if reservierung.taeglich:
                            print("reservierung täglich true")
                            # liegt form.anfangsDatum in einer bereits bestehenden reservierung
                            if reservierung.anfangsDatum < form.cleaned_data.get("anfangsDatum") and form.cleaned_data.get("anfangsDatum") < reservierung.endDatum:
                                # ist die reservierung täglich
                                print("liegt in reservierung")
                                if form.cleaned_data.get("taeglich"):
                                    # liegt die r.endZeit vor f.anfangsZeit oder r.anfangsZeit nach f.endZeit
                                    print("form täglich")
                                    if reservierung.endZeit <= form.cleaned_data.get("anfangsZeit") or reservierung.anfangsZeit >= form.cleaned_data.get("endZeit"):
                                        # trifft zu also reservierung möglich
                                        moeglich = True
                                    else:
                                        moeglich = False
                                        reserv = reservierung
                                        break
                                else:
                                    if reservierung.endZeit <= form.cleaned_data.get("anfangsZeit"):
                                        moeglich = True
                                    elif reservierung.anfangsZeit >= form.cleaned_data.get("endZeit"):
                                        moeglich = True
                                    else:
                                        # reservierung ganztägig
                                        # nicht möglich
                                        print("nicht möglich")
                                        moeglich = False
                                        reserv = reservierung
                                        break
                            else:
                                # liegt f.anfangsDatum nach r.endDatum
                                print("else block")
                                if reservierung.endDatum < form.cleaned_data.get("anfangsDatum"):
                                    moeglich = True
                                # liegen r.endDatum und f.anfangsDatum auf den gleichen Tag
                                elif reservierung.endDatum == form.cleaned_data.get("anfangsDatum"):
                                    # liegt die r.endZeit vor f.anfangsZeit
                                    if reservierung.endZeit <= form.cleaned_data.get("anfangsZeit"):
                                        # reservierung möglich
                                        moeglich = True
                                    # liegt r.anfangsZeit nach f.endZeit
                                    elif reservierung.anfangsZeit >= form.cleaned_data.get("endZeit"):
                                        #reservierung möglich
                                        moeglich = True
                                    else:
                                        # Reservierung nicht möglich
                                        moeglich = False
                                        reserv = reservierung
                                        break
                                # ist r.anfangsDatum und f.endDatum am gleichen Tag
                                elif reservierung.anfangsDatum == form.cleaned_data.get("endDatum"):
                                    if reservierung.endZeit <= form.cleaned_data.get("anfangsZeit"):
                                        #reservierung möglich
                                        moeglich = True
                                    elif reservierung.anfangsZeit >= form.cleaned_data.get("endZeit"):
                                        # reservierung möglich
                                        moeglich = True
                                    else:
                                        moeglich = False
                                        reserv = reservierung
                                        break
                        else:
                            if reservierung.anfangsDatum < form.cleaned_data.get("anfangsDatum") and form.cleaned_data.get("anfangsDatum") < reservierung.endDatum:
                                # fehlermeldung anzeigen
                                # verfügbare räume anzeigen
                                # reservierung die belegt anzeigen
                                print("Block 1")
                                moeglich = False
                                reserv = reservierung
                                break
                            else:
                                # aktuelle reservierungsende liegt vor dem beginn der neuen
                                if reservierung.endDatum < form.cleaned_data.get("anfangsDatum"):
                                    moeglich = True
                                    print("Block 2")
                                # reservierungsende und beginn der neuen gleicher tag
                                elif reservierung.endDatum == form.cleaned_data.get("anfangsDatum"):
                                    # reservierungs zeit ende vor oder gleich der neuen anfangszeit
                                    if reservierung.endZeit <= form.cleaned_data.get("anfangsZeit"):
                                        moeglich = True
                                        print("Block 3")
                                    elif reservierung.anfangsZeit >= form.cleaned_data.get("endZeit"):
                                        moeglich = True
                                    else:
                                        moeglich = False
                                        print("Block 4")
                                        reserv = reservierung
                                        break
                                elif reservierung.anfangsDatum > form.cleaned_data.get("endDatum"):
                                    moeglich = True
                                    print("Block 5")
                                elif reservierung.anfangsDatum == form.cleaned_data.get("endDatum"):
                                    if reservierung.anfangsZeit > form.cleaned_data.get("endZeit"):
                                        moeglich = True
                                        print("Block 6")
                                    else:
                                        moeglich = False
                                        print("Block 7")
                                        reserv = reservierung
                                        break
                else:
                    moeglich = True
                if moeglich:
                    reserv = models.Reservierung()
                    reserv.reserviert_von = request.user
                    reserv.reservierterRaum = models.Raum.objects.get(id=form.cleaned_data.get("reservierterRaum"))
                    reserv.reservierungsGrund = form.cleaned_data.get("reservierungsGrund")
                    reserv.anfangsDatum = form.cleaned_data.get("anfangsDatum")
                    reserv.endDatum = form.cleaned_data.get("endDatum")
                    reserv.anfangsZeit = form.cleaned_data.get("anfangsZeit")
                    reserv.endZeit = form.cleaned_data.get("endZeit")
                    reserv.taeglich = form.cleaned_data.get("taeglich")
                    reserv.save()
                    return redirect('schilder:schilder-detail', pk=int(pk))

                else:
                    # return free rooms
                    # restlichen reservierungen anschauen
                    rooms = models.Raum.objects.exclude(id=form.cleaned_data.get("reservierterRaum"))
                    if rooms.exists():
                        for room in rooms:
                            room_reservs = models.Reservierung.objects.filter(reservierterRaum=room)
                            # existieren reservierungen
                            if room_reservs.exists():
                                # für alle reservierungen
                                free_room = False
                                for room_reserv in room_reservs:
                                    # liegt die reservierung in dem zeitraum einer bestehenden Reservierung
                                    if form.cleaned_data.get("taeglich"):
                                        if room_reserv.anfangsDatum < form.cleaned_data.get("anfangsDatum") and form.cleaned_data.get("anfangsDatum") < room_reserv.endDatum:
                                            if room_reserv.taeglich:
                                                if room_reserv.endZeit <= form.cleaned_data.get("anfangsZeit") or room_reserv.anfangsZeit > form.cleaned_data.get("endZeit"):
                                                    free_room = True
                                                else:
                                                    free_room = False
                                                    break
                                            else:
                                                free_room = False
                                                break
                                        else:
                                            if room_reserv.endDatum < form.cleaned_data.get("anfangsDatum"):
                                                free_room = True
                                            elif room_reserv.endDatum == form.cleaned_data.get("anfangsDatum"):
                                                if room_reserv.endZeit <= form.cleaned_data.get("anfangsZeit"):
                                                    free_room = True
                                                elif room_reserv.anfangsZeit >= form.cleaned_data.get("endZeit"):
                                                    free_room = True
                                                else:
                                                    free_room = False
                                                    break
                                            elif room_reserv.anfangsDatum == form.cleaned_data.get("endDatum"):
                                                if room_reserv.endZeit <= form.cleaned_data.get("anfangsZeit"):
                                                    free_room = True
                                                elif room_reserv.anfangsZeit >= form.cleaned_data.get("endZeit"):
                                                    free_room = True
                                                else:
                                                    free_room = False
                                                    break
                                    else:
                                        if room_reserv.anfangsDatum < form.cleaned_data.get("anfangsDatum") and form.cleaned_data.get("anfangsDatum") < room_reserv.endDatum:
                                            # ja, raum also nicht frei
                                            free_room = False
                                            break
                                        else:
                                            # nein, also raum eventuell frei, prüfen ob anfangsDatum nach oder am endDatum
                                            if room_reserv.endDatum < form.cleaned_data.get("anfangsDatum"):
                                                # Raum Frei
                                                free_room = True
                                            elif room_reserv.endDatum == form.cleaned_data.get("anfangsDatum"):
                                                # gleicher Tag
                                                if room_reserv.endZeit <= form.cleaned_data.get("anfangsZeit"):
                                                    # Raum Frei
                                                    free_room = True
                                                else:
                                                    # Raum ist nicht Frei
                                                    free_room = False
                                                    break
                                            elif room_reserv.anfangsDatum > form.cleaned_data.get("endDatum"):
                                                # Raum Frei
                                                free_room = True
                                            elif room_reserv.anfangsDatum == form.cleaned_data.get("endDatum"):
                                                if room_reserv.anfangsZeit > form.cleaned_data.get("endZeit"):
                                                    # Raum frei
                                                    free_room = True
                                                else:
                                                    # Raum nicht Frei
                                                    free_room = False
                                                    break
                                if free_room:
                                    free_rooms.append(room)
                            else:
                                free_rooms.append(room)
                    else:
                        free_rooms = models.Raum.objects.all()
        else:
            form = forms.ReservierungForm()
        print(free_rooms)
        return render(request, 'schilder/reservierung_form.html', {'form':form,
        'reserv':reserv,'free_rooms':free_rooms,'current_room':current_room,})
    else:
        return redirect('schilder:login', room=int(pk))
