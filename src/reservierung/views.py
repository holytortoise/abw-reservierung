from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.dates import WeekArchiveView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django import forms as d_forms
import datetime
from . import forms
from . import models
# Create your views here.


class ReservierungList(ListView):
    model = models.Reservierung
    context_object_name = 'reservierungen'


class ReservierungUpdate(LoginRequiredMixin, UpdateView):
    login_url = 'account:login'
    redirect_field_name = 'redirect_to'
    model = models.Reservierung
    fields = ['reservierterRaum', 'reservierungsGrund', 'anfangsDatum',
              'endDatum', 'anfangsZeit', 'endZeit']


class ReservierungDelete(LoginRequiredMixin, DeleteView):
    login_url = 'account:login'
    redirect_field_name = 'redirect_to'
    model = models.Reservierung
    success_url = reverse_lazy('reservierung:reservierung-list')
    template_name = 'reservierung/reservierung_delete.html'


class ReservierungDetail(DetailView):
    model = models.Reservierung
    context_object_name = 'reservierung'
    template_name = 'reservierung/reservierung_detail.html'


# View für das Darstellen der Reservierungen für die aktuelle Woche


def index(request):
    """
    Diese Funktion stellt auf der Index Seite die Tabelle für die aktuelle
    Woche. Und ermöglicht Durch die Wochen zu gehen
    """
    current_week = datetime.date.today().isocalendar()[1]
    current_year = datetime.date.today().isocalendar()[0]
    is_week = None
    if request.method == 'POST':
        jahr = int(request.POST['jahr'])
        woche = int(request.POST['woche'])
        # Wurde der rechte Button für nächste Woche gedrückt wird woche um 1
        # hochgezählt
        if request.POST.__contains__('next_week'):
            if woche == datetime.date(jahr, 12, 28).isocalendar()[1]:
                woche = 1
                jahr = jahr + 1
            else:
                woche = woche + 1
        # Wurde der linke Button gedrückt wird Woche heruntergezählt
        if request.POST.__contains__('last_week'):
            if woche == 1:
                jahr = jahr -1
                woche = datetime.date(jahr,12,28).isocalendar()[1]
            else:
                woche = woche - 1

    else:
        jahr = datetime.date.today().isocalendar()[0]
        woche = datetime.date.today().isocalendar()[1]
    # Ergibt True wenn die aktuelle Woche gleich der auf dem Schild angezeigten ist
    if woche == current_week and jahr == current_year:
        is_week = True
    if woche != current_week or jahr != current_year:
        is_week = False

    # Erzeuge daten für die Aktuelle Woche
    datum = str(jahr)+'-W'+str(woche)
    r = datetime.datetime.strptime(datum + '-0', "%Y-W%W-%w")
    start = r - datetime.timedelta(days=r.weekday())
    end = start + datetime.timedelta(days=6)
    start = start.strftime('%d.%m')
    end = end.strftime('%d.%m')
    rooms = models.Raum.objects.all()
    rooms_return = []
    for room in rooms:
        room_return = []
        reservierungen = models.Reservierung.objects.filter(
            reservierterRaum=room).order_by('anfangsDatum')
        for reservierung in reservierungen:
            if reservierung.anfangsDatum.isocalendar()[1] < woche and woche < reservierung.endDatum.isocalendar()[1]:
                room_return.append(reservierung)
            if ((reservierung.anfangsDatum.isocalendar()[1] == woche and reservierung.anfangsDatum.isocalendar()[0] == jahr)
                    or (reservierung.endDatum.isocalendar()[1] == woche and reservierung.endDatum.isocalendar()[0] == jahr)):
                room_return.append(reservierung)
        if len(room_return) != 0:
            rooms_return.append(room_return)
    if len(rooms_return) == 0:
        rooms_return = None
    context_dict = {'rooms_return':rooms_return,'reserv':reservierungen,
    'woche':woche,'jahr':jahr,'current_week':current_week,
    'current_year':current_year,'is_week':is_week,'start':start,'end':end}
    return render(request, 'index.html', context_dict)

# View um Reservierungen zu erstellen


