import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
import ctypes
import os

# Parametry wejściowe
filename = 'data/d10.BFL.csv'
headerLine = 142  # Użytkownik wprowadza numer linii nagłówka
# initialZoom = float(input("Wprowadź procent początkowego przybliżenia (0-100%): "))
initialZoom=20
oxVal = 1 # Indeks wartości plotowanej na osi X (wybierz ten, gdzie znajduje się czas)
timeScale = 1000000
k = 7 # Zmienna do zmiany maski funkcji wygładzania wykresu (nieparzysta)

def main(filename, headerLine, initialZoom):

    #Pobieranie danych z pliku 
    header, data = load_csv(filename, headerLine)

    # Wyświetlanie nazw możliwych do wpisania zmiennych
    print("Możliwe zmienne do wykresowania:")
    for i, col_name in enumerate(header):
        print(f"{i}: {col_name}")

    # Pobierz indeksy kolumn od użytkownika
    columnIndices = input("Wprowadź indeksy kolumn do wykresowania (oddzielone spacją): ")
    columnIndices = list(map(int, columnIndices.split()))

    # Walidacja indeksów kolumn
    for index in columnIndices:
        if index < 0 or index >= len(header):
            print(f"Nieprawidłowy indeks kolumny: {index}")
            return
    
    #Tworzenie nowych list do nazw i wartosci danych z CSV
    columnNames = [header[index] for index in columnIndices]
    dataColumns = [data[index] for index in columnIndices]

    if oxVal < 0 or oxVal >= len(header):
        print(f"Nieprawidłowy indeks osi X: {oxVal}")
        return
        
    # Mapowanie czasu na wartość czytelną dla człowieka
    xData = mappedTime(data[oxVal])

    createUI(columnNames, dataColumns, xData, initialZoom)

# Funkcja do wczytania danych z pliku CSV
def load_csv(filename, line_number):
    with open(filename, 'r') as file:
        for _ in range(line_number - 1):
            next(file)
        header = next(file).strip().split(',')
        data = np.genfromtxt(file, delimiter=',', skip_header=0, unpack=True, filling_values=np.nan)
    return header, data

def mappedTime(timeData):
    startTime = timeData[0]
    mappedTime = (timeData-startTime)/timeScale
    return mappedTime

def createUI(names, values, xData, initialZoom):
    #Define initial values
    initAmp = 1
    centerOX = (xData[-1]+xData[0])/2

    fig, ax = plt.subplots(figsize=(12,8))

    # Rysowanie wykresow dla wybranych indeksow listy
    graphs = []
    for colName, y in zip(names, values):
        g, = ax.plot(xData, y,label=colName) 
        graphs.append(g)

    # Zmiana parametrów wykresu
    plt.subplots_adjust(0.1,0.25,0.75,0.9)
    plt.xlabel('Indeks')
    plt.ylabel('Wartość')
    plt.title('Wykres wybranych zmiennych')
    plt.legend()
    plt.grid(True)

    #Definicja komponentow UI
    # Slider OX
    timeAxis = fig.add_axes([0.1, 0.1, 0.65, 0.03])
    timeslider = Slider(
        ax=timeAxis,
        label='Czas [s]',
        valmin=xData[0],
        valmax=xData[-1],
        valinit=(xData[0]+xData[-1])/2,
    )

    # # Slider OY
    # ampAxis = fig.add_axes([0.04, 0.25, 0.0225, 0.63])
    # ampSlider = Slider(
    #     ax=ampAxis,
    #     label="Amplitude",
    #     valmin=0,
    #     valmax=10,
    #     valinit=initAmp,
    #     orientation="vertical"
    # )

    # Dodanie panelu sterowania
    axPanel = plt.axes([0.8, 0.25, 0.15, 0.65], facecolor='grey')
    axPanel.text(0.5, 0.95, 'Panel Sterowania', horizontalalignment='center', verticalalignment='center', transform=axPanel.transAxes, fontsize=12, fontweight='bold')
    axPanel.set_xticks([])
    axPanel.set_yticks([])
    axPanel.tick_params(axis='both', which='both', length=0)

    # Dodanie przycisków do przybliżania i oddalania
    btnWidth = 0.05
    btnHeigth = 0.04
    oxIn = plt.axes([0.825, 0.30, btnWidth, btnHeigth])
    btnZoomIn = Button(oxIn, '+', color='lightgoldenrodyellow', hovercolor='0.975')
    oxOut = plt.axes([0.88, 0.30, btnWidth, btnHeigth])
    btnZoomOut = Button(oxOut, '-', color='lightgoldenrodyellow', hovercolor='0.975')
    initialZoom = initialZoom/100

    # Dodanie checkboxów do wyboru zmiennych
    axCheck = plt.axes([0.8, 0.5, 0.15, 0.3], facecolor='lightgrey')
    btnCheck= CheckButtons(axCheck, names, [True] * len(colName))

    # Dodanie przycisku do wygładzania wykresów
    oxSmooth = plt.axes([0.8, 0.4, 0.15, 0.04], facecolor='lightgrey')
    btnSmooth = Button(oxSmooth, 'Smooth graphs', color='lightgoldenrodyellow', hovercolor='0.975')
    
    # Funkcja aktualizująca zakres OX (suwak oraz zoom)
    def updateOX(zoom, center):
        totalRange = xData[-1] - xData[0]
        visibleRange = totalRange * zoom 
        minOX = max(xData[0], center - visibleRange / 2)
        maxOX = min(xData[-1], center + visibleRange / 2)

        # Zablokowanie suwaka na granicy przedziału
        if maxOX >= xData[-1]:
            maxOX = xData[-1]
            minOX = maxOX - visibleRange
            timeslider.set_val(xData[-1] - visibleRange / 2)
        elif minOX <= xData[0]:
            minOX = xData[0]
            maxOX = minOX + visibleRange
            timeslider.set_val(xData[0] + visibleRange / 2)
        else:
            timeslider.set_active(True)

        ax.set_xlim([minOX, maxOX])
        fig.canvas.draw_idle()
        # print(f"Center: {center}, Zoom: {zoom}%, Range: ({minOX}, {maxOX})")

    def zoomIn(event):
        nonlocal initialZoom
        if initialZoom > 0.001:
            initialZoom -= 0.01
            updateOX(initialZoom, timeslider.val)

    def zoomOut(event):
        nonlocal initialZoom
        if initialZoom < 1:
            initialZoom += 0.01
            updateOX(initialZoom, timeslider.val)

    def toggleGraphs(label):
        index = colName.index(label)
        graphs[index].set_visible(not graphs[index].get_visible())
        plt.draw()

    def onSliderChange(val):
        updateOX(initialZoom, val)

    def smoothGraphs(event):
        for i, y in enumerate(values):
            if(isSmoothed):
                graphs[i].set_ydata(y)  
                isSmoothed = False           
            else:
                smoothed = moving_mean(y, k)
                graphs[i].set_ydata(smoothed)
                isSmoothed = True


        plt.draw()

    # Obsługa zdarzeń od przycisków i suwaka
    btnZoomIn.on_clicked(zoomIn)
    btnZoomOut.on_clicked(zoomOut)
    btnCheck.on_clicked(toggleGraphs)
    btnSmooth.on_clicked(smoothGraphs)
    timeslider.on_changed(onSliderChange)
    updateOX(initialZoom, centerOX)

    plt.show()

