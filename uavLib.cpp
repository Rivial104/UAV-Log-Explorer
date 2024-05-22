#include <stdio.h>

extern "C" {
    __declspec(dllexport) void calculateFlightTime(int capacity, double totalVoltage, double current[], double voltage[], int size, double flightTimeList[]) {
        double* percVoltage = new double[size];
        double* tempWork = new double[size];
        double* avaliableEnergy = new double[size];

        double totalEnergy = capacity * totalVoltage / 1000;

        for (int i = 0; i < size; i++) {
            percVoltage[i] = 100 * (totalVoltage - voltage[i]);
            tempWork[i] = current[i] * voltage[i];
            avaliableEnergy[i] = totalEnergy * percVoltage[i] / 100;
            flightTimeList[i] = (capacity * percVoltage[i]) / (current[i] * 60);
        }

        delete[] percVoltage;
        delete[] tempWork;
        delete[] avaliableEnergy;
    }

    __declspec(dllexport) void movingMean(double data[], int size, int k, double avgList[]) {
        int centerIndex = (k - 1) / 2;

        for (int i = 0; i < size; i++) {
            double sum = 0;
            int x = 0;
            for (int j = -centerIndex; j <= centerIndex; j++) {
                int index = i + j;
                if (index >= 0 && index < size) {
                    sum += data[index];
                    x++;
                }
            }
            avgList[i] = sum / x;
        }
    }
}