@login_required(login_url='account:login')
def reservierung_form(request):
    """
    Diese Funktion ist für die neuen Reservierungen zuständig.
    Sie Überprüft ob der Raum für den gewünschten Zeitraum zur verfügung steht.
    Wenn ja wird eine neue Reservierung angelegt und der Nutzer wird zur Index
    seite Umgeleitet. Wenn nein dann werden dem Nutzer alternative Räume
    vorgeschlagen, welche zum gewünschten Zeitpunkt frei sind.
    """
    nutzer = request.user
    free_rooms = None
    reserv = None
    moeglich = False
    if request.method == 'POST':
        form = forms.ReservierungForm(data=request.POST)
        if form.is_valid():
            free_rooms = []
            reservierungen = models.Reservierung.objects.filter(
                reservierterRaum=form.cleaned_data.get("reservierterRaum"))
            if reservierungen.exists():
                for reservierung in reservierungen:
                    print(reservierung)
                    if reservierung.täglich:
                        # liegt form.anfangsDatum in einer bereits bestehenden
                        # reservierung
                        if reservierung.anfangsDatum < form.cleaned_data.get("anfangsDatum") and form.cleaned_data.get("anfangsDatum") < reservierung.endDatum:
                            # ist die reservierung täglich
                            if form.cleaned_data.get("täglich"):
                                # liegt die r.endZeit vor f.anfangsZeit oder
                                # r.anfangsZeit nach f.endZeit
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
                                    moeglich = False
                                    reserv = reservierung
                                    break
                        else:
                            # liegt f.anfangsDatum nach r.endDatum
                            if reservierung.endDatum < form.cleaned_data.get("anfangsDatum"):
                                moeglich = True
                            # liegen r.endDatum und f.anfangsDatum auf den
                            # gleichen Tag
                            elif reservierung.endDatum == form.cleaned_data.get("anfangsDatum"):
                                # liegt die r.endZeit vor f.anfangsZeit
                                if reservierung.endZeit <= form.cleaned_data.get("anfangsZeit"):
                                    # reservierung möglich
                                    moeglich = True
                                # liegt r.anfangsZeit nach f.endZeit
                                elif reservierung.anfangsZeit >= form.cleaned_data.get("endZeit"):
                                    # reservierung möglich
                                    moeglich = True
                                else:
                                    # Reservierung nicht möglich
                                    moeglich = False
                                    reserv = reservierung
                                    break
                            # ist r.anfangsDatum und f.endDatum am gleichen Tag
                            elif reservierung.anfangsDatum == form.cleaned_data.get("endDatum"):
                                if reservierung.endZeit <= form.cleaned_data.get("anfangsZeit"):
                                    # reservierung möglich
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
                            moeglich = False
                            reserv = reservierung
                            break
                        else:
                            # aktuelle reservierungsende liegt vor dem beginn
                            # der neuen
                            if reservierung.endDatum < form.cleaned_data.get("anfangsDatum"):
                                moeglich = True
                            # reservierungsende und beginn der neuen gleicher
                            # tag
                            elif reservierung.endDatum == form.cleaned_data.get("anfangsDatum"):
                                # reservierungs zeit ende vor oder gleich der
                                # neuen anfangszeit
                                if reservierung.endZeit <= form.cleaned_data.get("anfangsZeit"):
                                    moeglich = True
                                elif reservierung.anfangsZeit >= form.cleaned_data.get("endZeit"):
                                    moeglich = True
                                else:
                                    moeglich = False
                                    reserv = reservierung
                                    break
                            elif reservierung.anfangsDatum > form.cleaned_data.get("endDatum"):
                                moeglich = True
                            elif reservierung.anfangsDatum == form.cleaned_data.get("endDatum"):
                                if reservierung.anfangsZeit > form.cleaned_data.get("endZeit"):
                                    moeglich = True
                                else:
                                    moeglich = False
                                    reserv = reservierung
                                    break
            else:
                moeglich = True
            if moeglich:
                reserv = models.Reservierung()
                reserv.reserviert_von = request.user
                reserv.reservierterRaum = models.Raum.objects.get(
                    id=form.cleaned_data.get("reservierterRaum"))
                reserv.reservierungsGrund = form.cleaned_data.get(
                    "reservierungsGrund")
                reserv.anfangsDatum = form.cleaned_data.get("anfangsDatum")
                reserv.endDatum = form.cleaned_data.get("endDatum")
                reserv.anfangsZeit = form.cleaned_data.get("anfangsZeit")
                reserv.endZeit = form.cleaned_data.get("endZeit")
                reserv.täglich = form.cleaned_data.get("täglich")
                reserv.save()
                return HttpResponseRedirect(reverse('reservierung:index'))
            else:
                # return free rooms
                # restlichen reservierungen anschauen
                rooms = models.Raum.objects.exclude(
                    id=form.cleaned_data.get("reservierterRaum"))
                if rooms.exists():
                    for room in rooms:
                        room_reservs = models.Reservierung.objects.filter(
                            reservierterRaum=room)
                        # existieren reservierungen
                        if room_reservs.exists():
                            # für alle reservierungen
                            free_room = False
                            for room_reserv in room_reservs:
                                # liegt die reservierung in dem zeitraum einer
                                # bestehenden Reservierung
                                if form.cleaned_data.get("täglich"):
                                    if room_reserv.anfangsDatum < form.cleaned_data.get("anfangsDatum") and form.cleaned_data.get("anfangsDatum") < room_reserv.endDatum:
                                        if room_reserv.täglich:
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
                                        # nein, also raum eventuell frei,
                                        # prüfen ob anfangsDatum nach oder am
                                        # endDatum
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
    return render(request, 'reservierung/reservierung_form.html', {'form': form, 'reserv': reserv, 'free_rooms': free_rooms, })

# View zum anzeigen aller Reservierungen des angemeldeten nutzers


@login_required(login_url='account:login')
def reservierung_user(request):
    user = request.user
    rooms = models.Raum.objects.all()
    rooms_return = []

    for room in rooms:
        room_return = []
        reservierungen = models.Reservierung.objects.filter(
            reservierterRaum=room).order_by('anfangsDatum')
        for reservierung in reservierungen:
            if reservierung.reserviert_von == user:
                room_return.append(reservierung)
        rooms_return.append(room_return)
    return render(request, 'reservierung/reservierung_user.html', {'user': user, 'rooms_return': rooms_return, })