#Obsługa zewnętrznej aplikacji w C do wykonywania obliczeń na zbiorze danych
# Definicje dla obsługi zewnętrznej biblioteki w C
uavPath = os.path.abspath('uavLib.dll')
meanPath = os.path.abspath('meanLib.dll')

# # Sprawdzenie czy plik istnieje
# if not os.path.exists(uavPath):
#     raise FileNotFoundError(f"Plik DLL nie został znaleziony: {uavPath}")

# print(f"Loading DLL from: {uavPath}")
# try:
#     uavLib = ctypes.CDLL(uavPath)
#     print("DLL successfully loaded.")
# except Exception as e:
#     print(f"Error loading DLL: {e}")

# gcc -shared -o myfunc.dll myfunc.cpp - komenda do wykonania aplikacji c


meanLib = ctypes.CDLL(meanPath)

# # Definiowanie argumentów i typów zwracanych dla funkcji w C++
# uavLib.calculateFlightTime.argtypes = (
#     ctypes.c_int, 
#     ctypes.c_double, 
#     ctypes.POINTER(ctypes.c_double), 
#     ctypes.POINTER(ctypes.c_double), 
#     ctypes.c_int, 
#     ctypes.POINTER(ctypes.c_double)
# )

meanLib.movingMean.argtypes = (
    ctypes.POINTER(ctypes.c_double), 
    ctypes.c_int, 
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_double),
)

def moving_mean(data, k):
    size = len(data)
    data_array = (ctypes.c_double * size)(*data)
    print(type(data_array))
    avg_list = (ctypes.c_double * size)()
    
    meanLib.movingMean(data_array, size, k, avg_list)
    
    return np.array(avg_list)

# def calculate_flight_time(capacity, total_voltage, current, voltage):
#     size = len(current)
#     current_array = (ctypes.c_double * size)(*current)
#     voltage_array = (ctypes.c_double * size)(*voltage)
#     flight_time_list = (ctypes.c_double * size)()
    
#     uavLib.calculateFlightTime(capacity, total_voltage, current_array, voltage_array, size, flight_time_list)
    
#     return np.array(flight_time_list)

# # Przykład użycia
# data = [5, 7, 7, 4, 3, 6, 7]
# k = 5
# avg = moving_mean(data, k)
# print("Średnia krocząca:", avg)

# Wywołanie funkcji głównej z parametrami początkowymi
main(filename, headerLine, initialZoom)